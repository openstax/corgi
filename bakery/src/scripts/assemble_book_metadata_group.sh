#!/bin/bash

exec 2> >(tee "${OUTPUT_NAME}/stderr" >&2)

shopt -s globstar nullglob
# Create an empty map file for invoking assemble-meta
echo "{}" > uuid-to-revised-map.json
for collection in "${ASSEMBLED_INPUT}/"*.assembled.xhtml; do
    slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')
    assemble-meta "${ASSEMBLED_INPUT}/$slug_name.assembled.xhtml" uuid-to-revised-map.json "${OUTPUT_NAME}/${slug_name}.assembled-metadata.json"
done
shopt -u globstar nullglob
