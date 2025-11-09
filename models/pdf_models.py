"""
Pydantic models for PDF document data structures
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class PDFDocument(BaseModel):
    """Pydantic model to represent PDF document information"""
    filename: str
    page_count: int
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None


class PDFPage(BaseModel):
    """Pydantic model to represent a PDF page"""
    page_number: int
    text_content: str
    filtered_content: str
    image_count: int
    link_count: int


class DocumentData(BaseModel):
    """Pydantic model for complete document data"""
    metadata: PDFDocument
    pages: List[PDFPage]
    full_text: str
    filtered_text: str


class TableRow(BaseModel):
    """Pydantic model for table row data"""
    disability_category: str
    participants: Optional[str] = None
    ballots_completed: Optional[str] = None
    completion_percentage: Optional[str] = None


class TableData(BaseModel):
    """Pydantic model for structured table data"""
    columns: List[str]
    rows: List[TableRow]