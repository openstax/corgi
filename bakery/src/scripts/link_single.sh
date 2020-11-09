#!/bin/bash

exec 2> >(tee "$LINKED_OUTPUT/stderr" >&2)

echo "{" > module-canonicals.json
find $FETCHED_INPUT/raw/modules/ -path *metadata.json | xargs cat | jq -r '. | "\"\(.id)\": \"\(.canonical)\","' >> module-canonicals.json
echo '"dummy": "dummy"' >> module-canonicals.json
echo "}" >> module-canonicals.json

link-single "$BAKED_INPUT" "$BAKED_META_INPUT" "$(cat "${BOOK_INPUT}"/slug)" "$FETCHED_INPUT/book-slugs.json" module-canonicals.json "$LINKED_OUTPUT/$(cat "$BOOK_INPUT"/slug).linked.xhtml"