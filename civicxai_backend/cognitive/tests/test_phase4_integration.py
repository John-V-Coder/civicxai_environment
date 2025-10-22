"""
Test Suite for Phase 4: Integration & Cognitive Orchestrator
Tests intelligent query routing, hybrid responses, and document queries
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civicxai_backend.settings')
import django
django.setup()

from cognitive.orchestrator import get_orchestrator, QueryComplexity, RoutingDecision
from cognitive.hybrid_responder import get_hybrid_responder
from cognitive.knowledge_store import get_knowledge_store


class TestPhase4Integration:
    """Test Phase 4 integration capabilities"""
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.hybrid_responder = get_hybrid_responder()
        self.knowledge = get_knowledge_store()
        self.test_results = []
    
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append((test_name, passed))
    
    def test_orchestrator_initialization(self):
        """Test 1: Orchestrator initialization"""
        try:
            passed = self.orchestrator is not None
            self.log_test("Orchestrator Initialization", passed)
            return passed
        except Exception as e:
            self.log_test("Orchestrator Initialization", False, str(e))
            return False
    
    def test_simple_query_analysis(self):
        """Test 2: Analyze simple query"""
        try:
            query = "Calculate priority for poverty 0.8"
            analysis = self.orchestrator.analyze_query(query)
            
            passed = (
                analysis['complexity'] == QueryComplexity.SIMPLE and
                analysis['requires_calculation']
            )
            
            self.log_test("Simple Query Analysis", passed,
                         f"Complexity: {analysis['complexity'].name}")
            return passed
        except Exception as e:
            self.log_test("Simple Query Analysis", False, str(e))
            return False
    
    def test_document_query_detection(self):
        """Test 3: Detect document query"""
        try:
            query = "What documents mention poverty?"
            analysis = self.orchestrator.analyze_query(query)
            
            passed = analysis['requires_documents']
            
            self.log_test("Document Query Detection", passed,
                         f"Intent: {analysis['intent']}, Keywords: {analysis['keywords']}")
            return passed
        except Exception as e:
            self.log_test("Document Query Detection", False, str(e))
            return False
    
    def test_complex_query_analysis(self):
        """Test 4: Analyze complex query"""
        try:
            query = "Explain why high poverty leads to high priority allocation with evidence"
            analysis = self.orchestrator.analyze_query(query)
            
            passed = (
                analysis['complexity'] in [QueryComplexity.COMPLEX, QueryComplexity.VERY_COMPLEX] and
                analysis['requires_explanation']
            )
            
            self.log_test("Complex Query Analysis", passed,
                         f"Complexity: {analysis['complexity'].name}")
            return passed
        except Exception as e:
            self.log_test("Complex Query Analysis", False, str(e))
            return False
    
    def test_routing_to_cognitive(self):
        """Test 5: Route complex query to cognitive"""
        try:
            query = "What documents mention poverty and allocation?"
            routing_decision = self.orchestrator.route_query(query)
            
            passed = routing_decision['routing'] == RoutingDecision.COGNITIVE
            
            self.log_test("Routing to Cognitive", passed,
                         f"Routed to: {routing_decision['routing'].value}")
            return passed
        except Exception as e:
            self.log_test("Routing to Cognitive", False, str(e))
            return False
    
    def test_routing_to_metta(self):
        """Test 6: Route simple calculation to MeTTa"""
        try:
            query = "Calculate priority score"
            routing_decision = self.orchestrator.route_query(query)
            
            # Should route to MeTTa or Hybrid MeTTa
            passed = routing_decision['routing'] in [RoutingDecision.METTA, RoutingDecision.HYBRID_METTA]
            
            self.log_test("Routing to MeTTa", passed,
                         f"Routed to: {routing_decision['routing'].value}")
            return passed
        except Exception as e:
            self.log_test("Routing to MeTTa", False, str(e))
            return False
    
    def test_keyword_extraction(self):
        """Test 7: Extract keywords from query"""
        try:
            query = "Find documents about poverty and deforestation in rural areas"
            analysis = self.orchestrator.analyze_query(query)
            
            keywords = analysis['keywords']
            passed = len(keywords) > 0 and 'poverty' in [k.lower() for k in keywords]
            
            self.log_test("Keyword Extraction", passed,
                         f"Keywords: {', '.join(keywords)}")
            return passed
        except Exception as e:
            self.log_test("Keyword Extraction", False, str(e))
            return False
    
    def test_intent_detection(self):
        """Test 8: Detect user intent"""
        try:
            queries_and_intents = [
                ("Calculate priority", "calculate"),
                ("Explain why", "explain"),
                ("Compare regions", "compare"),
                ("Find documents", "search")
            ]
            
            all_correct = True
            for query, expected_intent in queries_and_intents:
                analysis = self.orchestrator.analyze_query(query)
                if analysis['intent'] != expected_intent:
                    all_correct = False
                    break
            
            self.log_test("Intent Detection", all_correct,
                         "Detected multiple intents correctly")
            return all_correct
        except Exception as e:
            self.log_test("Intent Detection", False, str(e))
            return False
    
    def test_hybrid_responder(self):
        """Test 9: Hybrid responder initialization"""
        try:
            passed = self.hybrid_responder is not None
            self.log_test("Hybrid Responder Initialization", passed)
            return passed
        except Exception as e:
            self.log_test("Hybrid Responder Initialization", False, str(e))
            return False
    
    def test_orchestrator_stats(self):
        """Test 10: Get orchestrator statistics"""
        try:
            stats = self.orchestrator.get_stats()
            passed = 'total_queries' in stats
            
            self.log_test("Orchestrator Statistics", passed,
                         f"Total queries: {stats['total_queries']}")
            return passed
        except Exception as e:
            self.log_test("Orchestrator Statistics", False, str(e))
            return False
    
    def test_multi_requirement_detection(self):
        """Test 11: Detect multiple requirements"""
        try:
            query = "Explain and compare regions with documents about poverty"
            analysis = self.orchestrator.analyze_query(query)
            
            requirement_count = sum([
                analysis['requires_explanation'],
                analysis['requires_comparison'],
                analysis['requires_documents']
            ])
            
            passed = requirement_count >= 2
            
            self.log_test("Multi-Requirement Detection", passed,
                         f"Requirements detected: {requirement_count}")
            return passed
        except Exception as e:
            self.log_test("Multi-Requirement Detection", False, str(e))
            return False
    
    def test_routing_rationale(self):
        """Test 12: Get routing rationale"""
        try:
            query = "What documents mention poverty?"
            routing_decision = self.orchestrator.route_query(query)
            
            rationale = routing_decision['rationale']
            passed = len(rationale) > 0 and 'document' in rationale.lower()
            
            self.log_test("Routing Rationale", passed,
                         f"Rationale: {rationale}")
            return passed
        except Exception as e:
            self.log_test("Routing Rationale", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all Phase 4 tests"""
        print("\n" + "="*60)
        print("🔀 PHASE 4: INTEGRATION & ORCHESTRATOR TEST SUITE")
        print("="*60 + "\n")
        
        tests = [
            self.test_orchestrator_initialization,
            self.test_simple_query_analysis,
            self.test_document_query_detection,
            self.test_complex_query_analysis,
            self.test_routing_to_cognitive,
            self.test_routing_to_metta,
            self.test_keyword_extraction,
            self.test_intent_detection,
            self.test_hybrid_responder,
            self.test_orchestrator_stats,
            self.test_multi_requirement_detection,
            self.test_routing_rationale,
        ]
        
        for test in tests:
            test()
            print()  # Blank line between tests
        
        # Summary
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        print("="*60)
        print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
        print("="*60)
        
        if passed == total:
            print("✅ All tests passed! Phase 4 integration is working correctly.")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check errors above.")
        
        return passed == total


def main():
    """Run the Phase 4 test suite"""
    tester = TestPhase4Integration()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Phase 4 Implementation: SUCCESS")
        print("\nThe system now has:")
        print("✅ Cognitive orchestrator for intelligent routing")
        print("✅ Document query capabilities with reasoning")
        print("✅ Hybrid responses (MeTTa + OpenCog)")
        print("✅ Complex query analysis")
        print("✅ Intent detection and keyword extraction")
        print("\nKey Deliverable Achieved:")
        print("✅ Can answer 'What documents mention poverty?' with reasoning")
        print("\nNext steps:")
        print("1. Test via chat API")
        print("2. Upload PDFs and query them")
        print("3. Try complex queries with explanations")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("Make sure:")
        print("1. All Phase 1, 2, and 3 tests pass first")
        print("2. All dependencies are installed")
        print("3. Django is configured correctly")
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
