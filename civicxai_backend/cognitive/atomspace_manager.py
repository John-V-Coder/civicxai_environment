"""
AtomSpace Manager
Handles connection and basic operations with OpenCog's AtomSpace
"""
import logging
from typing import Optional, List, Dict, Any
from hyperon import *

logger = logging.getLogger(__name__)


class AtomSpaceManager:
    """
    Manages the MeTTa/Hyperon AtomSpace instance
    Provides high-level interface for atom operations
    """
    
    def __init__(self):
        """Initialize AtomSpace instance"""
        self.metta = MeTTa()
        self.atomspace = self.metta.space()
        logger.info("AtomSpace initialized successfully")
    
    def add_atom(self, atom_expr: str) -> bool:
        """
        Add an atom expression to the AtomSpace
        
        Args:
            atom_expr: MeTTa expression as string
            
        Returns:
            bool: Success status
            
        Example:
            add_atom("(: Region_Nairobi ConceptNode)")
        """
        try:
            result = self.metta.run(atom_expr)
            logger.debug(f"Added atom: {atom_expr}")
            return True
        except Exception as e:
            logger.error(f"Failed to add atom: {atom_expr}, Error: {e}")
            return False
    
    def add_node(self, node_type: str, node_name: str) -> bool:
        """
        Add a simple node to AtomSpace
        
        Args:
            node_type: Type of node (e.g., 'ConceptNode', 'PredicateNode')
            node_name: Name/identifier of the node
            
        Returns:
            bool: Success status
            
        Example:
            add_node('ConceptNode', 'Poverty')
        """
        atom_expr = f"(: {node_name} {node_type})"
        return self.add_atom(atom_expr)
    
    def add_link(self, link_type: str, source: str, target: str, 
                 confidence: float = 1.0) -> bool:
        """
        Add a link between two atoms
        
        Args:
            link_type: Type of link (e.g., 'InheritanceLink', 'SimilarityLink')
            source: Source node name
            target: Target node name
            confidence: Confidence value (0.0 to 1.0)
            
        Returns:
            bool: Success status
            
        Example:
            add_link('SimilarityLink', 'Poverty', 'Economic_Hardship', 0.9)
        """
        # MeTTa style link with confidence
        atom_expr = f"({link_type} {source} {target})"
        return self.add_atom(atom_expr)
    
    def query(self, query_expr: str) -> List[str]:
        """
        Execute a query against the AtomSpace
        
        Args:
            query_expr: MeTTa query expression
            
        Returns:
            List of matching results
            
        Example:
            query("(match &self (SimilarityLink Poverty $x) $x)")
        """
        try:
            results = self.metta.run(query_expr)
            return [str(r) for r in results]
        except Exception as e:
            logger.error(f"Query failed: {query_expr}, Error: {e}")
            return []
    
    def get_related_concepts(self, concept: str, max_results: int = 5) -> List[str]:
        """
        Find concepts related to the given concept
        
        Args:
            concept: Concept to find relations for
            max_results: Maximum number of results to return
            
        Returns:
            List of related concept names
        """
        # Query for similarity links
        query = f"!(match &self (SimilarityLink {concept} $x) $x)"
        results = self.query(query)
        return results[:max_results]
    
    def add_concept_with_properties(self, concept_name: str, 
                                    properties: Dict[str, Any]) -> bool:
        """
        Add a concept node with associated properties
        
        Args:
            concept_name: Name of the concept
            properties: Dictionary of property key-value pairs
            
        Returns:
            bool: Success status
            
        Example:
            add_concept_with_properties('Region_Nairobi', {
                'poverty_index': 0.8,
                'type': 'coastal',
                'population': 4500000
            })
        """
        try:
            # Add the main concept node
            self.add_node('ConceptNode', concept_name)
            
            # Add properties as evaluations
            for prop_name, prop_value in properties.items():
                prop_expr = f"(= ({prop_name} {concept_name}) {prop_value})"
                self.add_atom(prop_expr)
            
            logger.info(f"Added concept {concept_name} with {len(properties)} properties")
            return True
        except Exception as e:
            logger.error(f"Failed to add concept: {e}")
            return False
    
    def get_all_concepts(self) -> List[str]:
        """
        Retrieve all concept nodes in the AtomSpace
        
        Returns:
            List of concept names
        """
        query = "!(match &self (: $concept ConceptNode) $concept)"
        return self.query(query)
    
    def clear_atomspace(self) -> bool:
        """
        Clear all atoms from the AtomSpace
        WARNING: This will delete all knowledge!
        
        Returns:
            bool: Success status
        """
        try:
            # Create new instance
            self.metta = MeTTa()
            self.atomspace = self.metta.space()
            logger.warning("AtomSpace cleared - all knowledge deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to clear AtomSpace: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the AtomSpace
        
        Returns:
            Dictionary with statistics
        """
        concepts = self.get_all_concepts()
        
        return {
            'total_concepts': len(concepts),
            'status': 'active',
            'backend': 'Hyperon/MeTTa'
        }
    
    def export_knowledge(self, filepath: str) -> bool:
        """
        Export AtomSpace knowledge to a file
        
        Args:
            filepath: Path to save the knowledge
            
        Returns:
            bool: Success status
        """
        try:
            concepts = self.get_all_concepts()
            with open(filepath, 'w') as f:
                for concept in concepts:
                    f.write(f"{concept}\n")
            logger.info(f"Exported knowledge to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export knowledge: {e}")
            return False
    
    def import_knowledge(self, filepath: str) -> bool:
        """
        Import knowledge from a file
        
        Args:
            filepath: Path to the knowledge file
            
        Returns:
            bool: Success status
        """
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    self.add_atom(line.strip())
            logger.info(f"Imported knowledge from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to import knowledge: {e}")
            return False


# Singleton instance
_atomspace_manager_instance = None


def get_atomspace_manager() -> AtomSpaceManager:
    """
    Get the singleton AtomSpace manager instance
    
    Returns:
        AtomSpaceManager instance
    """
    global _atomspace_manager_instance
    if _atomspace_manager_instance is None:
        _atomspace_manager_instance = AtomSpaceManager()
    return _atomspace_manager_instance
