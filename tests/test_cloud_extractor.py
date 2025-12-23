import pytest
from unittest.mock import patch, MagicMock
from app.services.pdf_processor.cloud_extractor import GoogleVisionExtractor

@pytest.fixture
def mock_vision():
    
    with patch("app.services.pdf_processor.cloud_extractor.vision") as mock:
        yield mock

@pytest.fixture
def mock_pdf_structure():
    with patch("app.services.pdf_processor.cloud_extractor.fitz.open") as mock_open:
          
          mock_doc = MagicMock()
          mock_page = MagicMock()
          
          mock_open.return_value.__enter__.return_value = mock_doc
          mock_doc.__getitem__.return_value = mock_page

          mock_doc.page_count = 1
          mock_page.get_pixmap.return_value.tobytes.return_value = b"fake_image_bytes"

          yield mock_doc

@pytest.fixture
def extractor(mock_vision): 
    return GoogleVisionExtractor()
    
def test_client_lazy_loading(extractor, mock_vision):
    
    assert extractor._client is None  
        
    client1 = extractor.client
    assert client1 is not None
    mock_vision.ImageAnnotatorClient.assert_called_once() 

    client2 = extractor.client
    assert client1 is client2
        
    mock_vision.ImageAnnotatorClient.assert_called_once()

def test_extract_success(extractor, mock_vision, mock_pdf_structure):

     mock_client = mock_vision.ImageAnnotatorClient.return_value
     mock_response = MagicMock()
     mock_response.error.message = None
     mock_annotation = MagicMock()
     mock_annotation.description = "Extracted Text Success"
     mock_response.text_annotations = [mock_annotation]
     mock_client.text_detection.return_value = mock_response

     result = extractor.extract(b"pdf_bytes")

     assert result == "Extracted Text Success"

def test_extract_pdf_has_no_pages(extractor, mock_vision, mock_pdf_structure):

    mock_pdf_structure.page_count = 0
    result = extractor.extract(b"empty_pdf_bytes")

    assert result == ""

    mock_vision.ImageAnnotatorClient.return_value.text_detection.assert_not_called()

