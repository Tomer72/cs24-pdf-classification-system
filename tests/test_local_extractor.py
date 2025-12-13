import pytest
from unittest.mock import patch, MagicMock
from app.services.pdf_processor.local_extractor import PyMuPDFExtractor

@pytest.fixture
def extractor():
    return PyMuPDFExtractor()

@patch("app.services.pdf_processor.local_extractor.fitz.open")
def test_extract_text_success(mock_fitz_open, extractor):

    mock_page = MagicMock()
    mock_page.get_text.return_value = "Hello World"

    mock_doc = MagicMock()
    mock_doc.page_count = 1
    mock_doc.__getitem__.return_value = mock_page

    mock_fitz_open.return_value.__enter__.return_value = mock_doc

    result = extractor.extract(b"fake_pdf_content")

    assert result == "Hello World"
    mock_doc.__getitem__.assert_called_with(0)


@patch("app.services.pdf_processor.local_extractor.fitz.open")
def test_extract_scanned_pdf_returns_empty(mock_fitz_open, extractor):

    mock_page = MagicMock()
    mock_page.get_text.return_value = "" 

    mock_doc = MagicMock()
    mock_doc.page_count = 1
    mock_doc.__getitem__.return_value = mock_page

    mock_fitz_open.return_value.__enter__.return_value = mock_doc

    result = extractor.extract(b"scanned_pdf_bytes")

    assert result == ""


@patch("app.services.pdf_processor.local_extractor.fitz.open")
def test_extract_no_pages(mock_fitz_open, extractor):

    mock_doc = MagicMock()
    mock_doc.page_count = 0

    mock_fitz_open.return_value.__enter__.return_value = mock_doc

    result = extractor.extract(b"empty_pdf_bytes")

    assert result == ""


@patch("app.services.pdf_processor.local_extractor.fitz.open")
def test_extract_corrupted_file_handles_exception(mock_fitz_open, extractor):

    mock_fitz_open.side_effect = Exception("File is corrupted or invalid")

    result = extractor.extract(b"bad_data")

    assert result == ""

