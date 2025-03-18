import pytest
from pathlib import Path
from fetchFQfromENA.get_fq_meta import fetch_tsv
import requests_mock


def test_fetch_tsv_success(requests_mock):
    accession = "PRJNA661210"
    mock_response = "run_accession\tfastq_ftp\tfastq_md5\nSRR123\tftp://example.com\t12345"
    requests_mock.get(requests_mock.ANY, text=mock_response)
    
    result = fetch_tsv(accession)
    assert result is not None
    assert result.name == f"{accession}_metadata.tsv"
    assert Path(result).exists()


def test_fetch_tsv_invalid_accession(requests_mock):
    requests_mock.get(requests_mock.ANY, status_code=404)
    result = fetch_tsv("INVALID")
    assert result is None


def test_fetch_tsv_retries(requests_mock):
    accession = "PRJNA661210"
    requests_mock.get(requests_mock.ANY, exc=requests.exceptions.ConnectionError)
    
    result = fetch_tsv(accession, max_retries=3)
    assert result is None
    assert requests_mock.call_count == 3