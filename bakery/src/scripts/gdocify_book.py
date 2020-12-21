"""Make modifications to page XHTML files specific to GDoc outputs
"""
import sys
from lxml import etree
from pathlib import Path
import json
import re
import subprocess
from PIL import Image, UnidentifiedImageError
from tempfile import TemporaryDirectory
from . import utils

# folder where all resources are saved in checksum step
RESOURCES_FOLDER = '../resources/'
# sRGB color profile file in Debian icc-profiles-free package
SRGB_ICC = '/usr/share/color/icc/sRGB.icc'
# user installed Adobe ICC CMYK profile US Web Coated (SWOP)
USWEBCOATEDSWOP_ICC = '/usr/share/color/icc/USWebCoatedSWOP.icc'


def update_doc_links(doc, book_uuid, book_slugs_by_uuid):
    """Modify links in doc"""

    def _rex_url_builder(book, page, fragment):
        base_url = f"http://openstax.org/books/{book}/pages/{page}"
        if fragment:
            return f"{base_url}#{fragment}"
        else:
            return base_url

    # It's possible that all links starting with "/contents/"" are intra-book
    # and all links starting with "./" are inter-book, making the check redundant
    for node in doc.xpath(
        '//x:a[@href and starts-with(@href, "/contents/") or '
        'starts-with(@href, "./")]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"}
    ):
        # This is either an intra-book link or inter-book link. We can
        # differentiate the latter by data-book-uuid attrib).
        if node.attrib.get("data-book-uuid"):
            page_link = node.attrib["href"]
            # Link may have fragment
            page_fragment = page_link.split("#")[-1] if "#" in page_link else ''

            external_book_uuid = node.attrib["data-book-uuid"]
            external_book_slug = book_slugs_by_uuid[external_book_uuid]
            external_page_slug = node.attrib["data-page-slug"]
            node.attrib["href"] = _rex_url_builder(
                external_book_slug, external_page_slug, page_fragment
            )
        else:
            book_slug = book_slugs_by_uuid[book_uuid]
            page_slug = node.attrib["data-page-slug"]
            page_fragment = node.attrib["data-page-fragment"]
            node.attrib["href"] = _rex_url_builder(
                book_slug, page_slug, page_fragment
            )


def patch_math(doc):
    """Patch MathML as needed for the conversion process used for gdocs"""

    # It seems texmath used by pandoc has issues when the mathvariant
    # attribute value of "bold-italic" is used with <mtext>, but these convert
    # okay when the element is <mi>.
    for node in doc.xpath(
        '//x:mtext[@mathvariant="bold-italic"]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"}
    ):
        node.tag = "mi"

    # Pandoc renders StarMath annotation
    # which is btw out of specification of MathML.
    # The following lines removes all annotation-xml nodes.
    for node in doc.xpath(
        '//x:annotation-xml[ancestor::x:math]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"}
    ):
        node.getparent().remove(node)
    # remove also all annotation nodes which can confuse Pandoc
    for node in doc.xpath(
        '//x:annotation[ancestor::x:math]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"}
    ):
        node.getparent().remove(node)

    # MathJax 3.x behaves different than legacy MathJax 2.7.x on msubsup MathML.
    # If msubsup has fewer than 3 elements MathJax 3.x does not convert it to
    # msub itself anymore. We are keeping sure in this step that all msubsup
    # with fewer elements than 3 are converted to msub.
    # Pandoc is also confused by msubsup with elements fewer than 3.
    for node in doc.xpath(
        '//x:msubsup[count(*) < 3]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"}
    ):
        node.tag = "msub"


def _convert_cmyk2rgb_embedded_profile(img_filename):
    """ImageMagick commandline to convert from CMYK with
    an existing embedded icc profile"""
    # mogrify -profile sRGB.icc +profile '*' picture.jpg
    return ['mogrify', '-profile', SRGB_ICC, '+profile', "'*'", str(img_filename)]


def _convert_cmyk2rgb_no_profile(img_filename):
    """ImageMagick commandline to convert from CMYK without any
    embedded icc profile"""
    # mogrify -profile USWebCoatedSWOP.icc -profile sRGB.icc +profile '*' picture.jpg
    return ['mogrify', '-profile', USWEBCOATEDSWOP_ICC, '-profile', SRGB_ICC,
            '+profile', "'*'", str(img_filename)]


def _universal_convert_rgb_command(img_filename):
    """ImageMagick commandline to convert an unknown color profile to RGB.
    Warning: Probably does not work perfectly color accurate."""
    return ['mogrify', '-colorspace', 'sRGB', '-type', 'truecolor', str(img_filename)]


