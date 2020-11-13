#!/bin/bash

exec 2> >(tee "${ASSEMBLED_OUTPUT}/stderr" >&2)

shopt -s globstar nullglob
for collection in "${RAW_COLLECTION_DIR}/collections/"*; do
    slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')

    mv "$collection" "${RAW_COLLECTION_DIR}/modules/collection.xml"
    mv "${RAW_COLLECTION_DIR}/metadata/$slug_name.metadata.json" "${RAW_COLLECTION_DIR}/modules/metadata.json"

    # Assembly destination must nested EXACTLY one level under cwd for symlinks to work 
    neb assemble "${RAW_COLLECTION_DIR}/modules" temp-assembly/

    # We shouldn't we need this symlink
    rm temp-assembly/collection.xml

    find temp-assembly -type l -print0 | xargs -0 -I{} cp -P {} "${SYMLINK_OUTPUT}"
    find "${SYMLINK_OUTPUT}" -type l -print0 | xargs -0 -I{} cp -P {} "${ASSEMBLED_OUTPUT}"
    cp "temp-assembly/collection.assembled.xhtml" "${ASSEMBLED_OUTPUT}/$slug_name.assembled.xhtml"
done
shopt -u globstar nullglob
