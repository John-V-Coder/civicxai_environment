"""
Cognitive Orchestrator
Intelligently routes queries between simple (MeTTa/Gateway) and complex (OpenCog) reasoning
"""
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class QueryComplexity(Enum):
    """Query complexity levels"""
    SIMPLE = 1      # Direct lookup, basic calculation
    MODERATE = 2    # Requires some reasoning
    COMPLEX = 3     # Multi-hop reasoning, explanation needed
    VERY_COMPLEX = 4  # Deep analysis, multiple sources


class RoutingDecision(Enum):
    """Routing decisions"""
    METTA = "metta"              # Use MeTTa engine
    GATEWAY = "gateway"          # Use uAgents Gateway
    COGNITIVE = "cognitive"      # Use OpenCog reasoning
    HYBRID_METTA = "hybrid_metta"      # MeTTa + OpenCog
    HYBRID_GATEWAY = "hybrid_gateway"  # Gateway + OpenCog


class CognitiveOrchestrator:
    """
    Orchestrates query routing between different AI systems
    Analyzes query complexity and routes to appropriate system
    """
    
    def __init__(self):
        """Initialize orchestrator"""
        self.routing_stats = {
            'total_queries': 0,
            'metta_queries': 0,
            'gateway_queries': 0,
            'cognitive_queries': 0,
            'hybrid_queries': 0
        }
        logger.info("Cognitive Orchestrator initialized")
    
    def analyze_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze query to determine complexity and requirements
        
        Args:
            query: User query
            context: Optional context information
            
        Returns:
            Analysis results
        """
        query_lower = query.lower().strip()
        context = context or {}
        
        analysis = {
            'query': query,
            'complexity': QueryComplexity.SIMPLE,
            'requires_reasoning': False,
            'requires_explanation': False,
            'requires_documents': False,
            'requires_calculation': False,
            'requires_comparison': False,
            'requires_multi_hop': False,
            'keywords': [],
            'intent': 'unknown'
        }
        
        # Extract keywords
        analysis['keywords'] = self._extract_keywords(query_lower)
        
        # Detect intent
        analysis['intent'] = self._detect_intent(query_lower)
        
        # Check for calculation needs
        if self._needs_calculation(query_lower):
            analysis['requires_calculation'] = True
            analysis['complexity'] = QueryComplexity.SIMPLE
        
        # Check for document queries
        if self._needs_documents(query_lower):
            analysis['requires_documents'] = True
            analysis['complexity'] = QueryComplexity.MODERATE
        
        # Check for explanation needs
        if self._needs_explanation(query_lower):
            analysis['requires_explanation'] = True
            analysis['complexity'] = QueryComplexity.MODERATE
            analysis['requires_reasoning'] = True
        
        # Check for comparison needs
        if self._needs_comparison(query_lower):
            analysis['requires_comparison'] = True
            analysis['complexity'] = QueryComplexity.MODERATE
            analysis['requires_reasoning'] = True
        
        # Check for multi-hop reasoning
        if self._needs_multi_hop(query_lower):
            analysis['requires_multi_hop'] = True
            analysis['complexity'] = QueryComplexity.COMPLEX
            analysis['requires_reasoning'] = True
        
        # Check for very complex queries
        if self._is_very_complex(query_lower, analysis):
            analysis['complexity'] = QueryComplexity.VERY_COMPLEX
            analysis['requires_reasoning'] = True
        
        logger.info(f"Query analysis: Complexity={analysis['complexity'].name}, Intent={analysis['intent']}")
        return analysis
    
    def route_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route query to appropriate system based on analysis
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            Routing decision with details
        """
        self.routing_stats['total_queries'] += 1
        
        # Analyze query
        analysis = self.analyze_query(query, context)
        
        # Determine routing
        routing = self._determine_routing(analysis)
        
        # Update stats
        if routing == RoutingDecision.METTA:
            self.routing_stats['metta_queries'] += 1
        elif routing == RoutingDecision.GATEWAY:
            self.routing_stats['gateway_queries'] += 1
        elif routing == RoutingDecision.COGNITIVE:
            self.routing_stats['cognitive_queries'] += 1
        elif routing in [RoutingDecision.HYBRID_METTA, RoutingDecision.HYBRID_GATEWAY]:
            self.routing_stats['hybrid_queries'] += 1
        
        return {
            'routing': routing,
            'analysis': analysis,
            'rationale': self._get_routing_rationale(routing, analysis)
        }
    
    def _determine_routing(self, analysis: Dict[str, Any]) -> RoutingDecision:
        """Determine which system to route to"""
        complexity = analysis['complexity']
        intent = analysis['intent']
        
        # Document queries → Cognitive (needs knowledge base)
        if analysis['requires_documents']:
            return RoutingDecision.COGNITIVE
        
        # Multi-hop reasoning → Cognitive
        if analysis['requires_multi_hop']:
            return RoutingDecision.COGNITIVE
        
        # Simple calculation → MeTTa
        if complexity == QueryComplexity.SIMPLE and analysis['requires_calculation']:
            return RoutingDecision.METTA
        
        # Explanation with calculation → Hybrid MeTTa + Cognitive
        if analysis['requires_explanation'] and analysis['requires_calculation']:
            return RoutingDecision.HYBRID_METTA
        
        # Comparison or analysis → Gateway if available, else Cognitive
        if intent in ['compare', 'analyze'] and not analysis['requires_explanation']:
            return RoutingDecision.GATEWAY
        
        # Comparison with explanation → Hybrid Gateway + Cognitive
        if intent in ['compare', 'analyze'] and analysis['requires_explanation']:
            return RoutingDecision.HYBRID_GATEWAY
        
        # Complex reasoning → Cognitive
        if complexity in [QueryComplexity.COMPLEX, QueryComplexity.VERY_COMPLEX]:
            return RoutingDecision.COGNITIVE
        
        # Moderate with reasoning → Cognitive
        if complexity == QueryComplexity.MODERATE and analysis['requires_reasoning']:
            return RoutingDecision.COGNITIVE
        
        # Default to MeTTa for simple queries
        return RoutingDecision.METTA
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract key terms from query"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'why', 'when', 'where', 'which', 'who'}
        words = query.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords[:5]  # Top 5 keywords
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent from query"""
        if any(word in query for word in ['calculate', 'compute', 'score']):
            return 'calculate'
        
        if any(word in query for word in ['explain', 'why', 'how', 'reason']):
            return 'explain'
        
        if any(word in query for word in ['compare', 'difference', 'versus', 'vs']):
            return 'compare'
        
        if any(word in query for word in ['analyze', 'analysis', 'assess']):
            return 'analyze'
        
        if any(word in query for word in ['find', 'search', 'what documents', 'which sources', 'show me']):
            return 'search'
        
        if any(word in query for word in ['recommend', 'suggest', 'should']):
            return 'recommend'
        
        return 'general'
    
    def _needs_calculation(self, query: str) -> bool:
        """Check if query needs calculation"""
        calc_terms = ['calculate', 'compute', 'score', 'priority', 'value']
        return any(term in query for term in calc_terms)
    
    def _needs_documents(self, query: str) -> bool:
        """Check if query needs document search"""
        doc_terms = ['document', 'pdf', 'source', 'paper', 'research', 'policy', 'mention', 'reference']
        return any(term in query for term in doc_terms)
    
    def _needs_explanation(self, query: str) -> bool:
        """Check if query needs explanation"""
        explain_terms = ['why', 'how', 'explain', 'reason', 'because', 'rationale']
        return any(term in query for term in explain_terms)
    
    def _needs_comparison(self, query: str) -> bool:
        """Check if query needs comparison"""
        compare_terms = ['compare', 'difference', 'versus', 'vs', 'better', 'worse']
        return any(term in query for term in compare_terms)
    
    def _needs_multi_hop(self, query: str) -> bool:
        """Check if query needs multi-hop reasoning"""
        multi_hop_indicators = [
            'leads to', 'causes', 'results in', 'relationship between',
            'if.*then', 'impact on', 'effect of', 'consequence'
        ]
        return any(re.search(pattern, query) for pattern in multi_hop_indicators)
    
    def _is_very_complex(self, query: str, analysis: Dict[str, Any]) -> bool:
        """Check if query is very complex"""
        # Multiple requirements = very complex
        requirements = sum([
            analysis['requires_reasoning'],
            analysis['requires_explanation'],
            analysis['requires_documents'],
            analysis['requires_comparison'],
            analysis['requires_multi_hop']
        ])
        
        # Long queries with multiple clauses
        has_multiple_clauses = len(query.split('and')) > 2 or len(query.split('or')) > 2
        
        return requirements >= 3 or (requirements >= 2 and has_multiple_clauses)
    
    def _get_routing_rationale(self, routing: RoutingDecision, analysis: Dict[str, Any]) -> str:
        """Get human-readable rationale for routing decision"""
        rationales = {
            RoutingDecision.METTA: "Simple calculation - using fast MeTTa engine",
            RoutingDecision.GATEWAY: "Analysis required - using uAgents Gateway",
            RoutingDecision.COGNITIVE: "Complex reasoning needed - using OpenCog cognitive engine",
            RoutingDecision.HYBRID_METTA: "Calculation with explanation - combining MeTTa + OpenCog",
            RoutingDecision.HYBRID_GATEWAY: "Analysis with reasoning - combining Gateway + OpenCog"
        }
        
        base_rationale = rationales.get(routing, "Default routing")
        
        # Add specific reasons
        reasons = []
        if analysis['requires_documents']:
            reasons.append("document search")
        if analysis['requires_explanation']:
            reasons.append("explanation")
        if analysis['requires_multi_hop']:
            reasons.append("multi-hop reasoning")
        
        if reasons:
            return f"{base_rationale} ({', '.join(reasons)})"
        
        return base_rationale
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        total = self.routing_stats['total_queries']
        if total == 0:
            return {**self.routing_stats, 'percentages': {}}
        
        return {
            **self.routing_stats,
            'percentages': {
                'metta': (self.routing_stats['metta_queries'] / total) * 100,
                'gateway': (self.routing_stats['gateway_queries'] / total) * 100,
                'cognitive': (self.routing_stats['cognitive_queries'] / total) * 100,
                'hybrid': (self.routing_stats['hybrid_queries'] / total) * 100
            }
        }


# Singleton instance
_orchestrator_instance = None


def get_orchestrator() -> CognitiveOrchestrator:
    """
    Get singleton orchestrator instance
    
    Returns:
        CognitiveOrchestrator instance
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = CognitiveOrchestrator()
    return _orchestrator_instance