def fix_jpeg_colorspace(doc, out_dir):
    """Searches for JPEG image resources which are encoded in colorspace
    other than RGB or Greyscale and convert them to RGB"""

    # get all img resources from img and a nodes
    # assuming all resources from checksum step are in the same folder
    img_xpath = '//x:img[@src and starts-with(@src, "{0}")]/@src' \
        '|' \
        '//x:a[@href and starts-with(@href, "{0}")]/@href'.format(RESOURCES_FOLDER)
    for node in doc.xpath(img_xpath,
                          namespaces={'x': 'http://www.w3.org/1999/xhtml'}):
        img_filename = Path(node)
        img_filename = (out_dir / img_filename).resolve().absolute()

        if img_filename.is_file():
            mime_type = utils.get_mime_type(str(img_filename))

            # Only check colorspace of JPEGs (GIF, PNG etc. don't have breaking colorspaces)
            if mime_type == 'image/jpeg':
                try:
                    im = Image.open(str(img_filename))
                    # https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes
                    colorspace = im.mode
                    im.close()
                    if not re.match(r"^RGB.*", colorspace):
                        if colorspace != '1' and not re.match(r"^L\w?", colorspace):
                            # here we have a color space like CMYK or YCbCr most likely
                            # decide which command line to use
                            if colorspace == 'CMYK':
                                with TemporaryDirectory() as temp_dir:
                                    profile = Path(temp_dir) / Path('embedded.icc')
                                    # save embedded profile if existing
                                    cmd = ['convert', str(img_filename), str(profile)]
                                    extractembedded = subprocess.Popen(cmd,
                                                                       stdout=subprocess.PIPE,
                                                                       stderr=subprocess.PIPE)
                                    stdout, stderr = extractembedded.communicate()
                                    # was there an embedded icc profile?
                                    if extractembedded.returncode == 0 and \
                                       profile.is_file() and \
                                       profile.stat().st_size > 0:
                                        cmd = _convert_cmyk2rgb_embedded_profile(
                                            img_filename)
                                        print('Convert CMYK (embedded) to '
                                              'RGB: {}'.format(node))
                                    else:
                                        cmd = _convert_cmyk2rgb_no_profile(
                                            img_filename)
                                        print('Convert CMYK (no profile) to '
                                              'RGB: {}'.format(node))
                                    if profile.is_file():
                                        profile.unlink()  # delete file
                            else:
                                cmd = _universal_convert_rgb_command(img_filename)
                                print('Warning: Convert exceptional color '
                                      'space {} to RGB: {}'.format(colorspace, node))
                            # convert command itself
                            fconvert = subprocess.Popen(cmd,
                                                        stdout=subprocess.PIPE,
                                                        stderr=subprocess.PIPE)
                            stdout, stderr = fconvert.communicate()
                            if fconvert.returncode != 0:
                                raise Exception('Error converting file {}'.format(img_filename) +
                                                ' to RGB color space: {}'.format(stderr))
                except UnidentifiedImageError:
                    # do nothing if we cannot open the image
                    print('Warning: Could not parse JPEG image with PIL: ' + str(img_filename))
        else:
            raise Exception('Error: Resource file not existing: ' + str(img_filename))


def main():
    in_dir = Path(sys.argv[1]).resolve(strict=True)
    out_dir = Path(sys.argv[2]).resolve(strict=True)
    book_slugs_file = Path(sys.argv[3]).resolve(strict=True)

    xhtml_files = in_dir.glob("*@*.xhtml")
    book_metadata = in_dir / "collection.toc-metadata.json"

    # Get the UUID of the book being processed
    with book_metadata.open() as json_file:
        json_data = json.load(json_file)
        book_uuid = json_data["id"]

    # Build map of book UUIDs to slugs that can be used to construct both
    # inter-book and intra-book links
    with book_slugs_file.open() as json_file:
        json_data = json.load(json_file)
        book_slugs_by_uuid = {
            elem["uuid"]: elem["slug"] for elem in json_data
        }

    for xhtml_file in xhtml_files:
        doc = etree.parse(str(xhtml_file))
        update_doc_links(
            doc,
            book_uuid,
            book_slugs_by_uuid
        )
        patch_math(doc)
        fix_jpeg_colorspace(doc, out_dir)
        doc.write(str(out_dir / xhtml_file.name), encoding="utf8")


if __name__ == "__main__":
    main()
