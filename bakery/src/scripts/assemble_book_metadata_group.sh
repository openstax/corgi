exec 2> >(tee ${OUTPUT_NAME}/stderr >&2)
for collection in $(find "${ASSEMBLED_INPUT}}/" -path *.assembled.xhtml -type f); do
    slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')


    echo "{" > uuid-to-revised-map.json
    find ${FETCHED_INPUT}/raw/modules -path */m*/metadata.json | xargs cat | jq -r '. | "\"\(.id)\": \"\(.revised)\","' >> uuid-to-revised-map.json
    echo '"dummy": "dummy"' >> uuid-to-revised-map.json
    echo "}" >> uuid-to-revised-map.json

    assemble-meta "${ASSEMBLED_INPUT}/$slug_name.assembled.xhtml" uuid-to-revised-map.json "${OUTPUT_NAME}/${slug_name}.assembled-metadata.json"
done