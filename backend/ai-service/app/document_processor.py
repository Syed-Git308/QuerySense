import asyncio
from typing import BinaryIO, Dict, Any
import mimetypes
import pandas as pd
from docx import Document as DocxDocument
import json
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process various document types for AI embedding"""
    
    def __init__(self):
        self.supported_types = {
            'text/plain': self._process_text,
            'text/markdown': self._process_text,
            'text/csv': self._process_csv,
            'application/json': self._process_json,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self._process_docx,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': self._process_excel,
        }
    
    async def process_file(self, content: bytes, filename: str) -> str:
        """Process file content and return clean text for embedding"""
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        
        if not mime_type or mime_type not in self.supported_types:
            # Fallback to extension-based detection
            ext = filename.lower().split('.')[-1]
            mime_type = self._get_mime_from_extension(ext)
        
        if mime_type not in self.supported_types:
            raise ValueError(f"Unsupported file type: {mime_type}")
        
        try:
            # Process the content
            text = await self.supported_types[mime_type](content, filename)
            
            # Clean and normalize the text
            cleaned_text = self._clean_text(text)
            
            logger.info(f"Processed {filename}: {len(cleaned_text)} characters")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            raise
    
    def _get_mime_from_extension(self, ext: str) -> str:
        """Map file extensions to MIME types"""
        mapping = {
            'txt': 'text/plain',
            'md': 'text/markdown',
            'csv': 'text/csv',
            'json': 'application/json',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        return mapping.get(ext, 'text/plain')
    
    async def _process_text(self, content: bytes, filename: str) -> str:
        """Process plain text files"""
        try:
            # Try UTF-8 first, fallback to latin-1
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                return content.decode('latin-1')
        except Exception as e:
            raise ValueError(f"Failed to decode text file: {str(e)}")
    
    async def _process_csv(self, content: bytes, filename: str) -> str:
        """Process CSV files into structured text"""
        try:
            # Decode content
            text_content = content.decode('utf-8')
            
            # Parse CSV
            from io import StringIO
            df = pd.read_csv(StringIO(text_content))
            
            # Convert to structured text
            result = f"CSV File: {filename}\\n\\n"
            result += f"Columns: {', '.join(df.columns)}\\n\\n"
            
            # Add each row as structured text
            for idx, row in df.iterrows():
                row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                result += f"Row {idx + 1}: {row_text}\\n"
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to process CSV file: {str(e)}")
    
    async def _process_json(self, content: bytes, filename: str) -> str:
        """Process JSON files into readable text"""
        try:
            text_content = content.decode('utf-8')
            data = json.loads(text_content)
            
            # Convert JSON to structured text
            result = f"JSON File: {filename}\\n\\n"
            result += self._json_to_text(data)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to process JSON file: {str(e)}")
    
    async def _process_docx(self, content: bytes, filename: str) -> str:
        """Process DOCX files"""
        try:
            from io import BytesIO
            doc = DocxDocument(BytesIO(content))
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text.strip())
            
            return "\\n".join(text_parts)
            
        except Exception as e:
            raise ValueError(f"Failed to process DOCX file: {str(e)}")
    
    async def _process_excel(self, content: bytes, filename: str) -> str:
        """Process Excel files"""
        try:
            from io import BytesIO
            
            # Read all sheets
            excel_data = pd.read_excel(BytesIO(content), sheet_name=None)
            
            result = f"Excel File: {filename}\\n\\n"
            
            for sheet_name, df in excel_data.items():
                result += f"Sheet: {sheet_name}\\n"
                result += f"Columns: {', '.join(df.columns)}\\n\\n"
                
                # Add each row
                for idx, row in df.iterrows():
                    row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                    result += f"Row {idx + 1}: {row_text}\\n"
                
                result += "\\n"
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to process Excel file: {str(e)}")
    
    def _json_to_text(self, obj, indent=0) -> str:
        """Convert JSON object to readable text"""
        result = ""
        prefix = "  " * indent
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    result += f"{prefix}{key}:\\n"
                    result += self._json_to_text(value, indent + 1)
                else:
                    result += f"{prefix}{key}: {value}\\n"
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                result += f"{prefix}Item {i + 1}:\\n"
                result += self._json_to_text(item, indent + 1)
        else:
            result += f"{prefix}{obj}\\n"
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for embedding"""
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Remove very short lines that might be noise
        lines = text.split('\\n')
        cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 2]
        
        return "\\n".join(cleaned_lines)
