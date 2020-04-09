import sys
import json
import utils

from lxml import etree
from cnxepub.html_parsers import DocumentMetadataParser
from cnxepub.collation import reconstitute

raw_metadata_file, baked_xhtml_file, baked_metadata_file, collection_id = sys.argv[1:5]

def capture_book_metadata():

    with open(baked_xhtml_file, "r") as baked_xhtml:
        html = etree.parse(baked_xhtml)
        metadata = DocumentMetadataParser(html)
        binder = reconstitute(baked_xhtml)

    required_metadata = ('title', 'license_url')
    for required_data in required_metadata:
        if getattr(metadata, required_data) is None:
            raise ValueError("A value for '{}' could not be found.".format(required_data))
        
    legacy_id, legacy_version = utils.parse_uri(metadata.cnx_archive_uri)

    if legacy_id != collection_id:
        print("Warning: Legacy Id '{}' does not match Collection ID '{}'.".format(legacy_id, collection_id))

    with open(raw_metadata_file, "r") as raw_json :
        baked_metadata = json.load(raw_json)
    
    tree = utils.model_to_tree(binder)
    
    baked_book_json = {
        "title": metadata.title,
        "license": {
            "url": metadata.license_url
        },
        "legacy_id": legacy_id,
        "legacy_version": legacy_version,
        "tree": tree
    }
    baked_metadata[collection_id] = baked_book_json

    with open(baked_metadata_file, "w") as json_out:
        json.dump(
            baked_metadata,
            json_out
        )

if __name__ == "__main__":
    capture_book_metadata()