parse_book_dir

try patch-same-book-links "${IO_DISASSEMBLED}" "${IO_DISASSEMBLE_LINKED}" "$ARG_TARGET_SLUG_NAME"
try cp "${IO_DISASSEMBLED}"/*@*-metadata.json "${IO_DISASSEMBLE_LINKED}"
try cp "${IO_DISASSEMBLED}"/"$ARG_TARGET_SLUG_NAME".toc* "${IO_DISASSEMBLE_LINKED}"
