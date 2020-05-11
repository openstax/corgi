"""Tests to validate JSON metadata extraction and file generation pipeline"""
import subprocess
import os
import json
from glob import glob
from lxml import etree

from cnxepub.html_parsers import HTML_DOCUMENT_NAMESPACES

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(HERE, "data")
SCRIPT_DIR = os.path.join(HERE, "../scripts")

def test_jsonify_book(tmp_path):
    """Test basic input / output for jsonify-book script"""
    jsonify_book_script = os.path.join(SCRIPT_DIR, "jsonify-book.py")

    html_content = "<html><body>test body</body></html>"
    toc_content = "<nav>TOC</nav>"
    json_metadata_content = {
        "title": "subsection title",
        "abstract": "subsection abstract",
        "slug": "1-3-subsection-slug"
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
    json_metadata_input = disassembled_input_dir / f"{mock_ident_hash}:m00001-metadata.json"
    json_metadata_input.write_text(json.dumps(json_metadata_content))

    jsonified_output_dir = tmp_path / "jsonified"
    jsonified_output_dir.mkdir()

    subprocess.run(
        [
            "python",
            jsonify_book_script,
            disassembled_input_dir,
            tmp_path / "jsonified"
        ],
        cwd=HERE,
        check=True
    )

    jsonified_output = jsonified_output_dir / f"{mock_ident_hash}:m00001.json"
    jsonified_output_data = json.loads(jsonified_output.read_text())
    jsonified_toc_output = jsonified_output_dir / "collection.toc.json"
    jsonified_toc_data = json.loads(jsonified_toc_output.read_text())

    assert jsonified_output_data.get("title") == json_metadata_content["title"]
    assert jsonified_output_data.get("abstract") == json_metadata_content["abstract"]
    assert jsonified_output_data.get("slug") == json_metadata_content["slug"]
    assert jsonified_output_data.get("content") == html_content
    assert jsonified_toc_data.get("content") == toc_content

def test_disassemble_book(tmp_path):
    """Test basic input / output for disassemble-book script"""
    disassemble_book_script = os.path.join(SCRIPT_DIR, "disassemble-book.py")
    input_baked_xhtml = os.path.join(TEST_DATA_DIR, "collection.baked.xhtml")
    input_baked_metadata = os.path.join(TEST_DATA_DIR, "collection.baked-metadata.json")

    input_dir = tmp_path / "book"
    input_dir.mkdir()

    input_baked_xhtml_file = input_dir / "collection.baked.xhtml"
    input_baked_xhtml_file.write_bytes(open(input_baked_xhtml, "rb").read())
    input_baked_metadata_file = input_dir / "collection.baked-metadata.json"
    input_baked_metadata_file.write_text(open(input_baked_metadata, "r").read())

    disassembled_output = input_dir / "disassembled"
    disassembled_output.mkdir()

    mock_uuid = "00000000-0000-0000-0000-000000000000"
    mock_version = "0.0"
    mock_ident_hash = f"{mock_uuid}@{mock_version}"

    subprocess.run(
        [
            "python",
            disassemble_book_script,
            input_dir,
            mock_uuid,
            mock_version
        ],
        cwd=HERE,
        check=True
    )

    xhtml_output_files = glob(f"{disassembled_output}/*.xhtml")
    assert len(xhtml_output_files) == 3
    json_output_files = glob(f"{disassembled_output}/*-metadata.json")
    assert len(json_output_files) == 3

    # Check for expected files and metadata that should be generated in this step
    json_output_m42119 = disassembled_output / f"{mock_ident_hash}:m42119-metadata.json"
    json_output_m42092 = disassembled_output / f"{mock_ident_hash}:m42092-metadata.json"
    m42119_data = json.load(open(json_output_m42119, "r"))
    m42092_data = json.load(open(json_output_m42092, "r"))
    assert m42119_data.get("title") == \
        "Introduction to Science and the Realm of Physics, Physical Quantities, and Units"
    assert m42119_data.get("slug") == \
        "1-introduction-to-science-and-the-realm-of-physics-physical-quantities-and-units"
    assert m42119_data["abstract"] is None
    assert m42092_data.get("title") == "Physics: An Introduction"
    assert m42092_data.get("slug") == "1-1-physics-an-introduction"
    assert m42092_data.get("abstract") == "Explain the difference between a model and a theory"

    toc_output = disassembled_output / "collection.toc.xhtml"
    assert toc_output.exists()
    toc_output_tree = etree.parse(open(toc_output))
    nav = toc_output_tree.xpath("//xhtml:nav", namespaces=HTML_DOCUMENT_NAMESPACES)
    assert len(nav) == 1

def test_disassemble_book_empty_baked_metadata(tmp_path):
    """Test case for disassemble where there may not be associated metadata
    from previous steps in collection.baked-metadata.json
    """
    disassemble_book_script = os.path.join(SCRIPT_DIR, "disassemble-book.py")
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

    subprocess.run(
        [
            "python",
            disassemble_book_script,
            input_dir,
            mock_uuid,
            mock_version
        ],
        cwd=HERE,
        check=True
    )

    # Check for expected files and metadata that should be generated in this step
    json_output_m42119 = disassembled_output / f"{mock_ident_hash}:m42119-metadata.json"
    json_output_m42092 = disassembled_output / f"{mock_ident_hash}:m42092-metadata.json"
    m42119_data = json.load(open(json_output_m42119, "r"))
    m42092_data = json.load(open(json_output_m42092, "r"))
    assert m42119_data["abstract"] is None
    assert m42092_data["abstract"] is None

def test_assemble_book(tmp_path):
    """Test basic input / output for assemble-book script"""
    assemble_book_script = os.path.join(SCRIPT_DIR, "assemble-book-metadata.py")
    input_assembled_xhtml = os.path.join(TEST_DATA_DIR, "collection.assembled.xhtml")

    assembled_metadata_output = tmp_path / "collection.assembed-metadata.json"

    subprocess.run(
        [
            "python",
            assemble_book_script,
            input_assembled_xhtml,
            assembled_metadata_output
        ],
        cwd=HERE,
        check=True
    )

    assembled_metadata = json.loads(assembled_metadata_output.read_text())
    assert assembled_metadata["m42119@1.6"]["abstract"] is None
    assert "Explain the difference between a model and a theory" in \
        assembled_metadata["m42092@1.10"]["abstract"]

def test_bake_book(tmp_path):
    """Test basic input / output for bake-book script"""
    bake_book_script = os.path.join(SCRIPT_DIR, "bake-book-metadata.py")
    input_raw_metadata = os.path.join(TEST_DATA_DIR, "collection.assembled-metadata.json")
    input_baked_xhtml = os.path.join(TEST_DATA_DIR, "collection.baked.xhtml")
    output_baked_book_metadata = tmp_path / "collection.toc-metadata.json"
    input_baked_collection_id = os.path.join(TEST_DATA_DIR, "collection_id")
    collection_id = open(input_baked_collection_id, "r").read().strip()

    subprocess.run(
        [
            "python",
            bake_book_script,
            input_raw_metadata,
            input_baked_xhtml,
            output_baked_book_metadata,
            collection_id
        ],
        cwd=HERE,
        check=True
    )

    baked_metadata = json.loads(output_baked_book_metadata.read_text())

    assert isinstance(baked_metadata[collection_id]["tree"], dict) is True
    assert 'contents' in baked_metadata[collection_id]["tree"].keys()
    assert baked_metadata[collection_id]["legacy_id"] == 'col11406'
    assert "College Physics" in \
        baked_metadata[collection_id]["title"]