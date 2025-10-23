"""
Advanced PLN Reasoning Engine
Full implementation with forward/backward chaining and inference control
"""
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from cognitive.pln.pln_rules import TruthValue, get_pln_engine
from cognitive.atoms.atomspace_manager import get_atomspace_manager

logger = logging.getLogger(__name__)


@dataclass
class InferenceResult:
    """Result of an inference operation"""
    conclusion: str
    truth_value: TruthValue
    inference_path: List[str]
    premises_used: List[str]
    rules_applied: List[str]
    depth: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'conclusion': self.conclusion,
            'truth_value': {
                'strength': self.truth_value.strength,
                'confidence': self.truth_value.confidence
            },
            'inference_path': self.inference_path,
            'premises_used': self.premises_used,
            'rules_applied': self.rules_applied,
            'depth': self.depth
        }


class AdvancedPLNEngine:
    """
    Advanced PLN reasoning with forward and backward chaining
    """
    
    def __init__(self):
        """Initialize advanced PLN engine"""
        self.pln_engine = get_pln_engine()
        self.atomspace = get_atomspace_manager()
        self.inference_cache = {}
        self.max_depth = 5
        logger.info("Advanced PLN Engine initialized")
    
    def forward_chaining(self, premises: List[Tuple[str, TruthValue]], 
                        max_steps: int = 10) -> List[InferenceResult]:
        """
        Forward chaining: Start from premises and infer conclusions
        
        Args:
            premises: List of (premise, truth_value) tuples
            max_steps: Maximum inference steps
            
        Returns:
            List of inference results
        """
        results = []
        working_set = {p[0]: p[1] for p in premises}
        
        for step in range(max_steps):
            new_inferences = []
            
            # Try to apply rules to current working set
            for rule_name, rule in self.pln_engine.get_all_rules().items():
                condition = rule['condition']
                
                if condition in working_set:
                    # Apply rule
                    premise_tv = working_set[condition]
                    rule_tv = rule['truth_value']
                    
                    # Deduction: premise + rule → conclusion
                    conclusion_tv = self.pln_engine.deduction(premise_tv, rule_tv)
                    conclusion = rule['conclusion']
                    
                    if conclusion not in working_set:
                        new_inferences.append(
                            InferenceResult(
                                conclusion=conclusion,
                                truth_value=conclusion_tv,
                                inference_path=[condition, conclusion],
                                premises_used=[condition],
                                rules_applied=[rule_name],
                                depth=step + 1
                            )
                        )
                        working_set[conclusion] = conclusion_tv
            
            if new_inferences:
                results.extend(new_inferences)
            else:
                break  # No new inferences
        
        logger.info(f"Forward chaining produced {len(results)} inferences")
        return results
    
    def backward_chaining(self, goal: str, 
                         known_facts: Dict[str, TruthValue],
                         max_depth: int = 5) -> Optional[InferenceResult]:
        """
        Backward chaining: Start from goal and find supporting premises
        
        Args:
            goal: Target conclusion to prove
            known_facts: Dictionary of known facts with truth values
            max_depth: Maximum recursion depth
            
        Returns:
            Inference result if goal is proven
        """
        # Check if goal is already known
        if goal in known_facts:
            return InferenceResult(
                conclusion=goal,
                truth_value=known_facts[goal],
                inference_path=[goal],
                premises_used=[],
                rules_applied=[],
                depth=0
            )
        
        # Try to find rules that conclude the goal
        for rule_name, rule in self.pln_engine.get_all_rules().items():
            if rule['conclusion'] == goal:
                condition = rule['condition']
                
                # Recursively try to prove condition
                if max_depth > 0:
                    sub_result = self.backward_chaining(condition, known_facts, max_depth - 1)
                    
                    if sub_result:
                        # Apply rule
                        rule_tv = rule['truth_value']
                        conclusion_tv = self.pln_engine.deduction(sub_result.truth_value, rule_tv)
                        
                        return InferenceResult(
                            conclusion=goal,
                            truth_value=conclusion_tv,
                            inference_path=sub_result.inference_path + [goal],
                            premises_used=sub_result.premises_used + [condition],
                            rules_applied=sub_result.rules_applied + [rule_name],
                            depth=sub_result.depth + 1
                        )
        
        return None
    
    def abductive_reasoning(self, observation: str, 
                           possible_causes: List[str],
                           known_facts: Dict[str, TruthValue]) -> List[InferenceResult]:
        """
        Abductive reasoning: Find best explanations for an observation
        
        Args:
            observation: Observed fact
            possible_causes: List of possible causes
            known_facts: Known facts
            
        Returns:
            List of explanations ranked by plausibility
        """
        explanations = []
        
        for cause in possible_causes:
            # Check if cause could lead to observation
            rules = self.pln_engine.get_all_rules()
            
            for rule_name, rule in rules.items():
                if rule['condition'] == cause and rule['conclusion'] == observation:
                    # Found a potential explanation
                    rule_tv = rule['truth_value']
                    
                    # Abduction: observation + rule → cause (hypothesis)
                    obs_tv = known_facts.get(observation, TruthValue(1.0, 0.8))
                    cause_tv = self.pln_engine.abduction(rule_tv, obs_tv)
                    
                    explanations.append(
                        InferenceResult(
                            conclusion=cause,
                            truth_value=cause_tv,
                            inference_path=[observation, cause],
                            premises_used=[observation],
                            rules_applied=[rule_name],
                            depth=1
                        )
                    )
        
        # Sort by truth value strength
        explanations.sort(key=lambda x: x.truth_value.strength, reverse=True)
        
        logger.info(f"Abductive reasoning found {len(explanations)} explanations")
        return explanations
    
    def analogical_reasoning(self, source_case: Dict[str, Any],
                            target_case: Dict[str, Any]) -> Optional[InferenceResult]:
        """
        Analogical reasoning: Transfer knowledge from similar cases
        
        Args:
            source_case: Known case with solution
            target_case: New case needing solution
            
        Returns:
            Inferred solution for target case
        """
        # Calculate similarity between cases
        similarity = self._calculate_similarity(source_case, target_case)
        
        if similarity > 0.7:  # Threshold for analogical inference
            # Transfer solution with confidence based on similarity
            source_solution = source_case.get('solution')
            
            if source_solution:
                tv = TruthValue(0.8, similarity)
                
                return InferenceResult(
                    conclusion=f"Solution_for_{target_case.get('id', 'target')}",
                    truth_value=tv,
                    inference_path=[f"Similar_to_{source_case.get('id', 'source')}"],
                    premises_used=[str(source_case)],
                    rules_applied=['Analogical_Transfer'],
                    depth=1
                )
        
        return None
    
    def _calculate_similarity(self, case1: Dict[str, Any], case2: Dict[str, Any]) -> float:
        """Calculate similarity between two cases"""
        common_features = set(case1.keys()) & set(case2.keys())
        
        if not common_features:
            return 0.0
        
        similarities = []
        for feature in common_features:
            v1, v2 = case1[feature], case2[feature]
            
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                # Numeric similarity
                max_val = max(abs(v1), abs(v2), 1.0)
                sim = 1.0 - abs(v1 - v2) / max_val
                similarities.append(sim)
            elif v1 == v2:
                # Exact match
                similarities.append(1.0)
            else:
                similarities.append(0.0)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def probabilistic_inference(self, evidence: Dict[str, TruthValue],
                               query: str) -> TruthValue:
        """
        Probabilistic inference using PLN
        
        Args:
            evidence: Dictionary of evidence with truth values
            query: Query variable
            
        Returns:
            Probability distribution for query
        """
        # Simplified probabilistic inference
        # In full PLN, this would use PLN probabilistic formulas
        
        relevant_evidence = []
        for fact, tv in evidence.items():
            if query.lower() in fact.lower():
                relevant_evidence.append(tv)
        
        if relevant_evidence:
            # Combine evidence using conjunction
            combined_tv = relevant_evidence[0]
            for tv in relevant_evidence[1:]:
                combined_tv = self.pln_engine.conjunction(combined_tv, tv)
            return combined_tv
        
        # Default uncertain
        return TruthValue(0.5, 0.1)
    
    def clear_cache(self):
        """Clear inference cache"""
        self.inference_cache.clear()
        logger.info("Inference cache cleared")


# Singleton instance
_advanced_pln_instance = None


def get_advanced_pln() -> AdvancedPLNEngine:
    """
    Get singleton advanced PLN engine
    
    Returns:
        AdvancedPLNEngine instance
    """
    global _advanced_pln_instance
    if _advanced_pln_instance is None:
        _advanced_pln_instance = AdvancedPLNEngine()
    return _advanced_pln_instance
