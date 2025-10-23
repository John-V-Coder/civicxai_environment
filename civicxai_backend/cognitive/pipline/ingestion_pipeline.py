"""
Knowledge Ingestion Pipeline
Orchestrates the entire process of extracting knowledge from documents
"""
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from cognitive.processors.pdf_processor import get_pdf_processor
from cognitive.processors.concept_extractor import get_concept_extractor
from cognitive.atoms.atom_generator import get_atom_generator

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Orchestrates knowledge extraction and ingestion from documents
    """
    
    def __init__(self):
        """Initialize ingestion pipeline"""
        self.pdf_processor = get_pdf_processor()
        self.concept_extractor = get_concept_extractor()
        self.atom_generator = get_atom_generator()
        logger.info("Ingestion Pipeline initialized")
    
    def process_pdf_file(self, file_path: str, source_id: str) -> Dict[str, Any]:
        """
        Process a PDF file and ingest knowledge
        
        Args:
            file_path: Path to PDF file
            source_id: Unique identifier for this source
            
        Returns:
            Dictionary with processing results
            
        Example:
            pipeline = IngestionPipeline()
            result = pipeline.process_pdf_file('policy.pdf', 'Policy_2024')
            print(f"Extracted {result['atoms_created']} atoms")
        """
        try:
            logger.info(f"Starting PDF processing: {file_path}")
            
            # Step 1: Extract text from PDF
            extraction = self.pdf_processor.extract_text_from_file(file_path)
            
            if not extraction['success']:
                return {
                    'success': False,
                    'error': extraction['error'],
                    'stage': 'extraction'
                }
            
            # Step 2: Analyze text and extract concepts
            analysis = self.concept_extractor.analyze_document(extraction['text'])
            
            # Step 3: Generate atoms from analysis
            atom_stats = self.atom_generator.generate_from_analysis(analysis, source_id)
            
            result = {
                'success': True,
                'source_id': source_id,
                'file_name': extraction['file_name'],
                'pages': extraction['pages'],
                'word_count': extraction['word_count'],
                'concepts_extracted': len(analysis['concepts']),
                'entities_extracted': len(analysis['entities']),
                'topics_extracted': len(analysis['topics']),
                'relationships_extracted': len(analysis['relationships']),
                'atoms_created': sum(atom_stats.values()),
                'atom_breakdown': atom_stats,
                'key_topics': analysis['topics'][:5],
                'processing_stages': ['extraction', 'analysis', 'atomization']
            }
            
            logger.info(f"Successfully processed {file_path}: {result['atoms_created']} atoms created")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process PDF {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'source_id': source_id
            }
    
    def process_pdf_bytes(self, pdf_bytes: bytes, filename: str, source_id: str) -> Dict[str, Any]:
        """
        Process PDF from bytes (e.g., uploaded file)
        
        Args:
            pdf_bytes: PDF content as bytes
            filename: Original filename
            source_id: Unique identifier
            
        Returns:
            Processing results
        """
        try:
            logger.info(f"Starting PDF bytes processing: {filename}")
            
            # Step 1: Extract text
            extraction = self.pdf_processor.extract_text_from_bytes(pdf_bytes, filename)
            
            if not extraction['success']:
                return {
                    'success': False,
                    'error': extraction['error'],
                    'stage': 'extraction'
                }
            
            # Step 2: Analyze
            analysis = self.concept_extractor.analyze_document(extraction['text'])
            
            # Step 3: Generate atoms
            atom_stats = self.atom_generator.generate_from_analysis(analysis, source_id)
            
            result = {
                'success': True,
                'source_id': source_id,
                'file_name': filename,
                'pages': extraction['pages'],
                'word_count': extraction['word_count'],
                'concepts_extracted': len(analysis['concepts']),
                'entities_extracted': len(analysis['entities']),
                'topics_extracted': len(analysis['topics']),
                'atoms_created': sum(atom_stats.values()),
                'atom_breakdown': atom_stats,
                'key_topics': analysis['topics'][:5]
            }
            
            logger.info(f"Successfully processed {filename}: {result['atoms_created']} atoms created")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process PDF bytes {filename}: {e}")
            return {
                'success': False,
                'error': str(e),
                'source_id': source_id
            }
    
    def process_text(self, text: str, source_id: str) -> Dict[str, Any]:
        """
        Process plain text directly
        
        Args:
            text: Text content
            source_id: Unique identifier
            
        Returns:
            Processing results
        """
        try:
            logger.info(f"Starting text processing for {source_id}")
            
            # Analyze text
            analysis = self.concept_extractor.analyze_document(text)
            
            # Generate atoms
            atom_stats = self.atom_generator.generate_from_analysis(analysis, source_id)
            
            result = {
                'success': True,
                'source_id': source_id,
                'word_count': len(text.split()),
                'concepts_extracted': len(analysis['concepts']),
                'entities_extracted': len(analysis['entities']),
                'topics_extracted': len(analysis['topics']),
                'atoms_created': sum(atom_stats.values()),
                'atom_breakdown': atom_stats,
                'key_topics': analysis['topics'][:5]
            }
            
            logger.info(f"Successfully processed text: {result['atoms_created']} atoms created")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process text for {source_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'source_id': source_id
            }
    
    def batch_process_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Process multiple files in batch
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            Batch processing results
        """
        results = []
        successful = 0
        failed = 0
        
        for file_path in file_paths:
            path = Path(file_path)
            source_id = f"Source_{path.stem}"
            
            result = self.process_pdf_file(file_path, source_id)
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
        
        summary = {
            'total_files': len(file_paths),
            'successful': successful,
            'failed': failed,
            'results': results,
            'total_atoms_created': sum(r.get('atoms_created', 0) for r in results if r['success'])
        }
        
        logger.info(f"Batch processing complete: {successful}/{len(file_paths)} successful")
        return summary
    
    def initialize_domain_knowledge(self) -> Dict[str, Any]:
        """
        Initialize the knowledge base with pre-defined domain knowledge
        
        Returns:
            Initialization results
        """
        try:
            logger.info("Initializing domain knowledge")
            stats = self.atom_generator.generate_domain_knowledge()
            
            return {
                'success': True,
                'message': 'Domain knowledge initialized',
                'stats': stats
            }
        except Exception as e:
            logger.error(f"Failed to initialize domain knowledge: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_ingestion_pipeline_instance = None


def get_ingestion_pipeline() -> IngestionPipeline:
    """
    Get singleton IngestionPipeline instance
    
    Returns:
        IngestionPipeline instance
    """
    global _ingestion_pipeline_instance
    if _ingestion_pipeline_instance is None:
        _ingestion_pipeline_instance = IngestionPipeline()
    return _ingestion_pipeline_instance
