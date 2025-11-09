"""
Unit tests for document processing functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from processors.document_processor import DocumentProcessor
from models.pdf_models import DocumentData, PDFDocument, PDFPage, TableRow
from tests.conftest import SAMPLE_PDF_PATH, EXPECTED_CATEGORIES, EXPECTED_COLUMNS


class TestDocumentProcessor(unittest.TestCase):
    """Test cases for DocumentProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DocumentProcessor("input")
        
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.temp_processor = DocumentProcessor(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test DocumentProcessor initialization"""
        processor = DocumentProcessor("test_folder")
        
        self.assertEqual(processor.input_folder, "test_folder")
        self.assertEqual(str(processor.input_path), "test_folder")
    
    def test_validate_input_folder_exists(self):
        """Test validation of existing input folder"""
        # Test with actual input folder (should exist)
        if Path("input").exists():
            result = self.processor.validate_input_folder()
            self.assertTrue(result)
        else:
            self.skipTest("Input folder doesn't exist")
    
    def test_validate_input_folder_not_exists(self):
        """Test validation of non-existent folder"""
        processor = DocumentProcessor("nonexistent_folder")
        result = processor.validate_input_folder()
        self.assertFalse(result)
    
    def test_validate_input_folder_no_pdfs(self):
        """Test validation of folder with no PDF files"""
        # Use temporary directory (empty)
        result = self.temp_processor.validate_input_folder()
        self.assertFalse(result)
    
    def test_get_pdf_files(self):
        """Test getting PDF files from folder"""
        if Path("input").exists():
            pdf_files = self.processor.get_pdf_files()
            
            self.assertIsInstance(pdf_files, list)
            # Should have at least the sample PDF
            self.assertGreater(len(pdf_files), 0)
            
            # All items should be Path objects ending in .pdf
            for pdf_file in pdf_files:
                self.assertIsInstance(pdf_file, Path)
                self.assertTrue(pdf_file.name.endswith('.pdf'))
        else:
            self.skipTest("Input folder doesn't exist")
    
    @patch('processors.document_processor.PDFExtractor')
    @patch('processors.document_processor.TableExtractor')
    def test_process_single_pdf_success(self, mock_table_extractor, mock_pdf_extractor):
        """Test successful processing of single PDF"""
        # Mock PDF extraction
        mock_metadata = PDFDocument(
            filename="test.pdf",
            page_count=1,
            author="Test Author",
            creator="Test Creator"
        )
        mock_page = PDFPage(
            page_number=1,
            text_content="Test content",
            filtered_content="Test content",
            image_count=0,
            link_count=0
        )
        mock_doc_data = DocumentData(
            metadata=mock_metadata,
            pages=[mock_page],
            full_text="Test content",
            filtered_text="Test content"
        )
        
        mock_pdf_extractor.extract_complete_document_data.return_value = mock_doc_data
        
        # Mock table extraction
        mock_table_rows = [
            TableRow(
                disability_category="Blind",
                participants="5",
                ballots_completed="1",
                completion_percentage="34.5%"
            )
        ]
        mock_table_extractor.extract_table_data.return_value = mock_table_rows
        mock_table_extractor.get_target_columns.return_value = EXPECTED_COLUMNS
        
        # Test processing
        result = self.processor.process_single_pdf(Path("test.pdf"))
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertEqual(result["filename"], "test.pdf")
        self.assertIn("metadata", result)
        self.assertIn("table_data", result)
        self.assertIn("summary", result)
        
        # Verify table data structure
        table_data = result["table_data"]
        self.assertEqual(table_data["columns"], EXPECTED_COLUMNS)
        self.assertEqual(len(table_data["rows"]), 1)
        
        # Verify summary
        summary = result["summary"]
        self.assertEqual(summary["total_categories"], 1)
        self.assertEqual(len(summary["categories_found"]), 1)
    
    @patch('processors.document_processor.PDFExtractor')
    def test_process_single_pdf_exception(self, mock_pdf_extractor):
        """Test handling of exceptions during PDF processing"""
        # Mock an exception
        mock_pdf_extractor.extract_complete_document_data.side_effect = Exception("Test error")
        
        # Test processing
        result = self.processor.process_single_pdf(Path("test.pdf"))
        
        # Should return None on exception
        self.assertIsNone(result)
    
    @patch.object(DocumentProcessor, 'validate_input_folder')
    @patch.object(DocumentProcessor, 'get_pdf_files')
    @patch.object(DocumentProcessor, 'process_single_pdf')
    def test_process_all_pdfs_success(self, mock_process_single, mock_get_files, mock_validate):
        """Test processing all PDFs successfully"""
        # Mock validation and file discovery
        mock_validate.return_value = True
        mock_get_files.return_value = [Path("test1.pdf"), Path("test2.pdf")]
        
        # Mock processing results
        mock_doc1 = {"filename": "test1.pdf", "data": "test1"}
        mock_doc2 = {"filename": "test2.pdf", "data": "test2"}
        mock_process_single.side_effect = [mock_doc1, mock_doc2]
        
        # Test processing
        result = self.processor.process_all_pdfs()
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertEqual(result["processed_documents"], 2)
        self.assertEqual(len(result["documents"]), 2)
        self.assertEqual(result["documents"][0], mock_doc1)
        self.assertEqual(result["documents"][1], mock_doc2)
    
    @patch.object(DocumentProcessor, 'validate_input_folder')
    def test_process_all_pdfs_validation_fails(self, mock_validate):
        """Test processing when validation fails"""
        mock_validate.return_value = False
        
        result = self.processor.process_all_pdfs()
        
        # Should return empty result
        self.assertEqual(result["processed_documents"], 0)
        self.assertEqual(result["documents"], [])
    
    @patch.object(DocumentProcessor, 'validate_input_folder')
    @patch.object(DocumentProcessor, 'get_pdf_files')
    @patch.object(DocumentProcessor, 'process_single_pdf')
    def test_process_all_pdfs_with_failures(self, mock_process_single, mock_get_files, mock_validate):
        """Test processing with some PDF failures"""
        # Mock validation and file discovery
        mock_validate.return_value = True
        mock_get_files.return_value = [Path("test1.pdf"), Path("test2.pdf"), Path("test3.pdf")]
        
        # Mock processing results (one failure)
        mock_doc1 = {"filename": "test1.pdf", "data": "test1"}
        mock_process_single.side_effect = [mock_doc1, None, {"filename": "test3.pdf", "data": "test3"}]
        
        # Test processing
        result = self.processor.process_all_pdfs()
        
        # Should only include successful processes
        self.assertEqual(result["processed_documents"], 2)
        self.assertEqual(len(result["documents"]), 2)
    
    @patch.object(DocumentProcessor, 'process_all_pdfs')
    @patch('builtins.print')
    def test_process_and_output_json(self, mock_print, mock_process_all):
        """Test JSON output processing"""
        # Mock processing result
        mock_result = {
            "processed_documents": 1,
            "documents": [{"test": "data"}]
        }
        mock_process_all.return_value = mock_result
        
        # Test JSON output
        self.processor.process_and_output_json()
        
        # Verify print was called with JSON output
        mock_print.assert_called()
        # Check if the printed output contains JSON-like structure
        printed_args = mock_print.call_args[0]
        self.assertTrue(any("processed_documents" in str(arg) for arg in printed_args))


if __name__ == '__main__':
    unittest.main()