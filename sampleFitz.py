#!/usr/bin/env python3
"""
Sample script to read PDF documents using PyMuPDF (fitz)
"""

import fitz  # PyMuPDF
import os
import json
import re
from pathlib import Path
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


def read_pdf_metadata(pdf_path: str) -> PDFDocument:
    """
    Extract metadata from a PDF document
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        PDFDocument with metadata information
    """
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    
    pdf_info = PDFDocument(
        filename=os.path.basename(pdf_path),
        page_count=len(doc),
        title=metadata.get('title'),
        author=metadata.get('author'),
        subject=metadata.get('subject'),
        creator=metadata.get('creator')
    )
    
    doc.close()
    return pdf_info


def extract_table_data(text: str) -> List[Dict[str, Any]]:
    """
    Extract specific table columns: Disability Category, Participants, Ballots Completed
    
    Args:
        text: Original text content from PDF
        
    Returns:
        List of dictionaries with extracted table data
    """
    # Clean and normalize the text
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Initialize the data structure
    table_data = []
    
    # Based on the text structure, each category is followed by 3 numbers, then percentages
    # Pattern: Category Name -> Participants -> Ballots Completed -> Ballots Incomplete -> Percentage data
    
    categories_data = [
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
    
    # Convert text to single line for easier regex matching
    single_line_text = ' '.join(lines)
    
    for category_info in categories_data:
        category_data = {
            "disability_category": category_info["name"],
            "participants": None,
            "ballots_completed": None
        }
        
        # Try to match the pattern
        match = re.search(category_info["pattern"], single_line_text)
        
        if match:
            participants_total = match.group(1)  # First number after category
            ballots_completed = match.group(2)   # Second number (completed ballots)
            # Third number is incomplete ballots (we skip this)
            completion_percentage = match.group(4)  # The percentage
            
            category_data["participants"] = participants_total
            category_data["ballots_completed"] = ballots_completed
            
            # Also add the completion percentage as additional info
            category_data["completion_percentage"] = completion_percentage
        
        table_data.append(category_data)
    
    return table_data


def extract_text_from_pdf(pdf_path: str) -> List[PDFPage]:
    """
    Extract text content from all pages of a PDF
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of PDFPage objects with page information
    """
    doc = fitz.open(pdf_path)
    pages = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text
        text_content = page.get_text()
        
        # Extract table data instead of filtering
        filtered_content = text_content  # Keep original for now
        
        # Count images and links
        image_count = len(page.get_images())
        link_count = len(page.get_links())
        
        page_info = PDFPage(
            page_number=page_num + 1,
            text_content=text_content,
            filtered_content=filtered_content,
            image_count=image_count,
            link_count=link_count
        )
        
        pages.append(page_info)
    
    doc.close()
    return pages


def extract_complete_document_data(pdf_path: str) -> DocumentData:
    """
    Extract complete document data including metadata and all text content
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        DocumentData object with complete document information
    """
    # Get metadata
    metadata = read_pdf_metadata(pdf_path)
    
    # Get pages with text content
    pages = extract_text_from_pdf(pdf_path)
    
    # Combine all text content
    full_text = '\n\n'.join([page.text_content for page in pages])
    filtered_text = '\n\n'.join([page.filtered_content for page in pages])
    
    return DocumentData(
        metadata=metadata,
        pages=pages,
        full_text=full_text,
        filtered_text=filtered_text
    )


def process_pdfs_in_folder_json(input_folder: str = "input") -> None:
    """
    Process all PDF files in the input folder and extract specific table columns
    
    Args:
        input_folder: Path to the folder containing PDF files
    """
    input_path = Path(input_folder)
    
    if not input_path.exists():
        print(f"Error: Input folder '{input_folder}' does not exist!")
        return
    
    # Find all PDF files
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in '{input_folder}' folder!")
        return
    
    all_documents = []
    
    for pdf_file in pdf_files:
        try:
            # Extract complete document data
            document_data = extract_complete_document_data(str(pdf_file))
            
            # Extract table data from the full text
            table_data = extract_table_data(document_data.full_text)
            
            # Create simplified document structure
            doc_dict = {
                "filename": document_data.metadata.filename,
                "metadata": {
                    "author": document_data.metadata.author,
                    "creator": document_data.metadata.creator
                },
                "table_data": {
                    "columns": ["Disability Category", "Participants", "Ballots Completed"],
                    "rows": table_data
                },
                "summary": {
                    "total_categories": len(table_data),
                    "categories_found": [row["disability_category"] for row in table_data if row["participants"] is not None]
                }
            }
            
            all_documents.append(doc_dict)
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")
    
    # Output as JSON
    result = {
        "processed_documents": len(all_documents),
        "documents": all_documents
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("🔍 PDF Document Reader - JSON Output (Filtered)")
    print("=" * 60)
    
    # Process PDFs in the input folder and output as JSON
    process_pdfs_in_folder_json("input")
