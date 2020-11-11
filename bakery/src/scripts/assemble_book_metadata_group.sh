#!/bin/bash

exec 2> >(tee "${OUTPUT_NAME}/stderr" >&2)

shopt -s globstar nullglob
for collection in "${ASSEMBLED_INPUT}/"*.assembled.xhtml; do
#for collection in $(find "${ASSEMBLED_INPUT}/" -path "*.assembled.xhtml" -type f); do
    slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')
    {
        echo "{"
        find "${FETCHED_INPUT}/raw/modules" -path "*/m*/metadata.json" -print0 | xargs -0 cat | jq -r '. | "\"\(.id)\": \"\(.revised)\","'
        echo '"dummy": "dummy"'
        echo "}"
    } >> uuid-to-revised-map.json

    assemble-meta "${ASSEMBLED_INPUT}/$slug_name.assembled.xhtml" uuid-to-revised-map.json "${OUTPUT_NAME}/${slug_name}.assembled-metadata.json"
done
shopt -u globstar nullglob