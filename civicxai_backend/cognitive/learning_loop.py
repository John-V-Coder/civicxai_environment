"""
Learning Loop System
Tracks what works, learns from feedback, and improves over time
"""
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from .atomspace_manager import get_atomspace_manager

logger = logging.getLogger(__name__)


@dataclass
class QueryFeedback:
    """Feedback for a query and response"""
    query: str
    response: str
    routing_decision: str
    feedback_score: float  # -1.0 to 1.0
    timestamp: str
    user_rating: Optional[int] = None  # 1-5 stars
    success: bool = True
    response_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class LearningLoop:
    """
    Learning system that tracks performance and improves decisions
    """
    
    def __init__(self):
        """Initialize learning loop"""
        self.atomspace = get_atomspace_manager()
        self.feedback_history = []
        self.routing_performance = {}  # routing_decision -> performance metrics
        self.query_patterns = {}  # pattern -> success rate
        self.improvement_suggestions = []
        logger.info("Learning Loop initialized")
    
    def record_feedback(self, query: str, response: str,
                       routing_decision: str, feedback_score: float,
                       user_rating: Optional[int] = None,
                       response_time: float = 0.0):
        """
        Record feedback for a query-response pair
        
        Args:
            query: User query
            response: System response
            routing_decision: Which system was used
            feedback_score: Automated feedback score
            user_rating: Optional user rating (1-5)
            response_time: Response time in seconds
        """
        feedback = QueryFeedback(
            query=query,
            response=response,
            routing_decision=routing_decision,
            feedback_score=feedback_score,
            user_rating=user_rating,
            timestamp=datetime.now().isoformat(),
            success=feedback_score > 0,
            response_time=response_time
        )
        
        self.feedback_history.append(feedback)
        self._update_metrics(feedback)
        
        logger.info(f"Recorded feedback: score={feedback_score:.2f}, routing={routing_decision}")
    
    def _update_metrics(self, feedback: QueryFeedback):
        """Update performance metrics based on feedback"""
        routing = feedback.routing_decision
        
        if routing not in self.routing_performance:
            self.routing_performance[routing] = {
                'total_queries': 0,
                'successful_queries': 0,
                'average_score': 0.0,
                'average_response_time': 0.0,
                'user_ratings': []
            }
        
        metrics = self.routing_performance[routing]
        metrics['total_queries'] += 1
        
        if feedback.success:
            metrics['successful_queries'] += 1
        
        # Update running average
        n = metrics['total_queries']
        metrics['average_score'] = (
            (metrics['average_score'] * (n - 1) + feedback.feedback_score) / n
        )
        metrics['average_response_time'] = (
            (metrics['average_response_time'] * (n - 1) + feedback.response_time) / n
        )
        
        if feedback.user_rating:
            metrics['user_ratings'].append(feedback.user_rating)
    
    def get_routing_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all routing decisions"""
        performance = {}
        
        for routing, metrics in self.routing_performance.items():
            total = metrics['total_queries']
            successful = metrics['successful_queries']
            
            performance[routing] = {
                'total_queries': total,
                'success_rate': successful / total if total > 0 else 0.0,
                'average_score': metrics['average_score'],
                'average_response_time': metrics['average_response_time'],
                'average_user_rating': (
                    sum(metrics['user_ratings']) / len(metrics['user_ratings'])
                    if metrics['user_ratings'] else None
                )
            }
        
        return performance
    
    def learn_query_patterns(self) -> Dict[str, float]:
        """
        Learn which query patterns lead to success
        
        Returns:
            Dictionary of patterns and their success rates
        """
        pattern_stats = {}
        
        for feedback in self.feedback_history:
            # Extract pattern (simplified: first few words)
            words = feedback.query.lower().split()[:3]
            pattern = ' '.join(words)
            
            if pattern not in pattern_stats:
                pattern_stats[pattern] = {'total': 0, 'successful': 0}
            
            pattern_stats[pattern]['total'] += 1
            if feedback.success:
                pattern_stats[pattern]['successful'] += 1
        
        # Calculate success rates
        for pattern in pattern_stats:
            total = pattern_stats[pattern]['total']
            successful = pattern_stats[pattern]['successful']
            pattern_stats[pattern]['success_rate'] = successful / total if total > 0 else 0.0
        
        self.query_patterns = pattern_stats
        return {p: stats['success_rate'] for p, stats in pattern_stats.items()}
    
    def suggest_improvements(self) -> List[Dict[str, Any]]:
        """
        Analyze performance and suggest improvements
        
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Analyze routing performance
        performance = self.get_routing_performance()
        
        for routing, metrics in performance.items():
            # Suggest if success rate is low
            if metrics['success_rate'] < 0.6:
                suggestions.append({
                    'type': 'routing_performance',
                    'severity': 'high',
                    'routing': routing,
                    'issue': f"Low success rate: {metrics['success_rate']:.1%}",
                    'suggestion': f"Review {routing} routing criteria or improve underlying system"
                })
            
            # Suggest if response time is high
            if metrics['average_response_time'] > 3.0:
                suggestions.append({
                    'type': 'performance',
                    'severity': 'medium',
                    'routing': routing,
                    'issue': f"Slow response time: {metrics['average_response_time']:.2f}s",
                    'suggestion': 'Optimize processing or add caching'
                })
        
        # Analyze query patterns
        patterns = self.learn_query_patterns()
        for pattern, success_rate in patterns.items():
            if success_rate < 0.5 and pattern in self.query_patterns:
                total = self.query_patterns[pattern]['total']
                if total >= 5:  # Only suggest if pattern is common
                    suggestions.append({
                        'type': 'query_pattern',
                        'severity': 'medium',
                        'pattern': pattern,
                        'issue': f"Pattern fails often: {success_rate:.1%}",
                        'suggestion': 'Add specific handling for this query type'
                    })
        
        self.improvement_suggestions = suggestions
        return suggestions
    
    def adaptive_routing_suggestion(self, query: str) -> Optional[str]:
        """
        Suggest best routing based on learned patterns
        
        Args:
            query: User query
            
        Returns:
            Suggested routing or None
        """
        # Extract pattern from query
        words = query.lower().split()[:3]
        pattern = ' '.join(words)
        
        # Check if we have learned about similar patterns
        if pattern in self.query_patterns:
            pattern_data = self.query_patterns[pattern]
            if pattern_data['total'] >= 3:  # Enough data
                # Find best performing routing for this pattern
                pattern_routings = {}
                
                for feedback in self.feedback_history:
                    fb_words = feedback.query.lower().split()[:3]
                    fb_pattern = ' '.join(fb_words)
                    
                    if fb_pattern == pattern:
                        routing = feedback.routing_decision
                        if routing not in pattern_routings:
                            pattern_routings[routing] = {'total': 0, 'success': 0}
                        
                        pattern_routings[routing]['total'] += 1
                        if feedback.success:
                            pattern_routings[routing]['success'] += 1
                
                # Find best routing
                best_routing = None
                best_rate = 0.0
                
                for routing, stats in pattern_routings.items():
                    rate = stats['success'] / stats['total']
                    if rate > best_rate:
                        best_rate = rate
                        best_routing = routing
                
                if best_routing and best_rate > 0.7:
                    return best_routing
        
        return None
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get overall learning statistics"""
        if not self.feedback_history:
            return {
                'total_feedback': 0,
                'learning_active': False
            }
        
        total = len(self.feedback_history)
        successful = sum(1 for f in self.feedback_history if f.success)
        
        return {
            'total_feedback': total,
            'success_rate': successful / total if total > 0 else 0.0,
            'routing_performance': self.get_routing_performance(),
            'learned_patterns': len(self.query_patterns),
            'improvement_suggestions': len(self.improvement_suggestions),
            'learning_active': True,
            'data_quality': 'good' if total >= 50 else 'improving'
        }
    
    def export_learning_data(self, filepath: str):
        """Export learning data to file"""
        data = {
            'feedback_history': [f.to_dict() for f in self.feedback_history],
            'routing_performance': self.routing_performance,
            'query_patterns': self.query_patterns,
            'suggestions': self.improvement_suggestions,
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported learning data to {filepath}")
    
    def import_learning_data(self, filepath: str):
        """Import learning data from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Reconstruct feedback history
        self.feedback_history = [
            QueryFeedback(**fb) for fb in data.get('feedback_history', [])
        ]
        self.routing_performance = data.get('routing_performance', {})
        self.query_patterns = data.get('query_patterns', {})
        self.improvement_suggestions = data.get('suggestions', [])
        
        logger.info(f"Imported learning data from {filepath}")


# Singleton instance
_learning_loop_instance = None


def get_learning_loop() -> LearningLoop:
    """
    Get singleton learning loop instance
    
    Returns:
        LearningLoop instance
    """
    global _learning_loop_instance
    if _learning_loop_instance is None:
        _learning_loop_instance = LearningLoop()
    return _learning_loop_instance
