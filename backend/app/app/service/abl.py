import asyncio

import requests
from app.core import config
from lxml import etree


headers = {"authorization": f"token {config.GITHUB_API_TOKEN}"}


async def get_abl_info(repo_name, slug, version="main"):
    loop = asyncio.get_running_loop()
    metadata = await loop.run_in_executor(None, get_book_metadata,
                                          repo_name, slug, version)
    metadata["line_number"] = await loop.run_in_executor(
        None, get_abl_line_number, repo_name)

    return metadata


def get_abl_line_number(repo_name):
    abl_url = ("https://raw.githubusercontent.com/openstax/"
               "content-manager-approved-books/main/approved-book-list.json")
    abl_file = requests.get(abl_url).text.split("\n")
    for line_number, line in enumerate(abl_file):
        if repo_name in line:
            return line_number + 1
    return 1


def get_book_metadata(repo_name, slug, version="main"):
    owner = "openstax"
    repos_url = f"https://api.github.com/repos/{owner}"

    # commit_sha and committed_at
    commit = requests.get(
        f"{repos_url}/{repo_name}/commits/{version}", headers=headers)
    commit_obj = commit.json()
    commit_sha = commit_obj["sha"]
    commit_timestamp = commit_obj["commit"]["committer"]["date"]
    fixed_timestamp = f"{commit_timestamp[:-1]}+00:00"

    # books
    meta_inf = get_git_file(owner, repo_name, "META-INF/books.xml", version)
    meta = etree.fromstring(meta_inf)
    books = []
    for el in meta.xpath(f"//*[local-name()='book']"):
        book = {
            k: el.attrib[k] for k in ("slug", "style")
        }
        slug = book["slug"]

        collection_xml = get_git_file(
            owner, repo_name, f"/collections/{slug}.collection.xml", version)
        collection = etree.fromstring(collection_xml)
        uuid = collection.xpath("//*[local-name()='uuid']")[0].text
        book["uuid"] = uuid

        books.append(book)

    metadata = {
        "commit_sha": commit_sha,
        "committed_at": fixed_timestamp,
        "books": books
    }

    return metadata


def get_git_file(owner, repo_name, path, version):
    contents_url = (f"https://api.github.com/repos/{owner}/"
                    f"{repo_name}/contents/{path}?ref={version}")
    git_metadata = requests.get(contents_url, headers=dict(
        **headers, accept="application/vnd.github.v3.raw"))
    return git_metadata.text
