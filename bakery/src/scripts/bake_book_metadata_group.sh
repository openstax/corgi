#!/bin/bash

 exec 2> >(tee "${BAKED_META_OUTPUT}/stderr" >&2)

shopt -s globstar nullglob
for collection in "${BAKED_INPUT}/"*.baked.xhtml; do
    slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')

    book_metadata="${FETCHED_INPUT}/raw/metadata/$slug_name.metadata.json"
    book_uuid=$(jq -r '.id' "$book_metadata")
    book_version=$(jq -r '.version' "$book_metadata")
    book_legacy_id=$(jq -r '.legacy_id' "$book_metadata")
    book_legacy_version=$(jq -r '.legacy_version' "$book_metadata")
    book_ident_hash="$book_uuid@$book_version"
    book_license=$(jq -r '.license' "$book_metadata")
    book_slugs_file="${FETCHED_INPUT}/book-slugs.json"

    jq --arg ident_hash "$book_ident_hash" --arg uuid "$book_uuid" --arg version "$book_version" --argjson license "$book_license" \
        --arg legacy_id "$book_legacy_id" --arg legacy_version "$book_legacy_version" \
        '. + {($ident_hash): {id: $uuid, version: $version, license: $license, legacy_id: $legacy_id, legacy_version: $legacy_version}}' \
        "${ASSEMBLED_META_INPUT}/$slug_name.assembled-metadata.json" \
        > "/tmp/$slug_name.baked-input-metadata.json"
    bake-meta "/tmp/$slug_name.baked-input-metadata.json" "${BAKED_INPUT}/$slug_name.baked.xhtml" "$book_uuid" "$book_slugs_file" "${BAKED_META_OUTPUT}/$slug_name.baked-metadata.json"
done
shopt -u globstar nullglob
