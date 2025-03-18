import pytest
from fetchFQfromENA.get_fq_file import process_metadata

@pytest.fixture
def mock_metadata_file(tmp_path):
    meta_content = (
        "fastq_ftp\tfastq_aspera\n"
        "link1;link2\taspera1;aspera2\n"
        "singlelink\tsingleaspera\n"
        "\t\n"  # Empty line
    )
    meta_file = tmp_path / ".PRJTEST.meta.txt"
    meta_file.write_text(meta_content)
    return meta_file

def test_ftp_link_splitting(mock_metadata_file):
    links = process_metadata("PRJTEST", "ftp")
    assert links == ["link1", "link2", "singlelink"]

def test_aspera_link_splitting(mock_metadata_file):
    links = process_metadata("PRJTEST", "aspera")
    assert links == ["aspera1", "aspera2", "singleaspera"]

def test_empty_links_are_filtered(mock_metadata_file):
    links = process_metadata("PRJTEST", "ftp")
    assert "" not in links