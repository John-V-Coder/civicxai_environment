"""
Knowledge Graph Visualizer
Generates visualization data for the knowledge graph
"""
import logging
from typing import Dict, List, Any, Set, Optional, Tuple
from cognitive.atoms.atomspace_manager import get_atomspace_manager
from cognitive.knowledge.knowledge_store import get_knowledge_store
from cognitive.pipline.causal_inference import get_causal_inference

logger = logging.getLogger(__name__)


class KnowledgeGraphVisualizer:
    """
    Creates visualization data for the knowledge graph
    """
    
    def __init__(self):
        """Initialize knowledge graph visualizer"""
        self.atomspace = get_atomspace_manager()
        self.knowledge = get_knowledge_store()
        self.causal = get_causal_inference()
        logger.info("Knowledge Graph Visualizer initialized")
    
    def generate_full_graph(self, max_nodes: int = 100) -> Dict[str, Any]:
        """
        Generate complete knowledge graph
        
        Args:
            max_nodes: Maximum number of nodes to include
            
        Returns:
            Graph data with nodes and edges
        """
        nodes = []
        edges = []
        node_ids = set()
        
        # Get all concepts
        concepts = self.atomspace.get_all_concepts()
        
        for concept in concepts[:max_nodes]:
            concept_id = str(concept).strip()
            if concept_id and concept_id not in node_ids:
                nodes.append({
                    'id': concept_id,
                    'label': concept_id,
                    'type': 'concept',
                    'size': 10,
                    'color': '#4A90E2'
                })
                node_ids.add(concept_id)
        
        # Add relationships
        for concept in concepts[:max_nodes]:
            concept_id = str(concept).strip()
            if not concept_id:
                continue
            
            # Find related concepts
            related = self.atomspace.get_related_concepts(concept_id, max_results=5)
            
            for rel in related:
                rel_id = str(rel).strip()
                if rel_id and rel_id in node_ids:
                    edges.append({
                        'from': concept_id,
                        'to': rel_id,
                        'type': 'similarity',
                        'color': '#95A5A6',
                        'width': 1
                    })
        
        # Add causal edges
        causal_graph = self.causal.get_causal_graph()
        for edge in causal_graph.get('edges', []):
            if edge['from'] in node_ids and edge['to'] in node_ids:
                edges.append({
                    'from': edge['from'],
                    'to': edge['to'],
                    'type': 'causal',
                    'strength': edge['strength'],
                    'color': '#E74C3C',
                    'width': 2 + edge['strength'] * 2
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'graph_type': 'full_knowledge_graph'
            }
        }
    
    def generate_subgraph(self, center_concept: str, 
                         depth: int = 2) -> Dict[str, Any]:
        """
        Generate subgraph around a central concept
        
        Args:
            center_concept: Central concept to expand from
            depth: How many hops to include
            
        Returns:
            Subgraph data
        """
        nodes = []
        edges = []
        visited = set()
        
        def explore(concept: str, current_depth: int):
            if current_depth > depth or concept in visited:
                return
            
            visited.add(concept)
            
            # Add node
            nodes.append({
                'id': concept,
                'label': concept,
                'type': 'concept',
                'depth': current_depth,
                'size': 15 - current_depth * 3,
                'color': self._get_depth_color(current_depth)
            })
            
            # Get related concepts
            related = self.atomspace.get_related_concepts(concept, max_results=5)
            
            for rel_concept in related:
                rel_id = str(rel_concept).strip()
                if rel_id:
                    edges.append({
                        'from': concept,
                        'to': rel_id,
                        'type': 'relationship',
                        'depth': current_depth
                    })
                    
                    if current_depth < depth:
                        explore(rel_id, current_depth + 1)
        
        explore(center_concept, 0)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'center': center_concept,
            'metadata': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'depth': depth,
                'graph_type': 'subgraph'
            }
        }
    
    def generate_causal_graph(self) -> Dict[str, Any]:
        """
        Generate visualization of causal relationships
        
        Returns:
            Causal graph data
        """
        causal_data = self.causal.get_causal_graph()
        
        nodes = []
        node_ids = set()
        
        # Create nodes from causal graph
        for node_id in causal_data['nodes']:
            if node_id not in node_ids:
                nodes.append({
                    'id': node_id,
                    'label': node_id,
                    'type': 'causal_variable',
                    'size': 12,
                    'color': '#E67E22'
                })
                node_ids.add(node_id)
        
        # Create directed edges
        edges = []
        for edge in causal_data['edges']:
            edges.append({
                'from': edge['from'],
                'to': edge['to'],
                'type': 'causal',
                'strength': edge['strength'],
                'confidence': edge['confidence'],
                'label': f"{edge['strength']:.2f}",
                'color': self._get_strength_color(edge['strength']),
                'width': 1 + edge['strength'] * 3,
                'arrows': 'to'
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'graph_type': 'causal_graph'
            }
        }
    
    def generate_domain_graph(self, domain: str = 'allocation') -> Dict[str, Any]:
        """
        Generate graph for a specific domain
        
        Args:
            domain: Domain to visualize (e.g., 'allocation', 'policy')
            
        Returns:
            Domain-specific graph
        """
        domain_keywords = {
            'allocation': ['poverty', 'priority', 'allocation', 'resource', 'funding'],
            'policy': ['policy', 'rule', 'regulation', 'guideline'],
            'environment': ['deforestation', 'environment', 'sustainability']
        }
        
        keywords = domain_keywords.get(domain, [])
        nodes = []
        edges = []
        node_ids = set()
        
        # Get concepts related to domain keywords
        for keyword in keywords:
            # Add keyword node
            if keyword not in node_ids:
                nodes.append({
                    'id': keyword,
                    'label': keyword.title(),
                    'type': 'domain_concept',
                    'size': 15,
                    'color': '#9B59B6'
                })
                node_ids.add(keyword)
            
            # Get related concepts
            related = self.atomspace.get_related_concepts(keyword)
            
            for rel in related[:5]:
                rel_id = str(rel).strip()
                if rel_id and rel_id not in node_ids:
                    nodes.append({
                        'id': rel_id,
                        'label': rel_id,
                        'type': 'related_concept',
                        'size': 10,
                        'color': '#BDC3C7'
                    })
                    node_ids.add(rel_id)
                
                if rel_id:
                    edges.append({
                        'from': keyword,
                        'to': rel_id,
                        'type': 'domain_relation'
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'domain': domain,
            'metadata': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'graph_type': 'domain_graph'
            }
        }
    
    def generate_reasoning_path_graph(self, start: str, end: str) -> Dict[str, Any]:
        """
        Visualize reasoning path from start to end
        
        Args:
            start: Starting concept
            end: Target concept
            
        Returns:
            Reasoning path graph
        """
        # Get causal chains
        chains = self.causal.infer_causal_chain(start, end)
        
        nodes = []
        edges = []
        node_ids = set()
        
        if chains:
            # Use first chain
            chain = chains[0]
            
            for i, concept in enumerate(chain):
                if concept not in node_ids:
                    nodes.append({
                        'id': concept,
                        'label': concept,
                        'type': 'reasoning_step',
                        'step': i,
                        'size': 15,
                        'color': self._get_step_color(i, len(chain))
                    })
                    node_ids.add(concept)
                
                if i < len(chain) - 1:
                    edges.append({
                        'from': concept,
                        'to': chain[i + 1],
                        'type': 'reasoning_step',
                        'step': i,
                        'arrows': 'to',
                        'color': '#3498DB',
                        'width': 3
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'path': chains[0] if chains else [],
            'metadata': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'graph_type': 'reasoning_path',
                'paths_found': len(chains)
            }
        }
    
    def _get_depth_color(self, depth: int) -> str:
        """Get color based on depth"""
        colors = ['#2ECC71', '#3498DB', '#9B59B6', '#E67E22', '#95A5A6']
        return colors[min(depth, len(colors) - 1)]
    
    def _get_strength_color(self, strength: float) -> str:
        """Get color based on causal strength"""
        if strength > 0.8:
            return '#E74C3C'  # Strong - red
        elif strength > 0.6:
            return '#E67E22'  # Medium - orange
        else:
            return '#F39C12'  # Weak - yellow
    
    def _get_step_color(self, step: int, total: int) -> str:
        """Get color based on reasoning step"""
        # Gradient from green (start) to blue (end)
        ratio = step / max(total - 1, 1)
        
        if ratio < 0.5:
            return '#2ECC71'  # Start - green
        elif ratio < 0.75:
            return '#3498DB'  # Middle - blue
        else:
            return '#9B59B6'  # End - purple
    
    def export_to_cytoscape(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export graph in Cytoscape.js format
        
        Args:
            graph_data: Graph data from any generate method
            
        Returns:
            Cytoscape.js formatted data
        """
        elements = []
        
        # Add nodes
        for node in graph_data['nodes']:
            elements.append({
                'group': 'nodes',
                'data': node
            })
        
        # Add edges
        for edge in graph_data['edges']:
            elements.append({
                'group': 'edges',
                'data': edge
            })
        
        return {
            'elements': elements,
            'style': self._get_cytoscape_style(),
            'layout': {'name': 'cose', 'animate': True}
        }
    
    def _get_cytoscape_style(self) -> List[Dict[str, Any]]:
        """Get Cytoscape.js stylesheet"""
        return [
            {
                'selector': 'node',
                'style': {
                    'label': 'data(label)',
                    'background-color': 'data(color)',
                    'width': 'data(size)',
                    'height': 'data(size)'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'width': 'data(width)',
                    'line-color': 'data(color)',
                    'target-arrow-color': 'data(color)',
                    'target-arrow-shape': 'data(arrows)',
                    'curve-style': 'bezier'
                }
            }
        ]


# Singleton instance
_kg_visualizer_instance = None


def get_kg_visualizer() -> KnowledgeGraphVisualizer:
    """
    Get singleton knowledge graph visualizer
    
    Returns:
        KnowledgeGraphVisualizer instance
    """
    global _kg_visualizer_instance
    if _kg_visualizer_instance is None:
        _kg_visualizer_instance = KnowledgeGraphVisualizer()
    return _kg_visualizer_instance
