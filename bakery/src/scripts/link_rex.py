import sys
from lxml import etree
from pathlib import Path
import json


def update_doc_links(doc, book_slugs_by_uuid):
    """Modify links in doc"""

    def _rex_url_builder(book, page):
        return f"http://openstax.org/books/{book}/pages/{page}"

    external_link_elems = doc.xpath(
        '//x:a[@href and starts-with(@href, "./")]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"}
    )
    for node in external_link_elems:
        # This an inter-book link defined by data-book-uuid attrib
        if node.attrib.get("data-book-uuid"):
            print('BEFORE!!:')
            print(node.attrib)
            external_book_uuid = node.attrib["data-book-uuid"]
            external_book_slug = book_slugs_by_uuid[external_book_uuid]
            external_page_slug = node.attrib["data-page-slug"]
            node.attrib["href"] = _rex_url_builder(
                external_book_slug, external_page_slug
            )
            print('AFTER!!:')
            print(node.attrib)


def main():
    """Main function"""
    xhtml_file = Path(sys.argv[1]).resolve(strict=True)
    book_slugs_file = Path(sys.argv[2]).resolve(strict=True)
    # out_dir = Path(sys.argv[3]).resolve(strict=True)

    # Build map of book UUIDs to slugs that can be used to construct both
    # inter-book and intra-book links
    with book_slugs_file.open() as json_file:
        json_data = json.load(json_file)
        book_slugs_by_uuid = {
            elem["uuid"]: elem["slug"] for elem in json_data
        }

    doc = etree.parse(xhtml_file)
    update_doc_links(
        doc,
        book_slugs_by_uuid
    )
    # doc.write(str(out_dir / xhtml_file.name), encoding="utf8")


if __name__ == "__main__":
    main()
