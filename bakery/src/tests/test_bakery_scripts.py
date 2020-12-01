"""Tests to validate JSON metadata extraction and file generation pipeline"""
import os
import json
from glob import glob
from lxml import etree
import boto3
import botocore.stub
import requests_mock
import requests
import pytest
import re
from googleapiclient.discovery import build
import google.auth
from googleapiclient.http import RequestMockBuilder

from cnxepub.html_parsers import HTML_DOCUMENT_NAMESPACES
from cnxepub.collation import reconstitute
from bakery_scripts import (
    jsonify_book,
    disassemble_book,
    link_extras,
    assemble_book_metadata,
    bake_book_metadata,
    check_feed,
    gdocify_book,
    copy_resources_s3,
    upload_docx,
    checksum_resource,
    fetch_map_resources
)

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(HERE, "data")
SCRIPT_DIR = os.path.join(HERE, "../scripts")


def test_checksum_resource(tmp_path, mocker):
    book_dir = tmp_path / "col00000"
    book_dir.mkdir()
    html_file = book_dir / "0.xhtml"
    module_dir = book_dir / "0"
    module_dir.mkdir()
    image_src = module_dir / "image_src.svg"
    image_href = module_dir / "image_href.svg"
    image_none = module_dir / "image_none.svg"

    # libmagic yields image/svg without the xml declaration
    image_src_content = ('<?xml version=1.0 ?>'
                         '<svg height="30" width="120">'
                         '<text x="0" y="15" fill="red">'
                         'checksum me!'
                         '</text>'
                         '</svg>')
    image_src_sha1_expected = "527617b308327b8773c5105edc8c28bcbbe62553"
    image_src_md5_expected = "420c64c8dbe981f216989328f9ad97e7"
    image_src.write_text(image_src_content)

    # libmagic yields image/svg without the xml declaration
    image_href_content = ('<?xml version=1.0 ?>'
                          '<svg height="30" width="120">'
                          '<text x="0" y="15" fill="red">'
                          'checksum me too!'
                          '</text>'
                          '</svg>')
    image_href_sha1_expected = "ad32bb3de1c805920a0ab50ab1333f39df8687a1"
    image_href_md5_expected = "46137319b2adb8b09c8f432343b8bcca"
    image_href.write_text(image_href_content)

    # libmagic yields image/svg without the xml declaration
    image_none_content = ('<?xml version=1.0 ?>'
                          '<svg height="30" width="120">'
                          '<text x="0" y="15" fill="red">'
                          'nope.'
                          '</text>'
                          '</svg>')
    image_none.write_text(image_none_content)

    html_content = ('<html xmlns="http://www.w3.org/1999/xhtml">'
                    '<img src="0/image_src.svg"/>'
                    '<a href="image_href.svg">linko</a>'
                    '</html>')
    html_file.write_text(html_content)

    mocker.patch(
        "sys.argv",
        ["", book_dir, book_dir]
    )
    checksum_resource.main()

    resource_dir = book_dir / "resources"
    image_src_meta = f"{image_src_sha1_expected}.json"
    image_href_meta = f"{image_href_sha1_expected}.json"
    assert set(path.name for path in resource_dir.glob("*")) == set([
        image_src_meta,
        image_href_meta,
        image_src_sha1_expected,
        image_href_sha1_expected
    ])
    assert json.load((resource_dir / image_src_meta).open("r")) == {
        'mime_type': 'image/svg+xml',
        'original_name': 'image_src.svg',
        # AWS needs the MD5 quoted inside the string json value.
        # Despite looking like a mistake, this is correct behavior.
        's3_md5': f'"{image_src_md5_expected}"',
        'sha1': image_src_sha1_expected
    }
    assert json.load((resource_dir / image_href_meta).open("r")) == {
        'mime_type': 'image/svg+xml',
        'original_name': 'image_href.svg',
        # AWS needs the MD5 quoted inside the string json value.
        # Despite looking like a mistake, this is correct behavior.
        's3_md5': f'"{image_href_md5_expected}"',
        'sha1': image_href_sha1_expected
    }
    assert resource_dir.exists()

    tree = etree.parse(str(html_file))
    expected = (f'<html xmlns="http://www.w3.org/1999/xhtml">'
                f'<img src="../resources/{image_src_sha1_expected}"/>'
                f'<a href="../resources/{image_href_sha1_expected}">linko</a>'
                f'</html>')
    assert etree.tostring(tree, encoding="utf8") == expected.encode("utf8")


def test_jsonify_book(tmp_path, mocker):
    """Test jsonify_book script"""

    html_content = "<html><body>test body</body></html>"
    toc_content = "<nav>TOC</nav>"
    json_metadata_content = {
        "title": "subsection title",
        "abstract": "subsection abstract",
        "slug": "1-3-subsection-slug",
    }

    mock_uuid = "00000000-0000-0000-0000-000000000000"
    mock_version = "0.0"
    mock_ident_hash = f"{mock_uuid}@{mock_version}"

    disassembled_input_dir = tmp_path / "disassembled"
    disassembled_input_dir.mkdir()

    xhtml_input = disassembled_input_dir / f"{mock_ident_hash}:m00001.xhtml"
    xhtml_input.write_text(html_content)
    toc_input = disassembled_input_dir / "collection.toc.xhtml"
    toc_input.write_text(toc_content)
    json_metadata_input = (
        disassembled_input_dir / f"{mock_ident_hash}:m00001-metadata.json"
    )
    json_metadata_input.write_text(json.dumps(json_metadata_content))

    jsonified_output_dir = tmp_path / "jsonified"
    jsonified_output_dir.mkdir()

    mocker.patch(
        "sys.argv", ["", disassembled_input_dir, tmp_path / "jsonified"]
    )
    jsonify_book.main()

    jsonified_output = jsonified_output_dir / f"{mock_ident_hash}:m00001.json"
    jsonified_output_data = json.loads(jsonified_output.read_text())
    jsonified_toc_output = jsonified_output_dir / "collection.toc.json"
    jsonified_toc_data = json.loads(jsonified_toc_output.read_text())

    assert jsonified_output_data.get("title") == json_metadata_content["title"]
    assert (
        jsonified_output_data.get("abstract")
        == json_metadata_content["abstract"]
    )
    assert jsonified_output_data.get("slug") == json_metadata_content["slug"]
    assert jsonified_output_data.get("content") == html_content
    assert jsonified_toc_data.get("content") == toc_content


