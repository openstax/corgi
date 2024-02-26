from httpx import AsyncClient
from app.core import config
from lxml import etree
import json
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.github.api import get_file
from app.core.config import REX_WEB_REPO, REX_WEB_BOOKS_PATH, GITHUB_ORG
from app.github import AuthenticatedClient
from app.db.schema import ApprovedBook, Commit


async def get_rex_books(client: AuthenticatedClient):
    response = await get_file(
        client,
        REX_WEB_REPO,
        GITHUB_ORG,
        "main",
        REX_WEB_BOOKS_PATH
    )
    response["json"] = json.loads(response["text"])
    return response


async def add_new_entry(
    db: Session,
    book_uuids: List[str],
    code_version: str,
    client: AuthenticatedClient,
):
    rex_books = await get_rex_books(client)
    rex_books_json = rex_books["json"]
    rex_short_shas = [item["defaultVersion"] for item in rex_books_json.values()]
    db.delete()
    new_commit = db.query(Commit).where(Commit.commit_sha == commit_sha).first()
    # approved_commits = db.query(ApprovedCommit).all()
    rex_commits = db.query(Commit).where(
        or_(*[Commit.sha.like(substring + '%') for substring in rex_short_shas])
    )
    # Condition for removing an entry
    #   Entry is not in rex books config and it is older than the one they use
    commit_by_book_uuid = {}
    for commit in rex_commits:
        for book in commit.books:
            commit_by_book_uuid.setdefault(book.uuid, []).append(commit)
    for book in new_commit.books:
        commit_by_book_uuid.setdefault(book.uuid, []).append(commit)
    # TODO: delete extra entries or clear and repopulate table
    


def remove_approved_commit(db: Session, commit_sha: str):
    pass


def map_rex_to_database(rex_books):
    for book_uuid, info in rex_books.items():
        version = info.get("defaultVersion", None)
        assert version is not None, f"Expected defaultVersion in {book_uuid}"



async def get_abl_info(repo_name, version="main"):
    async with AsyncClient() as client:
        if config.GITHUB_API_TOKEN:
            client.headers.update({
                "Authorization": f"token {config.GITHUB_API_TOKEN}"
            })
        metadata = await get_book_metadata(client, repo_name, version)
        metadata["line_number"] = await get_abl_line_number(client, repo_name)

    return metadata


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
