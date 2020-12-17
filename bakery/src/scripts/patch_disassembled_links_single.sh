#!/bin/bash

exec 2> >(tee "${DISASSEMBLED_LINKED_OUTPUT}"/stderr >&2)

slug_name=$(cat "${BOOK_INPUT}/slug")
patch-same-book-links "${DISASSEMBLED_INPUT}" "${DISASSEMBLED_LINKED_OUTPUT}" "$slug_name"
cp "${DISASSEMBLED_INPUT}"/*@*-metadata.json "${DISASSEMBLED_LINKED_OUTPUT}"
cp "${DISASSEMBLED_INPUT}"/"$slug_name".toc* "${DISASSEMBLED_LINKED_OUTPUT}"
