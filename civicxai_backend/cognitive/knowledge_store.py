"""
Knowledge Store
High-level interface for storing domain-specific knowledge in AtomSpace
"""
import logging
from typing import Dict, List, Optional, Any
from .atomspace_manager import get_atomspace_manager

logger = logging.getLogger(__name__)


class KnowledgeStore:
    """
    High-level interface for storing CivicXAI domain knowledge
    Abstracts AtomSpace complexity with domain-specific methods
    """
    
    def __init__(self):
        """Initialize knowledge store with AtomSpace manager"""
        self.atomspace = get_atomspace_manager()
        logger.info("Knowledge Store initialized")
    
    # ===== Region Knowledge =====
    
    def add_region(self, region_id: str, region_data: Dict[str, Any]) -> bool:
        """
        Add a region with its characteristics to the knowledge base
        
        Args:
            region_id: Unique region identifier
            region_data: Dictionary with region properties
            
        Returns:
            bool: Success status
            
        Example:
            add_region('Region_Nairobi', {
                'name': 'Nairobi',
                'poverty_index': 0.8,
                'deforestation': 0.3,
                'population': 4500000,
                'type': 'coastal'
            })
        """
        try:
            # Add region as concept
            self.atomspace.add_node('ConceptNode', region_id)
            
            # Add region type
            self.atomspace.add_link('InheritanceLink', region_id, 'Region')
            
            # Add properties
            properties = {}
            for key, value in region_data.items():
                properties[key] = value
            
            self.atomspace.add_concept_with_properties(region_id, properties)
            
            # Add classification based on poverty level
            poverty = region_data.get('poverty_index', 0)
            if poverty > 0.7:
                self.atomspace.add_link('InheritanceLink', region_id, 'High_Poverty_Region')
            elif poverty > 0.4:
                self.atomspace.add_link('InheritanceLink', region_id, 'Medium_Poverty_Region')
            else:
                self.atomspace.add_link('InheritanceLink', region_id, 'Low_Poverty_Region')
            
            logger.info(f"Added region: {region_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add region {region_id}: {e}")
            return False
    
    def get_regions_by_poverty_level(self, level: str) -> List[str]:
        """
        Get regions by poverty level classification
        
        Args:
            level: 'high', 'medium', or 'low'
            
        Returns:
            List of region IDs
        """
        level_map = {
            'high': 'High_Poverty_Region',
            'medium': 'Medium_Poverty_Region',
            'low': 'Low_Poverty_Region'
        }
        
        category = level_map.get(level.lower())
        if not category:
            return []
        
        query = f"!(match &self (InheritanceLink $region {category}) $region)"
        return self.atomspace.query(query)
    
    # ===== Policy Knowledge =====
    
    def add_policy(self, policy_id: str, policy_data: Dict[str, Any]) -> bool:
        """
        Add a policy document to the knowledge base
        
        Args:
            policy_id: Unique policy identifier
            policy_data: Dictionary with policy information
            
        Returns:
            bool: Success status
            
        Example:
            add_policy('Policy_County_Act_2024', {
                'title': 'County Allocation Act 2024',
                'category': 'allocation',
                'effective_date': '2024-01-01'
            })
        """
        try:
            # Add policy as concept
            self.atomspace.add_node('ConceptNode', policy_id)
            self.atomspace.add_link('InheritanceLink', policy_id, 'Policy')
            
            # Add properties
            self.atomspace.add_concept_with_properties(policy_id, policy_data)
            
            logger.info(f"Added policy: {policy_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add policy {policy_id}: {e}")
            return False
    
    def add_policy_rule(self, rule_id: str, condition: str, 
                       action: str, confidence: float = 1.0) -> bool:
        """
        Add a policy rule expressing if-then logic
        
        Args:
            rule_id: Unique rule identifier
            condition: Condition expression
            action: Action to take
            confidence: Confidence in the rule (0.0 to 1.0)
            
        Returns:
            bool: Success status
            
        Example:
            add_policy_rule(
                'Rule_High_Poverty_Priority',
                'High_Poverty_Region',
                'High_Priority_Allocation',
                0.9
            )
        """
        try:
            rule_expr = f"(ImplicationLink {condition} {action})"
            self.atomspace.add_atom(rule_expr)
            logger.info(f"Added policy rule: {rule_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add policy rule {rule_id}: {e}")
            return False
    
    # ===== Data Source Knowledge =====
    
    def add_data_source(self, source_id: str, source_data: Dict[str, Any]) -> bool:
        """
        Add a data source (PDF, URL) to the knowledge base
        
        Args:
            source_id: Unique source identifier
            source_data: Dictionary with source information
            
        Returns:
            bool: Success status
            
        Example:
            add_data_source('Source_PDF_123', {
                'title': 'Poverty Impact Study',
                'type': 'pdf',
                'category': 'research',
                'topics': ['poverty', 'allocation', 'impact']
            })
        """
        try:
            # Add source as concept
            self.atomspace.add_node('ConceptNode', source_id)
            self.atomspace.add_link('InheritanceLink', source_id, 'DataSource')
            
            # Add properties
            self.atomspace.add_concept_with_properties(source_id, source_data)
            
            # Link to topics
            topics = source_data.get('topics', [])
            for topic in topics:
                topic_id = f"Topic_{topic.replace(' ', '_')}"
                self.atomspace.add_node('ConceptNode', topic_id)
                self.atomspace.add_link('ReferenceLink', source_id, topic_id)
            
            logger.info(f"Added data source: {source_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add data source {source_id}: {e}")
            return False
    
    def find_sources_for_topic(self, topic: str) -> List[str]:
        """
        Find data sources that reference a specific topic
        
        Args:
            topic: Topic to search for
            
        Returns:
            List of source IDs
        """
        topic_id = f"Topic_{topic.replace(' ', '_')}"
        query = f"!(match &self (ReferenceLink $source {topic_id}) $source)"
        return self.atomspace.query(query)
    
    # ===== Concept Relationships =====
    
    def add_concept_similarity(self, concept1: str, concept2: str, 
                              similarity: float) -> bool:
        """
        Add similarity relationship between two concepts
        
        Args:
            concept1: First concept
            concept2: Second concept
            similarity: Similarity score (0.0 to 1.0)
            
        Returns:
            bool: Success status
            
        Example:
            add_concept_similarity('Poverty', 'Economic_Hardship', 0.9)
        """
        return self.atomspace.add_link('SimilarityLink', concept1, concept2, similarity)
    
    def add_causal_relationship(self, cause: str, effect: str, 
                               strength: float = 1.0) -> bool:
        """
        Add causal relationship between concepts
        
        Args:
            cause: Cause concept
            effect: Effect concept
            strength: Strength of causation (0.0 to 1.0)
            
        Returns:
            bool: Success status
            
        Example:
            add_causal_relationship('High_Poverty', 'Requires_Allocation', 0.85)
        """
        causal_expr = f"(CausalLink {cause} {effect})"
        return self.atomspace.add_atom(causal_expr)
    
    # ===== Query and Retrieval =====
    
    def get_similar_concepts(self, concept: str, min_similarity: float = 0.7) -> List[tuple]:
        """
        Get concepts similar to the given concept
        
        Args:
            concept: Concept to find similarities for
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of (concept, similarity) tuples
        """
        return self.atomspace.get_related_concepts(concept)
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base
        
        Returns:
            Dictionary with statistics
        """
        base_stats = self.atomspace.get_stats()
        
        # Add domain-specific stats
        regions_query = "!(match &self (InheritanceLink $r Region) $r)"
        policies_query = "!(match &self (InheritanceLink $p Policy) $p)"
        sources_query = "!(match &self (InheritanceLink $s DataSource) $s)"
        
        base_stats.update({
            'regions': len(self.atomspace.query(regions_query)),
            'policies': len(self.atomspace.query(policies_query)),
            'data_sources': len(self.atomspace.query(sources_query)),
        })
        
        return base_stats
    
    # ===== Batch Operations =====
    
    def bulk_add_concepts(self, concepts: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Add multiple concepts in bulk
        
        Args:
            concepts: List of concept dictionaries with 'id' and 'data' keys
            
        Returns:
            Dictionary with success and failure counts
        """
        success_count = 0
        failure_count = 0
        
        for concept in concepts:
            concept_id = concept.get('id')
            concept_data = concept.get('data', {})
            
            if self.atomspace.add_concept_with_properties(concept_id, concept_data):
                success_count += 1
            else:
                failure_count += 1
        
        logger.info(f"Bulk add: {success_count} succeeded, {failure_count} failed")
        return {'success': success_count, 'failed': failure_count}
    
    def export_knowledge(self, filepath: str) -> bool:
        """Export knowledge to file"""
        return self.atomspace.export_knowledge(filepath)
    
    def import_knowledge(self, filepath: str) -> bool:
        """Import knowledge from file"""
        return self.atomspace.import_knowledge(filepath)


# Singleton instance
_knowledge_store_instance = None


def get_knowledge_store() -> KnowledgeStore:
    """
    Get the singleton KnowledgeStore instance
    
    Returns:
        KnowledgeStore instance
    """
    global _knowledge_store_instance
    if _knowledge_store_instance is None:
        _knowledge_store_instance = KnowledgeStore()
    return _knowledge_store_instance
