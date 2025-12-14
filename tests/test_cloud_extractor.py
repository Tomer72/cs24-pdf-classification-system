import pytest
from unittest.mock import patch, MagicMock
from app.services.pdf_processor.cloud_extractor import GoogleVisionExtractor

@pytest.fixture
def extractor():
    with patch("app.services.pdf_processor.cloud_extractor.vision"):
        return GoogleVisionExtractor()
    
def test_client_lazy_loading():
    with patch("app.services.pdf_processor.cloud_extractor.vision") as mock_vision:
        ext = GoogleVisionExtractor()
        
        assert ext._client is None  
        
        client1 = ext.client
        assert client1 is not None
        mock_vision.ImageAnnotatorClient.assert_called_once() 

        client2 = ext.client
        assert client1 is client2
        
        mock_vision.ImageAnnotatorClient.assert_called_once()

    
        