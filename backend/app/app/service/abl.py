from app.core.errors import CustomBaseError
# from app.data_models.models import RequestApproveBook
from httpx import AsyncClient, HTTPStatusError
from app.core import config
from lxml import etree
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session, lazyload
from sqlalchemy import or_, delete, select, desc, and_
from app.core.config import GITHUB_ORG
from app.github import AuthenticatedClient
from app.db.schema import ApprovedBook, Book, Commit, Repository, Consumer


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


# async def cleanup_rex_versions(
#     db: Session,
#     book_info: List[BookInfo],
#     client: AuthenticatedClient,
# ):
#     rex_book_uuids = [
#         b.uuid
#         for b in book_info
#         if b.platform == "REX"
#     ]
#     if len(rex_book_uuids) == 0:
#         return
#     rex_books = await get_rex_books(client)
#     rex_book_versions = get_rex_book_versions(rex_books, rex_book_uuids)
#     to_delete = db.scalars(
#         select(ApprovedBook).options(lazyload("*"))
#             .join(Book)
#             .join(Commit)
#             .where(ApprovedBook.platform == "REX")
#             .where(Book.uuid.in_())
#             .where(
#                 ~or_(*[
#                     and_(
#                         Book.uuid == rex_version["uuid"],
#                         Commit.sha.startswith(rex_version["sha"])
#                     )
#                     for rex_version in rex_book_versions
#                 ])
#             )
#     )
#     db.execute(
#         delete(ApprovedBook).where(ApprovedBook.book_id.in_([
#             c.id for c in to_delete
#         ]))
#     )


# async def add_new_entry(
#     db: Session,
#     book_info: List[BookInfo],
#     client: AuthenticatedClient,
# ):  
#     try:
#         await cleanup_rex_versions(db, book_info, client)
#         new_book_ids = db.scalars(
#             select(Book.id).options(lazyload("*"))
#                 .join(Commit)
#                 .where(
#                     or_(*[
#                         Book.uuid == b.uuid and
#                         Commit.sha == b.commit_sha
#                         for b in book_info
#                     ])
#                 )
#         )
#     except Exception:
#         db.rollback()
#         raise
    
#     # approved_commits = db.query(ApprovedCommit).all()
#     rex_commits = db.query(Commit).where(
#         or_(*[Commit.sha.like(substring + '%') for substring in rex_short_shas])
#     )
#     # Condition for removing an entry
#     #   Entry is not in rex books config and it is older than the one they use
#     commit_by_book_uuid = {}
#     for commit in rex_commits:
#         for book in commit.books:
#             commit_by_book_uuid.setdefault(book.uuid, []).append(commit)
#     for book in new_commit.books:
#         commit_by_book_uuid.setdefault(book.uuid, []).append(commit)
#     # TODO: delete extra entries or clear and repopulate table
    

def remove_approved_commit(db: Session, commit_sha: str):
    pass


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

async def get_abl_info_database(db: Session, consumer: Optional[str] = None, repo_name: Optional[str] = None, version: Optional[str] = None):
    query = db.query(ApprovedBook).options(lazyload("*"))
    if consumer:
        query = query.join(Consumer)
    if version:
        query = query.join(Book).join(Commit)
    if repo_name:
        query = query.join(Repository)

    if consumer:
        query = query.filter(Consumer.name == consumer)
    if repo_name:
        query = query.filter(Repository.name == repo_name)
    if version:
        query = query.filter(Commit.sha == version)

    return query.all()


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
