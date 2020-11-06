exec 2> >(tee $linkedOutput/stderr >&2)
echo "{" > module-canonicals.json
find $fetchedInput/raw/modules/ -path *metadata.json | xargs cat | jq -r '. | "\"\(.id)\": \"\(.canonical)\","' >> module-canonicals.json
echo '"dummy": "dummy"' >> module-canonicals.json
echo "}" >> module-canonicals.json

link-single "$bakedInput" "$bakedMetaInput" "$(cat ${bookInput}/slug)" "$fetchedInput/book-slugs.json" module-canonicals.json "$linkedOutput/$(cat $bookInput/slug).linked.xhtml"