"""
Concept Extractor
Uses NLP to extract concepts, entities, and relationships from text
"""
import logging
from typing import List, Dict, Set, Any, Tuple
import spacy
from collections import Counter
import re

logger = logging.getLogger(__name__)


class ConceptExtractor:
    """
    Extracts concepts and entities from text using NLP
    """
    
    def __init__(self, model_name: str = 'en_core_web_sm'):
        """
        Initialize concept extractor with spaCy model
        
        Args:
            model_name: spaCy model to use
        """
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.error(f"spaCy model '{model_name}' not found. Run: python -m spacy download {model_name}")
            raise
        
        # Domain-specific keywords for CivicXAI
        self.domain_keywords = {
            'poverty', 'allocation', 'priority', 'region', 'development',
            'resource', 'funding', 'budget', 'deforestation', 'environment',
            'corruption', 'governance', 'policy', 'economic', 'social',
            'infrastructure', 'education', 'health', 'unemployment',
            'impact', 'assessment', 'analysis', 'recommendation'
        }
    
    def extract_concepts(self, text: str, min_frequency: int = 2) -> List[Dict[str, Any]]:
        """
        Extract key concepts from text
        
        Args:
            text: Input text
            min_frequency: Minimum frequency for a concept to be included
            
        Returns:
            List of concepts with metadata
            
        Example:
            concepts = extractor.extract_concepts(document_text)
            for concept in concepts:
                print(f"{concept['text']}: {concept['category']}")
        """
        doc = self.nlp(text)
        
        concepts = []
        concept_counts = Counter()
        
        # Extract noun chunks as concepts
        for chunk in doc.noun_chunks:
            # Clean the chunk
            chunk_text = chunk.text.lower().strip()
            
            # Filter out very short or common words
            if len(chunk_text) < 3 or chunk_text in ['the', 'a', 'an', 'this', 'that']:
                continue
            
            concept_counts[chunk_text] += 1
        
        # Convert to concept objects
        for text, count in concept_counts.items():
            if count >= min_frequency:
                concepts.append({
                    'text': text,
                    'frequency': count,
                    'category': 'noun_phrase',
                    'importance': self._calculate_importance(text, count)
                })
        
        # Sort by importance
        concepts.sort(key=lambda x: x['importance'], reverse=True)
        
        logger.info(f"Extracted {len(concepts)} concepts from text")
        return concepts
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text
        
        Args:
            text: Input text
            
        Returns:
            List of entities with types and metadata
        """
        doc = self.nlp(text)
        
        entities = []
        seen_entities = set()
        
        for ent in doc.ents:
            entity_text = ent.text.strip()
            
            # Skip duplicates
            if entity_text in seen_entities:
                continue
            
            seen_entities.add(entity_text)
            
            entities.append({
                'text': entity_text,
                'type': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        logger.info(f"Extracted {len(entities)} entities from text")
        return entities
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[Tuple[str, float]]:
        """
        Extract keywords using frequency and importance scoring
        
        Args:
            text: Input text
            top_n: Number of top keywords to return
            
        Returns:
            List of (keyword, score) tuples
        """
        doc = self.nlp(text)
        
        # Count word frequencies (excluding stop words)
        word_freq = Counter()
        
        for token in doc:
            # Skip stop words, punctuation, and short words
            if (not token.is_stop and 
                not token.is_punct and 
                not token.is_space and
                len(token.text) > 2):
                
                word = token.lemma_.lower()
                word_freq[word] += 1
        
        # Calculate scores
        max_freq = max(word_freq.values()) if word_freq else 1
        
        scored_keywords = []
        for word, freq in word_freq.items():
            # Normalize frequency
            score = freq / max_freq
            
            # Boost domain-specific keywords
            if word in self.domain_keywords:
                score *= 1.5
            
            scored_keywords.append((word, score))
        
        # Sort and return top N
        scored_keywords.sort(key=lambda x: x[1], reverse=True)
        
        return scored_keywords[:top_n]
    
    def extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract relationships between concepts (subject-verb-object)
        
        Args:
            text: Input text
            
        Returns:
            List of relationships
        """
        doc = self.nlp(text)
        
        relationships = []
        
        for sent in doc.sents:
            # Find subject-verb-object patterns
            for token in sent:
                if token.dep_ == 'ROOT' and token.pos_ == 'VERB':
                    # Find subject
                    subjects = [child for child in token.children if child.dep_ in ['nsubj', 'nsubjpass']]
                    # Find object
                    objects = [child for child in token.children if child.dep_ in ['dobj', 'pobj', 'attr']]
                    
                    for subj in subjects:
                        for obj in objects:
                            relationships.append({
                                'subject': subj.text,
                                'predicate': token.text,
                                'object': obj.text,
                                'sentence': sent.text
                            })
        
        logger.info(f"Extracted {len(relationships)} relationships")
        return relationships
    
    def extract_topics(self, text: str, num_topics: int = 5) -> List[str]:
        """
        Extract main topics from text
        
        Args:
            text: Input text
            num_topics: Number of topics to extract
            
        Returns:
            List of topic strings
        """
        # Get keywords
        keywords = self.extract_keywords(text, top_n=num_topics * 3)
        
        # Group related keywords into topics
        topics = set()
        
        for keyword, score in keywords[:num_topics]:
            # Normalize to topic form
            topic = keyword.replace('_', ' ').title()
            topics.add(topic)
        
        return list(topics)[:num_topics]
    
    def _calculate_importance(self, text: str, frequency: int) -> float:
        """
        Calculate importance score for a concept
        
        Args:
            text: Concept text
            frequency: How often it appears
            
        Returns:
            Importance score (0.0 to 1.0)
        """
        score = 0.0
        
        # Base score from frequency
        score += min(frequency / 10.0, 0.5)
        
        # Boost if it's a domain keyword
        if any(keyword in text.lower() for keyword in self.domain_keywords):
            score += 0.3
        
        # Boost for multi-word concepts (usually more specific)
        if len(text.split()) > 1:
            score += 0.2
        
        return min(score, 1.0)
    
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive document analysis
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with all extracted information
        """
        logger.info("Starting comprehensive document analysis")
        
        analysis = {
            'concepts': self.extract_concepts(text),
            'entities': self.extract_entities(text),
            'keywords': self.extract_keywords(text),
            'topics': self.extract_topics(text),
            'relationships': self.extract_relationships(text),
            'statistics': {
                'word_count': len(text.split()),
                'char_count': len(text)
            }
        }
        
        logger.info(f"Analysis complete: {len(analysis['concepts'])} concepts, "
                   f"{len(analysis['entities'])} entities, {len(analysis['topics'])} topics")
        
        return analysis
    
    def find_domain_concepts(self, text: str) -> List[str]:
        """
        Find concepts specific to the CivicXAI domain
        
        Args:
            text: Document text
            
        Returns:
            List of domain-specific concepts found
        """
        text_lower = text.lower()
        found_concepts = []
        
        for keyword in self.domain_keywords:
            if keyword in text_lower:
                found_concepts.append(keyword)
        
        return found_concepts


# Singleton instance
_concept_extractor_instance = None


def get_concept_extractor() -> ConceptExtractor:
    """
    Get singleton ConceptExtractor instance
    
    Returns:
        ConceptExtractor instance
    """
    global _concept_extractor_instance
    if _concept_extractor_instance is None:
        _concept_extractor_instance = ConceptExtractor()
    return _concept_extractor_instance
