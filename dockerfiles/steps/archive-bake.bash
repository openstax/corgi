parse_book_dir

try $RECIPES_ROOT/bake_root -b "${ARG_RECIPE_NAME}" -r $CNX_RECIPES_RECIPES_ROOT/ -i "${IO_ARCHIVE_BOOK}/collection.linked.xhtml" -o "${IO_ARCHIVE_BOOK}/collection.baked.xhtml"
style_file="$CNX_RECIPES_STYLES_ROOT/${ARG_RECIPE_NAME}-pdf.css"

[[ -f "${style_file}" ]] || yell "Warning: Could not find style file for recipe name '${ARG_RECIPE_NAME}'"

if [ -f "${style_file}" ]
then
    cp "${style_file}" "${IO_ARCHIVE_BOOK}"
    try sed -i "s%<\\/head>%<link rel=\"stylesheet\" type=\"text/css\" href=\"$(basename ${style_file})\" />&%" "${IO_ARCHIVE_BOOK}/collection.baked.xhtml"
fi