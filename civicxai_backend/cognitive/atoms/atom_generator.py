"""
Atom Generator
Converts extracted concepts and relationships into AtomSpace atoms
"""
import logging
from typing import List, Dict, Any, Optional
from cognitive.atoms.atomspace_manager import get_atomspace_manager
from cognitive.knowledge.knowledge_store import get_knowledge_store

logger = logging.getLogger(__name__)


class AtomGenerator:
    """
    Generates AtomSpace atoms from extracted concepts and relationships
    """
    
    def __init__(self):
        """Initialize atom generator"""
        self.atomspace = get_atomspace_manager()
        self.knowledge = get_knowledge_store()
        logger.info("Atom Generator initialized")
    
    def generate_from_analysis(self, analysis: Dict[str, Any], source_id: str) -> Dict[str, int]:
        """
        Generate atoms from document analysis
        
        Args:
            analysis: Analysis results from ConceptExtractor
            source_id: ID of the data source
            
        Returns:
            Dictionary with counts of atoms created
        """
        stats = {
            'concepts_added': 0,
            'entities_added': 0,
            'relationships_added': 0,
            'topics_added': 0
        }
        
        # Add source node
        self.atomspace.add_node('ConceptNode', source_id)
        self.atomspace.add_link('InheritanceLink', source_id, 'DataSource')
        
        # Add concepts
        for concept in analysis.get('concepts', []):
            if self._add_concept(concept, source_id):
                stats['concepts_added'] += 1
        
        # Add entities
        for entity in analysis.get('entities', []):
            if self._add_entity(entity, source_id):
                stats['entities_added'] += 1
        
        # Add topics
        for topic in analysis.get('topics', []):
            if self._add_topic(topic, source_id):
                stats['topics_added'] += 1
        
        # Add relationships
        for relationship in analysis.get('relationships', []):
            if self._add_relationship(relationship):
                stats['relationships_added'] += 1
        
        logger.info(f"Generated atoms from analysis: {stats}")
        return stats
    
    def _add_concept(self, concept: Dict[str, Any], source_id: str) -> bool:
        """Add a concept as a node"""
        try:
            concept_text = concept['text']
            concept_id = self._normalize_concept_name(concept_text)
            
            # Add concept node
            self.atomspace.add_node('ConceptNode', concept_id)
            
            # Link to source
            self.atomspace.add_link('ReferenceLink', source_id, concept_id)
            
            # Add importance as property
            importance = concept.get('importance', 0.5)
            self.atomspace.add_atom(f"(= (importance {concept_id}) {importance})")
            
            return True
        except Exception as e:
            logger.error(f"Failed to add concept: {e}")
            return False
    
    def _add_entity(self, entity: Dict[str, Any], source_id: str) -> bool:
        """Add a named entity"""
        try:
            entity_text = entity['text']
            entity_type = entity['type']
            entity_id = self._normalize_concept_name(entity_text)
            
            # Add entity node
            self.atomspace.add_node('ConceptNode', entity_id)
            
            # Add type classification
            type_category = f"Entity_{entity_type}"
            self.atomspace.add_node('ConceptNode', type_category)
            self.atomspace.add_link('InheritanceLink', entity_id, type_category)
            
            # Link to source
            self.atomspace.add_link('ReferenceLink', source_id, entity_id)
            
            return True
        except Exception as e:
            logger.error(f"Failed to add entity: {e}")
            return False
    
    def _add_topic(self, topic: str, source_id: str) -> bool:
        """Add a topic"""
        try:
            topic_id = f"Topic_{self._normalize_concept_name(topic)}"
            
            # Add topic node
            self.atomspace.add_node('ConceptNode', topic_id)
            self.atomspace.add_link('InheritanceLink', topic_id, 'Topic')
            
            # Link source to topic
            self.atomspace.add_link('ReferenceLink', source_id, topic_id)
            
            return True
        except Exception as e:
            logger.error(f"Failed to add topic: {e}")
            return False
    
    def _add_relationship(self, relationship: Dict[str, Any]) -> bool:
        """Add a subject-predicate-object relationship"""
        try:
            subject = self._normalize_concept_name(relationship['subject'])
            predicate = self._normalize_concept_name(relationship['predicate'])
            obj = self._normalize_concept_name(relationship['object'])
            
            # Add nodes
            self.atomspace.add_node('ConceptNode', subject)
            self.atomspace.add_node('PredicateNode', predicate)
            self.atomspace.add_node('ConceptNode', obj)
            
            # Add evaluation link
            eval_expr = f"(EvaluationLink (PredicateNode {predicate}) (ListLink (ConceptNode {subject}) (ConceptNode {obj})))"
            self.atomspace.add_atom(eval_expr)
            
            return True
        except Exception as e:
            logger.error(f"Failed to add relationship: {e}")
            return False
    
    def _normalize_concept_name(self, text: str) -> str:
        """
        Normalize concept text to valid atom name
        
        Args:
            text: Raw concept text
            
        Returns:
            Normalized name suitable for AtomSpace
        """
        # Replace spaces with underscores
        normalized = text.replace(' ', '_')
        
        # Remove special characters
        normalized = ''.join(c for c in normalized if c.isalnum() or c == '_')
        
        # Capitalize first letter of each word
        normalized = '_'.join(word.capitalize() for word in normalized.split('_'))
        
        return normalized
    
    def link_similar_concepts(self, concept1: str, concept2: str, similarity: float) -> bool:
        """
        Create similarity link between concepts
        
        Args:
            concept1: First concept
            concept2: Second concept
            similarity: Similarity score (0.0 to 1.0)
            
        Returns:
            Success status
        """
        try:
            id1 = self._normalize_concept_name(concept1)
            id2 = self._normalize_concept_name(concept2)
            
            return self.atomspace.add_link('SimilarityLink', id1, id2, similarity)
        except Exception as e:
            logger.error(f"Failed to link concepts: {e}")
            return False
    
    def add_causal_link(self, cause: str, effect: str, strength: float = 0.8) -> bool:
        """
        Add causal relationship
        
        Args:
            cause: Cause concept
            effect: Effect concept
            strength: Strength of causation
            
        Returns:
            Success status
        """
        try:
            cause_id = self._normalize_concept_name(cause)
            effect_id = self._normalize_concept_name(effect)
            
            # Add nodes
            self.atomspace.add_node('ConceptNode', cause_id)
            self.atomspace.add_node('ConceptNode', effect_id)
            
            # Add causal link
            causal_expr = f"(CausalLink {cause_id} {effect_id})"
            return self.atomspace.add_atom(causal_expr)
        except Exception as e:
            logger.error(f"Failed to add causal link: {e}")
            return False
    
    def generate_domain_knowledge(self) -> Dict[str, int]:
        """
        Generate pre-defined domain knowledge for CivicXAI
        
        Returns:
            Dictionary with counts of atoms created
        """
        stats = {'concepts': 0, 'similarities': 0, 'causal_links': 0}
        
        # Define core domain concepts
        core_concepts = [
            'Poverty', 'Economic_Hardship', 'Unemployment', 'Income_Inequality',
            'Resource_Allocation', 'Priority', 'Development', 'Infrastructure',
            'Education', 'Health', 'Environment', 'Deforestation',
            'Corruption', 'Governance', 'Policy', 'Budget', 'Funding'
        ]
        
        # Add core concepts
        for concept in core_concepts:
            if self.atomspace.add_node('ConceptNode', concept):
                stats['concepts'] += 1
        
        # Define similarities
        similarities = [
            ('Poverty', 'Economic_Hardship', 0.9),
            ('Poverty', 'Unemployment', 0.7),
            ('Poverty', 'Income_Inequality', 0.8),
            ('Resource_Allocation', 'Budget', 0.85),
            ('Resource_Allocation', 'Funding', 0.9),
            ('Development', 'Infrastructure', 0.8),
            ('Development', 'Education', 0.75),
            ('Environment', 'Deforestation', 0.9),
            ('Governance', 'Policy', 0.85),
            ('Governance', 'Corruption', 0.6)
        ]
        
        for concept1, concept2, similarity in similarities:
            if self.link_similar_concepts(concept1, concept2, similarity):
                stats['similarities'] += 1
        
        # Define causal relationships
        causal_links = [
            ('Poverty', 'Priority', 0.9),
            ('High_Poverty', 'Requires_Allocation', 0.85),
            ('Deforestation', 'Environmental_Risk', 0.8),
            ('Corruption', 'Reduced_Effectiveness', 0.7),
            ('Education', 'Economic_Development', 0.75),
            ('Infrastructure', 'Economic_Growth', 0.8)
        ]
        
        for cause, effect, strength in causal_links:
            if self.add_causal_link(cause, effect, strength):
                stats['causal_links'] += 1
        
        logger.info(f"Generated domain knowledge: {stats}")
        return stats


# Singleton instance
_atom_generator_instance = None


def get_atom_generator() -> AtomGenerator:
    """
    Get singleton AtomGenerator instance
    
    Returns:
        AtomGenerator instance
    """
    global _atom_generator_instance
    if _atom_generator_instance is None:
        _atom_generator_instance = AtomGenerator()
    return _atom_generator_instance
