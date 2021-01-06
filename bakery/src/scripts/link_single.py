"""
Replaces legacy module ids in links to external modules with
uuids from the target module and corresponding canonical book       .
"""

import sys
import re
import json
from pathlib import Path

from lxml import etree
from urllib.parse import unquote
from cnxepub.collation import reconstitute
from cnxepub.models import flatten_to_documents


def load_baked_collection(input_dir, book_slug):
    """load assembled collection"""
    baked_collection = f"{input_dir}/{book_slug}.baked.xhtml"
    return etree.parse(baked_collection)


def parse_collection_binders(input_dir):
    """Create a list of binders from book collections"""
    baked_collections = Path(input_dir).glob("*.baked.xhtml")
    binders = []

    for baked_collection in baked_collections:
        with open(baked_collection, "r") as baked_file:
            binder = reconstitute(baked_file)
            binders.append(binder)

    return binders


def create_canonical_map(binders):
    """Create a canonical book map from a set of binders"""
    canonical_map = {}

    for binder in binders:
        for doc in flatten_to_documents(binder):
            canonical_map[doc.id] = doc.metadata['canonical_book_uuid']

    return canonical_map


def parse_book_metadata(binders, input_dir):
    """Create a list of book metadata for a set of binders using collection
    metadata files"""
    book_metadata = []

    for binder in binders:
        slug = binder.metadata["slug"]
        baked_metadata_file = Path(input_dir) / f"{slug}.baked-metadata.json"
        with open(baked_metadata_file, "r") as metadata_file:
            metadata = json.load(metadata_file)
            book_metadata.append(metadata[binder.ident_hash])

    return book_metadata


def get_target_uuid(link):
    """get target module uuid"""
    parsed = unquote(link)

    return re.search(
        r'/contents/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        parsed).group(1)


def gen_page_slug_resolver(baked_meta_dir, book_tree_by_uuid):
    """Generate a page slug resolver function"""

    def _get_page_slug(book_uuid, page_uuid):
        """Get page slug from book"""
        def _parse_tree_for_slug(tree, page_uuid):
            """Recursively walk through tree to find page slug"""
            curr_slug = tree["slug"]
            curr_id = tree["id"]
            if curr_id.startswith(page_uuid):
                return curr_slug
            if "contents" in tree:
                for node in tree["contents"]:
                    slug = _parse_tree_for_slug(node, page_uuid)
                    if slug:
                        return slug
            return None

        page_slug = _parse_tree_for_slug(
            book_tree_by_uuid[book_uuid], page_uuid)

        return page_slug

    return _get_page_slug


def patch_link(node, source_book_uuid, canonical_book_uuid,
               canonical_book_slug, page_slug):
    """replace legacy link"""
    # FIXME: Track and change EXTERNAL #id-based links in link-extras that have moved from baking
    # m12345 -> uuid::abcd
    # /content/m12345/index.xhtml#exercise -> /content/uuid::abcd/index.xhtml#exercise,
    # but if #exercise has moved, then it should be /content/uuid::other/index.xhtml#exercise
    # This can be fixed via searching the baked content when encountering link with a #.... suffix
    if not source_book_uuid == canonical_book_uuid:
        page_link = node.attrib["href"].split("/contents/")[1]
        # Link may have fragment
        if "#" in page_link:
            page_id, page_fragment = page_link.split('#')
            page_fragment = f"#{page_fragment}"
        else:
            page_id = page_link
            page_fragment = ""

        print('BEFORE:')
        print(node.attrib)
        node.attrib["data-book-uuid"] = canonical_book_uuid
        node.attrib["data-book-slug"] = canonical_book_slug
        node.attrib["data-page-slug"] = page_slug
        node.attrib["href"] = f"./{canonical_book_uuid}:{page_id}.xhtml{page_fragment}"
        print('AFTER:')
        print(node.attrib)


def save_linked_collection(output_path, doc):
    """write modified output"""
    with open(output_path, "wb") as f:
        doc.write(f, encoding="utf-8", xml_declaration=True)


def transform_links(
        baked_content_dir, baked_meta_dir, source_book_slug, output_path):
    doc = load_baked_collection(baked_content_dir, source_book_slug)
    binders = parse_collection_binders(baked_content_dir)
    canonical_map = create_canonical_map(binders)
    book_metadata = parse_book_metadata(binders, baked_meta_dir)

    uuid_by_slug = {entry["slug"]: entry["id"] for entry in book_metadata}
    book_tree_by_uuid = {
        entry["id"]: entry["tree"] for entry in book_metadata
    }
    source_book_uuid = uuid_by_slug[source_book_slug]
    page_slug_resolver = gen_page_slug_resolver(
        baked_meta_dir,
        book_tree_by_uuid
    )

    # look up uuids for external module links
    for node in doc.xpath(
        '//x:a[@href and starts-with(@href, "/contents/")]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    ):
        link = node.attrib["href"]

        target_module_uuid = get_target_uuid(link)
        canonical_book_uuid = canonical_map[target_module_uuid]
        canonical_book_slug = next(
            (slug for slug, uuid in uuid_by_slug.items()
             if uuid == canonical_book_uuid))

        page_slug = page_slug_resolver(canonical_book_uuid, target_module_uuid)
        if page_slug is None:
            raise Exception(
                f"Could not find page slug for module {target_module_uuid} "
                f"in canonical book UUID {canonical_book_uuid} "
                f"from link {link}"
            )
        patch_link(node, source_book_uuid, canonical_book_uuid,
                   canonical_book_slug, page_slug)

    save_linked_collection(output_path, doc)


def main():
    (baked_content_dir,
        baked_meta_dir,
        source_book_slug,
        output_path) = sys.argv[1:5]
    transform_links(
        baked_content_dir, baked_meta_dir, source_book_slug, output_path)


if __name__ == "__main__":
    main()
