"""
Hybrid Response Generator
Combines results from MeTTa/Gateway with OpenCog reasoning
"""
import logging
from typing import Dict, List, Any, Optional
from .reasoner import get_reasoner
from .knowledge_store import get_knowledge_store
from .confidence_scorer import get_confidence_scorer

logger = logging.getLogger(__name__)


class HybridResponder:
    """
    Generates hybrid responses combining multiple AI systems
    """
    
    def __init__(self):
        """Initialize hybrid responder"""
        self.reasoner = get_reasoner()
        self.knowledge = get_knowledge_store()
        self.confidence_scorer = get_confidence_scorer()
        logger.info("Hybrid Responder initialized")
    
    def combine_metta_with_reasoning(self, metta_result: Dict[str, Any], 
                                    query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine MeTTa calculation with OpenCog reasoning
        
        Args:
            metta_result: Result from MeTTa engine
            query: Original query
            context: Query context
            
        Returns:
            Enhanced response with reasoning
        """
        try:
            response = {
                'success': True,
                'calculation': metta_result,
                'reasoning': {},
                'explanation': '',
                'confidence': {},
                'sources': []
            }
            
            # Get reasoning for the calculation
            if 'priority_score' in metta_result:
                region_id = context.get('region_id', 'Unknown_Region')
                
                # Generate explanation with reasoning chain
                reasoning_result = self.reasoner.explain_with_chain(region_id)
                response['reasoning'] = reasoning_result
                
                # Score the overall response
                decision_data = {
                    'reasoning': reasoning_result,
                    'evidence': reasoning_result.get('steps', [])
                }
                confidence = self.confidence_scorer.score_decision(decision_data)
                response['confidence'] = confidence.to_dict()
                
                # Generate comprehensive explanation
                response['explanation'] = self._generate_hybrid_explanation(
                    metta_result, reasoning_result, confidence
                )
                
                # Find relevant sources
                topics = ['allocation', 'priority', 'poverty']
                sources = self.knowledge.find_sources_for_topic('allocation')
                response['sources'] = sources[:3]
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to combine MeTTa with reasoning: {e}")
            return {
                'success': False,
                'error': str(e),
                'calculation': metta_result
            }
    
    def combine_gateway_with_reasoning(self, gateway_result: Dict[str, Any],
                                      query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine Gateway analysis with OpenCog reasoning
        
        Args:
            gateway_result: Result from uAgents Gateway
            query: Original query
            context: Query context
            
        Returns:
            Enhanced response with reasoning
        """
        try:
            response = {
                'success': True,
                'analysis': gateway_result,
                'reasoning': {},
                'explanation': '',
                'confidence': {},
                'sources': []
            }
            
            # Add reasoning layer
            if 'regions' in context and len(context['regions']) == 2:
                # Comparison with confidence
                region1, region2 = context['regions']
                comparison = self.reasoner.compare_with_confidence(region1, region2)
                response['reasoning'] = comparison
                response['confidence'] = comparison.get('confidence', {})
                
                # Generate explanation
                response['explanation'] = self._generate_comparison_explanation(
                    gateway_result, comparison
                )
            else:
                # General analysis with reasoning
                response['explanation'] = self._enhance_gateway_response(gateway_result)
            
            # Find relevant sources
            topics = context.get('topics', ['allocation', 'analysis'])
            sources = []
            for topic in topics:
                topic_sources = self.knowledge.find_sources_for_topic(topic)
                sources.extend(topic_sources)
            response['sources'] = list(set(sources))[:5]
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to combine Gateway with reasoning: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': gateway_result
            }
    
    def enhance_with_documents(self, base_response: Dict[str, Any],
                              query: str) -> Dict[str, Any]:
        """
        Enhance response with relevant documents
        
        Args:
            base_response: Base response to enhance
            query: Original query
            
        Returns:
            Response enhanced with document references
        """
        try:
            # Extract topics from query
            keywords = query.lower().split()
            relevant_topics = [k for k in keywords if len(k) > 3]
            
            # Find relevant sources
            all_sources = []
            for topic in relevant_topics[:3]:  # Top 3 topics
                sources = self.knowledge.find_sources_for_topic(topic)
                all_sources.extend(sources)
            
            # Remove duplicates
            unique_sources = list(set(all_sources))
            
            # Add to response
            base_response['documents'] = {
                'count': len(unique_sources),
                'sources': unique_sources[:10],  # Top 10
                'topics': relevant_topics[:3]
            }
            
            return base_response
            
        except Exception as e:
            logger.error(f"Failed to enhance with documents: {e}")
            return base_response
    
    def _generate_hybrid_explanation(self, metta_result: Dict[str, Any],
                                    reasoning_result: Dict[str, Any],
                                    confidence: Any) -> str:
        """Generate comprehensive hybrid explanation"""
        parts = []
        
        # Part 1: Calculation result
        if 'priority_score' in metta_result:
            parts.append(f"**Priority Score:** {metta_result['priority_score']:.2f}")
            parts.append(f"*Calculated by MeTTa engine*\n")
        
        # Part 2: Reasoning chain
        if reasoning_result.get('success'):
            parts.append("**Reasoning:**")
            steps = reasoning_result.get('steps', [])
            for step in steps[:3]:  # Top 3 steps
                parts.append(f"• {step.get('conclusion', 'Step')}")
            parts.append("")
        
        # Part 3: Confidence
        if confidence:
            level = confidence.get('level', 'medium')
            score = confidence.get('overall_score', 0.5)
            parts.append(f"**Confidence:** {level.replace('_', ' ').title()} ({score:.0%})")
        
        return "\n".join(parts)
    
    def _generate_comparison_explanation(self, gateway_result: Dict[str, Any],
                                        comparison: Dict[str, Any]) -> str:
        """Generate comparison explanation"""
        parts = []
        
        # Gateway analysis
        parts.append("**Gateway Analysis:**")
        if 'recommendation' in gateway_result:
            parts.append(gateway_result['recommendation'])
        parts.append("")
        
        # Cognitive reasoning
        parts.append("**Reasoning:**")
        if 'recommendation' in comparison:
            parts.append(comparison['recommendation'])
        
        # Confidence
        if 'confidence' in comparison:
            conf = comparison['confidence']
            parts.append(f"\n**Confidence:** {conf.get('level', 'medium')} ({conf.get('overall_score', 0.5):.0%})")
        
        return "\n".join(parts)
    
    def _enhance_gateway_response(self, gateway_result: Dict[str, Any]) -> str:
        """Enhance gateway response with context"""
        if 'analysis' in gateway_result:
            return f"**Analysis:** {gateway_result['analysis']}"
        elif 'recommendation' in gateway_result:
            return f"**Recommendation:** {gateway_result['recommendation']}"
        else:
            return "Analysis complete. See details above."


# Singleton instance
_hybrid_responder_instance = None


def get_hybrid_responder() -> HybridResponder:
    """
    Get singleton hybrid responder instance
    
    Returns:
        HybridResponder instance
    """
    global _hybrid_responder_instance
    if _hybrid_responder_instance is None:
        _hybrid_responder_instance = HybridResponder()
    return _hybrid_responder_instance
