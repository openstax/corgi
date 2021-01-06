#!/bin/bash
exec > >(tee ${COMMON_LOG_DIR}/log >&2) 2>&1

if [[ -n "${TARGET_BOOK}" ]]; then
    cp "${BAKED_INPUT}/${TARGET_BOOK}.baked.xhtml" "${LINKED_OUTPUT}/${TARGET_BOOK}.linked.xhtml"
else
    link-single "$BAKED_INPUT" "$BAKED_META_INPUT" "$(cat "${BOOK_INPUT}"/slug)" "$LINKED_OUTPUT/$(cat "$BOOK_INPUT"/slug).linked.xhtml"
fi
