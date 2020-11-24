#!/bin/bash

exec 2> >(tee "${ASSEMBLED_OUTPUT}/stderr" >&2)

slug_name="$(cat "${BOOK_INPUT}"/slug)"

collection="${RAW_COLLECTION_DIR}/collections/$slug_name.collection.xml"

mv "$collection" "${RAW_COLLECTION_DIR}/modules/collection.xml"
mv "${RAW_COLLECTION_DIR}/metadata/$slug_name.metadata.json" "${RAW_COLLECTION_DIR}/modules/metadata.json"

# Assembly destination must nested EXACTLY one level under cwd for symlinks to work 
neb assemble "${RAW_COLLECTION_DIR}/modules" temp-assembly/

find temp-assembly -type l -print0 | xargs -0 -I{} cp -P {} "${SYMLINK_OUTPUT}"
find "${SYMLINK_OUTPUT}" -type l -print0 | xargs -0 -I{} cp -P {} "${ASSEMBLED_OUTPUT}"
cp "temp-assembly/collection.assembled.xhtml" "${ASSEMBLED_OUTPUT}/$slug_name.assembled.xhtml"
rm -rf temp-assembly
