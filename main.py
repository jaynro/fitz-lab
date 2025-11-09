#!/usr/bin/env python3
"""
Main entry point for the PDF Document Analysis Tool
Clean, modular version with separated concerns
"""

from processors.document_processor import DocumentProcessor
from config import Config


def main():
    """Main execution function"""
    print("🔍 PDF Document Reader - Modular Version")
    print("=" * 60)
    
    # Initialize the document processor
    processor = DocumentProcessor(Config.DEFAULT_INPUT_FOLDER)
    
    # Process PDFs and output results
    processor.process_and_output_json()


if __name__ == "__main__":
    main()