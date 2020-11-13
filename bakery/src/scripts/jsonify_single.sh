#!/bin/bash

exec 2> >(tee "${JSONIFIED_OUTPUT}"/stderr >&2)

jsonify "${DISASSEMBLED_INPUT}" "${JSONIFIED_OUTPUT}"
jsonschema -i "${JSONIFIED_OUTPUT}/$(cat "${BOOK_INPUT}/slug").toc.json /code/scripts/book-schema.json"

for jsonfile in "${JSONIFIED_OUTPUT}/"*@*.json; do
    jsonschema -i "$jsonfile" /code/scripts/page-schema.json
done
