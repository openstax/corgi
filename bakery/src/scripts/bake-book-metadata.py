import sys
import json

from lxml import etree
from cnxepub.html_parsers import DocumentMetadataParser

raw_metadata_file, baked_xhtml_file, baked_metadata_file = sys.argv[1:4]

def parse_uri(uri):
    if not uri.startswith('col', 0, 3): return None
    legacy_id, legacy_version = uri.split('@')
    return legacy_id, legacy_version

def capture_book_metadata():

    with open(raw_metadata_file, "r") as raw_json :
        baked_metadata = json.load(raw_json)
    
    with open(baked_xhtml_file, "r") as baked_xhtml:
        html = etree.parse(baked_xhtml)
        metadata = DocumentMetadataParser(html)

        required_metadata = ('title', 'license_url')
        for required_data in required_metadata:
            if getattr(metadata, required_data) is None:
                raise ValueError("A value for '{}' could not be found.")
        
        legacy_id, legacy_version = parse_uri(metadata.cnx_archive_uri)
        baked_book_json = {
            "title": metadata.title,
            "license": {
                "url": metadata.license_url
            },
            "legacy_id": legacy_id,
            "legacy_version": legacy_version
        }

        baked_metadata[legacy_id] = baked_book_json

    with open(baked_metadata_file, "w") as json_out:
        json.dump(
            baked_metadata,
            json_out
        )

if __name__ == "__main__":
    capture_book_metadata()