"""Make modifications to page XHTML files specific to GDoc outputs
"""
import sys
from lxml import etree
from pathlib import Path


def update_doc_links(doc):
    """Modify links in doc"""
    for node in doc.xpath(
        '//x:a[@href and starts-with(@href, "/contents/")]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"}
    ):
        # This is either an intra-book link or inter-book link (we can
        # differentiate the latter by data-book-uuid attrib). For now we're
        # just going to convert these to point at http://openstax.org, but
        # later we may convert one or both of these to point at REX via
        # http://openstax.org/books/{book_slug}/pages/{page_slug}, with
        # current gaps being looking up book_slugs from CMS by UUID as well
        # as having a lookup table of page UUIDs to slugs.
        node.attrib["href"] = "http://openstax.org"


def main():
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    out_dir = Path(sys.argv[2]).resolve(strict=True)

    xhtml_files = in_dir.glob("*@*.xhtml")
    for xhtml_file in xhtml_files:
        doc = etree.parse(str(xhtml_file))
        update_doc_links(doc)
        doc.write(str(out_dir / xhtml_file.name), encoding="utf8")


if __name__ == "__main__":
    main()
