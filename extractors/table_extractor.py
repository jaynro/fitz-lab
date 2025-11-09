"""
Table extraction and parsing utilities
"""

import re
from typing import List, Dict, Any

from models.pdf_models import TableRow


class TableExtractor:
    """Handles table data extraction from PDF text content"""
    
    # Predefined regex patterns for disability categories
    CATEGORY_PATTERNS = [
        {
            "name": "Blind",
            "pattern": r"Blind\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+%)"
        },
        {
            "name": "Low Vision", 
            "pattern": r"Low Vision\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+%)"
        },
        {
            "name": "Dexterity",
            "pattern": r"Dexterity\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+%)"
        },
        {
            "name": "Mobility",
            "pattern": r"Mobility\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+%)"
        }
    ]
    
    @classmethod
    def extract_table_data(cls, text: str) -> List[TableRow]:
        """
        Extract specific table columns: Disability Category, Participants, Ballots Completed
        
        Args:
            text: Original text content from PDF
            
        Returns:
            List of TableRow objects with extracted table data
        """
        # Clean and normalize the text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Convert text to single line for easier regex matching
        single_line_text = ' '.join(lines)
        
        table_data = []
        
        for category_info in cls.CATEGORY_PATTERNS:
            category_data = TableRow(
                disability_category=category_info["name"],
                participants=None,
                ballots_completed=None,
                completion_percentage=None
            )
            
            # Try to match the pattern
            match = re.search(category_info["pattern"], single_line_text)
            
            if match:
                participants_total = match.group(1)  # First number after category
                ballots_completed = match.group(2)   # Second number (completed ballots)
                # Third number is incomplete ballots (we skip this)
                completion_percentage = match.group(4)  # The percentage
                
                category_data.participants = participants_total
                category_data.ballots_completed = ballots_completed
                category_data.completion_percentage = completion_percentage
            
            table_data.append(category_data)
        
        return table_data
    
    @classmethod
    def get_target_columns(cls) -> List[str]:
        """
        Returns the list of target columns being extracted
        
        Returns:
            List of column names
        """
        return ["Disability Category", "Participants", "Ballots Completed"]