"""
Document Parser for NeuraDoc
Handles PDF and TXT file parsing
"""

import os
import fitz  # PyMuPDF
import re
from typing import Optional


class DocumentParser:
    """Parser for PDF and TXT documents"""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.txt'}
    
    def parse(self, filepath: str) -> Optional[str]:
        """
        Parse a document file and return its text content
        
        Args:
            filepath: Path to the document file
            
        Returns:
            Extracted text content or None if parsing fails
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        file_extension = os.path.splitext(filepath)[1].lower()
        
        if file_extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        try:
            if file_extension == '.pdf':
                return self._parse_pdf(filepath)
            elif file_extension == '.txt':
                return self._parse_txt(filepath)
        except Exception as e:
            print(f"Error parsing {filepath}: {str(e)}")
            return None
    
    def _parse_pdf(self, filepath: str) -> str:
        """Parse PDF file using PyMuPDF"""
        try:
            doc = fitz.open(filepath)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_content.append(text)
            
            doc.close()
            
            # Clean and join text
            full_text = '\n'.join(text_content)
            return self._clean_text(full_text)
            
        except Exception as e:
            raise Exception(f"PDF parsing failed: {str(e)}")
    
    def _parse_txt(self, filepath: str) -> str:
        """Parse TXT file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            return self._clean_text(content)
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(filepath, 'r', encoding='latin-1') as file:
                    content = file.read()
                return self._clean_text(content)
            except Exception as e:
                raise Exception(f"TXT parsing failed: {str(e)}")
        except Exception as e:
            raise Exception(f"TXT parsing failed: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'\b\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\']', ' ', text)
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace('–', '-').replace('—', '-')
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def get_document_info(self, filepath: str) -> dict:
        """
        Get basic information about the document
        
        Args:
            filepath: Path to the document file
            
        Returns:
            Dictionary with document information
        """
        info = {
            'filename': os.path.basename(filepath),
            'file_size': os.path.getsize(filepath),
            'file_type': os.path.splitext(filepath)[1].lower()
        }
        
        if info['file_type'] == '.pdf':
            try:
                doc = fitz.open(filepath)
                info['page_count'] = len(doc)
                info['title'] = doc.metadata.get('title', 'Unknown')
                info['author'] = doc.metadata.get('author', 'Unknown')
                doc.close()
            except:
                info['page_count'] = 0
                info['title'] = 'Unknown'
                info['author'] = 'Unknown'
        
        return info 