 exec 2> >(tee ${BAKED_META_OUTPUT}/stderr >&2)
for collection in $(find "${BAKED_INPUT}/" -path *.baked.xhtml -type f); do
    slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')

    book_metadata="${FETCHED_INPUT}/raw/metadata/$slug_name.metadata.json"
    book_uuid="$(cat $book_metadata | jq -r '.id')"
    book_version="$(cat $book_metadata | jq -r '.version')"
    book_legacy_id="$(cat $book_metadata | jq -r '.legacy_id')"
    book_legacy_version="$(cat $book_metadata | jq -r '.legacy_version')"
    book_ident_hash="$book_uuid@$book_version"
    book_license="$(cat $book_metadata | jq '.license')"
    book_slugs_file="${FETCHED_INPUT}/book-slugs.json"
    cat "${ASSEMBLED_META_INPUT}/$slug_name.assembled-metadata.json" | \
        jq --arg ident_hash "$book_ident_hash" --arg uuid "$book_uuid" --arg version "$book_version" --argjson license "$book_license" \
        --arg legacy_id "$book_legacy_id" --arg legacy_version "$book_legacy_version" \
        '. + {($ident_hash): {id: $uuid, version: $version, license: $license, legacy_id: $legacy_id, legacy_version: $legacy_version}}' > "/tmp/$slug_name.baked-input-metadata.json"
    bake-meta /tmp/$slug_name.baked-input-metadata.json "${BAKED_INPUT}/$slug_name.baked.xhtml" "$book_uuid" "$book_slugs_file" "${BAKED_META_OUTPUT}/$slug_name.baked-metadata.json"
done