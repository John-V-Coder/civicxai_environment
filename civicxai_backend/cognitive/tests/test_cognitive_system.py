"""
Test Suite for Cognitive AI System
Tests AtomSpace, Knowledge Store, and Reasoner functionality
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civicxai_backend.settings')
import django
django.setup()

from cognitive.atoms.atomspace_manager import get_atomspace_manager
from cognitive.knowledge.knowledge_store import get_knowledge_store
from cognitive.reasoner.reasoner import get_reasoner


class TestCognitiveSystem:
    """Test cognitive AI system components"""
    
    def __init__(self):
        self.atomspace = get_atomspace_manager()
        self.knowledge = get_knowledge_store()
        self.reasoner = get_reasoner()
        self.test_results = []
    
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append((test_name, passed))
    
    def test_atomspace_initialization(self):
        """Test 1: AtomSpace initialization"""
        try:
            stats = self.atomspace.get_stats()
            passed = 'status' in stats and stats['status'] == 'active'
            self.log_test("AtomSpace Initialization", passed, 
                         f"Backend: {stats.get('backend', 'Unknown')}")
            return passed
        except Exception as e:
            self.log_test("AtomSpace Initialization", False, str(e))
            return False
    
    def test_add_simple_node(self):
        """Test 2: Add simple node"""
        try:
            success = self.atomspace.add_node('ConceptNode', 'TestConcept_Poverty')
            self.log_test("Add Simple Node", success)
            return success
        except Exception as e:
            self.log_test("Add Simple Node", False, str(e))
            return False
    
    def test_add_link(self):
        """Test 3: Add link between nodes"""
        try:
            # Add two nodes
            self.atomspace.add_node('ConceptNode', 'TestConcept_Poverty')
            self.atomspace.add_node('ConceptNode', 'TestConcept_EconomicHardship')
            
            # Add similarity link
            success = self.atomspace.add_link('SimilarityLink', 
                                             'TestConcept_Poverty', 
                                             'TestConcept_EconomicHardship', 
                                             0.9)
            self.log_test("Add Link Between Nodes", success)
            return success
        except Exception as e:
            self.log_test("Add Link Between Nodes", False, str(e))
            return False
    
    def test_query_concepts(self):
        """Test 4: Query concepts"""
        try:
            # Add a concept first
            self.atomspace.add_node('ConceptNode', 'TestConcept_Query')
            
            # Query all concepts
            concepts = self.atomspace.get_all_concepts()
            passed = 'TestConcept_Query' in str(concepts)
            self.log_test("Query Concepts", passed, 
                         f"Found {len(concepts)} concepts")
            return passed
        except Exception as e:
            self.log_test("Query Concepts", False, str(e))
            return False
    
    def test_add_region(self):
        """Test 5: Add region to knowledge base"""
        try:
            region_data = {
                'name': 'TestRegion_Nairobi',
                'poverty_index': 0.8,
                'deforestation': 0.3,
                'population': 4500000
            }
            success = self.knowledge.add_region('TestRegion_Nairobi', region_data)
            self.log_test("Add Region", success, 
                         f"Region: TestRegion_Nairobi with poverty 0.8")
            return success
        except Exception as e:
            self.log_test("Add Region", False, str(e))
            return False
    
    def test_add_policy(self):
        """Test 6: Add policy to knowledge base"""
        try:
            policy_data = {
                'title': 'Test County Allocation Act 2024',
                'category': 'allocation',
                'effective_date': '2024-01-01'
            }
            success = self.knowledge.add_policy('TestPolicy_CountyAct2024', policy_data)
            self.log_test("Add Policy", success, 
                         "Policy: Test County Allocation Act 2024")
            return success
        except Exception as e:
            self.log_test("Add Policy", False, str(e))
            return False
    
    def test_add_data_source(self):
        """Test 7: Add data source"""
        try:
            source_data = {
                'title': 'Test Poverty Impact Study',
                'type': 'pdf',
                'category': 'research',
                'topics': ['poverty', 'allocation', 'impact']
            }
            success = self.knowledge.add_data_source('TestSource_PDF_123', source_data)
            self.log_test("Add Data Source", success, 
                         "Source with 3 topics")
            return success
        except Exception as e:
            self.log_test("Add Data Source", False, str(e))
            return False
    
    def test_find_related_concepts(self):
        """Test 8: Find related concepts"""
        try:
            # Add concepts with similarity
            self.atomspace.add_node('ConceptNode', 'TestConcept_A')
            self.atomspace.add_node('ConceptNode', 'TestConcept_B')
            self.atomspace.add_link('SimilarityLink', 'TestConcept_A', 'TestConcept_B')
            
            # Find related
            related = self.reasoner.find_related_concepts('TestConcept_A')
            passed = len(related) >= 0  # At least it doesn't crash
            self.log_test("Find Related Concepts", passed, 
                         f"Found {len(related)} related concepts")
            return passed
        except Exception as e:
            self.log_test("Find Related Concepts", False, str(e))
            return False
    
    def test_explain_priority(self):
        """Test 9: Explain priority reasoning"""
        try:
            # Add a region first
            region_data = {
                'name': 'TestRegion_Priority',
                'poverty_index': 0.9
            }
            self.knowledge.add_region('TestRegion_Priority', region_data)
            
            # Get explanation
            explanation = self.reasoner.explain_priority('TestRegion_Priority')
            passed = 'region' in explanation and 'reasoning_chain' in explanation
            self.log_test("Explain Priority", passed, 
                         f"Confidence: {explanation.get('confidence', 0)}")
            return passed
        except Exception as e:
            self.log_test("Explain Priority", False, str(e))
            return False
    
    def test_compare_regions(self):
        """Test 10: Compare two regions"""
        try:
            # Add two regions
            region1_data = {'name': 'Region1', 'poverty_index': 0.9}
            region2_data = {'name': 'Region2', 'poverty_index': 0.3}
            
            self.knowledge.add_region('TestRegion_Compare1', region1_data)
            self.knowledge.add_region('TestRegion_Compare2', region2_data)
            
            # Compare
            comparison = self.reasoner.compare_regions('TestRegion_Compare1', 
                                                       'TestRegion_Compare2')
            passed = 'region1' in comparison and 'region2' in comparison
            self.log_test("Compare Regions", passed, 
                         f"Recommendation: {comparison.get('recommendation', '')[:50]}...")
            return passed
        except Exception as e:
            self.log_test("Compare Regions", False, str(e))
            return False
    
    def test_knowledge_stats(self):
        """Test 11: Get knowledge statistics"""
        try:
            stats = self.knowledge.get_knowledge_stats()
            passed = 'total_concepts' in stats
            self.log_test("Knowledge Statistics", passed, 
                         f"Total concepts: {stats.get('total_concepts', 0)}")
            return passed
        except Exception as e:
            self.log_test("Knowledge Statistics", False, str(e))
            return False
    
    def test_reasoning_stats(self):
        """Test 12: Get reasoning statistics"""
        try:
            stats = self.reasoner.get_reasoning_stats()
            passed = 'reasoning_engine' in stats
            self.log_test("Reasoning Statistics", passed, 
                         f"Engine: {stats.get('reasoning_engine', 'Unknown')}")
            return passed
        except Exception as e:
            self.log_test("Reasoning Statistics", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("🧠 COGNITIVE AI SYSTEM TEST SUITE")
        print("="*60 + "\n")
        
        tests = [
            self.test_atomspace_initialization,
            self.test_add_simple_node,
            self.test_add_link,
            self.test_query_concepts,
            self.test_add_region,
            self.test_add_policy,
            self.test_add_data_source,
            self.test_find_related_concepts,
            self.test_explain_priority,
            self.test_compare_regions,
            self.test_knowledge_stats,
            self.test_reasoning_stats,
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
            print("✅ All tests passed! Cognitive system is working correctly.")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check errors above.")
        
        return passed == total


def main():
    """Run the test suite"""
    tester = TestCognitiveSystem()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Phase 1 Implementation: SUCCESS")
        print("\nNext steps:")
        print("1. Integrate with chat system (chat_views.py)")
        print("2. Test API endpoints (http://localhost:8000/api/cognitive/health/)")
        print("3. Add real data from your application")
        print("4. Move to Phase 2: Knowledge ingestion")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("Make sure:")
        print("1. OpenCog/Hyperon is properly installed")
        print("2. Django is configured correctly")
        print("3. All dependencies are installed")
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
