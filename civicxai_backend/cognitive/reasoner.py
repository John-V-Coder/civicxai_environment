"""
Cognitive Reasoner
Handles reasoning and inference operations using AtomSpace
Enhanced with PLN rules, confidence scoring, and reasoning chains
"""
import logging
from typing import List, Dict, Any, Optional
from .atomspace_manager import get_atomspace_manager
from .knowledge_store import get_knowledge_store
from .pln_rules import get_pln_engine, TruthValue
from .confidence_scorer import get_confidence_scorer
from .reasoning_chain import get_chain_builder, ReasoningChain

logger = logging.getLogger(__name__)


class CognitiveReasoner:
    """
    Performs reasoning operations over the knowledge base
    Uses pattern matching, PLN rules, and inference chains
    Phase 3: Enhanced with confidence scoring and reasoning visualization
    """
    
    def __init__(self):
        """Initialize reasoner with all Phase 3 components"""
        self.atomspace = get_atomspace_manager()
        self.knowledge = get_knowledge_store()
        self.pln_engine = get_pln_engine()
        self.confidence_scorer = get_confidence_scorer()
        self.chain_builder = get_chain_builder()
        logger.info("Cognitive Reasoner initialized with Phase 3 capabilities")
    
    def find_related_concepts(self, concept: str, depth: int = 1) -> List[str]:
        """
        Find concepts related to the given concept
        
        Args:
            concept: Starting concept
            depth: How many hops to traverse (1 = direct relations only)
            
        Returns:
            List of related concept names
        """
        try:
            related = set()
            
            # Find direct relationships
            query = f"!(match &self (SimilarityLink {concept} $x) $x)"
            direct_relations = self.atomspace.query(query)
            related.update(direct_relations)
            
            # If depth > 1, recursively find relations
            if depth > 1:
                for rel in direct_relations:
                    nested = self.find_related_concepts(rel, depth - 1)
                    related.update(nested)
            
            return list(related)
        except Exception as e:
            logger.error(f"Failed to find related concepts for {concept}: {e}")
            return []
    
    def find_regions_matching_criteria(self, criteria: Dict[str, Any]) -> List[str]:
        """
        Find regions that match given criteria
        
        Args:
            criteria: Dictionary of criteria (e.g., {'poverty_index': '>0.7'})
            
        Returns:
            List of matching region IDs
        """
        try:
            matching_regions = []
            
            # Get all regions
            all_regions_query = "!(match &self (InheritanceLink $r Region) $r)"
            all_regions = self.atomspace.query(all_regions_query)
            
            # For now, return all regions (filtering logic can be added)
            # In Phase 2, we'll add proper criteria matching
            return all_regions
            
        except Exception as e:
            logger.error(f"Failed to find matching regions: {e}")
            return []
    
    def explain_priority(self, region_id: str) -> Dict[str, Any]:
        """
        Generate explanation for why a region has certain priority
        
        Args:
            region_id: Region to explain
            
        Returns:
            Dictionary with explanation details
        """
        try:
            explanation = {
                'region': region_id,
                'reasoning_chain': [],
                'evidence': [],
                'confidence': 0.0
            }
            
            # Check if region has high poverty
            high_poverty_query = f"!(match &self (InheritanceLink {region_id} High_Poverty_Region) High_Poverty_Region)"
            is_high_poverty = len(self.atomspace.query(high_poverty_query)) > 0
            
            if is_high_poverty:
                explanation['reasoning_chain'].append({
                    'step': 1,
                    'condition': f'{region_id} is a High_Poverty_Region',
                    'inference': 'High poverty regions require priority allocation',
                    'confidence': 0.9
                })
                explanation['confidence'] = 0.9
            
            # Find relevant policies
            policy_query = "!(match &self (InheritanceLink $p Policy) $p)"
            policies = self.atomspace.query(policy_query)
            explanation['evidence'] = policies
            
            return explanation
            
        except Exception as e:
            logger.error(f"Failed to explain priority for {region_id}: {e}")
            return {'error': str(e)}
    
    def compare_regions(self, region1_id: str, region2_id: str) -> Dict[str, Any]:
        """
        Compare two regions and explain differences
        
        Args:
            region1_id: First region ID
            region2_id: Second region ID
            
        Returns:
            Dictionary with comparison details
        """
        try:
            comparison = {
                'region1': region1_id,
                'region2': region2_id,
                'differences': [],
                'similarities': [],
                'recommendation': ''
            }
            
            # Check poverty classifications
            high_poverty_query_1 = f"!(match &self (InheritanceLink {region1_id} High_Poverty_Region) High_Poverty_Region)"
            high_poverty_query_2 = f"!(match &self (InheritanceLink {region2_id} High_Poverty_Region) High_Poverty_Region)"
            
            region1_high_poverty = len(self.atomspace.query(high_poverty_query_1)) > 0
            region2_high_poverty = len(self.atomspace.query(high_poverty_query_2)) > 0
            
            if region1_high_poverty != region2_high_poverty:
                comparison['differences'].append({
                    'factor': 'poverty_level',
                    'region1_value': 'high' if region1_high_poverty else 'not_high',
                    'region2_value': 'high' if region2_high_poverty else 'not_high'
                })
            else:
                comparison['similarities'].append('Similar poverty levels')
            
            # Generate recommendation
            if region1_high_poverty and not region2_high_poverty:
                comparison['recommendation'] = f'{region1_id} should receive higher priority due to higher poverty'
            elif region2_high_poverty and not region1_high_poverty:
                comparison['recommendation'] = f'{region2_id} should receive higher priority due to higher poverty'
            else:
                comparison['recommendation'] = 'Both regions have similar priority characteristics'
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare regions: {e}")
            return {'error': str(e)}
    
    def find_evidence_for_decision(self, decision: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find evidence (data sources, policies) supporting a decision
        
        Args:
            decision: Decision made (e.g., 'high_priority_allocation')
            context: Context information (region, metrics, etc.)
            
        Returns:
            List of evidence items with source and relevance
        """
        try:
            evidence_list = []
            
            # Find relevant data sources
            topics = context.get('topics', ['allocation', 'poverty'])
            for topic in topics:
                sources = self.knowledge.find_sources_for_topic(topic)
                for source in sources:
                    evidence_list.append({
                        'source_id': source,
                        'type': 'data_source',
                        'topic': topic,
                        'relevance': 0.8
                    })
            
            # Find relevant policies
            policy_query = "!(match &self (InheritanceLink $p Policy) $p)"
            policies = self.atomspace.query(policy_query)
            for policy in policies:
                evidence_list.append({
                    'source_id': policy,
                    'type': 'policy',
                    'relevance': 0.9
                })
            
            return evidence_list
            
        except Exception as e:
            logger.error(f"Failed to find evidence: {e}")
            return []
    
    def infer_causal_chain(self, start_concept: str, end_concept: str, 
                          max_hops: int = 3) -> List[List[str]]:
        """
        Find causal chains from start to end concept
        
        Args:
            start_concept: Starting concept
            end_concept: Target concept
            max_hops: Maximum chain length
            
        Returns:
            List of causal chains (each chain is a list of concepts)
        """
        try:
            # Basic implementation - find direct causal link
            chains = []
            
            # Check for direct causal link
            direct_query = f"!(match &self (CausalLink {start_concept} {end_concept}) {end_concept})"
            direct_result = self.atomspace.query(direct_query)
            
            if direct_result:
                chains.append([start_concept, end_concept])
            
            # For Phase 2: Add multi-hop reasoning
            # This will use recursive pattern matching
            
            return chains
            
        except Exception as e:
            logger.error(f"Failed to infer causal chain: {e}")
            return []
    
    def generate_recommendation(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate recommendation based on query and context
        
        Args:
            query: User query
            context: Context information
            
        Returns:
            Dictionary with recommendation and reasoning
        """
        try:
            recommendation = {
                'answer': '',
                'reasoning': [],
                'evidence': [],
                'confidence': 0.0
            }
            
            # Extract key terms from query
            keywords = query.lower().split()
            
            # Check for allocation-related queries
            if 'priority' in keywords or 'allocation' in keywords:
                region_id = context.get('region_id')
                if region_id:
                    explanation = self.explain_priority(region_id)
                    recommendation['answer'] = f"Priority assessment for {region_id}"
                    recommendation['reasoning'] = explanation.get('reasoning_chain', [])
                    recommendation['evidence'] = explanation.get('evidence', [])
                    recommendation['confidence'] = explanation.get('confidence', 0.0)
            
            # Check for comparison queries
            elif 'compare' in keywords:
                region1 = context.get('region1')
                region2 = context.get('region2')
                if region1 and region2:
                    comparison = self.compare_regions(region1, region2)
                    recommendation['answer'] = comparison.get('recommendation', '')
                    recommendation['reasoning'] = comparison.get('differences', [])
                    recommendation['confidence'] = 0.8
            
            else:
                recommendation['answer'] = "Query type not yet supported in basic reasoning"
                recommendation['confidence'] = 0.3
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Failed to generate recommendation: {e}")
            return {'error': str(e)}
    
    # ===== Phase 3: Advanced Reasoning Methods =====
    
    def reason_with_pln(self, premises: List[Dict[str, Any]], 
                       goal: str) -> Dict[str, Any]:
        """
        Perform PLN-based reasoning from premises to goal
        
        Args:
            premises: List of premise dictionaries with truth values
            goal: Goal to reach
            
        Returns:
            Reasoning result with chain and confidence
        """
        try:
            # Start reasoning chain
            chain = self.chain_builder.start_chain(goal)
            
            # Apply PLN rules
            current_tv = TruthValue(1.0, 1.0)
            
            for premise in premises:
                premise_tv = TruthValue(
                    premise.get('strength', 0.8),
                    premise.get('confidence', 0.7)
                )
                
                # Apply deduction
                current_tv = self.pln_engine.deduction(current_tv, premise_tv)
                
                chain.add_step(
                    premise=premise.get('statement', 'premise'),
                    conclusion=premise.get('conclusion', 'intermediate'),
                    rule="PLN Deduction",
                    truth_value=current_tv,
                    evidence=premise.get('evidence', [])
                )
            
            # Finalize chain
            result = chain.get_chain_summary()
            result['success'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"PLN reasoning failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def explain_with_chain(self, region_id: str) -> Dict[str, Any]:
        """
        Explain priority decision with full reasoning chain
        
        Args:
            region_id: Region to explain
            
        Returns:
            Explanation with reasoning chain and confidence
        """
        try:
            chain = self.chain_builder.start_chain(f"Priority decision for {region_id}")
            
            # Step 1: Check poverty classification
            high_poverty_query = f"!(match &self (InheritanceLink {region_id} High_Poverty_Region) High_Poverty_Region)"
            is_high_poverty = len(self.atomspace.query(high_poverty_query)) > 0
            
            if is_high_poverty:
                step1_tv = TruthValue(0.9, 0.85)
                chain.add_step(
                    premise=f"{region_id} is classified as High_Poverty_Region",
                    conclusion="Region has urgent need",
                    rule="Domain Rule: Poverty Classification",
                    truth_value=step1_tv,
                    evidence=["Classification based on poverty index > 0.7"]
                )
                
                # Step 2: Apply PLN rule
                rule_result = self.pln_engine.apply_rule('poverty_implies_priority', {
                    'High_Poverty_Region': True
                })
                
                if rule_result and rule_result['applied']:
                    step2_tv = rule_result['truth_value']
                    chain.add_step(
                        premise="Region has urgent need",
                        conclusion="Region receives high priority",
                        rule="PLN Rule: poverty_implies_priority",
                        truth_value=step2_tv,
                        evidence=["Policy: High poverty areas prioritized"]
                    )
            
            # Get chain summary
            result = chain.get_chain_summary()
            result['success'] = True
            result['text_explanation'] = chain.current_chain.to_text_explanation() if chain.current_chain else ""
            
            return result
            
        except Exception as e:
            logger.error(f"Explanation with chain failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def compare_with_confidence(self, region1_id: str, region2_id: str) -> Dict[str, Any]:
        """
        Compare regions with confidence scoring
        
        Args:
            region1_id: First region
            region2_id: Second region
            
        Returns:
            Comparison with confidence scores
        """
        try:
            # Get basic comparison
            comparison = self.compare_regions(region1_id, region2_id)
            
            # Score the decision confidence
            decision_data = {
                'reasoning': {'chain': comparison.get('differences', [])},
                'evidence': comparison.get('similarities', []),
                'alternatives': []
            }
            
            confidence = self.confidence_scorer.score_decision(decision_data)
            
            return {
                'success': True,
                'region1': region1_id,
                'region2': region2_id,
                'comparison': comparison,
                'confidence': confidence.to_dict(),
                'recommendation': comparison.get('recommendation', ''),
                'explanation': f"{comparison.get('recommendation', '')} (Confidence: {confidence.level})"
            }
            
        except Exception as e:
            logger.error(f"Comparison with confidence failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def multi_hop_inference(self, start: str, goal: str, max_hops: int = 3) -> Dict[str, Any]:
        """
        Perform multi-hop inference from start to goal
        
        Args:
            start: Starting concept
            goal: Goal concept
            max_hops: Maximum reasoning hops
            
        Returns:
            Inference result with reasoning chain
        """
        try:
            chain = self.chain_builder.start_chain(f"Infer: {start} → {goal}")
            
            # Simple 2-hop reasoning for now
            # In production, would use graph search algorithms
            
            # Check for direct link
            direct_query = f"!(match &self (SimilarityLink {start} {goal}) {goal})"
            direct_result = self.atomspace.query(direct_query)
            
            if direct_result:
                tv = TruthValue(0.9, 0.8)
                chain.add_step(
                    premise=start,
                    conclusion=goal,
                    rule="Direct Similarity",
                    truth_value=tv
                )
            else:
                # Try finding intermediate concepts
                related = self.find_related_concepts(start)
                
                for intermediate in related[:3]:  # Check top 3
                    # Check if intermediate connects to goal
                    intermediate_query = f"!(match &self (SimilarityLink {intermediate} {goal}) {goal})"
                    if self.atomspace.query(intermediate_query):
                        # Found 2-hop path
                        tv1 = TruthValue(0.7, 0.7)
                        chain.add_step(
                            premise=start,
                            conclusion=intermediate,
                            rule="Similarity Link",
                            truth_value=tv1
                        )
                        
                        tv2 = TruthValue(0.7, 0.7)
                        chain.add_step(
                            premise=intermediate,
                            conclusion=goal,
                            rule="Similarity Link",
                            truth_value=tv2
                        )
                        break
            
            result = chain.get_chain_summary()
            result['success'] = len(chain.current_chain.steps) > 0 if chain.current_chain else False
            
            return result
            
        except Exception as e:
            logger.error(f"Multi-hop inference failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_reasoning_stats(self) -> Dict[str, Any]:
        """
        Get statistics about reasoning capabilities
        
        Returns:
            Dictionary with stats
        """
        pln_rules = self.pln_engine.get_all_rules()
        
        return {
            'knowledge_base_stats': self.knowledge.get_knowledge_stats(),
            'reasoning_engine': 'PLN + Pattern Matching (Phase 3)',
            'pln_rules_count': len(pln_rules),
            'pln_rules': list(pln_rules.keys()),
            'capabilities': [
                'concept_similarity',
                'pln_based_inference',
                'multi_hop_reasoning',
                'confidence_scoring',
                'reasoning_chain_visualization',
                'evidence_finding',
                'advanced_explanations'
            ],
            'phase': 3,
            'status': 'active'
        }


# Singleton instance
_reasoner_instance = None


def get_reasoner() -> CognitiveReasoner:
    """
    Get the singleton CognitiveReasoner instance
    
    Returns:
        CognitiveReasoner instance
    """
    global _reasoner_instance
    if _reasoner_instance is None:
        _reasoner_instance = CognitiveReasoner()
    return _reasoner_instance
