"""
Cognitive AI Module for CivicXAI
OpenCog AtomSpace integration for advanced reasoning and knowledge representation
"""

__version__ = '0.3.0'
__author__ = 'CivicXAI Team'

from .atomspace_manager import AtomSpaceManager, get_atomspace_manager
from .knowledge_store import KnowledgeStore, get_knowledge_store
from .reasoner import CognitiveReasoner, get_reasoner
from .ingestion_pipeline import IngestionPipeline, get_ingestion_pipeline

__all__ = [
    'AtomSpaceManager',
    'KnowledgeStore',
    'CognitiveReasoner',
    'IngestionPipeline',
    'get_atomspace_manager',
    'get_knowledge_store',
    'get_reasoner',
    'get_ingestion_pipeline',
]

# Module configuration
default_app_config = 'cognitive.apps.CognitiveConfig'