def test_disassemble_book(tmp_path, mocker):
    """Test disassemble_book script"""
    input_baked_xhtml = os.path.join(TEST_DATA_DIR, "collection.baked.xhtml")
    input_baked_metadata = os.path.join(
        TEST_DATA_DIR, "collection.baked-metadata.json"
    )

    input_dir = tmp_path / "book"
    input_dir.mkdir()

    input_baked_xhtml_file = input_dir / "collection.baked.xhtml"
    input_baked_xhtml_file.write_bytes(open(input_baked_xhtml, "rb").read())
    input_baked_metadata_file = input_dir / "collection.baked-metadata.json"
    input_baked_metadata_file.write_text(
        open(input_baked_metadata, "r").read()
    )

    disassembled_output = input_dir / "disassembled"
    disassembled_output.mkdir()

    mock_uuid = "00000000-0000-0000-0000-000000000000"
    mock_version = "0.0"
    mock_ident_hash = f"{mock_uuid}@{mock_version}"

    mocker.patch("sys.argv", ["",
                              str(input_baked_xhtml_file),
                              str(input_baked_metadata_file),
                              "collection",
                              str(disassembled_output)])
    disassemble_book.main()

    xhtml_output_files = glob(f"{disassembled_output}/*.xhtml")
    assert len(xhtml_output_files) == 3
    json_output_files = glob(f"{disassembled_output}/*-metadata.json")
    assert len(json_output_files) == 3

    # Check for expected files and metadata that should be generated in
    # this step
    json_output_m42119 = (
        disassembled_output / f"{mock_ident_hash}:m42119-metadata.json"
    )
    json_output_m42092 = (
        disassembled_output / f"{mock_ident_hash}:m42092-metadata.json"
    )
    m42119_data = json.load(open(json_output_m42119, "r"))
    m42092_data = json.load(open(json_output_m42092, "r"))
    assert (
        m42119_data.get("title")
        == "Introduction to Science and the Realm of Physics, "
        "Physical Quantities, and Units"
    )
    assert (
        m42119_data.get("slug")
        == "1-introduction-to-science-and-the-realm-of-physics-physical-"
        "quantities-and-units"
    )
    assert m42119_data["abstract"] is None
    assert m42119_data["revised"] == "2018/08/03 15:49:52 -0500"
    assert m42092_data.get("title") == "Physics: An Introduction"
    assert m42092_data.get("slug") == "1-1-physics-an-introduction"
    assert (
        m42092_data.get("abstract")
        == "Explain the difference between a model and a theory"
    )
    assert m42092_data["revised"] is not None

    toc_output = disassembled_output / "collection.toc.xhtml"
    assert toc_output.exists()
    toc_output_tree = etree.parse(open(toc_output))
    nav = toc_output_tree.xpath(
        "//xhtml:nav", namespaces=HTML_DOCUMENT_NAMESPACES
    )
    assert len(nav) == 1
    toc_metadata_output = disassembled_output / "collection.toc-metadata.json"
    assert toc_metadata_output.exists()
    toc_metadata = json.load(open(toc_metadata_output, "r"))
    assert toc_metadata.get("title") == "College Physics"


def test_disassemble_book_empty_baked_metadata(tmp_path, mocker):
    """Test case for disassemble where there may not be associated metadata
    from previous steps in collection.baked-metadata.json
    """
    input_baked_xhtml = os.path.join(TEST_DATA_DIR, "collection.baked.xhtml")

    input_dir = tmp_path / "book"
    input_dir.mkdir()

    input_baked_xhtml_file = input_dir / "collection.baked.xhtml"
    input_baked_xhtml_file.write_bytes(open(input_baked_xhtml, "rb").read())
    input_baked_metadata_file = input_dir / "collection.baked-metadata.json"
    input_baked_metadata_file.write_text(json.dumps({}))

    disassembled_output = input_dir / "disassembled"
    disassembled_output.mkdir()

    mock_uuid = "00000000-0000-0000-0000-000000000000"
    mock_version = "0.0"
    mock_ident_hash = f"{mock_uuid}@{mock_version}"

    mocker.patch("sys.argv", ["",
                              str(input_baked_xhtml_file),
                              str(input_baked_metadata_file),
                              "collection",
                              str(disassembled_output)])
    disassemble_book.main()

    # Check for expected files and metadata that should be generated in this
    # step
    json_output_m42119 = (
        disassembled_output / f"{mock_ident_hash}:m42119-metadata.json"
    )
    json_output_m42092 = (
        disassembled_output / f"{mock_ident_hash}:m42092-metadata.json"
    )
    m42119_data = json.load(open(json_output_m42119, "r"))
    m42092_data = json.load(open(json_output_m42092, "r"))
    assert m42119_data["abstract"] is None
    assert m42119_data["id"] == "m42119"
    assert m42092_data["abstract"] is None
    assert m42092_data["id"] == "m42092"


def test_canonical_list_order():
    """Test if legacy ordering of canonical books is preserved"""
    canonical_list = os.path.join(SCRIPT_DIR, "canonical-book-list.json")

    with open(canonical_list) as canonical:
        books = json.load(canonical)
        names = [book["_name"] for book in books["canonical_books"]]

    assert {"College Algebra", "Precalculus"}.issubset(set(names))
    assert names.index("College Algebra") < names.index("Precalculus")

    # All 1e books should come after 2e variants
    assert names.index("American Government 2e") < \
        names.index("American Government 1e")
    assert names.index("Biology 2e") < names.index("Biology 1e")
    assert names.index("Chemistry 2e") < names.index("Chemistry 1e")
    assert names.index("Chemistry 2e") < \
        names.index("Chemistry: Atoms First 1e")
    assert names.index("Biology 2e") < \
        names.index("Concepts of Biology")
    assert names.index("Introduction to Sociology 2e") < \
        names.index("Introduction to Sociology 1e")
    assert names.index("Principles of Economics 2e") < \
        names.index("Principles of Economics 1e")
    assert names.index("Principles of Economics 2e") < \
        names.index("Principles of Macroeconomics 1e")
    assert names.index("Principles of Economics 2e") < \
        names.index("Principles of Macroeconomics for AP Courses 1e")
    assert names.index("Principles of Economics 2e") < \
        names.index("Principles of Microeconomics 1e")
    assert names.index("Principles of Economics 2e") < \
        names.index("Principles of Microeconomics for AP Courses 1e")

    # Check for expected ordering within 1e variants
    assert names.index("Biology 1e") < names.index("Concepts of Biology")
    assert names.index("Chemistry 1e") < \
        names.index("Chemistry: Atoms First 1e")
    assert names.index("Principles of Economics 1e") < \
        names.index("Principles of Macroeconomics 1e")
    assert names.index("Principles of Macroeconomics 1e") < \
        names.index("Principles of Microeconomics 1e")
    assert names.index("Principles of Microeconomics 1e") < \
        names.index("Principles of Macroeconomics for AP Courses 1e")
    assert names.index("Principles of Macroeconomics for AP Courses 1e") < \
        names.index("Principles of Microeconomics for AP Courses 1e")


