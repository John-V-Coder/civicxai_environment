"""
PDF Processor
Extracts text and metadata from PDF documents
"""
import logging
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import pypdf

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Processes PDF documents to extract text and metadata
    """
    
    def __init__(self):
        """Initialize PDF processor"""
        self.supported_formats = ['.pdf']
        logger.info("PDF Processor initialized")
    
    def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from a PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text and metadata
            
        Example:
            result = processor.extract_text_from_file('document.pdf')
            print(result['text'])
            print(result['metadata'])
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if file_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported format: {file_path.suffix}")
            
            # Extract text using pypdf
            reader = pypdf.PdfReader(str(file_path))
            
            # Extract metadata
            metadata = self._extract_metadata(reader)
            
            # Extract text from all pages
            text_content = []
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_content.append({
                        'page': page_num,
                        'text': page_text
                    })
            
            # Combine all text
            full_text = "\n\n".join([p['text'] for p in text_content])
            
            result = {
                'success': True,
                'file_path': str(file_path),
                'file_name': file_path.name,
                'text': full_text,
                'pages': len(reader.pages),
                'page_contents': text_content,
                'metadata': metadata,
                'word_count': len(full_text.split()),
                'char_count': len(full_text)
            }
            
            logger.info(f"Extracted text from {file_path.name}: {len(text_content)} pages, {result['word_count']} words")
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }
    
    def extract_text_from_bytes(self, pdf_bytes: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
        """
        Extract text from PDF bytes (e.g., from uploaded file)
        
        Args:
            pdf_bytes: PDF file content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            from io import BytesIO
            
            pdf_stream = BytesIO(pdf_bytes)
            reader = pypdf.PdfReader(pdf_stream)
            
            # Extract metadata
            metadata = self._extract_metadata(reader)
            
            # Extract text
            text_content = []
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_content.append({
                        'page': page_num,
                        'text': page_text
                    })
            
            full_text = "\n\n".join([p['text'] for p in text_content])
            
            result = {
                'success': True,
                'file_name': filename,
                'text': full_text,
                'pages': len(reader.pages),
                'page_contents': text_content,
                'metadata': metadata,
                'word_count': len(full_text.split()),
                'char_count': len(full_text)
            }
            
            logger.info(f"Extracted text from bytes: {len(text_content)} pages, {result['word_count']} words")
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract text from bytes: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_name': filename
            }
    
    def _extract_metadata(self, reader: pypdf.PdfReader) -> Dict[str, Any]:
        """Extract metadata from PDF reader"""
        metadata = {}
        
        try:
            if reader.metadata:
                metadata = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                    'creation_date': str(reader.metadata.get('/CreationDate', '')),
                    'modification_date': str(reader.metadata.get('/ModDate', ''))
                }
        except Exception as e:
            logger.warning(f"Could not extract metadata: {e}")
        
        return metadata
    
    def extract_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Split text into logical sections based on headings
        
        Args:
            text: Full document text
            
        Returns:
            List of sections with titles and content
        """
        sections = []
        
        # Simple section detection based on common patterns
        # Look for:
        # 1. Lines in ALL CAPS
        # 2. Lines ending with colon
        # 3. Numbered sections (1., 2., etc.)
        
        lines = text.split('\n')
        current_section = {'title': 'Introduction', 'content': []}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a heading
            is_heading = (
                line.isupper() and len(line) > 3 or  # ALL CAPS
                line.endswith(':') and len(line.split()) < 10 or  # Ends with colon
                re.match(r'^\d+\.?\s+[A-Z]', line)  # Numbered heading
            )
            
            if is_heading:
                # Save current section
                if current_section['content']:
                    current_section['content'] = '\n'.join(current_section['content'])
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'title': line.rstrip(':'),
                    'content': []
                }
            else:
                current_section['content'].append(line)
        
        # Add last section
        if current_section['content']:
            current_section['content'] = '\n'.join(current_section['content'])
            sections.append(current_section)
        
        logger.info(f"Extracted {len(sections)} sections from document")
        return sections
    
    def extract_key_sentences(self, text: str, num_sentences: int = 5) -> List[str]:
        """
        Extract key sentences from text (simple extractive summary)
        
        Args:
            text: Full document text
            num_sentences: Number of key sentences to extract
            
        Returns:
            List of key sentences
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) <= num_sentences:
            return sentences
        
        # Simple scoring: prefer sentences with important words
        important_words = [
            'priority', 'allocation', 'poverty', 'important', 'significant',
            'recommend', 'conclude', 'result', 'show', 'demonstrate',
            'policy', 'require', 'must', 'should', 'critical', 'essential'
        ]
        
        scored_sentences = []
        for sentence in sentences:
            score = sum(1 for word in important_words if word in sentence.lower())
            scored_sentences.append((score, sentence))
        
        # Sort by score and take top N
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        key_sentences = [sent for _, sent in scored_sentences[:num_sentences]]
        
        return key_sentences
    
    def get_statistics(self, text: str) -> Dict[str, Any]:
        """
        Get text statistics
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with statistics
        """
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        
        return {
            'word_count': len(words),
            'char_count': len(text),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0
        }


# Singleton instance
_pdf_processor_instance = None


def get_pdf_processor() -> PDFProcessor:
    """
    Get singleton PDFProcessor instance
    
    Returns:
        PDFProcessor instance
    """
    global _pdf_processor_instance
    if _pdf_processor_instance is None:
        _pdf_processor_instance = PDFProcessor()
    return _pdf_processor_instance
