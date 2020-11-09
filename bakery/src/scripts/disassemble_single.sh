#!/bin/bash

exec 2> >(tee disassembled-book/stderr >&2)

slug_name=$(cat "${BOOK_INPUT}/slug")
disassemble "${RESOURCE_LINKED_INPUT}/$slug_name.resource-linked.xhtml" "${BAKED_BOOK_META_INPUT}/$slug_name.baked-metadata.json" "$slug_name" "${DISASSEMBLED_OUTPUT}"