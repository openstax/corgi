import os
import sys
import hashlib
import magic
import json
from pathlib import Path
from lxml import etree

BUF_SIZE = 65536  # read files in 64kb chunks, faster.
RESOURCES_DIR = 'resources'

# https://stackoverflow.com/a/22058673/756056
def get_checksum(filename):
    """ generate SHA1 checksum from file """
    sha1 = hashlib.sha1()
    try:
        with open(filename, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()
    except IOError:     # file does not exist
        return None


def get_mime_type(filename):
    """ get MIME type of file with libmagic """
    mime_type = ''
    try:
        mime_type = magic.from_file(filename, mime=True)
    finally:
        return mime_type


def create_symlink(img_filename, output_dir, sha1):
    """ Create symlinks for resources to raw files """
    raw_img_filename = os.path.realpath(img_filename)
    dest_path = os.path.join(output_dir, RESOURCES_DIR)
    dest_img_filename = os.path.join(dest_path, sha1)
    rel_raw_img_filename = os.path.relpath(raw_img_filename, dest_path)
    try:
        # set a relative symlink to raw file
        os.symlink(rel_raw_img_filename, dest_img_filename)
    except FileExistsError:     # ignore symlink file existing
        pass


def create_mime_json(output_dir, sha1, mime_type):
    """ Create json with MIME type of a (symlinked) resource file """
    data = {}
    data['Content-Type'] = mime_type
    json_filename = os.path.join(output_dir, RESOURCES_DIR, sha1+'.json')
    with open(json_filename, 'w') as outfile:
        json.dump(data, outfile)


def generate_checksum_resources_from_xhtml(filename, output_dir):
    """ Go through HTML and checksum/copy/mime type all <img> and <a> resources """
    doc = etree.parse(filename)
    source_path = os.path.dirname(filename)
    basename = os.path.basename(filename)
    module_name = os.path.splitext(basename)[0]
    # get all img @src resources
    for node in doc.xpath('//x:img[@src and not(starts-with(@src, "http") or starts-with(@src, "//"))]',
                          namespaces={'x': 'http://www.w3.org/1999/xhtml'}):
        img_filename = node.attrib['src']
        img_filename = os.path.join(source_path, img_filename)

        sha1 = get_checksum(img_filename)
        mime_type = get_mime_type(img_filename)

        if sha1:    # file exists
            node.attrib['src'] = '../' + RESOURCES_DIR + '/' + sha1

            create_symlink(img_filename, output_dir, sha1)
            create_mime_json(output_dir, sha1, mime_type)
            # print('{}, {}, {}'.format(img_filename, sha1, mime_type)) # debug

    # get all a @href resources
    for node in doc.xpath('//x:a[@href and not(starts-with(@href, "http") or starts-with(@href, "//") or starts-with(@href, "#"))]',
                          namespaces={'x': 'http://www.w3.org/1999/xhtml'}):
        img_filename = node.attrib['href']

        # fix a @href links to module_name directories
        # they are pointing relatively to ./image.jpg but need to point to ./m123/image.jpg
        img_filename = os.path.join(source_path, module_name, img_filename)

        sha1 = get_checksum(img_filename)
        mime_type = get_mime_type(img_filename)

        if sha1:    # file exists
            node.attrib['href'] = '../' + RESOURCES_DIR + '/' + sha1

            create_symlink(img_filename, output_dir, sha1)
            create_mime_json(output_dir, sha1, mime_type)
            # print('{}, {}, {}'.format(img_filename, sha1, mime_type)) # debug

    output_file = os.path.join(output_dir, basename)
    # note: non self closing tags in xhtml are probably not respected here
    with open(output_file, 'wb') as f:
        doc.write(f, encoding="ASCII", xml_declaration=False)


def mkdir_resources(path):
    resources = os.path.join(path, RESOURCES_DIR)
    os.makedirs(resources, exist_ok=True)


def main():
    """Main function"""
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    out_dir = in_dir # overwrite baked book xhtml files
    mkdir_resources(out_dir)
    for xhtml_file in Path(in_dir).glob('*.xhtml'):
        generate_checksum_resources_from_xhtml(str(xhtml_file), out_dir)

if __name__ == "__main__":
    main()