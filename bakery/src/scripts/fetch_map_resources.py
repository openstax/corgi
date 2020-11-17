"""Map resource files used in CNXML to provided path"""

import sys
from pathlib import Path
from lxml import etree


def main():
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    resource_rel_path_prefix = sys.argv[2]

    cnxml_files = in_dir.glob("**/*.cnxml")

    for cnxml_file in cnxml_files:
        doc = etree.parse(str(cnxml_file))
        for node in doc.xpath(
            '//x:image',
            namespaces={"x": "http://cnx.rice.edu/cnxml"}
        ):
            resource_file = node.attrib["src"]
            file_link_name = (cnxml_file.parent / resource_file)

            # Create a symlink to the resource file associated with this image
            # if it doesn't already exist
            if not file_link_name.is_symlink():
                file_link_name.symlink_to(
                    f"{resource_rel_path_prefix}/{resource_file}"
                )

            # Check if the symlink resolves, otherwise print warning
            if not file_link_name.exists():
                print(f"WARNING: Resource file '{resource_file}' not found")


if __name__ == "__main__":
    main()
