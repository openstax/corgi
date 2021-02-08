#!/bin/bash
exec > >(tee "${COMMON_LOG_DIR}"/log >&2) 2>&1

link-single "$BAKED_INPUT" "$BAKED_META_INPUT" "$(cat "${BOOK_INPUT}"/slug)" "$LINKED_OUTPUT/$(cat "$BOOK_INPUT"/slug).linked.xhtml" "$TARGET_BOOK"
