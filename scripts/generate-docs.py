import os
import re
import sys
from urllib.parse import quote
from urllib.parse import urljoin
import logging
import shutil


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generate-docs")

REPO = "openstax/corgi"
MAIN_BRANCH = "main"
GITHUB_REPO = f"https://github.com/{REPO}/tree/{MAIN_BRANCH}/"


def to_fsname(s: str):
    return quote(s.replace("#", "").strip().replace(" ", "_"))


def process_line(repo_root, parent_dir, line):
    def resolve_relative_link(match):
        link = match.group(1)
        full_path = os.path.join(parent_dir, link)
        if not os.path.exists(full_path):
            return match.group(0)
        relative_to_repo = os.path.relpath(full_path, repo_root)
        return f"]({urljoin(GITHUB_REPO, relative_to_repo)})"

    line = re.sub(r"\]\((\.+/[^)]+)\)", resolve_relative_link, line)
    return line


if __name__ == "__main__":
    path_parts = __file__.split(os.sep)
    repo_root = os.path.realpath(sys.argv[1])
    readme_file = sys.argv[2]
    output_dir = sys.argv[3]
    readme_parent = os.path.dirname(readme_file)
    if os.path.exists(output_dir):
        logger.info(f"Removing: {output_dir}")
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    fout = None
    counter = 0
    with open(readme_file, "r") as fin:
        for line in fin:
            if re.match(r"^\s*## ", line):
                filename = f"{counter:04x}-{to_fsname(line)}.md"
                full_path = os.path.join(output_dir, filename)
                logger.info(f"Generating: {full_path}")
                if fout is not None:
                    fout.close()
                fout = open(full_path, "w")
                counter += 1
            if fout is not None:
                fout.write(process_line(repo_root, readme_parent, line))
    if fout is not None:
        fout.close()
