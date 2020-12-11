#!/bin/bash

exec 2> >(tee "${UPLOAD_OUTPUT}"/stderr >&2)
target_dir="${UPLOAD_OUTPUT}/contents"
mkdir -p "$target_dir"
book_dir="${JSONIFIED_INPUT}"
resources_dir="${CHECKSUM_INPUT}/resources"
book_uuid=$(cat "${BOOK_INPUT}"/uuid)
book_version=$(cat "${BOOK_INPUT}"/version)
book_slug=$(cat "${BOOK_INPUT}"/slug)
for jsonfile in "$book_dir/"*@*.json; do cp "$jsonfile" "$target_dir/$(basename "$jsonfile")"; done;
for xhtmlfile in "$book_dir/"*@*.xhtml; do cp "$xhtmlfile" "$target_dir/$(basename "$xhtmlfile")"; done;
aws s3 cp --recursive "$target_dir" "s3://${BUCKET}/${BUCKET_PREFIX}/contents"
copy-resources-s3 "$resources_dir" "${BUCKET}" "${BUCKET_PREFIX}/resources"

#######################################
# UPLOAD BOOK LEVEL FILES LAST
# so that if an error is encountered
# on prior upload steps, those files
# will not be found by watchers
#######################################
toc_s3_link_json="s3://${BUCKET}/${BUCKET_PREFIX}/contents/$book_uuid@$book_version.json"
toc_s3_link_xhtml="s3://${BUCKET}/${BUCKET_PREFIX}/contents/$book_uuid@$book_version.xhtml"
aws s3 cp "$book_dir/$book_slug.toc.json" "$toc_s3_link_json"
aws s3 cp "$book_dir/$book_slug.toc.xhtml" "$toc_s3_link_xhtml"
