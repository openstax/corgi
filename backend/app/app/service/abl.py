import asyncio
from base64 import b64decode

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

    # commit_sha
    refs = requests.get(
        f"{repos_url}/{repo_name}/git/refs/heads/{version}", headers=headers)
    refs_obj = refs.json()
    commit_sha = refs_obj["object"]["sha"]

    # committed_at
    commit = requests.get(
        f"{repos_url}/{repo_name}/commits/{commit_sha}", headers=headers)
    commit_obj = commit.json()
    commit_timestamp = commit_obj["commit"]["committer"]["date"]
    fixed_timestamp = f"{commit_timestamp[:-1]}+00:00"

    # style
    meta_inf = get_git_file(owner, repo_name, "META-INF/books.xml", version)
    meta = etree.fromstring(meta_inf)
    style = meta.xpath(
        f"//*[local-name()='book'][@slug='{slug}']")[0].attrib["style"]

    # uuid
    collection_xml = get_git_file(
        owner, repo_name, f"/collections/{slug}.collection.xml", version)
    collection = etree.fromstring(collection_xml)
    uuid = collection.xpath("//*[local-name()='uuid']")[0].text

    metadata = {
        "commit_sha": commit_sha,
        "committed_at": fixed_timestamp,
        "uuid": uuid,
        "style": style
    }

    return metadata


def get_git_file(owner, repo_name, path, version):
    contents_url = (f"https://api.github.com/repos/{owner}/"
                    f"{repo_name}/contents/{path}?ref={version}")
    git_metadata = requests.get(contents_url, headers=headers)
    base64_content = git_metadata.json()["content"]
    content = b64decode(base64_content)
    return content
