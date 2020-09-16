"""Make modifications to page XHTML files specific to GDoc outputs
"""
import sys
from lxml import etree
from pathlib import Path
import json


def gen_page_slug_resolver(metadata_files):
    """Generate a page slug resolver function"""
    page_slugs_by_uuid = {}
    metadata_file_by_uuid = {
        filepath.name.split(":")[1].split("-metadata")[0]:
            filepath for filepath in metadata_files
    }

    def _get_page_slug(page_uuid):
        """Lookup a page slug by UUID using metadata files"""
        cached_slug = page_slugs_by_uuid.get(page_uuid)
        if cached_slug:
            return cached_slug

        with metadata_file_by_uuid[page_uuid].open() as json_file:
            json_data = json.load(json_file)
            page_slug = json_data.get("slug")
            page_slugs_by_uuid[page_uuid] = page_slug

        if not page_slug:
            raise ValueError(f"Unable to resolve page slug for {page_uuid}")

        return page_slug

    return _get_page_slug


def update_doc_links(doc, book_uuid, book_slugs_by_uuid, page_slug_resolver):
    """Modify links in doc"""

    def _rex_url_builder(book, page, fragment):
        base_url = f"http://openstax.org/books/{book}/pages/{page}"
        if fragment:
            return f"{base_url}#{fragment}"
        else:
            return base_url

    for node in doc.xpath(
        '//x:a[@href and starts-with(@href, "/contents/")]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"}
    ):
        page_link = node.attrib["href"].split("/")[-1]
        # Link may have fragment
        if "#" in page_link:
            page_uuid, page_fragment = page_link.split("#")
        else:
            page_uuid = page_link
            page_fragment = None

        # This is either an intra-book link or inter-book link. We can
        # differentiate the latter by data-book-uuid attrib).
        if node.attrib.get("data-book-uuid"):
            external_book_uuid = node.attrib["data-book-uuid"]
            external_book_slug = book_slugs_by_uuid[external_book_uuid]
            external_page_slug = node.attrib["data-page-slug"]
            node.attrib["href"] = _rex_url_builder(
                external_book_slug, external_page_slug, page_fragment
            )
        else:
            book_slug = book_slugs_by_uuid[book_uuid]
            page_slug = page_slug_resolver(page_uuid)
            node.attrib["href"] = _rex_url_builder(
                book_slug, page_slug, page_fragment
            )


def main():
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    out_dir = Path(sys.argv[2]).resolve(strict=True)
    book_slugs_file = Path(sys.argv[3]).resolve(strict=True)

    xhtml_files = in_dir.glob("*@*.xhtml")
    metadata_files = in_dir.glob("*@*-metadata.json")
    book_metadata = in_dir / "collection.toc-metadata.json"

    # Get the UUID of the book being processed
    with book_metadata.open() as json_file:
        json_data = json.load(json_file)
        book_uuid = json_data["id"]

    # Build map of book UUIDs to slugs that can be used to construct both
    # inter-book and intra-book links
    with book_slugs_file.open() as json_file:
        json_data = json.load(json_file)
        book_slugs_by_uuid = {
            elem["uuid"]: elem["slug"] for elem in json_data
        }

    # Build a slug resolver for pages in the book being processed
    page_slug_resolver = gen_page_slug_resolver(metadata_files)

    for xhtml_file in xhtml_files:
        doc = etree.parse(str(xhtml_file))
        update_doc_links(
            doc,
            book_uuid,
            book_slugs_by_uuid,
            page_slug_resolver
        )
        doc.write(str(out_dir / xhtml_file.name), encoding="utf8")


if __name__ == "__main__":
    main()
