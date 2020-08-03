"""
Replaces legacy module ids in links to external modules with
uuids from the target module and corresponding canonical book.
"""

import sys
import json
from lxml import etree
import requests


def main():
    data_dir, server, canonical_list = sys.argv[1:4]

    # define the canonical books
    with open(canonical_list) as canonical_file:
        canonical_books = json.load(canonical_file)["canonical_books"]
        canonical_ids = [book["uuid"] for book in canonical_books]

    # load assembled collection
    assembled_collection = f"{data_dir}/collection.assembled.xhtml"
    doc = etree.parse(assembled_collection)

    # look up uuids for external module links
    for node in doc.xpath(
        '//x:a[@href and starts-with(@href, "/contents/m")]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    ):
        # find legacy module id
        link = node.attrib["href"]
        module_id = link.lstrip("/contents/")

        # get target module uuid
        req = requests.get(f"https://{server}/content/{module_id}")
        req.raise_for_status()

        module_uuid = req.url.split("/")[-1]

        # get list of books containing module
        req = requests.get(f"https://{server}/extras/{module_uuid}")
        req.raise_for_status()

        content = req.json(req.content)
        containing_books = {
            book["ident_hash"].split("@")[0]: book["title"]
            for book in content["books"]
        }

        # match uuid in canonical book list
        match = None
        for book_uuid in canonical_ids:
            if book_uuid in containing_books:
                match = book_uuid
                break

        if match is None:
            if len(containing_books) > 1:
                # TODO: more specific exception
                raise Exception(
                    "Multiple containing books, no canonical match!")
            [match] = containing_books

        node.attrib["href"] = f"/contents/{module_uuid}"
        node.attrib["data-book-uuid"] = match
        break

    linked_collection = f"{data_dir}/collection.linked.xhtml"
    with open(f"{linked_collection}", "wb") as f:
        doc.write(f, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
