"""Tests to validate JSON metadata extraction and file generation pipeline"""
import os
import json
from glob import glob
from lxml import etree
import boto3
import botocore.stub

from cnxepub.html_parsers import HTML_DOCUMENT_NAMESPACES
from cnxepub.collation import reconstitute
from bakery_scripts import jsonify_book, disassemble_book, \
    assemble_book_metadata, bake_book_metadata, check_feed

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(HERE, "data")
SCRIPT_DIR = os.path.join(HERE, "../scripts")


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
        'sys.argv',
        ['', disassembled_input_dir, tmp_path / "jsonified"]
    )
    jsonify_book.main()

    jsonified_output = jsonified_output_dir / f"{mock_ident_hash}:m00001.json"
    jsonified_output_data = json.loads(jsonified_output.read_text())
    jsonified_toc_output = jsonified_output_dir / "collection.toc.json"
    jsonified_toc_data = json.loads(jsonified_toc_output.read_text())

    assert jsonified_output_data.get("title") == json_metadata_content["title"]
    assert jsonified_output_data.get("abstract") == \
        json_metadata_content["abstract"]
    assert jsonified_output_data.get("slug") == json_metadata_content["slug"]
    assert jsonified_output_data.get("content") == html_content
    assert jsonified_toc_data.get("content") == toc_content


def test_disassemble_book(tmp_path, mocker):
    """Test disassemble_book script"""
    input_baked_xhtml = os.path.join(TEST_DATA_DIR, "collection.baked.xhtml")
    input_baked_metadata = os.path.join(
        TEST_DATA_DIR, "collection.baked-metadata.json")

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

    mocker.patch(
        'sys.argv',
        ['', input_dir, mock_uuid, mock_version]
    )
    disassemble_book.main()

    xhtml_output_files = glob(f"{disassembled_output}/*.xhtml")
    assert len(xhtml_output_files) == 3
    json_output_files = glob(f"{disassembled_output}/*-metadata.json")
    assert len(json_output_files) == 3

    # Check for expected files and metadata that should be generated in
    # this step
    json_output_m42119 = \
        disassembled_output / f"{mock_ident_hash}:m42119-metadata.json"
    json_output_m42092 = \
        disassembled_output / f"{mock_ident_hash}:m42092-metadata.json"
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
        "//xhtml:nav",
        namespaces=HTML_DOCUMENT_NAMESPACES
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

    mocker.patch(
        'sys.argv',
        ['', input_dir, mock_uuid, mock_version]
    )
    disassemble_book.main()

    # Check for expected files and metadata that should be generated in this
    # step
    json_output_m42119 = \
        disassembled_output / f"{mock_ident_hash}:m42119-metadata.json"
    json_output_m42092 = \
        disassembled_output / f"{mock_ident_hash}:m42092-metadata.json"
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


