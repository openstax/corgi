exec 2> >(tee ${BAKED_OUTPUT}/stderr >&2)

# FIXME: We assume that every book in the group uses the same style
# This assumption will not hold true forever, and book style + recipe name should
# be pulled from fetched-book-group (while still allowing injection w/ CLI)

# FIXME: Style devs will probably not like having to bake multiple books repeatedly,
# especially since they shouldn't care about link-extras correctness during their
# work cycle.

# FIXME: Separate style injection step from baking step. This is way too much work to change a line injected into the head tag
style_file="cnx-recipes-output/rootfs/styles/$(cat ${BOOK_INPUT}/style)-pdf.css"

recipe_file="cnx-recipes-output/rootfs/recipes/$(cat ${BOOK_INPUT}/style).css"

# FIXME: symlinks should only be needed to preview intermediate state
find "${SYMLINK_INPUT}" -type l | xargs -I{} cp -P {} "${BAKED_OUTPUT}"

if [[ -f "$style_file" ]]
    then
        cp "$style_file" ${BAKED_OUTPUT}
        cp "$style_file" ${STYLE_OUTPUT}
    else
        echo "Warning: Style Not Found" > ${BAKED_OUTPUT}/stderr
fi

for collection in $(find "${ASSEMBLED_INPUT}/" -path *.assembled.xhtml -type f); do
    slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')
    cnx-easybake -q "$recipe_file" "${ASSEMBLED_INPUT}/$slug_name.assembled.xhtml" "${BAKED_OUTPUT}/$slug_name.baked.xhtml"
    if [[ -f "$style_file" ]]
        then
            sed -i "s%<\\/head>%<link rel=\"stylesheet\" type=\"text/css\" href=\"$(basename $style_file)\" />&%" "${BAKED_OUTPUT}/$slug_name.baked.xhtml"
    fi
done