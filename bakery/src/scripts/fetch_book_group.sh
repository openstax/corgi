#!/bin/bash

reference=$(cat "${BOOK_INPUT}/version")
[[ "$reference" = latest ]] && reference=master
set +x
# Do not show creds
remote="https://${GH_SECRET_CREDS}@github.com/openstax/$(cat "${BOOK_INPUT}"/repo).git"
git clone --depth 1 "$remote" --branch "$reference" "${OUTPUT_NAME}/raw"
set -x
wget "${BOOK_SLUGS_URL}" -O "${OUTPUT_NAME}/book-slugs.json"