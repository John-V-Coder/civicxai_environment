"""
PLN (Probabilistic Logic Networks) Rules Engine
Implements reasoning rules with confidence scores
"""
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TruthValue:
    """
    Truth value with strength and confidence
    Based on PLN truth value semantics
    """
    strength: float  # 0.0 to 1.0 (how true is it)
    confidence: float  # 0.0 to 1.0 (how confident are we)
    
    def __str__(self):
        return f"TV({self.strength:.3f}, {self.confidence:.3f})"
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high confidence truth value"""
        return self.confidence > 0.7
    
    @property
    def is_strong(self) -> bool:
        """Check if this is a strong truth value"""
        return self.strength > 0.7


class PLNRulesEngine:
    """
    Probabilistic Logic Networks rules for reasoning
    Implements basic PLN inference rules
    """
    
    def __init__(self):
        """Initialize PLN rules engine"""
        self.rules = {}
        self._initialize_rules()
        logger.info("PLN Rules Engine initialized")
    
    def _initialize_rules(self):
        """Initialize basic PLN rules"""
        # Domain-specific rules for CivicXAI
        self.rules = {
            'poverty_implies_priority': {
                'condition': 'High_Poverty_Region',
                'conclusion': 'High_Priority',
                'truth_value': TruthValue(0.85, 0.90),
                'description': 'High poverty regions get high priority'
            },
            'impact_boosts_priority': {
                'condition': 'High_Impact_Project',
                'conclusion': 'Increased_Priority',
                'truth_value': TruthValue(0.80, 0.85),
                'description': 'High impact projects boost priority'
            },
            'corruption_reduces_allocation': {
                'condition': 'High_Corruption_Risk',
                'conclusion': 'Reduced_Allocation',
                'truth_value': TruthValue(0.75, 0.80),
                'description': 'High corruption risk reduces allocation'
            },
            'deforestation_needs_intervention': {
                'condition': 'High_Deforestation',
                'conclusion': 'Environmental_Intervention_Needed',
                'truth_value': TruthValue(0.80, 0.85),
                'description': 'High deforestation requires intervention'
            }
        }
    
    def deduction(self, premise1_tv: TruthValue, premise2_tv: TruthValue) -> TruthValue:
        """
        PLN Deduction Rule: (A→B) ∧ (B→C) ⊢ (A→C)
        
        Args:
            premise1_tv: Truth value of first premise
            premise2_tv: Truth value of second premise
            
        Returns:
            Truth value of conclusion
        """
        # Simplified PLN deduction formula
        strength = premise1_tv.strength * premise2_tv.strength
        confidence = min(premise1_tv.confidence, premise2_tv.confidence) * 0.9
        
        return TruthValue(strength, confidence)
    
    def abduction(self, implication_tv: TruthValue, consequent_tv: TruthValue) -> TruthValue:
        """
        PLN Abduction Rule: (A→B) ∧ B ⊢ A
        
        Args:
            implication_tv: Truth value of A→B
            consequent_tv: Truth value of B
            
        Returns:
            Truth value of A (hypothesis)
        """
        # Simplified PLN abduction
        strength = implication_tv.strength * consequent_tv.strength * 0.8
        confidence = min(implication_tv.confidence, consequent_tv.confidence) * 0.7
        
        return TruthValue(strength, confidence)
    
    def induction(self, instances: List[TruthValue]) -> TruthValue:
        """
        PLN Induction Rule: multiple instances → generalization
        
        Args:
            instances: List of truth values from instances
            
        Returns:
            Truth value of generalization
        """
        if not instances:
            return TruthValue(0.5, 0.0)
        
        # Average strength, increase confidence with more instances
        avg_strength = sum(tv.strength for tv in instances) / len(instances)
        confidence = min(0.9, len(instances) / 10.0)  # More instances = higher confidence
        
        return TruthValue(avg_strength, confidence)
    
    def conjunction(self, tv1: TruthValue, tv2: TruthValue) -> TruthValue:
        """
        PLN Conjunction: A ∧ B
        
        Args:
            tv1: Truth value of A
            tv2: Truth value of B
            
        Returns:
            Truth value of A ∧ B
        """
        strength = tv1.strength * tv2.strength
        confidence = min(tv1.confidence, tv2.confidence)
        
        return TruthValue(strength, confidence)
    
    def disjunction(self, tv1: TruthValue, tv2: TruthValue) -> TruthValue:
        """
        PLN Disjunction: A ∨ B
        
        Args:
            tv1: Truth value of A
            tv2: Truth value of B
            
        Returns:
            Truth value of A ∨ B
        """
        strength = tv1.strength + tv2.strength - (tv1.strength * tv2.strength)
        confidence = min(tv1.confidence, tv2.confidence)
        
        return TruthValue(strength, confidence)
    
    def negation(self, tv: TruthValue) -> TruthValue:
        """
        PLN Negation: ¬A
        
        Args:
            tv: Truth value of A
            
        Returns:
            Truth value of ¬A
        """
        return TruthValue(1.0 - tv.strength, tv.confidence)
    
    def apply_rule(self, rule_name: str, evidence: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Apply a specific PLN rule
        
        Args:
            rule_name: Name of the rule to apply
            evidence: Evidence data
            
        Returns:
            Reasoning result with conclusion and truth value
        """
        if rule_name not in self.rules:
            logger.warning(f"Rule '{rule_name}' not found")
            return None
        
        rule = self.rules[rule_name]
        
        # Check if condition is met in evidence
        condition_met = evidence.get(rule['condition'], False)
        
        if condition_met:
            return {
                'rule': rule_name,
                'condition': rule['condition'],
                'conclusion': rule['conclusion'],
                'truth_value': rule['truth_value'],
                'description': rule['description'],
                'applied': True
            }
        
        return {
            'rule': rule_name,
            'condition': rule['condition'],
            'applied': False,
            'reason': 'Condition not met in evidence'
        }
    
    def multi_hop_reasoning(self, start: str, goal: str, 
                           knowledge: Dict[str, TruthValue]) -> Optional[List[Dict[str, Any]]]:
        """
        Multi-hop reasoning from start to goal
        
        Args:
            start: Starting concept
            goal: Goal concept
            knowledge: Knowledge base with truth values
            
        Returns:
            Reasoning chain if path found
        """
        # Simple breadth-first search for reasoning path
        # In production, this would use proper PLN inference
        
        if start == goal:
            return [{
                'step': 1,
                'from': start,
                'to': goal,
                'truth_value': knowledge.get(start, TruthValue(1.0, 1.0)),
                'reasoning': 'Direct match'
            }]
        
        # Check for direct implication
        implication_key = f"{start}→{goal}"
        if implication_key in knowledge:
            return [{
                'step': 1,
                'from': start,
                'to': goal,
                'truth_value': knowledge[implication_key],
                'reasoning': 'Direct implication'
            }]
        
        # For now, return None (full implementation would do graph search)
        return None
    
    def explain_with_confidence(self, conclusion: str, 
                               evidence: List[Tuple[str, TruthValue]]) -> Dict[str, Any]:
        """
        Generate explanation with confidence scoring
        
        Args:
            conclusion: The conclusion reached
            evidence: List of (fact, truth_value) tuples
            
        Returns:
            Explanation with overall confidence
        """
        if not evidence:
            return {
                'conclusion': conclusion,
                'confidence': TruthValue(0.5, 0.0),
                'evidence': [],
                'explanation': 'No evidence provided'
            }
        
        # Calculate overall confidence using conjunction
        overall_tv = evidence[0][1]
        for _, tv in evidence[1:]:
            overall_tv = self.conjunction(overall_tv, tv)
        
        explanation_parts = []
        for fact, tv in evidence:
            conf_level = "high" if tv.is_high_confidence else "medium" if tv.confidence > 0.5 else "low"
            explanation_parts.append(f"{fact} (confidence: {conf_level}, {tv})")
        
        return {
            'conclusion': conclusion,
            'confidence': overall_tv,
            'evidence_count': len(evidence),
            'evidence': [
                {
                    'fact': fact,
                    'truth_value': {'strength': tv.strength, 'confidence': tv.confidence},
                    'confidence_level': "high" if tv.is_high_confidence else "medium" if tv.confidence > 0.5 else "low"
                }
                for fact, tv in evidence
            ],
            'explanation': ' AND '.join(explanation_parts),
            'overall_confidence_level': "high" if overall_tv.is_high_confidence else "medium" if overall_tv.confidence > 0.5 else "low"
        }
    
    def get_all_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get all available rules"""
        return self.rules
    
    def add_rule(self, rule_name: str, condition: str, conclusion: str, 
                truth_value: TruthValue, description: str = ""):
        """
        Add a new rule to the engine
        
        Args:
            rule_name: Unique name for the rule
            condition: Condition that triggers the rule
            conclusion: Conclusion if condition is met
            truth_value: Truth value of the rule
            description: Human-readable description
        """
        self.rules[rule_name] = {
            'condition': condition,
            'conclusion': conclusion,
            'truth_value': truth_value,
            'description': description or f"{condition} implies {conclusion}"
        }
        logger.info(f"Added rule: {rule_name}")


# Singleton instance
_pln_engine_instance = None


def get_pln_engine() -> PLNRulesEngine:
    """
    Get singleton PLN engine instance
    
    Returns:
        PLNRulesEngine instance
    """
    global _pln_engine_instance
    if _pln_engine_instance is None:
        _pln_engine_instance = PLNRulesEngine()
    return _pln_engine_instance
