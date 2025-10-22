"""
Causal Inference Engine
Discovers and reasons about causal relationships
"""
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from .pln_rules import TruthValue
from .atomspace_manager import get_atomspace_manager

logger = logging.getLogger(__name__)


@dataclass
class CausalRelation:
    """Represents a causal relationship"""
    cause: str
    effect: str
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    evidence: List[str]
    mechanism: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'cause': self.cause,
            'effect': self.effect,
            'strength': self.strength,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'mechanism': self.mechanism
        }


class CausalInferenceEngine:
    """
    Discovers and reasons about causal relationships
    """
    
    def __init__(self):
        """Initialize causal inference engine"""
        self.atomspace = get_atomspace_manager()
        self.causal_graph = {}  # cause -> [effects]
        self.observed_correlations = []
        logger.info("Causal Inference Engine initialized")
    
    def discover_causal_relations(self, data: List[Dict[str, Any]]) -> List[CausalRelation]:
        """
        Discover causal relations from observational data
        
        Args:
            data: List of observations with variables
            
        Returns:
            List of discovered causal relations
        """
        relations = []
        
        if len(data) < 3:
            logger.warning("Insufficient data for causal discovery")
            return relations
        
        # Get all variables
        variables = set()
        for observation in data:
            variables.update(observation.keys())
        
        # Check pairs of variables for potential causation
        for var1 in variables:
            for var2 in variables:
                if var1 != var2:
                    correlation = self._calculate_correlation(data, var1, var2)
                    
                    if abs(correlation) > 0.6:  # Threshold for potential causation
                        # Check temporal precedence if available
                        # For now, assume correlation suggests causation
                        strength = abs(correlation)
                        confidence = min(0.7, len(data) / 10.0)  # More data = higher confidence
                        
                        relations.append(
                            CausalRelation(
                                cause=var1,
                                effect=var2,
                                strength=strength,
                                confidence=confidence,
                                evidence=[f"Correlation: {correlation:.2f}"],
                                mechanism="Statistical association"
                            )
                        )
        
        logger.info(f"Discovered {len(relations)} potential causal relations")
        return relations
    
    def add_causal_relation(self, cause: str, effect: str, 
                           strength: float, confidence: float,
                           evidence: List[str] = None):
        """
        Add a known causal relation
        
        Args:
            cause: Cause variable
            effect: Effect variable
            strength: Causal strength
            confidence: Confidence in the relation
            evidence: Supporting evidence
        """
        if cause not in self.causal_graph:
            self.causal_graph[cause] = []
        
        self.causal_graph[cause].append({
            'effect': effect,
            'strength': strength,
            'confidence': confidence,
            'evidence': evidence or []
        })
        
        # Store in AtomSpace
        self.atomspace.add_node('ConceptNode', cause)
        self.atomspace.add_node('ConceptNode', effect)
        
        causal_expr = f"(CausalLink {cause} {effect})"
        self.atomspace.add_atom(causal_expr)
        
        logger.info(f"Added causal relation: {cause} → {effect} (strength: {strength:.2f})")
    
    def infer_causal_chain(self, start: str, end: str, 
                          max_depth: int = 5) -> List[List[str]]:
        """
        Find causal chains from start to end
        
        Args:
            start: Starting variable
            end: Target variable
            max_depth: Maximum chain length
            
        Returns:
            List of causal chains
        """
        chains = []
        visited = set()
        
        def dfs(current: str, target: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            
            if current == target:
                chains.append(path.copy())
                return
            
            if current in visited:
                return
            
            visited.add(current)
            
            # Get direct effects
            if current in self.causal_graph:
                for effect_info in self.causal_graph[current]:
                    effect = effect_info['effect']
                    if effect not in path:  # Avoid cycles
                        path.append(effect)
                        dfs(effect, target, path, depth + 1)
                        path.pop()
            
            visited.remove(current)
        
        dfs(start, end, [start], 0)
        
        logger.info(f"Found {len(chains)} causal chains from {start} to {end}")
        return chains
    
    def estimate_causal_effect(self, cause: str, effect: str,
                              intervention: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Estimate the causal effect of an intervention
        
        Args:
            cause: Cause variable
            effect: Effect variable
            intervention: Intervention values
            
        Returns:
            Estimated causal effect
        """
        # Find direct causal relation
        if cause in self.causal_graph:
            for effect_info in self.causal_graph[cause]:
                if effect_info['effect'] == effect:
                    base_strength = effect_info['strength']
                    confidence = effect_info['confidence']
                    
                    # Adjust based on intervention if provided
                    if intervention:
                        intervention_value = intervention.get(cause, 1.0)
                        adjusted_strength = base_strength * intervention_value
                    else:
                        adjusted_strength = base_strength
                    
                    return {
                        'cause': cause,
                        'effect': effect,
                        'estimated_effect': adjusted_strength,
                        'confidence': confidence,
                        'method': 'Direct causal relation'
                    }
        
        # Try to find indirect effect through causal chains
        chains = self.infer_causal_chain(cause, effect)
        
        if chains:
            # Estimate effect through shortest chain
            shortest_chain = min(chains, key=len)
            
            # Multiply strengths along the chain
            total_strength = 1.0
            min_confidence = 1.0
            
            for i in range(len(shortest_chain) - 1):
                c = shortest_chain[i]
                e = shortest_chain[i + 1]
                
                if c in self.causal_graph:
                    for effect_info in self.causal_graph[c]:
                        if effect_info['effect'] == e:
                            total_strength *= effect_info['strength']
                            min_confidence = min(min_confidence, effect_info['confidence'])
            
            return {
                'cause': cause,
                'effect': effect,
                'estimated_effect': total_strength,
                'confidence': min_confidence * 0.8,  # Reduce for indirect
                'method': f'Indirect through {len(shortest_chain)} steps',
                'chain': shortest_chain
            }
        
        return {
            'cause': cause,
            'effect': effect,
            'estimated_effect': 0.0,
            'confidence': 0.0,
            'method': 'No causal path found'
        }
    
    def counterfactual_reasoning(self, actual_outcome: Dict[str, Any],
                                 counterfactual_intervention: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reason about counterfactual scenarios
        
        Args:
            actual_outcome: What actually happened
            counterfactual_intervention: What if this had been different
            
        Returns:
            Counterfactual analysis
        """
        results = {}
        
        for cause, new_value in counterfactual_intervention.items():
            actual_value = actual_outcome.get(cause)
            
            if actual_value is None:
                continue
            
            # Find effects of this cause
            if cause in self.causal_graph:
                for effect_info in self.causal_graph[cause]:
                    effect = effect_info['effect']
                    strength = effect_info['strength']
                    
                    # Estimate counterfactual effect
                    if isinstance(actual_value, (int, float)) and isinstance(new_value, (int, float)):
                        value_change = new_value - actual_value
                        effect_change = value_change * strength
                        
                        actual_effect_value = actual_outcome.get(effect, 0)
                        counterfactual_value = actual_effect_value + effect_change
                        
                        results[effect] = {
                            'actual': actual_effect_value,
                            'counterfactual': counterfactual_value,
                            'change': effect_change,
                            'confidence': effect_info['confidence']
                        }
        
        return {
            'intervention': counterfactual_intervention,
            'effects': results
        }
    
    def explain_with_causality(self, outcome: str, 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain an outcome using causal reasoning
        
        Args:
            outcome: Outcome to explain
            context: Context variables
            
        Returns:
            Causal explanation
        """
        explanations = []
        
        # Find all causes that could lead to this outcome
        for cause, effects in self.causal_graph.items():
            for effect_info in effects:
                if effect_info['effect'] == outcome:
                    # Check if cause is present in context
                    cause_value = context.get(cause)
                    
                    if cause_value:
                        explanations.append({
                            'cause': cause,
                            'strength': effect_info['strength'],
                            'confidence': effect_info['confidence'],
                            'evidence': effect_info['evidence'],
                            'value': cause_value
                        })
        
        # Sort by strength * confidence
        explanations.sort(key=lambda x: x['strength'] * x['confidence'], reverse=True)
        
        return {
            'outcome': outcome,
            'explanations': explanations,
            'primary_cause': explanations[0] if explanations else None
        }
    
    def _calculate_correlation(self, data: List[Dict[str, Any]], 
                              var1: str, var2: str) -> float:
        """Calculate correlation between two variables"""
        values1, values2 = [], []
        
        for observation in data:
            if var1 in observation and var2 in observation:
                v1, v2 = observation[var1], observation[var2]
                if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                    values1.append(v1)
                    values2.append(v2)
        
        if len(values1) < 2:
            return 0.0
        
        # Simple correlation calculation
        mean1 = sum(values1) / len(values1)
        mean2 = sum(values2) / len(values2)
        
        numerator = sum((v1 - mean1) * (v2 - mean2) for v1, v2 in zip(values1, values2))
        denom1 = sum((v1 - mean1) ** 2 for v1 in values1) ** 0.5
        denom2 = sum((v2 - mean2) ** 2 for v2 in values2) ** 0.5
        
        if denom1 == 0 or denom2 == 0:
            return 0.0
        
        return numerator / (denom1 * denom2)
    
    def get_causal_graph(self) -> Dict[str, Any]:
        """Get the complete causal graph"""
        return {
            'nodes': list(set(list(self.causal_graph.keys()) + 
                            [e['effect'] for effects in self.causal_graph.values() for e in effects])),
            'edges': [
                {
                    'from': cause,
                    'to': effect_info['effect'],
                    'strength': effect_info['strength'],
                    'confidence': effect_info['confidence']
                }
                for cause, effects in self.causal_graph.items()
                for effect_info in effects
            ]
        }


# Singleton instance
_causal_inference_instance = None


def get_causal_inference() -> CausalInferenceEngine:
    """
    Get singleton causal inference engine
    
    Returns:
        CausalInferenceEngine instance
    """
    global _causal_inference_instance
    if _causal_inference_instance is None:
        _causal_inference_instance = CausalInferenceEngine()
    return _causal_inference_instance
