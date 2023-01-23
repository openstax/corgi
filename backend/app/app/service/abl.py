from httpx import AsyncClient
from app.core import config
from lxml import etree


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
    meta = etree.fromstring(meta_inf, parser=None)
    books = []
    for el in meta.xpath(f"//*[local-name()='book']"):
        book = {
            k: el.attrib[k] for k in ("slug", "style")
        }
        slug = book["slug"]

        collection_xml = await get_git_file(
            client, owner, repo_name, f"/collections/{slug}.collection.xml",
            version)
        collection = etree.fromstring(collection_xml, parser=None)
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
