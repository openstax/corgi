#!/bin/bash
reference=$(cat "${BOOK_INPUT}"/version)
[[ "$reference" = latest ]] && reference=master
set +x
# Do not show creds
remote="https://$GH_SECRET_CREDS@github.com/openstax/$(cat "${BOOK_INPUT}/repo").git"
git clone --depth 1 "$remote" --branch "$reference" "${CONTENT_OUTPUT}/raw"
set -x
if [[ ! -f "${CONTENT_OUTPUT}/raw/collections/$(cat "${BOOK_INPUT}/slug").collection.xml" ]]; then
    echo "No matching book for slug in this repo"
    exit 1
fi
rm -rf "${CONTENT_OUTPUT}/raw/.git"
wget "${BOOK_SLUGS_URL}" -O "${CONTENT_OUTPUT}/book-slugs.json"
fetch-map-resources "${CONTENT_OUTPUT}/raw/modules" "${CONTENT_OUTPUT}/raw/media" . "${UNUSED_RESOURCE_OUTPUT}"
# Either the media is in resources or unused-resources, this folder should be empty (-d will fail otherwise)
rm -d "${CONTENT_OUTPUT}/raw/media"