#!/bin/bash

exec 2> >(tee "$LINKED_OUTPUT/stderr" >&2)
if [[ -n "${TARGET_BOOK}" ]]; then
    cp "${BAKED_INPUT}/${TARGET_BOOK}.baked.xhtml" "${LINKED_OUTPUT}/${TARGET_BOOK}.linked.xhtml"
else
    link-single "$BAKED_INPUT" "$BAKED_META_INPUT" "$(cat "${BOOK_INPUT}"/slug)" "$FETCHED_INPUT/book-slugs.json" "$LINKED_OUTPUT/$(cat "$BOOK_INPUT"/slug).linked.xhtml"
fi
