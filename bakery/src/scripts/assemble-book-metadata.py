import sys
import json
from pathlib import Path
from cnxepub.collation import reconstitute
from cnxepub.models import flatten_to_documents

ASSEMBLED_FILENAME = 'collection.assembled.xhtml'

in_dir = Path(sys.argv[1]).resolve(strict=True)
output_file_path = sys.argv[2]

input_assembled_file = in_dir / ASSEMBLED_FILENAME

json_data = {}

with open(input_assembled_file, "r") as in_file:
    binder = reconstitute(in_file)

for doc in flatten_to_documents(binder):
    abstract = doc.metadata.get("summary")
    json_data[doc.ident_hash] = { "abstract": abstract }

with open(output_file_path, "w") as out_file:
    json.dump(json_data, out_file)
