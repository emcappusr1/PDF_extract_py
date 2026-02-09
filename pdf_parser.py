import fitz  # PyMuPDF
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PDFParser:
    """Extract text from PDF using PyMuPDF"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> Optional[str]:
        """
        Extract all text from PDF file
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Extracted text as string or None if error
        """
        doc = None
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Extract text from all pages
            full_text = ""
            page_count = len(doc)
            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text()
                full_text += text + "\n"
            
            logger.info(f"Successfully extracted text from PDF ({page_count} pages)")
            return full_text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return None
        finally:
            if doc:
                doc.close()
    
    @staticmethod
    def validate_pdf(pdf_bytes: bytes) -> bool:
        """
        Validate if the file is a valid PDF
        
        Args:
            pdf_bytes: File bytes to validate
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            is_valid = doc.page_count > 0
            doc.close()
            return is_valid
        except:
            return False
