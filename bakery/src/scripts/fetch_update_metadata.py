"""Inject / modify metadata for book CNXML from git"""

import sys
from pathlib import Path
from pygit2 import Repository
from datetime import datetime, timezone
from lxml import etree

NS_MDML = "http://cnx.rice.edu/mdml"
NS_CNXML = "http://cnx.rice.edu/cnxml"


def add_metadata_entries(cnxml_doc, new_metadata):
    metadata = cnxml_doc.xpath(
        "//x:metadata",
        namespaces={"x": NS_CNXML}
    )[0]

    for tag, value in new_metadata.items():
        element = etree.Element(f"{{{NS_MDML}}}{tag}")
        element.text = value
        element.tail = "\n"
        metadata.append(element)


def main():
    git_repo = Path(sys.argv[1]).resolve(strict=True)
    modules_dir = Path(sys.argv[2]).resolve(strict=True)
    repo = Repository(git_repo)

    # For the time being, we're going to parse the timestamp of the HEAD
    # commit and use that as the revised time for all module pages.
    revised_time = datetime.fromtimestamp(
        repo.revparse_single('HEAD').commit_time,
        timezone.utc
    ).isoformat()

    module_files = [
        cf.resolve(strict=True) for cf in modules_dir.glob("**/*")
        if cf.is_file() and cf.name == "index.cnxml"
    ]

    for module_file in module_files:
        cnxml_doc = etree.parse(str(module_file))
        new_metadata = {
            "revised": revised_time
        }
        add_metadata_entries(cnxml_doc, new_metadata)

        with open(module_file, "wb") as f:
            cnxml_doc.write(f, encoding="utf-8", xml_declaration=False)


if __name__ == "__main__":
    main()
