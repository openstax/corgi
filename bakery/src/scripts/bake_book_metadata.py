import sys
import json
from scripts import utils

from lxml import etree
from cnxepub.html_parsers import DocumentMetadataParser
from cnxepub.collation import reconstitute

def main():

    raw_metadata_file, baked_xhtml_file, baked_metadata_file = sys.argv[1:4]

    with open(baked_xhtml_file, "r") as baked_xhtml:
        html = etree.parse(baked_xhtml)
        metadata = DocumentMetadataParser(html)
        binder = reconstitute(baked_xhtml)

    required_metadata = ('title', 'revised')
    for required_data in required_metadata:
        if getattr(metadata, required_data) is None:
            raise ValueError("A value for '{}' could not be found.".format(required_data))

    with open(raw_metadata_file, "r") as raw_json :
        baked_metadata = json.load(raw_json)

    tree = utils.model_to_tree(binder)

    baked_book_json = {
        "title": metadata.title,
        "revised": metadata.revised,
        "tree": tree
    }

    # If there is existing book metadata provided, update with data above
    if baked_metadata.get(binder.ident_hash):
        baked_metadata[binder.ident_hash].update(baked_book_json)
    else:
        baked_metadata[binder.ident_hash] = baked_book_json

    with open(baked_metadata_file, "w") as json_out:
        json.dump(
            baked_metadata,
            json_out
        )

if __name__ == "__main__":
    main()
