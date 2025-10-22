"""
Reasoning Chain Visualizer
Creates structured representations of reasoning chains for explanation
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from .pln_rules import TruthValue
from .confidence_scorer import get_confidence_scorer

logger = logging.getLogger(__name__)


@dataclass
class ReasoningStep:
    """Single step in a reasoning chain"""
    step_number: int
    premise: str
    conclusion: str
    rule_applied: str
    truth_value: Optional[TruthValue] = None
    evidence: List[str] = field(default_factory=list)
    confidence_level: str = "medium"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'step': self.step_number,
            'premise': self.premise,
            'conclusion': self.conclusion,
            'rule': self.rule_applied,
            'truth_value': {
                'strength': self.truth_value.strength if self.truth_value else 0.5,
                'confidence': self.truth_value.confidence if self.truth_value else 0.5
            } if self.truth_value else None,
            'evidence': self.evidence,
            'confidence_level': self.confidence_level
        }


class ReasoningChain:
    """
    Represents a complete reasoning chain from premises to conclusion
    """
    
    def __init__(self, goal: str):
        """
        Initialize reasoning chain
        
        Args:
            goal: The goal/conclusion to reach
        """
        self.goal = goal
        self.steps: List[ReasoningStep] = []
        self.overall_confidence = None
        self.confidence_scorer = get_confidence_scorer()
        logger.info(f"Created reasoning chain for goal: {goal}")
    
    def add_step(self, premise: str, conclusion: str, rule: str,
                 truth_value: Optional[TruthValue] = None,
                 evidence: Optional[List[str]] = None) -> ReasoningStep:
        """
        Add a step to the reasoning chain
        
        Args:
            premise: Starting premise
            conclusion: Conclusion reached
            rule: Rule applied
            truth_value: Optional truth value
            evidence: Optional evidence list
            
        Returns:
            The created reasoning step
        """
        step_number = len(self.steps) + 1
        
        # Determine confidence level
        if truth_value:
            if truth_value.confidence >= 0.8:
                conf_level = "high"
            elif truth_value.confidence >= 0.6:
                conf_level = "medium"
            else:
                conf_level = "low"
        else:
            conf_level = "medium"
        
        step = ReasoningStep(
            step_number=step_number,
            premise=premise,
            conclusion=conclusion,
            rule_applied=rule,
            truth_value=truth_value,
            evidence=evidence or [],
            confidence_level=conf_level
        )
        
        self.steps.append(step)
        logger.debug(f"Added reasoning step {step_number}: {premise} → {conclusion}")
        
        return step
    
    def calculate_confidence(self) -> Dict[str, Any]:
        """
        Calculate overall confidence of the reasoning chain
        
        Returns:
            Confidence score details
        """
        chain_data = [step.to_dict() for step in self.steps]
        confidence = self.confidence_scorer.score_reasoning_chain(chain_data)
        self.overall_confidence = confidence
        return confidence.to_dict()
    
    def get_chain_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the reasoning chain
        
        Returns:
            Summary with key information
        """
        if not self.overall_confidence:
            self.calculate_confidence()
        
        return {
            'goal': self.goal,
            'total_steps': len(self.steps),
            'confidence': self.overall_confidence.to_dict() if self.overall_confidence else None,
            'steps': [step.to_dict() for step in self.steps],
            'path': ' → '.join([step.premise for step in self.steps] + [self.goal])
        }
    
    def to_text_explanation(self) -> str:
        """
        Convert chain to human-readable text explanation
        
        Returns:
            Text explanation of the reasoning
        """
        lines = [f"**Reasoning Chain: {self.goal}**\n"]
        
        for step in self.steps:
            lines.append(f"**Step {step.step_number}:** {step.premise}")
            lines.append(f"  ↓ (using: {step.rule_applied})")
            lines.append(f"  → {step.conclusion}")
            
            if step.truth_value:
                lines.append(f"  Confidence: {step.truth_value.confidence:.2f}")
            
            if step.evidence:
                lines.append(f"  Evidence: {', '.join(step.evidence)}")
            
            lines.append("")  # Blank line
        
        if self.overall_confidence:
            lines.append(f"**Overall Confidence:** {self.overall_confidence.level} ({self.overall_confidence.overall_score:.2f})")
        
        return "\n".join(lines)
    
    def to_graph_data(self) -> Dict[str, Any]:
        """
        Convert chain to graph structure for visualization
        
        Returns:
            Graph data with nodes and edges
        """
        nodes = []
        edges = []
        
        # Add start node
        nodes.append({
            'id': 'start',
            'label': 'Start',
            'type': 'start'
        })
        
        # Add step nodes
        prev_id = 'start'
        for step in self.steps:
            node_id = f"step_{step.step_number}"
            
            nodes.append({
                'id': node_id,
                'label': step.conclusion,
                'type': 'step',
                'confidence': step.confidence_level,
                'rule': step.rule_applied
            })
            
            edges.append({
                'from': prev_id,
                'to': node_id,
                'label': step.rule_applied,
                'confidence': step.truth_value.confidence if step.truth_value else 0.5
            })
            
            prev_id = node_id
        
        # Add goal node
        nodes.append({
            'id': 'goal',
            'label': self.goal,
            'type': 'goal'
        })
        
        edges.append({
            'from': prev_id,
            'to': 'goal',
            'label': 'conclusion'
        })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_steps': len(self.steps),
                'confidence': self.overall_confidence.to_dict() if self.overall_confidence else None
            }
        }


