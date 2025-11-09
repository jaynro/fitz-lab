"""
Main document processing orchestration
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from extractors.pdf_extractor import PDFExtractor
from extractors.table_extractor import TableExtractor
from models.pdf_models import TableRow


class DocumentProcessor:
    """Orchestrates the complete PDF processing pipeline"""
    
    def __init__(self, input_folder: str = "input"):
        """
        Initialize the document processor
        
        Args:
            input_folder: Path to the folder containing PDF files
        """
        self.input_folder = input_folder
        self.input_path = Path(input_folder)
    
    def validate_input_folder(self) -> bool:
        """
        Validate that the input folder exists and contains PDF files
        
        Returns:
            True if valid, False otherwise
        """
        if not self.input_path.exists():
            print(f"Error: Input folder '{self.input_folder}' does not exist!")
            return False
        
        pdf_files = list(self.input_path.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in '{self.input_folder}' folder!")
            return False
        
        return True
    
    def get_pdf_files(self) -> List[Path]:
        """
        Get list of PDF files in the input folder
        
        Returns:
            List of PDF file paths
        """
        return list(self.input_path.glob("*.pdf"))
    
    def process_single_pdf(self, pdf_file: Path) -> Dict[str, Any]:
        """
        Process a single PDF file and extract table data
        
        Args:
            pdf_file: Path to the PDF file
            
        Returns:
            Dictionary with processed document data
        """
        try:
            # Extract complete document data
            document_data = PDFExtractor.extract_complete_document_data(str(pdf_file))
            
            # Extract table data from the full text
            table_rows = TableExtractor.extract_table_data(document_data.full_text)
            
            # Create simplified document structure
            doc_dict = {
                "filename": document_data.metadata.filename,
                "metadata": {
                    "author": document_data.metadata.author,
                    "creator": document_data.metadata.creator
                },
                "table_data": {
                    "columns": TableExtractor.get_target_columns(),
                    "rows": [row.dict() for row in table_rows]
                },
                "summary": {
                    "total_categories": len(table_rows),
                    "categories_found": [
                        row.disability_category 
                        for row in table_rows 
                        if row.participants is not None
                    ]
                }
            }
            
            return doc_dict
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")
            return None
    
    def process_all_pdfs(self) -> Dict[str, Any]:
        """
        Process all PDF files in the input folder
        
        Returns:
            Dictionary with all processed documents
        """
        if not self.validate_input_folder():
            return {"processed_documents": 0, "documents": []}
        
        pdf_files = self.get_pdf_files()
        all_documents = []
        
        for pdf_file in pdf_files:
            processed_doc = self.process_single_pdf(pdf_file)
            if processed_doc:
                all_documents.append(processed_doc)
        
        return {
            "processed_documents": len(all_documents),
            "documents": all_documents
        }
    
    def process_and_output_json(self) -> None:
        """
        Process all PDFs and output results as JSON
        """
        result = self.process_all_pdfs()
        print(json.dumps(result, indent=2, ensure_ascii=False))