def mock_link_extras(tmp_path, content_dict, contents_dict, extras_dict,
                     page_content):
    input_dir = tmp_path / "linked-extras"
    input_dir.mkdir()

    server = "mock.archive"

    canonical_list = f"{SCRIPT_DIR}/canonical-book-list.json"

    adapter = requests_mock.Adapter()

    content_matcher = re.compile(f"https://{server}/content/")

    def content_callback(request, context):
        module_uuid = content_dict[request.url.split("/")[-1]]
        context.status_code = 301
        context.headers['Location'] = \
            f"https://{server}/contents/{module_uuid}"
        return

    adapter.register_uri("GET", content_matcher, json=content_callback)

    extras_matcher = re.compile(f"https://{server}/extras/")

    def extras_callback(request, context):
        return extras_dict[request.url.split("/")[-1]]

    adapter.register_uri("GET", extras_matcher, json=extras_callback)

    contents_matcher = re.compile(f"https://{server}/contents/")

    def contents_callback(request, context):
        return contents_dict[request.url.split("/")[-1]]

    adapter.register_uri("GET", contents_matcher, json=contents_callback)

    collection_name = "collection.assembled.xhtml"
    collection_input = input_dir / collection_name
    collection_input.write_text(page_content)

    link_extras.transform_links(input_dir, server, canonical_list, adapter)


