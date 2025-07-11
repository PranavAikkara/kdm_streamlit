"""
File Parser Tool for KDM Student Onboarding System

This module provides tools for parsing various document formats including PDF,
with support for text extraction and basic document analysis.
"""

import os
import io
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import logging

# PDF processing
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    logging.warning("pypdf not available. Install with: pip install pypdf")

# Image processing (for future OCR support)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class FileParserTool:
    """
    Comprehensive file parser tool for student documents.
    
    Supports:
    - PDF text extraction
    - Basic document metadata extraction
    - File validation
    """
    
    def __init__(self):
        self.supported_formats = [".pdf"]
        if PIL_AVAILABLE:
            self.supported_formats.extend([".jpg", ".jpeg", ".png", ".bmp", ".tiff"])
    
    def parse_document(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Parse a document and extract text and metadata.
        
        Args:
            file_path: Path to the document file
            **kwargs: Additional parsing options
            
        Returns:
            Dictionary containing extracted text, metadata, and parsing info
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        result = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "file_extension": file_extension,
            "text_content": "",
            "metadata": {},
            "page_count": 0,
            "parsing_errors": [],
            "success": False
        }
        
        try:
            if file_extension == ".pdf":
                result.update(self._parse_pdf(file_path, **kwargs))
            else:
                # For image files, we'll add OCR support later
                result["parsing_errors"].append(f"Parser for {file_extension} not yet implemented")
            
            result["success"] = len(result["parsing_errors"]) == 0
            
        except Exception as e:
            result["parsing_errors"].append(str(e))
            logging.error(f"Error parsing {file_path}: {e}")
        
        return result
    
    def _parse_pdf(self, file_path: Path, **kwargs) -> Dict[str, Any]:
        """
        Parse PDF file and extract text and metadata.
        
        Args:
            file_path: Path to PDF file
            **kwargs: Additional options (extract_metadata, max_pages, etc.)
            
        Returns:
            Dictionary with PDF content and metadata
        """
        if not PYPDF_AVAILABLE:
            raise ImportError("pypdf is required for PDF parsing. Install with: pip install pypdf")
        
        result = {
            "text_content": "",
            "metadata": {},
            "page_count": 0,
            "parsing_errors": []
        }
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Get page count
                result["page_count"] = len(pdf_reader.pages)
                
                # Extract metadata
                if kwargs.get("extract_metadata", True):
                    metadata = pdf_reader.metadata
                    if metadata:
                        result["metadata"] = {
                            "title": getattr(metadata, "title", ""),
                            "author": getattr(metadata, "author", ""),
                            "subject": getattr(metadata, "subject", ""),
                            "creator": getattr(metadata, "creator", ""),
                            "producer": getattr(metadata, "producer", ""),
                            "creation_date": str(getattr(metadata, "creation_date", "")),
                            "modification_date": str(getattr(metadata, "modification_date", ""))
                        }
                
                # Extract text from pages
                max_pages = kwargs.get("max_pages", None)
                pages_to_process = min(len(pdf_reader.pages), max_pages) if max_pages else len(pdf_reader.pages)
                
                text_parts = []
                for page_num in range(pages_to_process):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    except Exception as e:
                        result["parsing_errors"].append(f"Error extracting text from page {page_num + 1}: {e}")
                
                result["text_content"] = "\n\n".join(text_parts)
                
        except Exception as e:
            result["parsing_errors"].append(f"PDF parsing error: {e}")
        
        return result
    
    def validate_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate if a file can be processed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with validation results
        """
        file_path = Path(file_path)
        
        validation = {
            "valid": False,
            "file_exists": file_path.exists(),
            "supported_format": False,
            "file_size_ok": False,
            "errors": []
        }
        
        if not validation["file_exists"]:
            validation["errors"].append("File does not exist")
            return validation
        
        # Check file format
        file_extension = file_path.suffix.lower()
        validation["supported_format"] = file_extension in self.supported_formats
        if not validation["supported_format"]:
            validation["errors"].append(f"Unsupported file format: {file_extension}")
        
        # Check file size (limit to 50MB for now)
        file_size = file_path.stat().st_size
        max_size = 50 * 1024 * 1024  # 50MB
        validation["file_size_ok"] = file_size <= max_size
        if not validation["file_size_ok"]:
            validation["errors"].append(f"File too large: {file_size} bytes (max: {max_size})")
        
        validation["valid"] = (validation["file_exists"] and 
                              validation["supported_format"] and 
                              validation["file_size_ok"])
        
        return validation


# Convenience functions
def parse_pdf(file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
    """
    Convenience function to parse a PDF file.
    
    Args:
        file_path: Path to PDF file
        **kwargs: Additional parsing options
        
    Returns:
        Dictionary with extracted content and metadata
    """
    parser = FileParserTool()
    return parser.parse_document(file_path, **kwargs)


def parse_document(file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
    """
    Convenience function to parse any supported document.
    
    Args:
        file_path: Path to document file
        **kwargs: Additional parsing options
        
    Returns:
        Dictionary with extracted content and metadata
    """
    parser = FileParserTool()
    return parser.parse_document(file_path, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    # Test the file parser
    parser = FileParserTool()
    
    print("🔧 Testing File Parser Tool")
    print("=" * 40)
    
    # Test with a sample PDF (if available)
    test_files = ["sample.pdf", "test_document.pdf", "example.pdf"]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n📄 Testing with: {test_file}")
            
            # Validate file first
            validation = parser.validate_file(test_file)
            print(f"Validation: {validation}")
            
            if validation["valid"]:
                # Parse the document
                result = parser.parse_document(test_file)
                print(f"Success: {result['success']}")
                print(f"Pages: {result['page_count']}")
                print(f"Text length: {len(result['text_content'])} characters")
                if result['parsing_errors']:
                    print(f"Errors: {result['parsing_errors']}")
            break
    else:
        print("No test PDF files found. Place a PDF file in the current directory to test.")
    
    print(f"\nSupported formats: {parser.supported_formats}")
    print("✅ File Parser Tool test completed!") 