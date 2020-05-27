import sys
import json
from lxml import etree
from pathlib import Path
from cnxepub.collation import reconstitute
from cnxepub.models import flatten_to_documents
from cnxepub.html_parsers import DocumentMetadataParser

ASSEMBLED_FILENAME = 'collection.assembled.xhtml'

def get_module_xhtml_metadata(module_xhtml):
    """Parse module metadata using XHTML file"""
    with open(module_xhtml, "r") as module_xhtml_file:
        html = etree.parse(module_xhtml_file)
        metadata = DocumentMetadataParser(html)

    return metadata

def main():
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    output_file_path = sys.argv[2]

    input_assembled_file = in_dir / ASSEMBLED_FILENAME

    json_data = {}

    with open(input_assembled_file, "r") as in_file:
        binder = reconstitute(in_file)

    for doc in flatten_to_documents(binder):
        # Parse the metadata from the supporting module XHTML files generated
        # by neb during assemble to gain access to metadata that is in the
        # head and doesn't get incorporated into the colllection assembled
        # XHTML
        module_xhtml_metadata = get_module_xhtml_metadata(
            in_dir / f"{doc.id}.xhtml"
        )
        abstract = doc.metadata.get("summary")
        json_data[doc.ident_hash] = {
            "abstract": abstract,
            "revised": module_xhtml_metadata.revised
        }

    with open(output_file_path, "w") as out_file:
        json.dump(json_data, out_file)

if __name__ == "__main__":
    main()
