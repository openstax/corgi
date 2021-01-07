#!/bin/bash
exec > >(tee "${COMMON_LOG_DIR}"/log >&2) 2>&1

cp "${STYLE_INPUT}"/* "${MATHIFIED_INPUT}"

echo -n "https://${BUCKET_NAME}.s3.amazonaws.com/$(cat "${BOOK_INPUT}"/pdf_filename)" > "${ARTIFACTS_OUTPUT}/pdf_url"
prince -v --output="${ARTIFACTS_OUTPUT}/$(cat "${BOOK_INPUT}"/pdf_filename)" "${MATHIFIED_INPUT}/$(cat "${BOOK_INPUT}"/slug).mathified.xhtml"