def test_assemble_book_metadata(tmp_path, mocker):
    """Test assemble_book_metadata script"""
    input_assembled_book = os.path.join(TEST_DATA_DIR, "assembled-book")

    assembled_metadata_output = tmp_path / "collection.assembed-metadata.json"

    mocker.patch(
        'sys.argv',
        ['', input_assembled_book, assembled_metadata_output]
    )
    assemble_book_metadata.main()

    assembled_metadata = json.loads(assembled_metadata_output.read_text())
    assert assembled_metadata["m42119@1.6"]["abstract"] is None
    assert (
        "Explain the difference between a model and a theory"
        in assembled_metadata["m42092@1.10"]["abstract"]
    )
    assert (
        assembled_metadata["m42092@1.10"]["revised"] ==
        "2018/09/18 09:55:13.413 GMT-5"
    )
    assert (
        assembled_metadata["m42119@1.6"]["revised"] ==
        "2018/08/03 15:49:52 -0500"
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
        'sys.argv',
        [
            '',
            input_raw_metadata,
            input_baked_xhtml,
            output_baked_book_metadata,
        ]
    )
    bake_book_metadata.main()

    baked_metadata = json.loads(output_baked_book_metadata.read_text())

    assert isinstance(baked_metadata[book_ident_hash]["tree"], dict) is True
    assert "contents" in baked_metadata[book_ident_hash]["tree"].keys()
    assert "license" in baked_metadata[book_ident_hash].keys()
    assert (
        baked_metadata[book_ident_hash]["revised"] ==
        "2019-08-30T16:35:37.569966-05:00"
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
            "uuid": "02040312-72c8-441e-a685-20e9333f3e1d"
        },
        {
            "name": "College Physics",
            "collection_id": "col11406",
            "style": "college-physics",
            "version": "1.20.15",
            "server": "cnx.foobar.org",
            "uuid": "031da8d3-b525-429c-80cf-6c8ed997733a"
        }
    ]

    json_feed_input = (
        tmp_path / "book-feed.json"
    )
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

    queue_state_bucket = 'queue-state-bucket'
    queue_filename = 'queue-state-filename.json'
    code_version = 'code-version'
    book1 = input_book_feed[0]
    book1_col = book1['collection_id']
    book1_vers = book1['version']
    book2 = input_book_feed[1]
    book2_col = book2['collection_id']
    book2_vers = book2['version']

    s3_client = boto3.client('s3')
    s3_stubber = botocore.stub.Stubber(s3_client)

    def _stubber_add_head_object_404(expected_key):
        s3_stubber.add_client_error(
            'head_object',
            service_error_meta={
                'Code': '404'
            },
            expected_params={
                'Bucket': queue_state_bucket,
                'Key': expected_key
            }
        )

    def _stubber_add_head_object(expected_key):
        s3_stubber.add_response(
            'head_object',
            {},
            expected_params={
                'Bucket': queue_state_bucket,
                'Key': expected_key
            }
        )

    def _stubber_add_put_object(expected_key, expected_body):
        s3_stubber.add_response(
            'put_object',
            {},
            expected_params={
                'Bucket': queue_state_bucket,
                'Key': expected_key,
                'Body': expected_body
            }
        )

    # Book 1: Check for .complete file
    _stubber_add_head_object_404(
        f"{code_version}/.{book1_col}@{book1_vers}.complete"
    )

    # Book 1: Check for .pending file
    _stubber_add_head_object_404(
        f"{code_version}/.{book1_col}@{book1_vers}.pending"
    )

    # Book 1: Put book data
    _stubber_add_put_object(queue_filename, json.dumps(book1))

    # Book 1: Put book .pending
    _stubber_add_put_object(
        f"{code_version}/.{book1_col}@{book1_vers}.pending",
        botocore.stub.ANY
    )

    # Book 1: Check for .complete file
    _stubber_add_head_object_404(
        f"{code_version}/.{book1_col}@{book1_vers}.complete"
    )

    # Book 1: Check for .pending file (return as though it exists)
    _stubber_add_head_object(
        f"{code_version}/.{book1_col}@{book1_vers}.pending"
    )

    # Book 1: Check for .retry file
    _stubber_add_head_object_404(
        f"{code_version}/.{book1_col}@{book1_vers}.retry"
    )

    # Book 1: Put book data again
    _stubber_add_put_object(queue_filename, json.dumps(book1))

    # Book 1: Put book .retry
    _stubber_add_put_object(
        f"{code_version}/.{book1_col}@{book1_vers}.retry",
        botocore.stub.ANY
    )

    # Book 1: Check for .complete file
    _stubber_add_head_object(
        f"{code_version}/.{book1_col}@{book1_vers}.complete"
    )

    # Book 2: Check for .complete file
    _stubber_add_head_object_404(
        f"{code_version}/.{book2_col}@{book2_vers}.complete"
    )

    # Book 2: Check for .pending file
    _stubber_add_head_object_404(
        f"{code_version}/.{book2_col}@{book2_vers}.pending"
    )

    # Book 2: Put book data
    _stubber_add_put_object(queue_filename, json.dumps(book2))

    # Book 2: Put book .pending
    _stubber_add_put_object(
        f"{code_version}/.{book2_col}@{book2_vers}.pending",
        botocore.stub.ANY
    )

    s3_stubber.activate()

    mocker.patch(
        'boto3.client',
        lambda service: s3_client
    )
    mocker.patch(
        'sys.argv',
        [
            '',
            json_feed_input,
            code_version,
            queue_state_bucket,
            queue_filename,
            1
        ]
    )

    for _ in range(3):
        check_feed.main()

    s3_stubber.assert_no_pending_responses()
