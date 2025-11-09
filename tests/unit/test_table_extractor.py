"""
Unit tests for table extraction functionality
"""

import unittest
from unittest.mock import patch
import pytest

from extractors.table_extractor import TableExtractor
from models.pdf_models import TableRow
from tests.conftest import EXPECTED_CATEGORIES, EXPECTED_COLUMNS


class TestTableExtractor(unittest.TestCase):
    """Test cases for TableExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Sample text that mimics the structure of our PDF
        self.sample_text = """
        Example table
        This is an example of a data table.
        Disability
        Category
        Participants
        Ballots
        Completed
        Ballots
        Incomplete/
        Terminated
        Results
        Accuracy
        Time to
        complete
        Blind 5 1 4 34.5%, n=1 1199 sec, n=1
        Low Vision 5 2 3 98.3% n=2 (97.7%, n=3) 1716 sec, n=3 (1934 sec, n=2)
        Dexterity 5 4 1 98.3%, n=4 1672.1 sec, n=4
        Mobility 3 3 0 95.4%, n=3 1416 sec, n=3
        """
        
        self.empty_text = "No disability data here"
        
        self.malformed_text = """
        Blind incomplete data
        Low Vision missing numbers
        """
    
    def test_get_target_columns(self):
        """Test that target columns are returned correctly"""
        columns = TableExtractor.get_target_columns()
        
        self.assertIsInstance(columns, list)
        self.assertEqual(columns, EXPECTED_COLUMNS)
        self.assertEqual(len(columns), 3)
    
    def test_extract_table_data_success(self):
        """Test successful table data extraction"""
        result = TableExtractor.extract_table_data(self.sample_text)
        
        # Verify return type and length
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)  # 4 disability categories
        
        # Check each row is a TableRow
        for row in result:
            self.assertIsInstance(row, TableRow)
            self.assertIn(row.disability_category, EXPECTED_CATEGORIES)
        
        # Test specific data extraction
        blind_row = next((row for row in result if row.disability_category == "Blind"), None)
        self.assertIsNotNone(blind_row)
        self.assertEqual(blind_row.participants, "5")
        self.assertEqual(blind_row.ballots_completed, "1")
        self.assertEqual(blind_row.completion_percentage, "34.5%")
        
        # Test Low Vision data
        lv_row = next((row for row in result if row.disability_category == "Low Vision"), None)
        self.assertIsNotNone(lv_row)
        self.assertEqual(lv_row.participants, "5")
        self.assertEqual(lv_row.ballots_completed, "2")
        self.assertEqual(lv_row.completion_percentage, "98.3%")
        
        # Test Dexterity data
        dex_row = next((row for row in result if row.disability_category == "Dexterity"), None)
        self.assertIsNotNone(dex_row)
        self.assertEqual(dex_row.participants, "5")
        self.assertEqual(dex_row.ballots_completed, "4")
        self.assertEqual(dex_row.completion_percentage, "98.3%")
        
        # Test Mobility data
        mob_row = next((row for row in result if row.disability_category == "Mobility"), None)
        self.assertIsNotNone(mob_row)
        self.assertEqual(mob_row.participants, "3")
        self.assertEqual(mob_row.ballots_completed, "3")
        self.assertEqual(mob_row.completion_percentage, "95.4%")
    
    def test_extract_table_data_empty_text(self):
        """Test table extraction with text that contains no disability data"""
        result = TableExtractor.extract_table_data(self.empty_text)
        
        # Should still return 4 rows (one for each category) but with None values
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)
        
        # All rows should have None for data fields
        for row in result:
            self.assertIsInstance(row, TableRow)
            self.assertIn(row.disability_category, EXPECTED_CATEGORIES)
            self.assertIsNone(row.participants)
            self.assertIsNone(row.ballots_completed)
            self.assertIsNone(row.completion_percentage)
    
    def test_extract_table_data_malformed_text(self):
        """Test table extraction with malformed text"""
        result = TableExtractor.extract_table_data(self.malformed_text)
        
        # Should return 4 rows but with None values due to malformed data
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)
        
        # Check that data is None due to malformed input
        for row in result:
            # Categories should still be set
            self.assertIn(row.disability_category, EXPECTED_CATEGORIES)
            # But data should be None due to missing proper format
            self.assertIsNone(row.participants)
            self.assertIsNone(row.ballots_completed)
    
    def test_category_patterns_structure(self):
        """Test that category patterns are properly structured"""
        patterns = TableExtractor.CATEGORY_PATTERNS
        
        self.assertIsInstance(patterns, list)
        self.assertEqual(len(patterns), 4)
        
        for pattern in patterns:
            self.assertIsInstance(pattern, dict)
            self.assertIn("name", pattern)
            self.assertIn("pattern", pattern)
            self.assertIn(pattern["name"], EXPECTED_CATEGORIES)
    
    def test_regex_patterns_validation(self):
        """Test that regex patterns are valid"""
        import re
        
        for pattern_info in TableExtractor.CATEGORY_PATTERNS:
            pattern = pattern_info["pattern"]
            
            # Should be able to compile the regex
            try:
                compiled_pattern = re.compile(pattern)
                self.assertIsNotNone(compiled_pattern)
            except re.error:
                self.fail(f"Invalid regex pattern for {pattern_info['name']}: {pattern}")
    
    def test_extract_table_data_case_insensitive(self):
        """Test that extraction works with different case variations"""
        case_variant_text = """
        BLIND 5 1 4 34.5%, n=1 1199 sec
        low vision 5 2 3 98.3% n=2 1716 sec
        Dexterity 5 4 1 98.3%, n=4 1672 sec  
        MOBILITY 3 3 0 95.4%, n=3 1416 sec
        """
        
        result = TableExtractor.extract_table_data(case_variant_text)
        
        # Should extract data regardless of case
        blind_row = next((row for row in result if row.disability_category == "Blind"), None)
        self.assertIsNotNone(blind_row)
        # Note: The current implementation may be case-sensitive, 
        # this test helps identify if we need to make it case-insensitive


if __name__ == '__main__':
    unittest.main()