#!/bin/bash

exec 2> >(tee checksum-book/stderr >&2)

# Add symlinks to fetched-book-group to be able to find images
find "${SYMLINK_INPUT}" -type l -print0 | xargs -0 -I{} cp -P {} "${LINKED_INPUT}"

checksum "${LINKED_INPUT}" "${RESOURCES_OUTPUT}"

slug_name=$(cat "${BOOK_INPUT}/slug")
mv "${RESOURCES_OUTPUT}/$slug_name.linked.xhtml" "${RESOURCES_LINKED_SINGLE_OUTPUT}/$slug_name.resource-linked.xhtml"