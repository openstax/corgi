from typing import List, Dict, Any, Optional

from lxml import etree
from httpx import AsyncClient, HTTPStatusError
from sqlalchemy.orm import Session, lazyload
from sqlalchemy import or_, delete, select, desc, and_
from app.core.errors import CustomBaseError
from app.data_models.models import RequestApproveBook, ResponseApprovedBook
from app.core import config
from app.core.config import GITHUB_ORG
from app.github import AuthenticatedClient
from app.db.schema import ApprovedBook, Book, CodeVersion, Commit, Repository, Consumer


async def get_rex_books(client: AuthenticatedClient):
    try:
        response = await client.get(
            "https://openstax.org/rex/release.json",
            headers={ "Accept": "application/json" }
        )
        response.raise_for_status()
        release_json = response.json()
        return release_json["books"]
    except HTTPStatusError as he:
        raise CustomBaseError(
            f"Failed to fetch rex release: {he.response.status_code}"
        )


def get_rex_book_versions(rex_books: Dict[str, Any], book_uuids: List[str]):
    rex_book_versions = []
    for book_uuid in book_uuids:
        if book_uuid not in rex_books:
            continue
        rex_book = rex_books[book_uuid]
        version = rex_book.get("defaultVersion", None)
        assert version is not None, \
            f"Could not get defaultVersion for {book_uuid}"
        rex_book_versions.append({"uuid": book_uuid, "sha": version})
    return rex_book_versions


def group_by(arr, key):
    groups = {}
    for obj in arr:
        value = key(obj)
        groups.setdefault(value, []).append(obj)
    return groups


def remove_old_versions(
    db: Session,
    consumer_id: int,
    to_keep: List[RequestApproveBook] = [],
):
    query = (
        select(ApprovedBook)
        .options(lazyload("*"))
        .where(ApprovedBook.consumer_id == consumer_id)
    )
    if to_keep:
        query = (
            query.join(Book)
            .join(Commit)
            .where(
                ~or_(
                    *[
                        and_(
                            Book.uuid == version.uuid,
                            Commit.sha.startswith(version.commit_sha),
                        )
                        for version in to_keep
                    ]
                )
            )
        )
    to_delete = db.scalars(query).all()
    if len(to_delete):
        condition = or_(
            *[
                and_(
                    ApprovedBook.consumer_id == approved_book.consumer_id,
                    ApprovedBook.book_id == approved_book.book_id,
                    ApprovedBook.code_version_id
                    == approved_book.code_version_id,
                )
                for approved_book in to_delete
            ]
        )
        db.execute(delete(ApprovedBook).where(condition))


def get_or_add_code_version(
    db: Session,
    code_version: str,
):
    db_code_version = db.scalars(
        select(CodeVersion).where(CodeVersion.version == code_version)
    ).first()
    if db_code_version is None:
        db_code_version = CodeVersion(version=code_version)
        db.add(db_code_version)
        db.flush()  # populate id
    return db_code_version


def update_versions_by_consumer(
    db: Session,
    consumer_name: str,
    to_add: List[RequestApproveBook],
    to_keep: List[RequestApproveBook] = [],
):
    consumer_id = db.scalars(
        select(Consumer.id).where(Consumer.name == consumer_name)
    ).first()
    if consumer_id is not None:
        remove_old_versions(db, consumer_id, to_keep)
    for entry in to_add:
        db_book = db.scalars(
            select(Book)
            .options(lazyload("*"))
            .join(Commit)
            .where(Book.uuid == entry.uuid)
            .where(Commit.sha == entry.commit_sha)
        ).first()
        # insert or get code_version
        db_code_version = get_or_add_code_version(db, entry.code_version)
        # insert entry
        db_approved_book = ApprovedBook(
            book_id=db_book.id,
            consumer_id=consumer_id,
            code_version_id=db_code_version.id,
        )
        db.add(db_approved_book)


