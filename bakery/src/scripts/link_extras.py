"""
Replaces legacy module ids in links to external modules with
uuids from the target module and corresponding canonical book.
"""

import sys
import json
import requests

from lxml import etree
from urllib.parse import unquote


MAX_RETRIES = 2


def load_canonical_list(canonical_list):
    with open(canonical_list) as canonical_file:
        canonical_books = json.load(canonical_file)["canonical_books"]
        canonical_ids = [book["uuid"] for book in canonical_books]

    return canonical_ids


def load_assembled_collection(input_dir):
    """load assembled collection"""
    assembled_collection = f"{input_dir}/collection.assembled.xhtml"
    return etree.parse(assembled_collection)


def find_legacy_id(node):
    """find legacy module id"""
    link = node.attrib["href"]
    parsed = unquote(link)

    return parsed.lstrip("/contents/").rstrip()


def init_requests_session(max_retries):
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
    session.mount("https://", adapter)
    return session


def get_target_uuid(session, server, legacy_id):
    """get target module uuid"""
    req = session.get(f"https://{server}/content/{legacy_id}")
    req.raise_for_status()

    return req.url.split("/")[-1]


def get_containing_books(session, server, module_uuid):
    """get list of books containing module"""
    req = session.get(f"https://{server}/extras/{module_uuid}")
    req.raise_for_status()

    content = req.json()

    return [book["ident_hash"].split("@")[0] for book in content["books"]]


def match_canonical_book(canonical_ids, containing_books):
    """match uuid in canonical book list"""
    if len(containing_books) == 0:
        raise Exception("No containing books")

    if len(containing_books) == 1:
        return containing_books[0]

    try:
        match = next(uuid
                     for uuid in canonical_ids
                     if uuid in containing_books)
    except StopIteration:
        raise Exception("Multiple containing books, no canonical match!")

    return match


def patch_link(node, module_uuid, match):
    """replace legacy link"""
    node.attrib["href"] = f"/contents/{module_uuid}"
    node.attrib["data-book-uuid"] = match


def save_linked_collection(output_dir, doc):
    """write modified output"""
    linked_collection = f"{output_dir}/collection.linked.xhtml"
    with open(f"{linked_collection}", "wb") as f:
        doc.write(f, encoding="utf-8", xml_declaration=True)


def main():
    data_dir, server, canonical_list = sys.argv[1:4]

    # define the canonical books
    canonical_ids = load_canonical_list(canonical_list)

    doc = load_assembled_collection(data_dir)

    # look up uuids for external module links
    for node in doc.xpath(
        '//x:a[@href and starts-with(@href, "/contents/m")]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    ):

        legacy_id = find_legacy_id(node)

        session = init_requests_session(MAX_RETRIES)

        module_uuid = get_target_uuid(session, server, legacy_id)
        containing_books = get_containing_books(session, server, module_uuid)

        match = match_canonical_book(canonical_ids, containing_books)
        patch_link(node, module_uuid, match)

    save_linked_collection(data_dir, doc)


if __name__ == "__main__":
    main()
