"""
Unit tests for Pydantic models
"""

import unittest
from pydantic import ValidationError
import pytest

from models.pdf_models import PDFDocument, PDFPage, DocumentData, TableRow, TableData


class TestPydanticModels(unittest.TestCase):
    """Test cases for Pydantic model validation and behavior"""
    
    def test_pdf_document_valid_data(self):
        """Test PDFDocument with valid data"""
        doc = PDFDocument(
            filename="test.pdf",
            page_count=5,
            title="Test Document",
            author="Test Author",
            subject="Test Subject",
            creator="Test Creator"
        )
        
        self.assertEqual(doc.filename, "test.pdf")
        self.assertEqual(doc.page_count, 5)
        self.assertEqual(doc.title, "Test Document")
        self.assertEqual(doc.author, "Test Author")
        self.assertEqual(doc.subject, "Test Subject")
        self.assertEqual(doc.creator, "Test Creator")
    
    def test_pdf_document_required_fields_only(self):
        """Test PDFDocument with only required fields"""
        doc = PDFDocument(
            filename="test.pdf",
            page_count=1
        )
        
        self.assertEqual(doc.filename, "test.pdf")
        self.assertEqual(doc.page_count, 1)
        self.assertIsNone(doc.title)
        self.assertIsNone(doc.author)
        self.assertIsNone(doc.subject)
        self.assertIsNone(doc.creator)
    
    def test_pdf_document_missing_required_fields(self):
        """Test PDFDocument validation with missing required fields"""
        with self.assertRaises(ValidationError):
            PDFDocument(filename="test.pdf")  # Missing page_count
        
        with self.assertRaises(ValidationError):
            PDFDocument(page_count=1)  # Missing filename
    
    def test_pdf_document_invalid_types(self):
        """Test PDFDocument validation with invalid types"""
        with self.assertRaises(ValidationError):
            PDFDocument(
                filename=123,  # Should be string
                page_count=1
            )
        
        with self.assertRaises(ValidationError):
            PDFDocument(
                filename="test.pdf",
                page_count="not_a_number"  # Should be int
            )
    
    def test_pdf_page_valid_data(self):
        """Test PDFPage with valid data"""
        page = PDFPage(
            page_number=1,
            text_content="Sample text content",
            filtered_content="Filtered text content",
            image_count=2,
            link_count=3
        )
        
        self.assertEqual(page.page_number, 1)
        self.assertEqual(page.text_content, "Sample text content")
        self.assertEqual(page.filtered_content, "Filtered text content")
        self.assertEqual(page.image_count, 2)
        self.assertEqual(page.link_count, 3)
    
    def test_pdf_page_validation_errors(self):
        """Test PDFPage validation errors"""
        with self.assertRaises(ValidationError):
            PDFPage(
                page_number="not_a_number",
                text_content="Sample text",
                filtered_content="Filtered text",
                image_count=0,
                link_count=0
            )
    
    def test_table_row_valid_data(self):
        """Test TableRow with valid data"""
        row = TableRow(
            disability_category="Blind",
            participants="5",
            ballots_completed="1",
            completion_percentage="34.5%"
        )
        
        self.assertEqual(row.disability_category, "Blind")
        self.assertEqual(row.participants, "5")
        self.assertEqual(row.ballots_completed, "1")
        self.assertEqual(row.completion_percentage, "34.5%")
    
    def test_table_row_optional_fields(self):
        """Test TableRow with optional fields as None"""
        row = TableRow(
            disability_category="Mobility",
            participants=None,
            ballots_completed=None,
            completion_percentage=None
        )
        
        self.assertEqual(row.disability_category, "Mobility")
        self.assertIsNone(row.participants)
        self.assertIsNone(row.ballots_completed)
        self.assertIsNone(row.completion_percentage)
    
    def test_table_row_missing_required_field(self):
        """Test TableRow with missing required field"""
        with self.assertRaises(ValidationError):
            TableRow(
                participants="5",
                ballots_completed="1"
                # Missing disability_category
            )
    
    def test_table_data_valid(self):
        """Test TableData with valid data"""
        rows = [
            TableRow(disability_category="Blind", participants="5", ballots_completed="1"),
            TableRow(disability_category="Mobility", participants="3", ballots_completed="3")
        ]
        
        table = TableData(
            columns=["Disability Category", "Participants", "Ballots Completed"],
            rows=rows
        )
        
        self.assertEqual(len(table.columns), 3)
        self.assertEqual(len(table.rows), 2)
        self.assertIsInstance(table.rows[0], TableRow)
    
    def test_document_data_valid(self):
        """Test DocumentData with valid nested models"""
        # Create nested models
        metadata = PDFDocument(filename="test.pdf", page_count=1)
        pages = [PDFPage(
            page_number=1,
            text_content="Sample text",
            filtered_content="Filtered text",
            image_count=0,
            link_count=0
        )]
        
        doc_data = DocumentData(
            metadata=metadata,
            pages=pages,
            full_text="Sample text",
            filtered_text="Filtered text"
        )
        
        self.assertIsInstance(doc_data.metadata, PDFDocument)
        self.assertEqual(len(doc_data.pages), 1)
        self.assertIsInstance(doc_data.pages[0], PDFPage)
        self.assertEqual(doc_data.full_text, "Sample text")
        self.assertEqual(doc_data.filtered_text, "Filtered text")
    
    def test_document_data_validation_error(self):
        """Test DocumentData validation with invalid nested data"""
        with self.assertRaises(ValidationError):
            DocumentData(
                metadata="not_a_pdf_document",  # Should be PDFDocument
                pages=[],
                full_text="Sample text",
                filtered_text="Filtered text"
            )
    
    def test_model_serialization(self):
        """Test model serialization to dictionary"""
        row = TableRow(
            disability_category="Blind",
            participants="5",
            ballots_completed="1",
            completion_percentage="34.5%"
        )
        
        # Test .dict() method
        row_dict = row.dict()
        self.assertIsInstance(row_dict, dict)
        self.assertEqual(row_dict["disability_category"], "Blind")
        self.assertEqual(row_dict["participants"], "5")
    
    def test_model_json_serialization(self):
        """Test model JSON serialization"""
        doc = PDFDocument(filename="test.pdf", page_count=1, author="Test")
        
        # Test .json() method
        json_str = doc.json()
        self.assertIsInstance(json_str, str)
        self.assertIn("test.pdf", json_str)
        self.assertIn("Test", json_str)
    
    def test_model_from_dict(self):
        """Test creating model from dictionary"""
        data = {
            "disability_category": "Dexterity",
            "participants": "5",
            "ballots_completed": "4",
            "completion_percentage": "98.3%"
        }
        
        row = TableRow(**data)
        self.assertEqual(row.disability_category, "Dexterity")
        self.assertEqual(row.participants, "5")
        self.assertEqual(row.ballots_completed, "4")
        self.assertEqual(row.completion_percentage, "98.3%")


if __name__ == '__main__':
    unittest.main()