#!/bin/bash

exec 2> >(tee "${ARTIFACTS_OUTPUT}"/stderr >&2)

cp "${STYLE_INPUT}"/* "${MATHIFIED_INPUT}"

echo -n "https://${BUCKET_NAME}.s3.amazonaws.com/$(cat "${BOOK_INPUT}"/pdf_filename)" > "${ARTIFACTS_OUTPUT}/pdf_url"
prince -v --output="${ARTIFACTS_OUTPUT}/$(cat "${BOOK_INPUT}"/pdf_filename)" "${MATHIFIED_INPUT}/$(cat "${BOOK_INPUT}"/slug).mathified.xhtml"
