#!/bin/bash

exec 2> >(tee "${OUTPUT_NAME}/stderr" >&2)
slug_name="$(cat "${BOOK_INPUT}"/slug)"

{
    echo "{"
    find "${FETCHED_INPUT}/raw/modules" -path "*/m*/metadata.json" -print0 | xargs -0 cat | jq -r '. | "\"\(.id)\": \"\(.revised)\","'
    echo '"dummy": "dummy"'
    echo "}"
} >> uuid-to-revised-map.json

assemble-meta "${ASSEMBLED_INPUT}/$slug_name.assembled.xhtml" uuid-to-revised-map.json "${OUTPUT_NAME}/${slug_name}.assembled-metadata.json"
