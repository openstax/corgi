from typing import List, Dict, Any, Optional
from itertools import groupby

from httpx import HTTPStatusError
from sqlalchemy.orm import Session, lazyload
from sqlalchemy import or_, delete, select, and_
from app.core.errors import CustomBaseError
from app.data_models.models import BaseApprovedBook, RequestApproveBook
from app.core import config
from httpx import AsyncClient
from app.db.schema import (
    ApprovedBook,
    Book,
    CodeVersion,
    Commit,
    Repository,
    Consumer,
)


async def get_rex_books(client: AsyncClient):
    try:
        response = await client.get(
            config.REX_WEB_RELEASE_URL, headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        release_json = response.json()
        return release_json["books"]
    except HTTPStatusError as he:
        raise CustomBaseError(
            f"Failed to fetch rex release: {he.response.status_code}"
        )


def get_rex_book_versions(rex_books: Dict[str, Any], book_uuids: List[str]):
    rex_book_versions: List[BaseApprovedBook] = []
    for book_uuid in book_uuids:
        if book_uuid not in rex_books:
            continue
        rex_book = rex_books[book_uuid]
        version = rex_book.get("defaultVersion", None)
        assert (
            version is not None
        ), f"Could not get defaultVersion for {book_uuid}"
        rex_book_versions.append(
            BaseApprovedBook(commit_sha=version, uuid=book_uuid)
        )
    return rex_book_versions


def remove_old_versions(
    db: Session,
    consumer_id: int,
    to_add: List[RequestApproveBook],
    to_keep: List[BaseApprovedBook] = [],
):
    # Default: Remove all previous versions of the books in the set
    query = (
        select(ApprovedBook)
        .options(lazyload("*"))
        .join(Book)
        .where(Book.uuid.in_([b.uuid for b in to_add]))
        .where(ApprovedBook.consumer_id == consumer_id)
    )
    if to_keep:
        # Keep a subset (`~or_` is like `if not any(...)`)
        query = query.join(Commit).where(
            ~or_(
                *[
                    and_(
                        Book.uuid == entry.uuid,
                        Commit.sha.startswith(entry.commit_sha),
                    )
                    for entry in to_keep
                ]
            )
        )
    to_delete = db.scalars(query).all()
    # NOTE: If to_delete is empty, the condition will be True (delete all)
    if to_delete:
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
    db_books_by_uuid: Dict[str, Book],
    to_add: List[RequestApproveBook],
    to_keep: List[BaseApprovedBook] = [],
):
    consumer_id = db.scalars(
        select(Consumer.id).where(Consumer.name == consumer_name)
    ).first()
    if consumer_id is None:
        raise CustomBaseError(f"Unsupported consumer: {consumer_name}")
    remove_old_versions(db, consumer_id, to_add, to_keep)
    for entry in to_add:
        db_book = db_books_by_uuid.get(entry.uuid, None)
        if db_book is None:
            raise CustomBaseError(f"Could not find book: {entry.uuid}")
        # insert or get code_version
        db_code_version = get_or_add_code_version(db, entry.code_version)
        # insert entry
        db_approved_book = ApprovedBook(
            book_id=db_book.id,
            consumer_id=consumer_id,
            code_version_id=db_code_version.id,
        )
        db.merge(db_approved_book)


def guess_consumer(book_slug: str) -> str:
    if book_slug.endswith("-ancillary") or book_slug.endswith("-ancillaries"):
        return "ancillary"
    return "REX"


async def add_new_entries(
    db: Session,
    to_add: List[RequestApproveBook],
    client: AsyncClient,
):
    if not to_add:  # pragma: no cover
        raise CustomBaseError("No entries to add")
    for uuid, items in groupby(to_add, lambda o: o.uuid):
        collected = tuple(items)
        if len(collected) > 1:  # pragma: no cover
            raise CustomBaseError(
                f"Found multiple versions for {uuid} - ({collected})"
            )
    db_books = db.scalars(
        select(Book)
        .options(lazyload("*"))
        .join(Commit)
        .where(
            or_(*[
                and_(
                    Book.uuid == entry.uuid,
                    Commit.sha == entry.commit_sha
                )
                for entry in to_add
            ])
        )
    ).all()
    db_books_by_uuid = {
        dbb.uuid: dbb
        for dbb in db_books
    }
    book_info_by_consumer = groupby(
        to_add, lambda entry: guess_consumer(db_books_by_uuid[entry.uuid].slug)
    )
    try:
        for consumer, entries in book_info_by_consumer:
            to_keep = []
            if consumer == "REX":
                rex_books = await get_rex_books(client)
                to_keep = get_rex_book_versions(
                    rex_books, [b.uuid for b in to_add]
                )
            update_versions_by_consumer(
                db, consumer, db_books_by_uuid, list(entries), to_keep
            )
        db.commit()
    except Exception:
        db.rollback()
        raise


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
        query = join(query, Book, Commit).where(Commit.sha == version)
    if code_version:
        query = join(query, CodeVersion).where(
            CodeVersion.version <= code_version
        )

    return db.scalars(query).all()
