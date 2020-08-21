"""Tests to validate JSON metadata extraction and file generation pipeline"""
import os
import json
from glob import glob
from lxml import etree
import boto3
import botocore.stub
import requests_mock
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
    upload_docx,
    checksum_resource
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
        ["", book_dir]
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

    mocker.patch("sys.argv", ["", input_dir, mock_uuid, mock_version])
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

    mocker.patch("sys.argv", ["", input_dir, mock_uuid, mock_version])
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


def mock_link_extras(tmp_path, content_dict, extras_dict, page_content):
    input_dir = tmp_path / "linked-extras"
    input_dir.mkdir()

    server = "mock.archive"

    canonical_list = f"{SCRIPT_DIR}/canonical-book-list.json"

    adapter = requests_mock.Adapter()

    content_matcher = re.compile(f"https://{server}/content/")

    def content_callback(request, context):
        module_uuid = content_dict[request.url.split("/")[-1]]
        request.url = f"https://{server}/content/{module_uuid}"
        return

    adapter.register_uri("GET", content_matcher, json=content_callback)

    extras_matcher = re.compile(f"https://{server}/extras/")

    def extras_callback(request, context):
        return extras_dict[request.url.split("/")[-1]]

    adapter.register_uri("GET", extras_matcher, json=extras_callback)

    collection_name = "collection.assembled.xhtml"
    collection_input = input_dir / collection_name
    collection_input.write_text(page_content)

    link_extras.transform_links(input_dir, server, canonical_list, adapter)


def test_link_extras_single_match(tmp_path, mocker):
    """Test for link_extras script case with single
    containing book and a canonical match"""

    content_dict = {"m1234": "1234-5678-1234-5678"}

    extras_dict = {
        "1234-5678-1234-5678": {
            "books": [{"ident_hash": "00000000-0000-0000-0000-000000000000"}]
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
            href="/contents/m1234"
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
            ("data-book-uuid", "00000000-0000-0000-0000-000000000000"),
        ],
    ]

    mock_link_extras(tmp_path, content_dict, extras_dict, page_content)

    output_dir = tmp_path / "linked-extras"

    collection_output = output_dir / "collection.linked.xhtml"
    tree = etree.parse(str(collection_output))

    parsed_links = tree.xpath(
        '//x:a[@href and starts-with(@href, "/contents/")]',
        namespaces={"x": "http://www.w3.org/1999/xhtml"},
    )

    for pair in zip(expected_links, parsed_links):
        assert pair[0] == pair[1].items()


def test_link_extras_single_no_match(tmp_path, mocker):
    """Test for link_extras script case with single
    containing book and no canonical match"""

    content_dict = {"m1234": "1234-5678-1234-5678"}

    extras_dict = {
        "1234-5678-1234-5678": {
            "books": [{"ident_hash": "02776133-d49d-49cb-bfaa-67c7f61b25a1"}]
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
            href="/contents/m1234"
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
            ("data-book-uuid", "02776133-d49d-49cb-bfaa-67c7f61b25a1"),
        ],
    ]

    mock_link_extras(tmp_path, content_dict, extras_dict, page_content)

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

    content_dict = {"m1234": "1234-5678-1234-5678"}

    extras_dict = {
        "1234-5678-1234-5678": {
            "books": [
                {"ident_hash": "00000000-0000-0000-0000-000000000000"},
                {"ident_hash": "02776133-d49d-49cb-bfaa-67c7f61b25a1"},
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
            href="/contents/m1234"
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
            ("data-book-uuid", "02776133-d49d-49cb-bfaa-67c7f61b25a1"),
        ],
    ]

    mock_link_extras(tmp_path, content_dict, extras_dict, page_content)

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

    content_dict = {"m1234": "1234-5678-1234-5678"}

    extras_dict = {
        "1234-5678-1234-5678": {
            "books": [
                {"ident_hash": "00000000-0000-0000-0000-000000000000"},
                {"ident_hash": "11111111-1111-1111-1111-111111111111"},
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
            href="/contents/m1234"
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

    with pytest.raises(Exception):
        mock_link_extras(tmp_path, content_dict, extras_dict, page_content)


def test_assemble_book_metadata(tmp_path, mocker):
    """Test assemble_book_metadata script"""
    input_assembled_book = os.path.join(TEST_DATA_DIR, "assembled-book")

    assembled_metadata_output = tmp_path / "collection.assembed-metadata.json"

    mocker.patch(
        "sys.argv", ["", input_assembled_book, assembled_metadata_output]
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

    with open(input_baked_xhtml, "r") as baked_xhtml:
        binder = reconstitute(baked_xhtml)
        book_ident_hash = binder.ident_hash

    mocker.patch(
        "sys.argv",
        [
            "",
            input_raw_metadata,
            input_baked_xhtml,
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

    # Populate a dummy TOC to confirm it is ignored
    toc_input = input_dir / "collection.toc.xhtml"
    toc_input.write_text("DUMMY")
    page_name = "bookuuid1@version:pageuuid1.xhtml"
    page_input = input_dir / page_name
    page_input.write_text(page_content)

    mocker.patch("sys.argv", ["", input_dir, output_dir])
    gdocify_book.main()

    page_output = output_dir / page_name
    assert page_output.exists()

    expected_links_by_id = {
        "l1": "http://openstax.org",
        "l2": "http://openstax.org",
        "l3": "#foobar",
        "l4": "http://www.openstax.org/l/shorturl",
    }

    updated_doc = etree.parse(str(page_output))

    for node in updated_doc.xpath(
        "//x:a[@href]", namespaces={"x": "http://www.w3.org/1999/xhtml"},
    ):
        assert expected_links_by_id[node.attrib["id"]] == node.attrib["href"]


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
