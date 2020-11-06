exec 2> >(tee ${MATHIFIED_OUTPUT}/stderr >&2)
slug_name="$(cat ${BOOK_INPUT}/slug)"

# FIXME: symlinks should only be needed to preview intermediate state
find "${SYMLINK_INPUT}" -type l | xargs -I{} cp -P {} "${MATHIFIED_OUTPUT}"

# Style needed because mathjax will size converted math according to surrounding text
cp ${STYLE_INPUT}/* ${LINKED_INPUT}

node /src/typeset/start -i "${LINKED_INPUT}/$slug_name.linked.xhtml" -o "${MATHIFIED_OUTPUT}/$slug_name.mathified.xhtml" -f svg  