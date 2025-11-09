"""
PDF extraction utilities using PyMuPDF (fitz)
"""

import fitz
import os
from typing import List

from models.pdf_models import PDFDocument, PDFPage, DocumentData


class PDFExtractor:
    """Handles PDF document reading and basic content extraction"""
    
    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def extract_complete_document_data(pdf_path: str) -> DocumentData:
        """
        Extract complete document data including metadata and all text content
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            DocumentData object with complete document information
        """
        # Get metadata
        metadata = PDFExtractor.read_pdf_metadata(pdf_path)
        
        # Get pages with text content
        pages = PDFExtractor.extract_text_from_pdf(pdf_path)
        
        # Combine all text content
        full_text = '\n\n'.join([page.text_content for page in pages])
        filtered_text = '\n\n'.join([page.filtered_content for page in pages])
        
        return DocumentData(
            metadata=metadata,
            pages=pages,
            full_text=full_text,
            filtered_text=filtered_text
        )