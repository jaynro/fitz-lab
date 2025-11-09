"""
Unit tests for PDF extraction functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
from pathlib import Path

from extractors.pdf_extractor import PDFExtractor
from models.pdf_models import PDFDocument, PDFPage, DocumentData
from tests.conftest import SAMPLE_PDF_PATH, EXPECTED_CATEGORIES


class TestPDFExtractor(unittest.TestCase):
    """Test cases for PDFExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_pdf_path = str(SAMPLE_PDF_PATH)
        
    def test_read_pdf_metadata_success(self):
        """Test successful PDF metadata extraction"""
        if SAMPLE_PDF_PATH.exists():
            metadata = PDFExtractor.read_pdf_metadata(self.sample_pdf_path)
            
            # Verify return type
            self.assertIsInstance(metadata, PDFDocument)
            
            # Verify required fields
            self.assertEqual(metadata.filename, "table.pdf")
            self.assertGreater(metadata.page_count, 0)
            
            # Verify optional fields (from our known test file)
            self.assertEqual(metadata.author, "Mary")
            self.assertIn("Acrobat", metadata.creator or "")
        else:
            self.skipTest("Sample PDF file not found")
    
    @patch('fitz.open')
    def test_read_pdf_metadata_mock(self, mock_fitz_open):
        """Test PDF metadata extraction with mocked fitz"""
        # Create mock PDF document
        mock_doc = Mock()
        mock_doc.metadata = {
            'title': 'Test Document',
            'author': 'Test Author',
            'subject': 'Test Subject',
            'creator': 'Test Creator'
        }
        mock_doc.__len__ = Mock(return_value=2)  # 2 pages
        mock_fitz_open.return_value = mock_doc
        
        # Test the function
        result = PDFExtractor.read_pdf_metadata("test.pdf")
        
        # Assertions
        self.assertIsInstance(result, PDFDocument)
        self.assertEqual(result.filename, "test.pdf")
        self.assertEqual(result.page_count, 2)
        self.assertEqual(result.title, "Test Document")
        self.assertEqual(result.author, "Test Author")
        
        # Verify fitz operations
        mock_fitz_open.assert_called_once_with("test.pdf")
        mock_doc.close.assert_called_once()
    
    def test_extract_text_from_pdf_success(self):
        """Test successful text extraction from PDF"""
        if SAMPLE_PDF_PATH.exists():
            pages = PDFExtractor.extract_text_from_pdf(self.sample_pdf_path)
            
            # Verify return type and structure
            self.assertIsInstance(pages, list)
            self.assertGreater(len(pages), 0)
            
            # Check first page
            first_page = pages[0]
            self.assertIsInstance(first_page, PDFPage)
            self.assertEqual(first_page.page_number, 1)
            self.assertIsInstance(first_page.text_content, str)
            self.assertGreater(len(first_page.text_content), 0)
            
            # Verify our expected content is present
            text_content = first_page.text_content.lower()
            for category in EXPECTED_CATEGORIES:
                self.assertIn(category.lower(), text_content)
        else:
            self.skipTest("Sample PDF file not found")
    
    @patch('fitz.open')
    def test_extract_text_from_pdf_mock(self, mock_fitz_open):
        """Test text extraction with mocked fitz"""
        # Create mock PDF with pages
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "Sample text content"
        mock_page.get_images.return_value = []
        mock_page.get_links.return_value = [{"uri": "test"}]  # 1 link
        
        mock_doc.__len__ = Mock(return_value=1)
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz_open.return_value = mock_doc
        
        # Test the function
        result = PDFExtractor.extract_text_from_pdf("test.pdf")
        
        # Assertions
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        
        page = result[0]
        self.assertIsInstance(page, PDFPage)
        self.assertEqual(page.page_number, 1)
        self.assertEqual(page.text_content, "Sample text content")
        self.assertEqual(page.image_count, 0)
        self.assertEqual(page.link_count, 1)
    
    def test_extract_complete_document_data(self):
        """Test complete document data extraction"""
        if SAMPLE_PDF_PATH.exists():
            doc_data = PDFExtractor.extract_complete_document_data(self.sample_pdf_path)
            
            # Verify return type
            self.assertIsInstance(doc_data, DocumentData)
            
            # Verify structure
            self.assertIsInstance(doc_data.metadata, PDFDocument)
            self.assertIsInstance(doc_data.pages, list)
            self.assertGreater(len(doc_data.pages), 0)
            
            # Verify text aggregation
            self.assertIsInstance(doc_data.full_text, str)
            self.assertGreater(len(doc_data.full_text), 0)
            
            # Verify content contains expected categories
            full_text_lower = doc_data.full_text.lower()
            for category in EXPECTED_CATEGORIES:
                self.assertIn(category.lower(), full_text_lower)
        else:
            self.skipTest("Sample PDF file not found")
    
    def test_extract_complete_document_data_file_not_found(self):
        """Test handling of non-existent PDF file"""
        with self.assertRaises(Exception):
            PDFExtractor.extract_complete_document_data("nonexistent.pdf")


if __name__ == '__main__':
    unittest.main()