def test_link_extras_single_match(tmp_path, mocker):
    """Test for link_extras script case with single
    containing book and a canonical match"""

    content_dict = {"m12345": "1234-5678-1234-5678@version"}

    contents_dict = {
        "00000000-0000-0000-0000-000000000000": {
            "tree": {
                "id": "",
                "slug": "",
                "contents": [
                    {
                        "id": "1234-5678-1234-5678@version",
                        "slug": "1234-slug"
                    }
                ]
            }
        }
    }

    extras_dict = {
        "1234-5678-1234-5678@version": {
            "books": [{"ident_hash": "00000000-0000-0000-0000-000000000000@1"}]
        }
    }

    page_content = """
        <html xmlns="http://www.w3.org/1999/xhtml">
        <body>
        <div data-type="page">
        <p><a id="l1"
            href="/contents/internal-uuid"
            class="target-chapter">Intra-book module link</a></p>
        <p><a id="l2"
            href="/contents/m12345"
            class="target-chapter"
            data-book-uuid="otheruuid">Inter-book module link</a></p>
        <p><a id="l3"
            href="#foobar"
            class="autogenerated-content">Reference in page</a></p>
        <p><a id="l4" href="http://www.openstax.org/l/shorturl">
            External shortened link</a></p>
        <p><a id="l5"
            href="/contents/m12345#fragment"
            class="target-chapter"
            data-book-uuid="otheruuid">Inter-book link with fragment</a></p>
        </div>
        </body>
        </html>
    """

    expected_links = [
        [
            ("id", "l1"),
            ("href", "/contents/internal-uuid"),
            ("class", "target-chapter"),
        ],
        [
            ("id", "l2"),
            ("href", "/contents/1234-5678-1234-5678"),
            ("class", "target-chapter"),
            ("data-book-uuid", "00000000-0000-0000-0000-000000000000"),
            ("data-page-slug", "1234-slug"),
        ],
        [
            ("id", "l5"),
            ("href", "/contents/1234-5678-1234-5678#fragment"),
            ("class", "target-chapter"),
            ("data-book-uuid", "00000000-0000-0000-0000-000000000000"),
            ("data-page-slug", "1234-slug"),
        ],
    ]

    mock_link_extras(tmp_path, content_dict, contents_dict, extras_dict,
                     page_content)

    output_dir = tmp_path / "linked-extras"

    collection_output = output_dir / "collection.linked.xhtml"
    tree = etree.parse(str(collection_output))

    parsed_links = tree.xpath(
        '//x:a[@href and starts-with(@href, "/contents/")]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    )

    for pair in zip(expected_links, parsed_links):
        assert pair[0] == pair[1].items()


def test_link_extras_no_containing(tmp_path, mocker):
    """Test for link_extras script case with no
    containing books"""

    content_dict = {"m12345": "1234-5678-1234-5678@version"}

    contents_dict = {}

    extras_dict = {
        "1234-5678-1234-5678@version": {
            "books": []
        }
    }

    page_content = """
        <html xmlns="http://www.w3.org/1999/xhtml">
        <body>
        <div data-type="page">
        <p><a id="l1"
            href="/contents/internal-uuid"
            class="target-chapter">Intra-book module link</a></p>
        <p><a id="l2"
            href="/contents/m12345"
            class="target-chapter"
            data-book-uuid="otheruuid">Inter-book module link</a></p>
        <p><a id="l3"
            href="#foobar"
            class="autogenerated-content">Reference in page</a></p>
        <p><a id="l4" href="http://www.openstax.org/l/shorturl">
            External shortened link</a></p>
        </div>
        </body>
        </html>
    """

    with pytest.raises(
        Exception,
        match=r'(No containing books).*\n(content).*\n(module link)'
    ):
        mock_link_extras(tmp_path, content_dict, contents_dict, extras_dict,
                         page_content)


def test_link_extras_single_no_match(tmp_path, mocker):
    """Test for link_extras script case with single
    containing book and no canonical match"""

    content_dict = {"m12345": "1234-5678-1234-5678@version"}

    contents_dict = {
        "4664c267-cd62-4a99-8b28-1cb9b3aee347": {
            "tree": {
                "id": "",
                "slug": "",
                "contents": [
                    {
                        "id": "1234-5678-1234-5678@version",
                        "slug": "1234-slug"
                    }
                ]
            }
        }
    }

    extras_dict = {
        "1234-5678-1234-5678@version": {
            "books": [{"ident_hash": "4664c267-cd62-4a99-8b28-1cb9b3aee347@1"}]
        }
    }

    page_content = """
        <html xmlns="http://www.w3.org/1999/xhtml">
        <body>
        <div data-type="page">
        <p><a id="l1"
            href="/contents/internal-uuid"
            class="target-chapter">Intra-book module link</a></p>
        <p><a id="l2"
            href="/contents/m12345"
            class="target-chapter"
            data-book-uuid="otheruuid">Inter-book module link</a></p>
        <p><a id="l3"
            href="#foobar"
            class="autogenerated-content">Reference in page</a></p>
        <p><a id="l4" href="http://www.openstax.org/l/shorturl">
            External shortened link</a></p>
        </div>
        </body>
        </html>
    """

    expected_links = [
        [
            ("id", "l1"),
            ("href", "/contents/internal-uuid"),
            ("class", "target-chapter"),
        ],
        [
            ("id", "l2"),
            ("href", "/contents/1234-5678-1234-5678"),
            ("class", "target-chapter"),
            ("data-book-uuid", "4664c267-cd62-4a99-8b28-1cb9b3aee347"),
            ("data-page-slug", "1234-slug"),
        ],
    ]

    mock_link_extras(tmp_path, content_dict, contents_dict, extras_dict,
                     page_content)

    output_dir = tmp_path / "linked-extras"

    collection_output = output_dir / "collection.linked.xhtml"
    tree = etree.parse(str(collection_output))

    parsed_links = tree.xpath(
        '//x:a[@href and starts-with(@href, "/contents/")]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    )

    for pair in zip(expected_links, parsed_links):
        assert pair[0] == pair[1].items()


def test_link_extras_multi_match(tmp_path, mocker):
    """Test for link_extras script case with multiple
    containing book and a canonical match"""

    content_dict = {"m12345": "1234-5678-1234-5678@version"}

    contents_dict = {
        "4664c267-cd62-4a99-8b28-1cb9b3aee347": {
            "tree": {
                "id": "",
                "slug": "",
                "contents": [
                    {
                        "id": "1234-5678-1234-5678@version",
                        "slug": "1234-slug"
                    }
                ]
            }
        }
    }

    extras_dict = {
        "1234-5678-1234-5678@version": {
            "books": [
                {"ident_hash": "00000000-0000-0000-0000-000000000000@1"},
                {"ident_hash": "4664c267-cd62-4a99-8b28-1cb9b3aee347@1"},
            ]
        }
    }

    page_content = """
        <html xmlns="http://www.w3.org/1999/xhtml">
        <body>
        <div data-type="page">
        <p><a id="l1"
            href="/contents/internal-uuid"
            class="target-chapter">Intra-book module link</a></p>
        <p><a id="l2"
            href="/contents/m12345"
            class="target-chapter"
            data-book-uuid="otheruuid">Inter-book module link</a></p>
        <p><a id="l3"
            href="#foobar"
            class="autogenerated-content">Reference in page</a></p>
        <p><a id="l4" href="http://www.openstax.org/l/shorturl">
            External shortened link</a></p>
        </div>
        </body>
        </html>
    """

    expected_links = [
        [
            ("id", "l1"),
            ("href", "/contents/internal-uuid"),
            ("class", "target-chapter"),
        ],
        [
            ("id", "l2"),
            ("href", "/contents/1234-5678-1234-5678"),
            ("class", "target-chapter"),
            ("data-book-uuid", "4664c267-cd62-4a99-8b28-1cb9b3aee347"),
            ("data-page-slug", "1234-slug"),
        ],
    ]

    mock_link_extras(tmp_path, content_dict, contents_dict, extras_dict,
                     page_content)

    output_dir = tmp_path / "linked-extras"

    collection_output = output_dir / "collection.linked.xhtml"
    tree = etree.parse(str(collection_output))

    parsed_links = tree.xpath(
        '//x:a[@href and starts-with(@href, "/contents/")]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    )

    for pair in zip(expected_links, parsed_links):
        assert pair[0] == pair[1].items()


def test_link_extras_multi_no_match(tmp_path, mocker):
    """Test for link_extras script case with multiple
    containing book and a canonical match"""

    content_dict = {"m12345": "1234-5678-1234-5678@version"}

    contents_dict = {}

    extras_dict = {
        "1234-5678-1234-5678@version": {
            "books": [
                {"ident_hash": "00000000-0000-0000-0000-000000000000@1"},
                {"ident_hash": "11111111-1111-1111-1111-111111111111@1"},
            ]
        }
    }

    page_content = """
        <html xmlns="http://www.w3.org/1999/xhtml">
        <body>
        <div data-type="page">
        <p><a id="l1"
            href="/contents/internal-uuid"
            class="target-chapter">Intra-book module link</a></p>
        <p><a id="l2"
            href="/contents/m12345"
            class="target-chapter"
            data-book-uuid="otheruuid">Inter-book module link</a></p>
        <p><a id="l3"
            href="#foobar"
            class="autogenerated-content">Reference in page</a></p>
        <p><a id="l4" href="http://www.openstax.org/l/shorturl">
            External shortened link</a></p>
        </div>
        </body>
        </html>
    """

    with pytest.raises(
        Exception,
        match=r'(no canonical).*\n.*(content).*\n.*(link).*\n.*(containing)'
    ):
        mock_link_extras(tmp_path, content_dict, contents_dict, extras_dict,
                         page_content)


def test_link_extras_page_slug_not_found(tmp_path):
    """Test for exception if page slug is not found"""
    content_dict = {"m12345": "1234-5678-1234-5678@version"}

    contents_dict = {
        "00000000-0000-0000-0000-000000000000": {
            "tree": {
                "id": "",
                "slug": "",
                "contents": [
                    {
                        "id": "",
                        "slug": ""
                    }
                ]
            }
        }
    }

    extras_dict = {
        "1234-5678-1234-5678@version": {
            "books": [{"ident_hash": "00000000-0000-0000-0000-000000000000@1"}]
        }
    }

    page_content = """
        <html xmlns="http://www.w3.org/1999/xhtml">
        <body>
        <div data-type="page">
        <p><a id="l1"
            href="/contents/m12345"
            class="target-chapter"
            data-book-uuid="otheruuid">Inter-book module link</a></p>
        </div>
        </body>
        </html>
    """

    with pytest.raises(
        Exception,
        match=r'(Could not find page slug for module)'
    ):
        mock_link_extras(tmp_path, content_dict, contents_dict, extras_dict,
                         page_content)


def test_link_extras_page_slug_resolver(requests_mock):
    """Test page slug resolver in link_extras script"""
    requests_mock.get(
        "/contents/4664c267-cd62-4a99-8b28-1cb9b3aee347",
        json={
            "tree": {
                "id": "",
                "slug": "",
                "contents": [
                    {
                        "id": "1234-5678-1234-5678@version",
                        "slug": "1234-slug"
                    },
                    {
                        "id": "1111-2222-3333-4444@version",
                        "slug": "1111-slug"
                    }
                ]
            }
        }
    )

    page_slug_resolver = link_extras.gen_page_slug_resolver(
        requests.Session(),
        "mock.archive"
    )

    res = page_slug_resolver(
        "4664c267-cd62-4a99-8b28-1cb9b3aee347",
        "1234-5678-1234-5678@version"
    )
    assert res == "1234-slug"
    assert requests_mock.call_count == 1
    # Query slug for different page in same book to ensure the mocker isn't
    # called again
    requests_mock.reset_mock()
    res = page_slug_resolver(
        "4664c267-cd62-4a99-8b28-1cb9b3aee347",
        "1111-2222-3333-4444@version"
    )
    assert res == "1111-slug"
    assert requests_mock.call_count == 0

    # Test for unmatched slug
    res = page_slug_resolver(
        "4664c267-cd62-4a99-8b28-1cb9b3aee347",
        "foobar@version"
    )
    assert res is None


def test_assemble_book_metadata(tmp_path, mocker):
    """Test assemble_book_metadata script"""
    input_assembled_book = os.path.join(TEST_DATA_DIR,
                                        "assembled-book",
                                        "collection.assembled.xhtml")

    input_uuid_to_revised = tmp_path / "uuid-to-revised-map.json"
    with open(input_uuid_to_revised, 'w') as f:
        json.dump({
            "m42119": "2018/08/03 15:49:52 -0500",
            "m42092": "2018/09/18 09:55:13.413 GMT-5"
        }, f)

    assembled_metadata_output = tmp_path / "collection.assembed-metadata.json"

    mocker.patch(
        "sys.argv", ["", input_assembled_book, input_uuid_to_revised, assembled_metadata_output]
    )
    assemble_book_metadata.main()

    assembled_metadata = json.loads(assembled_metadata_output.read_text())
    assert assembled_metadata["m42119@1.6"]["abstract"] is None
    assert (
        "Explain the difference between a model and a theory"
        in assembled_metadata["m42092@1.10"]["abstract"]
    )
    assert (
        assembled_metadata["m42092@1.10"]["revised"]
        == "2018/09/18 09:55:13.413 GMT-5"
    )
    assert (
        assembled_metadata["m42119@1.6"]["revised"]
        == "2018/08/03 15:49:52 -0500"
    )


def test_bake_book_metadata(tmp_path, mocker):
    """Test bake_book_metadata script"""
    input_raw_metadata = os.path.join(
        TEST_DATA_DIR, "collection.assembled-metadata.json"
    )
    input_baked_xhtml = os.path.join(TEST_DATA_DIR, "collection.baked.xhtml")
    output_baked_book_metadata = tmp_path / "collection.toc-metadata.json"
    book_uuid = "031da8d3-b525-429c-80cf-6c8ed997733a"
    book_slugs = [
        {
            "uuid": book_uuid,
            "slug": "test-book-slug"
        }
    ]
    book_slugs_input = tmp_path / "book-slugs.json"
    book_slugs_input.write_text(json.dumps(book_slugs))

    with open(input_baked_xhtml, "r") as baked_xhtml:
        binder = reconstitute(baked_xhtml)
        book_ident_hash = binder.ident_hash

    mocker.patch(
        "sys.argv",
        [
            "",
            input_raw_metadata,
            input_baked_xhtml,
            book_uuid,
            book_slugs_input,
            output_baked_book_metadata,
        ],
    )
    bake_book_metadata.main()

    baked_metadata = json.loads(output_baked_book_metadata.read_text())

    assert isinstance(baked_metadata[book_ident_hash]["tree"], dict) is True
    assert "contents" in baked_metadata[book_ident_hash]["tree"].keys()
    assert "license" in baked_metadata[book_ident_hash].keys()
    assert (
        baked_metadata[book_ident_hash]["revised"]
        == "2019-08-30T16:35:37.569966-05:00"
    )
    assert "College Physics" in baked_metadata[book_ident_hash]["title"]
    assert baked_metadata[book_ident_hash]["slug"] == "test-book-slug"


def test_check_feed(tmp_path, mocker):
    """Test check_feed script"""
    input_book_feed = [
        {
            "name": "Introduction to Sociology 2e",
            "collection_id": "col11762",
            "style": "sociology",
            "version": "1.14.1",
            "server": "cnx.foobar.org",
            "uuid": "02040312-72c8-441e-a685-20e9333f3e1d",
        },
        {
            "name": "College Physics",
            "collection_id": "col11406",
            "style": "college-physics",
            "version": "1.20.15",
            "server": "cnx.foobar.org",
            "uuid": "031da8d3-b525-429c-80cf-6c8ed997733a",
        },
    ]

    json_feed_input = tmp_path / "book-feed.json"
    json_feed_input.write_text(json.dumps(input_book_feed))

    # We'll use the botocore stubber to play out a simple scenario to test the
    # script where we'll trigger multiple invocations to "build" all books
    # above. Documenting this in words just to help with readability and
    # maintainability.
    #
    # Expected s3 requests / responses by invocation:
    #
    # Invocation 1:
    #   - book 1
    #       - Initial check for .complete: head_object => Return a 404
    #       - Check for .pending: head_object => Return a 404
    #       - put_object by script with book data
    #       - put_object by script with .pending state

    # Invocation 2:
    #   - book 1 (emulate a failure from first invocation)
    #       - Check for .complete => head_object => Return a 404
    #       - Check for .pending: head_object => Return data
    #       - Check for .retry: head_object => Return 404
    #       - put_object by script with book data
    #       - put_object by script with .retry state
    #
    # Invocation 3:
    #   - book 1
    #       - Check for .complete => head_object return object
    #   - book 2
    #       - Initial check for .complete: head_object => Return a 404
    #       - Check for .pending head_object => Return a 404
    #       - put_object by script with book data
    #       - put_object by script with .pending state

    queue_state_bucket = "queue-state-bucket"
    queue_filename = "queue-state-filename.json"
    code_version = "code-version"
    state_prefix = "foobar"
    book1 = input_book_feed[0]
    book1_col = book1["collection_id"]
    book1_vers = book1["version"]
    book2 = input_book_feed[1]
    book2_col = book2["collection_id"]
    book2_vers = book2["version"]

    s3_client = boto3.client("s3")
    s3_stubber = botocore.stub.Stubber(s3_client)

    def _stubber_add_head_object_404(expected_key):
        s3_stubber.add_client_error(
            "head_object",
            service_error_meta={"Code": "404"},
            expected_params={
                "Bucket": queue_state_bucket,
                "Key": expected_key,
            },
        )

    def _stubber_add_head_object(expected_key):
        s3_stubber.add_response(
            "head_object",
            {},
            expected_params={
                "Bucket": queue_state_bucket,
                "Key": expected_key,
            },
        )

    def _stubber_add_put_object(expected_key, expected_body):
        s3_stubber.add_response(
            "put_object",
            {},
            expected_params={
                "Bucket": queue_state_bucket,
                "Key": expected_key,
                "Body": expected_body,
            },
        )

    # Book 1: Check for .complete file
    _stubber_add_head_object_404(
        f"{code_version}/.{state_prefix}.{book1_col}@{book1_vers}.complete"
    )

    # Book 1: Check for .pending file
    _stubber_add_head_object_404(
        f"{code_version}/.{state_prefix}.{book1_col}@{book1_vers}.pending"
    )

    # Book 1: Put book data
    _stubber_add_put_object(queue_filename, json.dumps(book1))

    # Book 1: Put book .pending
    _stubber_add_put_object(
        f"{code_version}/.{state_prefix}.{book1_col}@{book1_vers}.pending",
        botocore.stub.ANY
    )

    # Book 1: Check for .complete file
    _stubber_add_head_object_404(
        f"{code_version}/.{state_prefix}.{book1_col}@{book1_vers}.complete"
    )

    # Book 1: Check for .pending file (return as though it exists)
    _stubber_add_head_object(
        f"{code_version}/.{state_prefix}.{book1_col}@{book1_vers}.pending"
    )

    # Book 1: Check for .retry file
    _stubber_add_head_object_404(
        f"{code_version}/.{state_prefix}.{book1_col}@{book1_vers}.retry"
    )

    # Book 1: Put book data again
    _stubber_add_put_object(queue_filename, json.dumps(book1))

    # Book 1: Put book .retry
    _stubber_add_put_object(
        f"{code_version}/.{state_prefix}.{book1_col}@{book1_vers}.retry",
        botocore.stub.ANY
    )

    # Book 1: Check for .complete file
    _stubber_add_head_object(
        f"{code_version}/.{state_prefix}.{book1_col}@{book1_vers}.complete"
    )

    # Book 2: Check for .complete file
    _stubber_add_head_object_404(
        f"{code_version}/.{state_prefix}.{book2_col}@{book2_vers}.complete"
    )

    # Book 2: Check for .pending file
    _stubber_add_head_object_404(
        f"{code_version}/.{state_prefix}.{book2_col}@{book2_vers}.pending"
    )

    # Book 2: Put book data
    _stubber_add_put_object(queue_filename, json.dumps(book2))

    # Book 2: Put book .pending
    _stubber_add_put_object(
        f"{code_version}/.{state_prefix}.{book2_col}@{book2_vers}.pending",
        botocore.stub.ANY
    )

    s3_stubber.activate()

    mocker.patch("boto3.client", lambda service: s3_client)
    mocker.patch(
        "sys.argv",
        [
            "",
            json_feed_input,
            code_version,
            queue_state_bucket,
            queue_filename,
            1,
            state_prefix
        ],
    )

    for _ in range(3):
        check_feed.main()

    s3_stubber.assert_no_pending_responses()
    s3_stubber.deactivate()


def test_gdocify_book(tmp_path, mocker):
    """Test gdocify_book script"""

    input_dir = tmp_path / "disassembled"
    input_dir.mkdir()
    output_dir = tmp_path / "gdocified"
    output_dir.mkdir()

    page_content = """
        <html xmlns="http://www.w3.org/1999/xhtml">
        <body>
        <div data-type="page">
        <p><a id="l1"
            href="/contents/internal-uuid"
            class="target-chapter">Intra-book module link</a></p>
        <p><a id="l2"
            href="/contents/external-uuid"
            class="target-chapter"
            data-book-uuid="otheruuid"
            data-page-slug="l2-page-slug">Inter-book module link</a></p>
        <p><a id="l3"
            href="#foobar"
            class="autogenerated-content">Reference in page</a></p>
        <p><a id="l4" href="http://www.openstax.org/l/shorturl">
            External shortened link</a></p>
        <p><a id="l5"
            href="/contents/internal-uuid#foobar"
            class="target-chapter">Intra-book module link with fragment</a></p>
        <math>
            <mrow>
                <mtext mathvariant="bold-italic">x</mtext>
            </mrow>
        </math>
        <math>
            <semantics>
                <mrow>
                    <mrow>
                        <mrow>
                            <msubsup>
                                <mrow>
                                    <mi>N</mi>
                                    <mo>′</mo>
                                </mrow>
                                <mrow>
                                    <mtext>R</mtext>
                                </mrow>
                            </msubsup>
                        </mrow>
                        <mrow></mrow>
                    </mrow>
                </mrow>
                <annotation-xml encoding="MathML-Content">
                    <semantics>
                        <mrow>
                            <mrow>
                                <msubsup>
                                    <mrow>
                                        <mi>N</mi>
                                        <mo>′</mo>
                                    </mrow>
                                    <mrow>
                                        <mtext>R</mtext>
                                    </mrow>
                                </msubsup>
                            </mrow>
                            <mrow></mrow>
                        </mrow>
                        <annotation encoding="StarMath 5.0"> size 12{ { {N}} sup { x } rSub { size 8{R} } } {}</annotation>
                    </semantics>
                </annotation-xml>
            </semantics>
        </math>
        </div>
        </body>
        </html>
    """

    l1_page_metadata = {
        "slug": "l1-page-slug"
    }

    book_metadata = {
        "id": "bookuuid1"
    }

    book_slugs = [
        {
            "uuid": "bookuuid1",
            "slug": "bookuuid1-slug"
        },
        {
            "uuid": "otheruuid",
            "slug": "otheruuid-slug"
        }
    ]

    # Populate a dummy TOC to confirm it is ignored
    toc_input = input_dir / "collection.toc.xhtml"
    toc_input.write_text("DUMMY")
    book_metadata_input = input_dir / "collection.toc-metadata.json"
    book_metadata_input.write_text(json.dumps(book_metadata))
    page_name = "bookuuid1@version:pageuuid1.xhtml"
    page_input = input_dir / page_name
    page_input.write_text(page_content)
    l1_page_metadata_name = "bookuuid1@version:internal-uuid-metadata.json"
    l1_page_metadata_input = input_dir / l1_page_metadata_name
    book_slugs_input = tmp_path / "book-slugs.json"
    book_slugs_input.write_text(json.dumps(book_slugs))

    # Test gen_page_slug_resolver
    page_slug_resolver = gdocify_book.gen_page_slug_resolver(
        [l1_page_metadata_input]
    )
    # Run a query that should raise
    with pytest.raises(ValueError):
        l1_page_metadata_input.write_text(json.dumps({}))
        res = page_slug_resolver("internal-uuid")

    l1_page_metadata_input.write_text(json.dumps(l1_page_metadata))
    res = page_slug_resolver("internal-uuid")
    assert res == "l1-page-slug"
    # Temporarily change data in file to ensure on a subsequent request we
    # get the cached value
    l1_page_metadata_input.write_text(json.dumps({}))
    res = page_slug_resolver("internal-uuid")
    assert res == "l1-page-slug"

    l1_page_metadata_input.write_text(json.dumps(l1_page_metadata))

    # Test complete script
    mocker.patch("sys.argv", ["", input_dir, output_dir, book_slugs_input])
    gdocify_book.main()

    page_output = output_dir / page_name
    assert page_output.exists()

    expected_links_by_id = {
        "l1": "http://openstax.org/books/bookuuid1-slug/pages/l1-page-slug",
        "l2": "http://openstax.org/books/otheruuid-slug/pages/l2-page-slug",
        "l3": "#foobar",
        "l4": "http://www.openstax.org/l/shorturl",
        "l5": "http://openstax.org/books/bookuuid1-slug/"
              "pages/l1-page-slug#foobar",
    }

    updated_doc = etree.parse(str(page_output))

    for node in updated_doc.xpath(
        "//x:a[@href]", namespaces={"x": "http://www.w3.org/1999/xhtml"},
    ):
        assert expected_links_by_id[node.attrib["id"]] == node.attrib["href"]

    for node in updated_doc.xpath(
        '//x:*[@mathvariant="bold-italic"]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    ):
        assert "mi" == node.tag.split("}")[1]

    unwanted_nodes = updated_doc.xpath(
        '//x:annotation-xml',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    )
    assert len(unwanted_nodes) == 0

    unwanted_nodes = updated_doc.xpath(
        '//x:annotation[@encoding="StarMath 5.0"]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    )
    assert len(unwanted_nodes) == 0

    unwanted_nodes = updated_doc.xpath(
        '//x:msubsup[count(*) < 3]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    )
    assert len(unwanted_nodes) == 0

    unwanted_nodes = updated_doc.xpath(
        '//x:msub[count(*) > 2]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    )
    assert len(unwanted_nodes) == 0

    msub_nodes = updated_doc.xpath(
        '//x:msub',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    )
    assert len(msub_nodes) == 1


class ANY_OF:
    def __init__(self, items):
        self.items = items

    def __eq__(self, other):
        return other in self.items

    def __ne__(self, other):
        return other not in self.items

    def __repr__(self):
        return f'<ANY OF {self.items}>'


def test_copy_resource_s3(tmp_path, mocker):
    """Test copy_resource_s3 script"""

    resource_sha = 'fffe62254ef635871589a848b65db441318171eb'
    resource_a_name = resource_sha
    resource_b_name = resource_sha + '.json'

    book_dir = tmp_path / "col11762"
    book_dir.mkdir()
    resources_dir = book_dir / "resources"
    resources_dir.mkdir()

    resource_a = resources_dir / resource_a_name
    resource_b = resources_dir / resource_b_name

    # copy over the test data a to the tmp_path
    resource_a_data = os.path.join(TEST_DATA_DIR, resource_a_name)
    resource_a_data = open(resource_a_data, "rb").read()
    resource_a.write_bytes(resource_a_data)

    # copy over the test data b to the tmp_path
    resource_b_data = os.path.join(TEST_DATA_DIR, resource_b_name)
    resource_b_data = open(resource_b_data, "rb").read()
    resource_b.write_bytes(resource_b_data)

    bucket = 'distribution-bucket-1234'
    prefix = 'master/resources'

    key_a = prefix + '/' + resource_a_name
    key_b = prefix + '/' + resource_sha + '-unused.json'

    s3_client = boto3.client('s3')
    s3_stubber = botocore.stub.Stubber(s3_client)
    s3_stubber.add_response(
        'list_objects',
        {},
        expected_params={
            'Bucket': bucket,
            'Prefix': prefix + '/',
            'Delimiter': '/'
        }
    )
    s3_stubber.add_response(
        "put_object",
        {},
        expected_params={
            'Body': botocore.stub.ANY,
            'Bucket': bucket,
            'ContentType': ANY_OF(['application/json', 'image/jpeg']),
            'Key': ANY_OF([key_b, key_a]),
        }
    )
    s3_stubber.add_response(
        "put_object",
        {},
        expected_params={
            'Body':  botocore.stub.ANY,
            'Bucket': bucket,
            'ContentType': ANY_OF(['application/json', 'image/jpeg']),
            'Key': ANY_OF([key_b, key_a]),
        }
    )
    s3_stubber.activate()

    mocked_session = boto3.session.Session
    mocked_session.client = mocker.MagicMock(return_value=s3_client)
    mocker.patch(
        'boto3.session.Session',
        mocked_session
    )
    mocker.patch(
        'sys.argv',
        ['',
         resources_dir,
         bucket,
         prefix]
    )

    os.environ['AWS_ACCESS_KEY_ID'] = 'dummy-key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy-secret'

    copy_resources_s3.main()

    del os.environ['AWS_ACCESS_KEY_ID']
    del os.environ['AWS_SECRET_ACCESS_KEY']

    s3_stubber.assert_no_pending_responses()
    s3_stubber.deactivate()


def test_copy_resource_s3_environment(tmp_path, mocker):
    """Test copy_resource_s3 script errors without aws credentials"""

    book_dir = tmp_path / "col11762"
    book_dir.mkdir()
    resources_dir = book_dir / "resources"
    resources_dir.mkdir()

    dist_bucket = 'distribution-bucket-1234'
    dist_bucket_prefix = 'master/resources'

    s3_client = boto3.client('s3')
    s3_stubber = botocore.stub.Stubber(s3_client)
    s3_stubber.add_response(
        'list_objects',
        {},
        expected_params={
            'Bucket': dist_bucket,
            'Prefix': dist_bucket_prefix + '/',
            'Delimiter': '/'
        }
    )
    s3_stubber.activate()

    mocked_session = boto3.session.Session
    mocked_session.client = mocker.MagicMock(return_value=s3_client)

    mocker.patch(
        'boto3.session.Session',
        mocked_session
    )

    mocker.patch(
        'sys.argv',
        ['',
         resources_dir,
         dist_bucket,
         dist_bucket_prefix]
    )

    with pytest.raises(OSError):
        copy_resources_s3.main()

    s3_stubber.assert_no_pending_responses()
    s3_stubber.deactivate()


def test_s3_existence(tmp_path, mocker):
    """Test copy_resource_s3.test_s3_existence function"""

    resource_name = "fffe62254ef635871589a848b65db441318171eb.json"
    bucket = 'distribution-bucket-1234'
    key = 'master/resources/' + resource_name
    resource = os.path.join(TEST_DATA_DIR, resource_name)
    test_resource = {
        "input_metadata_file": resource,
        "output_s3": key,
    }

    aws_key = 'dummy-key'
    aws_secret = 'dummy-secret'

    s3_client = boto3.client('s3')
    s3_stubber = botocore.stub.Stubber(s3_client)
    s3_stubber.add_response(
        "head_object",
        {"ETag": '14e273e6f416c4b90a071f59ac01206a'},
        expected_params={
            "Bucket": bucket,
            "Key": key,
        },
    )
    s3_stubber.activate()

    upload_resource = copy_resources_s3.check_s3_existence(
        aws_key, aws_secret,
        bucket, test_resource,
        disable_check=False
    )

    test_input_metadata = test_resource['input_metadata_file']
    test_output_s3 = test_resource['output_s3']
    uploaded_input_metadata = upload_resource['input_metadata_file']
    uploaded_output_s3 = upload_resource['output_s3']

    assert test_input_metadata == uploaded_input_metadata
    assert test_output_s3 == uploaded_output_s3

    s3_stubber.deactivate()


def test_s3_existence_404(tmp_path, mocker):
    """Test copy_resource_s3.test_s3_existence
    function errors with wrong file name"""

    resource_name = "fffe62254ef635871589a848b65db441318171eb"
    bucket = 'distribution-bucket-1234'
    key = 'master/resources/' + resource_name

    wrong_resource = "babybeluga.json"
    test_resource = os.path.join(TEST_DATA_DIR, wrong_resource)
    resource_for_test = {
        "input_metadata_file": test_resource,
        "output_s3": key,
    }

    aws_key = 'dummy-key'
    aws_secret = 'dummy-secret'

    s3_client = boto3.client('s3')
    s3_stubber = botocore.stub.Stubber(s3_client)
    s3_stubber.activate()

    with pytest.raises(FileNotFoundError):
        copy_resources_s3.check_s3_existence(
            aws_key, aws_secret,
            bucket, resource_for_test,
            disable_check=False
        )

    s3_stubber.assert_no_pending_responses()
    s3_stubber.deactivate()


def test_upload_docx(tmp_path, mocker):
    """Test upload-docx script"""

    mock_creds = mocker.Mock(spec=google.auth.credentials.Credentials)
    parent_google_folder_id = "parentfolderID"
    book_folder = "How to be awesome"
    book_folder_id = "bookfolderID"

    # Test find_or_create_folder_by_name when folder does not exist
    request_builder = RequestMockBuilder(
        {
            "drive.files.list": (None, json.dumps({"files": []})),
            "drive.files.create": (
                None,
                json.dumps({"id": book_folder_id}),
                {
                    "name": book_folder,
                    "parents": [parent_google_folder_id],
                    "mimeType": "application/vnd.google-apps.folder"
                }
            )
        },
        check_unexpected=True
    )

    mock_drive_service = build(
        "drive", "v3", requestBuilder=request_builder, credentials=mock_creds
    )

    result = upload_docx.find_or_create_folder_by_name(
        mock_drive_service,
        parent_google_folder_id,
        book_folder
    )
    assert result == book_folder_id

    # Test find_or_create_folder_by_name when multiple folders returned
    request_builder = RequestMockBuilder(
        {
            "drive.files.list": (
                None,
                json.dumps({"files": [{"id": ""}, {"id": ""}]})
            )
        },
        check_unexpected=True
    )

    mock_drive_service = build(
        "drive", "v3", requestBuilder=request_builder, credentials=mock_creds
    )

    with pytest.raises(Exception):
        upload_docx.find_or_create_folder_by_name(
            mock_drive_service,
            parent_google_folder_id,
            book_folder
        )

    # Test find_or_create_folder_by_name when folder exists
    request_builder = RequestMockBuilder(
        {
            "drive.files.list": (
                None,
                json.dumps({"files": [{"id": book_folder_id}]})
            )
        },
        check_unexpected=True
    )

    mock_drive_service = build(
        "drive", "v3", requestBuilder=request_builder, credentials=mock_creds
    )

    result = upload_docx.find_or_create_folder_by_name(
        mock_drive_service,
        parent_google_folder_id,
        book_folder
    )

    assert result == book_folder_id

    # Test get_gdocs_in_folder
    request_builder = RequestMockBuilder(
        {
            "drive.files.list": (
                None,
                json.dumps({
                    "files": [
                        {"id": "gdoc1", "name": "gdoc1"},
                        {"id": "gdoc2", "name": "gdoc2"}
                    ]
                })
            )
        },
        check_unexpected=True
    )

    mock_drive_service = build(
        "drive", "v3", requestBuilder=request_builder, credentials=mock_creds
    )

    result = upload_docx.get_gdocs_in_folder(
        mock_drive_service,
        book_folder_id
    )

    assert result == [
        {"id": "gdoc1", "name": "gdoc1"},
        {"id": "gdoc2", "name": "gdoc2"}
    ]

    # Test upsert_docx_to_folder
    input_dir = tmp_path / "docx-book" / "col12345" / "docx"
    input_dir.mkdir(parents=True)
    input_docx = []
    for doc_name in ["chapter1", "chapter2"]:
        docx = input_dir / f"{doc_name}.docx"
        docx.write_text("Test")
        input_docx.append(docx)

    request_builder = RequestMockBuilder(
        {
            "drive.files.list": (
                None,
                json.dumps({
                    "files": [
                        {"id": "ch1exists", "name": "chapter1"}
                    ]
                })
            ),
            "drive.files.create": (
                None,
                json.dumps({"id": "ch2new"})
            ),
            "drive.files.update": (
                None,
                json.dumps({})
            )
        },
        check_unexpected=True
    )

    mock_drive_service = build(
        "drive", "v3", requestBuilder=request_builder, credentials=mock_creds
    )

    results = upload_docx.upsert_docx_to_folder(
        mock_drive_service,
        input_docx,
        book_folder_id
    )

    assert results == [
        {"id": "ch1exists", "name": "chapter1"},
        {"id": "ch2new", "name": "chapter2"},
    ]


def test_fetch_map_resources(tmp_path, mocker):
    """Test fetch-map-resources script"""
    book_dir = tmp_path / "book_slug/fetched-book-group/raw/modules"
    resources_dir = tmp_path / "book_slug/fetched-book-group-resources/resources"
    resource_rel_path_prefix = "../../../../fetched-book-group-resources/resources"

    book_dir.mkdir(parents=True)
    resources_dir.mkdir(parents=True)

    module_0001_dir = book_dir / "m00001"
    module_0001_dir.mkdir()
    module_00001 = book_dir / "m00001/index.cnxml"
    module_00001_content = """
        <document xmlns="http://cnx.rice.edu/cnxml">
            <content>
                <image src="image1.jpg"/>
                <image src="image2.jpg"/>
            </content>
        </document>
    """
    module_00001.write_text(module_00001_content)

    # Write one of the two images expected to test for case where an image file
    # is missing / mistyped
    image1 = resources_dir / "image1.jpg"
    image1.write_text("")

    mocker.patch(
        "sys.argv",
        ["", book_dir, resource_rel_path_prefix]
    )
    fetch_map_resources.main()

    assert (module_0001_dir / "image1.jpg").is_symlink()
    assert (module_0001_dir / "image2.jpg").is_symlink()
    assert (module_0001_dir / "image1.jpg").exists()
    assert not (module_0001_dir / "image2.jpg").exists()
