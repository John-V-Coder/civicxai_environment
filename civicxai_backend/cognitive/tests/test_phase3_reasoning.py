"""
Test Suite for Phase 3: Advanced Reasoning
Tests PLN rules, confidence scoring, and reasoning chains
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civicxai_backend.settings')
import django
django.setup()

from cognitive.pln_rules import get_pln_engine, TruthValue
from cognitive.confidence_scorer import get_confidence_scorer
from cognitive.reasoning_chain import get_chain_builder
from cognitive.reasoner import get_reasoner


class TestPhase3Reasoning:
    """Test Phase 3 advanced reasoning capabilities"""
    
    def __init__(self):
        self.pln_engine = get_pln_engine()
        self.confidence_scorer = get_confidence_scorer()
        self.chain_builder = get_chain_builder()
        self.reasoner = get_reasoner()
        self.test_results = []
    
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append((test_name, passed))
    
    def test_pln_engine_initialization(self):
        """Test 1: PLN engine initialization"""
        try:
            rules = self.pln_engine.get_all_rules()
            passed = len(rules) > 0
            self.log_test("PLN Engine Initialization", passed,
                         f"Loaded {len(rules)} PLN rules")
            return passed
        except Exception as e:
            self.log_test("PLN Engine Initialization", False, str(e))
            return False
    
    def test_truth_value_operations(self):
        """Test 2: Truth value operations"""
        try:
            tv1 = TruthValue(0.8, 0.9)
            tv2 = TruthValue(0.7, 0.8)
            
            # Test deduction
            result = self.pln_engine.deduction(tv1, tv2)
            passed = 0.0 <= result.strength <= 1.0 and 0.0 <= result.confidence <= 1.0
            
            self.log_test("Truth Value Operations", passed,
                         f"Deduction result: {result}")
            return passed
        except Exception as e:
            self.log_test("Truth Value Operations", False, str(e))
            return False
    
    def test_pln_conjunction(self):
        """Test 3: PLN conjunction"""
        try:
            tv1 = TruthValue(0.9, 0.8)
            tv2 = TruthValue(0.8, 0.9)
            
            result = self.pln_engine.conjunction(tv1, tv2)
            passed = result.strength < min(tv1.strength, tv2.strength)
            
            self.log_test("PLN Conjunction", passed,
                         f"A ∧ B = {result}")
            return passed
        except Exception as e:
            self.log_test("PLN Conjunction", False, str(e))
            return False
    
    def test_pln_rule_application(self):
        """Test 4: PLN rule application"""
        try:
            evidence = {'High_Poverty_Region': True}
            result = self.pln_engine.apply_rule('poverty_implies_priority', evidence)
            
            passed = result is not None and result['applied']
            
            self.log_test("PLN Rule Application", passed,
                         f"Rule applied: {result['conclusion'] if result else 'none'}")
            return passed
        except Exception as e:
            self.log_test("PLN Rule Application", False, str(e))
            return False
    
    def test_confidence_scoring(self):
        """Test 5: Confidence scoring"""
        try:
            chain_data = [
                {'truth_value': TruthValue(0.9, 0.8)},
                {'truth_value': TruthValue(0.8, 0.7)}
            ]
            
            score = self.confidence_scorer.score_reasoning_chain(chain_data)
            passed = 0.0 <= score.overall_score <= 1.0
            
            self.log_test("Confidence Scoring", passed,
                         f"Score: {score.overall_score:.2f}, Level: {score.level}")
            return passed
        except Exception as e:
            self.log_test("Confidence Scoring", False, str(e))
            return False
    
    def test_evidence_scoring(self):
        """Test 6: Evidence quality scoring"""
        try:
            evidence = [
                {'type': 'policy', 'relevance': 0.9},
                {'type': 'research', 'relevance': 0.8},
                {'type': 'data', 'relevance': 0.85}
            ]
            
            score = self.confidence_scorer.score_evidence(evidence)
            passed = score.overall_score > 0.0
            
            self.log_test("Evidence Scoring", passed,
                         f"Evidence score: {score.overall_score:.2f}")
            return passed
        except Exception as e:
            self.log_test("Evidence Scoring", False, str(e))
            return False
    
    def test_reasoning_chain_creation(self):
        """Test 7: Reasoning chain creation"""
        try:
            chain = self.chain_builder.start_chain("Test Goal")
            
            tv = TruthValue(0.9, 0.8)
            chain.add_step(
                premise="Test Premise",
                conclusion="Test Conclusion",
                rule="Test Rule",
                truth_value=tv,
                evidence=["Evidence 1", "Evidence 2"]
            )
            
            summary = chain.get_chain_summary()
            passed = summary['total_steps'] == 1
            
            self.log_test("Reasoning Chain Creation", passed,
                         f"Created chain with {summary['total_steps']} steps")
            return passed
        except Exception as e:
            self.log_test("Reasoning Chain Creation", False, str(e))
            return False
    
    def test_chain_confidence_calculation(self):
        """Test 8: Chain confidence calculation"""
        try:
            chain = self.chain_builder.start_chain("Test Goal")
            
            chain.add_step("P1", "C1", "Rule1", TruthValue(0.9, 0.8))
            chain.add_step("C1", "C2", "Rule2", TruthValue(0.8, 0.7))
            
            confidence = chain.calculate_confidence()
            passed = 'overall_score' in confidence
            
            self.log_test("Chain Confidence Calculation", passed,
                         f"Overall confidence: {confidence.get('overall_score', 0):.2f}")
            return passed
        except Exception as e:
            self.log_test("Chain Confidence Calculation", False, str(e))
            return False
    
    def test_chain_text_explanation(self):
        """Test 9: Chain text explanation"""
        try:
            chain = self.chain_builder.start_chain("Test Goal")
            chain.add_step("Premise", "Conclusion", "Rule", TruthValue(0.9, 0.8))
            
            text = chain.current_chain.to_text_explanation()
            passed = len(text) > 0 and "Step 1" in text
            
            self.log_test("Chain Text Explanation", passed,
                         f"Generated {len(text)} characters of explanation")
            return passed
        except Exception as e:
            self.log_test("Chain Text Explanation", False, str(e))
            return False
    
    def test_chain_graph_data(self):
        """Test 10: Chain graph visualization data"""
        try:
            chain = self.chain_builder.start_chain("Test Goal")
            chain.add_step("P1", "C1", "Rule1", TruthValue(0.9, 0.8))
            chain.add_step("C1", "C2", "Rule2", TruthValue(0.8, 0.7))
            
            graph_data = chain.current_chain.to_graph_data()
            passed = 'nodes' in graph_data and 'edges' in graph_data
            
            self.log_test("Chain Graph Visualization", passed,
                         f"Generated {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges")
            return passed
        except Exception as e:
            self.log_test("Chain Graph Visualization", False, str(e))
            return False
    
    def test_enhanced_reasoner_stats(self):
        """Test 11: Enhanced reasoner statistics"""
        try:
            stats = self.reasoner.get_reasoning_stats()
            passed = (
                'pln_rules_count' in stats and
                'phase' in stats and
                stats['phase'] == 3
            )
            
            self.log_test("Enhanced Reasoner Stats", passed,
                         f"Phase {stats.get('phase', 0)}, {stats.get('pln_rules_count', 0)} PLN rules")
            return passed
        except Exception as e:
            self.log_test("Enhanced Reasoner Stats", False, str(e))
            return False
    
    def test_pln_reasoning_integration(self):
        """Test 12: PLN reasoning integration"""
        try:
            premises = [
                {
                    'statement': 'Region has high poverty',
                    'conclusion': 'Region needs resources',
                    'strength': 0.9,
                    'confidence': 0.8
                },
                {
                    'statement': 'Region needs resources',
                    'conclusion': 'Region gets priority',
                    'strength': 0.85,
                    'confidence': 0.9
                }
            ]
            
            result = self.reasoner.reason_with_pln(premises, "High Priority Allocation")
            passed = result.get('success', False)
            
            self.log_test("PLN Reasoning Integration", passed,
                         f"Reasoning {'succeeded' if passed else 'failed'}")
            return passed
        except Exception as e:
            self.log_test("PLN Reasoning Integration", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all Phase 3 tests"""
        print("\n" + "="*60)
        print("🧠 PHASE 3: ADVANCED REASONING TEST SUITE")
        print("="*60 + "\n")
        
        tests = [
            self.test_pln_engine_initialization,
            self.test_truth_value_operations,
            self.test_pln_conjunction,
            self.test_pln_rule_application,
            self.test_confidence_scoring,
            self.test_evidence_scoring,
            self.test_reasoning_chain_creation,
            self.test_chain_confidence_calculation,
            self.test_chain_text_explanation,
            self.test_chain_graph_data,
            self.test_enhanced_reasoner_stats,
            self.test_pln_reasoning_integration,
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
            print("✅ All tests passed! Phase 3 reasoning is working correctly.")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check errors above.")
        
        return passed == total


def main():
    """Run the Phase 3 test suite"""
    tester = TestPhase3Reasoning()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Phase 3 Implementation: SUCCESS")
        print("\nThe system now has:")
        print("✅ PLN-based reasoning with truth values")
        print("✅ Confidence scoring for decisions")
        print("✅ Reasoning chain visualization")
        print("✅ Multi-hop inference")
        print("✅ Enhanced explanations")
        print("\nNext steps:")
        print("1. Test via API endpoints")
        print("2. Integrate with chat system")
        print("3. Move to Phase 4: Chat Integration")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("Make sure:")
        print("1. All Phase 1 and 2 tests pass first")
        print("2. All dependencies are installed")
        print("3. Django is configured correctly")
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
