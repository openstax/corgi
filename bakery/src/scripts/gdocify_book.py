"""Make modifications to page XHTML files specific to GDoc outputs
"""
import sys
from lxml import etree
from pathlib import Path
import requests
import json


MAX_RETRIES = 2
CMS_BASE_URL = "https://openstax.org/apps/cms/api/v2/pages"


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


def gen_book_slug_resolver(session):
    """Generate a book slug resolver function"""
    book_slugs_by_uuid = {}

    def _get_book_slug(book_uuid):
        """Lookup a book slug by UUID using CMS"""
        cached_slug = book_slugs_by_uuid.get(book_uuid)
        if cached_slug:
            return cached_slug

        request_params = {
            "type": "books.Book",
            "fields": "slug,cnx_id",
            "cnx_id": book_uuid
        }
        response = session.get(CMS_BASE_URL, params=request_params)
        response.raise_for_status()
        data = response.json()

        for item in data.get("items", []):
            if item["cnx_id"] == book_uuid:
                slug = item["meta"]["slug"]
                book_slugs_by_uuid[book_uuid] = slug
                return slug

        raise ValueError(f"Unable to resolve book slug for {book_uuid}")

    return _get_book_slug


def update_doc_links(doc, book_uuid, book_slug_resolver, page_slug_resolver):
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
            # Point inter-book links to generic URL for now
            node.attrib["href"] = "http://openstax.org"
        else:
            book_slug = book_slug_resolver(book_uuid)
            page_slug = page_slug_resolver(page_uuid)
            node.attrib["href"] = _rex_url_builder(
                book_slug, page_slug, page_fragment
            )


def main():
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    out_dir = Path(sys.argv[2]).resolve(strict=True)

    adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
    session = requests.Session()
    session.mount("https://", adapter)

    xhtml_files = in_dir.glob("*@*.xhtml")
    metadata_files = in_dir.glob("*@*-metadata.json")
    book_metadata = in_dir / "collection.toc-metadata.json"

    with book_metadata.open() as json_file:
        json_data = json.load(json_file)
        book_uuid = json_data["id"]

    # Create a book slug resolver that can be used to lookup slugs for the
    # current book (intra-book links) and other books (inter-book links)
    book_slug_resolver = gen_book_slug_resolver(session)
    page_slug_resolver = gen_page_slug_resolver(metadata_files)

    for xhtml_file in xhtml_files:
        doc = etree.parse(str(xhtml_file))
        update_doc_links(
            doc, book_uuid, book_slug_resolver, page_slug_resolver
        )
        doc.write(str(out_dir / xhtml_file.name), encoding="utf8")


if __name__ == "__main__":
    main()
