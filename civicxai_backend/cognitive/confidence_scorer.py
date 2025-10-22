"""
Confidence Scoring System
Calculates confidence scores for reasoning and decisions
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .pln_rules import TruthValue, get_pln_engine

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceScore:
    """Confidence score with breakdown"""
    overall_score: float  # 0.0 to 1.0
    level: str  # 'very_high', 'high', 'medium', 'low', 'very_low'
    components: Dict[str, float]  # Individual confidence components
    explanation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'overall_score': round(self.overall_score, 3),
            'level': self.level,
            'percentage': round(self.overall_score * 100, 1),
            'components': {k: round(v, 3) for k, v in self.components.items()},
            'explanation': self.explanation
        }


class ConfidenceScorer:
    """
    Calculates confidence scores for reasoning results
    """
    
    def __init__(self):
        """Initialize confidence scorer"""
        self.pln_engine = get_pln_engine()
        logger.info("Confidence Scorer initialized")
    
    def score_reasoning_chain(self, chain: List[Dict[str, Any]]) -> ConfidenceScore:
        """
        Score a reasoning chain's confidence
        
        Args:
            chain: List of reasoning steps
            
        Returns:
            Confidence score
        """
        if not chain:
            return ConfidenceScore(
                overall_score=0.0,
                level='very_low',
                components={'chain_length': 0.0},
                explanation='No reasoning chain provided'
            )
        
        components = {}
        
        # 1. Chain length factor (shorter is better)
        chain_length = len(chain)
        if chain_length == 1:
            components['chain_length'] = 1.0
        elif chain_length <= 3:
            components['chain_length'] = 0.9
        elif chain_length <= 5:
            components['chain_length'] = 0.7
        else:
            components['chain_length'] = 0.5
        
        # 2. Truth value confidence (average of all steps)
        if 'truth_value' in chain[0]:
            avg_confidence = sum(
                step.get('truth_value', TruthValue(0.5, 0.5)).confidence 
                for step in chain if 'truth_value' in step
            ) / len(chain)
            components['truth_values'] = avg_confidence
        else:
            components['truth_values'] = 0.7  # Default
        
        # 3. Evidence quality
        evidence_count = sum(1 for step in chain if step.get('evidence'))
        if evidence_count > 0:
            components['evidence'] = min(1.0, evidence_count / len(chain))
        else:
            components['evidence'] = 0.5
        
        # Calculate overall score (weighted average)
        weights = {'chain_length': 0.3, 'truth_values': 0.5, 'evidence': 0.2}
        overall = sum(components[k] * weights.get(k, 0.33) for k in components)
        
        return ConfidenceScore(
            overall_score=overall,
            level=self._get_confidence_level(overall),
            components=components,
            explanation=self._generate_explanation(overall, components, chain_length)
        )
    
    def score_evidence(self, evidence: List[Dict[str, Any]]) -> ConfidenceScore:
        """
        Score evidence quality
        
        Args:
            evidence: List of evidence items
            
        Returns:
            Confidence score
        """
        if not evidence:
            return ConfidenceScore(
                overall_score=0.0,
                level='very_low',
                components={'evidence_count': 0.0},
                explanation='No evidence provided'
            )
        
        components = {}
        
        # 1. Evidence quantity
        evidence_count = len(evidence)
        if evidence_count >= 5:
            components['quantity'] = 1.0
        elif evidence_count >= 3:
            components['quantity'] = 0.8
        elif evidence_count >= 1:
            components['quantity'] = 0.6
        else:
            components['quantity'] = 0.3
        
        # 2. Evidence diversity (different types)
        types = set(e.get('type', 'unknown') for e in evidence)
        components['diversity'] = min(1.0, len(types) / 3.0)
        
        # 3. Evidence relevance (average)
        if any('relevance' in e for e in evidence):
            avg_relevance = sum(e.get('relevance', 0.5) for e in evidence) / len(evidence)
            components['relevance'] = avg_relevance
        else:
            components['relevance'] = 0.7
        
        # Calculate overall
        overall = sum(components.values()) / len(components)
        
        return ConfidenceScore(
            overall_score=overall,
            level=self._get_confidence_level(overall),
            components=components,
            explanation=f"Based on {evidence_count} evidence items from {len(types)} different sources"
        )
    
    def score_decision(self, decision: Dict[str, Any]) -> ConfidenceScore:
        """
        Score a decision's confidence
        
        Args:
            decision: Decision data with reasoning
            
        Returns:
            Confidence score
        """
        components = {}
        
        # 1. Data completeness
        required_fields = ['reasoning', 'evidence', 'alternatives']
        present_fields = sum(1 for field in required_fields if field in decision)
        components['data_completeness'] = present_fields / len(required_fields)
        
        # 2. Reasoning quality
        reasoning = decision.get('reasoning', {})
        if isinstance(reasoning, dict):
            reasoning_steps = len(reasoning.get('chain', []))
            components['reasoning_quality'] = min(1.0, reasoning_steps / 3.0)
        else:
            components['reasoning_quality'] = 0.5
        
        # 3. Evidence support
        evidence = decision.get('evidence', [])
        if evidence:
            evidence_score = self.score_evidence(evidence)
            components['evidence_support'] = evidence_score.overall_score
        else:
            components['evidence_support'] = 0.3
        
        # 4. Consensus (if available)
        if 'consensus' in decision:
            components['consensus'] = decision['consensus']
        
        # Calculate overall
        overall = sum(components.values()) / len(components)
        
        return ConfidenceScore(
            overall_score=overall,
            level=self._get_confidence_level(overall),
            components=components,
            explanation=self._generate_decision_explanation(overall, components)
        )
    
    def score_from_truth_value(self, tv: TruthValue) -> ConfidenceScore:
        """
        Convert PLN truth value to confidence score
        
        Args:
            tv: Truth value
            
        Returns:
            Confidence score
        """
        # Combine strength and confidence
        overall = (tv.strength + tv.confidence) / 2.0
        
        return ConfidenceScore(
            overall_score=overall,
            level=self._get_confidence_level(overall),
            components={
                'strength': tv.strength,
                'confidence': tv.confidence
            },
            explanation=f"Truth value: strength={tv.strength:.2f}, confidence={tv.confidence:.2f}"
        )
    
    def compare_alternatives(self, alternatives: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple alternatives and rank by confidence
        
        Args:
            alternatives: List of alternative decisions/conclusions
            
        Returns:
            Ranked alternatives with confidence scores
        """
        scored_alternatives = []
        
        for alt in alternatives:
            score = self.score_decision(alt)
            scored_alternatives.append({
                'alternative': alt,
                'confidence': score.to_dict(),
                'rank': 0  # Will be set after sorting
            })
        
        # Sort by confidence
        scored_alternatives.sort(key=lambda x: x['confidence']['overall_score'], reverse=True)
        
        # Assign ranks
        for idx, alt in enumerate(scored_alternatives, 1):
            alt['rank'] = idx
        
        return {
            'total_alternatives': len(alternatives),
            'ranked_alternatives': scored_alternatives,
            'best_alternative': scored_alternatives[0] if scored_alternatives else None,
            'confidence_range': {
                'highest': scored_alternatives[0]['confidence']['overall_score'] if scored_alternatives else 0,
                'lowest': scored_alternatives[-1]['confidence']['overall_score'] if scored_alternatives else 0
            }
        }
    
    def _get_confidence_level(self, score: float) -> str:
        """Get confidence level from score"""
        if score >= 0.9:
            return 'very_high'
        elif score >= 0.7:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        elif score >= 0.3:
            return 'low'
        else:
            return 'very_low'
    
    def _generate_explanation(self, overall: float, components: Dict[str, float], 
                             chain_length: int) -> str:
        """Generate human-readable explanation"""
        level = self._get_confidence_level(overall)
        
        explanations = {
            'very_high': f"Very high confidence based on {chain_length}-step reasoning with strong evidence",
            'high': f"High confidence based on {chain_length}-step reasoning",
            'medium': f"Moderate confidence based on {chain_length}-step reasoning",
            'low': f"Low confidence - reasoning chain has {chain_length} steps which may introduce uncertainty",
            'very_low': f"Very low confidence - insufficient evidence or weak reasoning"
        }
        
        return explanations.get(level, "Confidence assessment complete")
    
    def _generate_decision_explanation(self, overall: float, components: Dict[str, float]) -> str:
        """Generate decision confidence explanation"""
        level = self._get_confidence_level(overall)
        
        weak_components = [k for k, v in components.items() if v < 0.5]
        
        if not weak_components:
            return f"{level.replace('_', ' ').title()} confidence - all factors are strong"
        else:
            return f"{level.replace('_', ' ').title()} confidence - weaker in: {', '.join(weak_components)}"


# Singleton instance
_confidence_scorer_instance = None


def get_confidence_scorer() -> ConfidenceScorer:
    """
    Get singleton ConfidenceScorer instance
    
    Returns:
        ConfidenceScorer instance
    """
    global _confidence_scorer_instance
    if _confidence_scorer_instance is None:
        _confidence_scorer_instance = ConfidenceScorer()
    return _confidence_scorer_instance