async def add_new_entries(
    db: Session,
    book_info: List[RequestApproveBook],
    client: AuthenticatedClient,
):  
    book_info_by_consumer = group_by(book_info, lambda o: o.consumer)
    try:
        for consumer, entries in book_info_by_consumer.items():
            to_keep = []
            if consumer == "REX":
                to_keep = []  # Get the versions REX uses
            update_versions_by_consumer(db, consumer, entries, to_keep)
        db.commit()
    except Exception:
        db.rollback()
        raise


def map_rex_to_database(rex_books):
    for book_uuid, info in rex_books.items():
        version = info.get("defaultVersion", None)
        assert version is not None, f"Expected defaultVersion in {book_uuid}"


async def get_abl_info_github(repo_name, version="main"):
    async with AsyncClient() as client:
        if config.GITHUB_API_TOKEN:
            client.headers.update({
                "Authorization": f"token {config.GITHUB_API_TOKEN}"
            })
        metadata = await get_book_metadata(client, repo_name, version)
        metadata["line_number"] = await get_abl_line_number(client, repo_name)

    return metadata


def stable_join():
    joined = set()
    def inner(query, *tables):
        for table in (t for t in tables if t not in joined):
            query = query.join(table)
            joined.add(table)
        return query
    return inner


def get_abl_info_database(
    db: Session,
    consumer: Optional[str] = None,
    repo_name: Optional[str] = None,
    version: Optional[str] = None,
    code_version: Optional[str] = None,
):
    query = select(ApprovedBook).options(lazyload("*"))
    join = stable_join()
    if consumer:
        query = join(query, Consumer).where(Consumer.name == consumer)
    if repo_name:
        query = join(query, Book, Commit, Repository).where(
            Repository.name == repo_name
        )
    if version:
        query = join(query, Book, Commit).where(
            Commit.sha == version
        )
    if code_version:
        query = join(query, CodeVersion).where(
            CodeVersion.version <= code_version
        )

    return db.scalars(query).all()


async def get_abl_line_number(client, repo_name):
    abl_url = ("https://raw.githubusercontent.com/openstax/"
               "content-manager-approved-books/main/approved-book-list.json")
    response = await client.get(abl_url)
    response.raise_for_status()
    abl_file = response.text.split("\n")
    for line_number, line in enumerate(abl_file):
        if repo_name in line:
            return line_number + 1
    return 1


async def get_book_metadata(client, repo_name, version="main"):
    owner = "openstax"
    repos_url = f"https://api.github.com/repos/{owner}"

    # commit_sha and committed_at
    commit = await client.get(
        f"{repos_url}/{repo_name}/commits/{version}")
    commit_obj = commit.json()
    commit_sha = commit_obj["sha"]
    commit_timestamp = commit_obj["commit"]["committer"]["date"]
    fixed_timestamp = f"{commit_timestamp[:-1]}+00:00"

    # books
    meta_inf = await get_git_file(client, owner, repo_name, "META-INF/books.xml", version)
    meta = etree.fromstring(meta_inf.encode(), parser=None)
    books = []
    for el in meta.xpath(f"//*[local-name()='book']"):
        book = {
            k: el.attrib[k] for k in ("slug", "style")
        }
        slug = book["slug"]

        collection_xml = await get_git_file(
            client, owner, repo_name, f"/collections/{slug}.collection.xml",
            version)
        collection = etree.fromstring(collection_xml.encode(), parser=None)
        uuid = collection.xpath("//*[local-name()='uuid']")[0].text
        book["uuid"] = uuid

        books.append(book)

    metadata = {
        "commit_sha": commit_sha,
        "committed_at": fixed_timestamp,
        "books": books
    }

    return metadata


async def get_git_file(client, owner, repo_name, path, version):
    contents_url = (f"https://api.github.com/repos/{owner}/"
                    f"{repo_name}/contents/{path}?ref={version}")
    git_metadata = await client.get(contents_url, headers={
        "Accept": "application/vnd.github.v3.raw"})
    return git_metadata.text
