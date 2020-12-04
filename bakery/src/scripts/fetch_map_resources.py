"""Map resource files used in CNXML to provided path"""

import hashlib
import json
import magic
import shutil
import sys
from pathlib import Path
from lxml import etree

# same as boto3 default chunk size. Don't modify.
BUF_SIZE = 8 * 1024 * 1024

# relative links must work both locally, on PDF, and on REX, and images are
# uploaded with the prefix 'resources/' in S3 for REX
# so the output directory name MUST be resources
RESOURCES_DIR_NAME = 'resources'


def create_json_metadata(output_dir, sha1, mime_type, s3_md5, original_name):
    """ Create json with MIME type of a (symlinked) resource file """
    data = {}
    data['original_name'] = original_name
    data['mime_type'] = mime_type
    data['s3_md5'] = s3_md5
    data['sha1'] = sha1
    json_file = output_dir / f'{sha1}.json'
    with json_file.open(mode='w') as outfile:
        json.dump(data, outfile)


def get_mime_type(filename):
    """ get MIME type of file with libmagic """
    mime_type = ''
    try:
        mime_type = magic.from_file(filename, mime=True)
    finally:
        return mime_type


# https://stackoverflow.com/a/22058673/756056
def get_checksums(filename):
    """ generate SHA1 and S3 MD5 etag checksums from file """
    sha1 = hashlib.sha1()
    md5s = []
    try:
        with open(filename, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
                md5s.append(hashlib.md5(data))
        # chunked calculation for AWS S3 MD5 etag
        # https://stackoverflow.com/a/43819225/756056
        #
        # AWS needs the MD5 quoted inside the string json value.
        # Despite looking like a mistake, this is correct behavior.
        if len(md5s) < 1:
            s3_md5 = '"{}"'.format(hashlib.md5().hexdigest())
        elif len(md5s) == 1:
            s3_md5 = '"{}"'.format(md5s[0].hexdigest())
        else:
            digests = b''.join(m.digest() for m in md5s)
            digests_md5 = hashlib.md5(digests)
            s3_md5 = '"{}-{}"'.format(digests_md5.hexdigest(), len(md5s))
        return sha1.hexdigest(), s3_md5
    except IOError:     # file does not exist
        return None, None


def main():
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    original_resources_dir = Path(sys.argv[2]).resolve(strict=True)
    resources_parent_dir = Path(sys.argv[3]).resolve(strict=True)
    unused_resources_dump = Path(sys.argv[4]).resolve()
    resources_dir = resources_parent_dir / RESOURCES_DIR_NAME
    resources_dir.mkdir(exist_ok=True)
    unused_resources_dump.mkdir(exist_ok=True)

    cnxml_files = in_dir.glob("**/*.cnxml")

    filename_to_data = {}

    for cnxml_file in cnxml_files:
        doc = etree.parse(str(cnxml_file))
        for node in doc.xpath(
            '//x:image',
            namespaces={"x": "http://cnx.rice.edu/cnxml"}
        ):
            resource_original_name = node.attrib["src"]
            resource_original_file = original_resources_dir / resource_original_name

            sha1, s3_md5 = get_checksums(str(resource_original_file))
            mime_type = get_mime_type(str(resource_original_file))

            if sha1 is None:
                print(
                    f"WARNING: Resource file '{resource_original_name}' not found",
                    file=sys.stderr
                )
                continue

            filename_to_data[resource_original_name] = (sha1, s3_md5, mime_type)
            node.attrib["src"] = f"../{RESOURCES_DIR_NAME}/{sha1}"

        with cnxml_file.open(mode="wb") as f:
            doc.write(f, encoding="utf-8", xml_declaration=False)

    for resource_original_name in filename_to_data:
        sha1, s3_md5, mime_type = filename_to_data[resource_original_name]

        resource_original_file = original_resources_dir / resource_original_name
        checksum_resource_file = resources_dir / sha1

        shutil.move(str(resource_original_file), str(checksum_resource_file))
        create_json_metadata(resources_dir, sha1, mime_type, s3_md5, resource_original_name)

    for unused_resource_file in original_resources_dir.glob('**/*'):
        shutil.move(str(unused_resource_file), unused_resources_dump)
        print(
            f"WARNING: Resource file '{unused_resource_file.name}' seems to be unused",
            file=sys.stderr
        )


if __name__ == "__main__":
    main()