class ReasoningChainBuilder:
    """
    Helper class to build reasoning chains
    """
    
    def __init__(self):
        """Initialize builder"""
        self.current_chain: Optional[ReasoningChain] = None
    
    def start_chain(self, goal: str) -> ReasoningChain:
        """
        Start a new reasoning chain
        
        Args:
            goal: Goal to reach
            
        Returns:
            New reasoning chain
        """
        self.current_chain = ReasoningChain(goal)
        return self.current_chain
    
    def add_deduction(self, premise: str, conclusion: str, 
                     truth_value: TruthValue,
                     evidence: Optional[List[str]] = None) -> ReasoningStep:
        """Add a deduction step"""
        if not self.current_chain:
            raise ValueError("No active chain. Call start_chain() first.")
        
        return self.current_chain.add_step(
            premise=premise,
            conclusion=conclusion,
            rule="Deduction",
            truth_value=truth_value,
            evidence=evidence
        )
    
    def add_abduction(self, observation: str, hypothesis: str,
                     truth_value: TruthValue,
                     evidence: Optional[List[str]] = None) -> ReasoningStep:
        """Add an abduction step (hypothesis generation)"""
        if not self.current_chain:
            raise ValueError("No active chain. Call start_chain() first.")
        
        return self.current_chain.add_step(
            premise=observation,
            conclusion=hypothesis,
            rule="Abduction",
            truth_value=truth_value,
            evidence=evidence
        )
    
    def add_induction(self, instances: str, generalization: str,
                     truth_value: TruthValue,
                     evidence: Optional[List[str]] = None) -> ReasoningStep:
        """Add an induction step (generalization from instances)"""
        if not self.current_chain:
            raise ValueError("No active chain. Call start_chain() first.")
        
        return self.current_chain.add_step(
            premise=instances,
            conclusion=generalization,
            rule="Induction",
            truth_value=truth_value,
            evidence=evidence
        )
    
    def finalize(self) -> Dict[str, Any]:
        """
        Finalize the chain and get summary
        
        Returns:
            Complete chain summary
        """
        if not self.current_chain:
            raise ValueError("No active chain to finalize.")
        
        summary = self.current_chain.get_chain_summary()
        self.current_chain = None
        return summary


# Singleton instance
_chain_builder_instance = None


def get_chain_builder() -> ReasoningChainBuilder:
    """
    Get singleton chain builder instance
    
    Returns:
        ReasoningChainBuilder instance
    """
    global _chain_builder_instance
    if _chain_builder_instance is None:
        _chain_builder_instance = ReasoningChainBuilder()
    return _chain_builder_instance
