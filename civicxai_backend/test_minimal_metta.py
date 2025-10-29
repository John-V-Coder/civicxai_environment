"""
Test Minimal MeTTa setup for Civic Allocation Domain
Demonstrates eval, chain, and query operations following Minimal MeTTa principles
"""
import logging
from atomspace_manager import get_atomspace_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_minimal_eval():
    """Test Minimal MeTTa eval operation"""
    print("\n" + "="*60)
    print("TEST 1: Minimal Eval - One Step Evaluation")
    print("="*60)
    
    manager = get_atomspace_manager()
    
    # Test eval with civic allocation rules
    # According to civic_allocation.metta:
    # (= (foo) (bar)) means eval(foo) -> bar
    
    # Add test rules
    manager.add_atom("(= (test-region) Region_Nairobi)")
    manager.add_atom("(= (get-poverty Region_Nairobi) HighPoverty)")
    
    # Test one-step eval
    result1 = manager.minimal_eval("(test-region)")
    print(f"\neval (test-region) = {result1}")
    print(f"  Expected: Region_Nairobi (one step only)")
    
    result2 = manager.minimal_eval("(get-poverty Region_Nairobi)")
    print(f"\neval (get-poverty Region_Nairobi) = {result2}")
    print(f"  Expected: HighPoverty")
    
    # Test NotReducible
    result3 = manager.minimal_eval("(undefined-function)")
    print(f"\neval (undefined-function) = {result3}")
    print(f"  Expected: NotReducible")


def test_chain_eval():
    """Test chained evaluation"""
    print("\n" + "="*60)
    print("TEST 2: Chain Eval - Multiple Step Evaluation")
    print("="*60)
    
    manager = get_atomspace_manager()
    
    # Add chained rules
    manager.add_atom("(= (foo) (bar))")
    manager.add_atom("(= (bar) (baz))")
    manager.add_atom("(= (baz) final-value)")
    
    # Test chained evaluation
    result = manager.chain_eval("(foo)", max_steps=5)
    print(f"\nchain_eval (foo) with max 5 steps = {result}")
    print(f"  Expected: final-value (after 3 steps: foo->bar->baz->final-value)")


def test_civic_queries():
    """Test civic allocation queries using Minimal MeTTa"""
    print("\n" + "="*60)
    print("TEST 3: Civic Allocation Queries")
    print("="*60)
    
    manager = get_atomspace_manager()
    
    # Get all regions
    regions = manager.get_all_regions()
    print(f"\nAll regions in knowledge base: {regions}")
    
    # Query specific regions
    for region in ['Region_Nairobi', 'Region_Mombasa', 'Region_Kisumu']:
        print(f"\n--- Query: {region} ---")
        result = manager.query_civic_allocation(region)
        print(f"  High Poverty: {result.get('has_high_poverty')}")
        print(f"  Requires Investment: {result.get('requires_investment')}")
        print(f"  Corruption Level: {result.get('corruption_level')}")


def test_match_queries():
    """Test match queries from civic_allocation.metta"""
    print("\n" + "="*60)
    print("TEST 4: Match Queries (from civic_allocation.metta examples)")
    print("="*60)
    
    manager = get_atomspace_manager()
    
    # Test queries from civic_allocation.metta comments
    queries = [
        ("Find regions with high poverty", 
         "!(match &self (EvaluationLink (PredicateNode \"hasHighPoverty\") (ListLink (ConceptNode $region))) $region)"),
        
        ("Find regions requiring investment",
         "!(match &self (EvaluationLink (PredicateNode \"requiresInvestment\") $region) $region)"),
        
        ("Find all urban regions",
         "!(match &self (InheritanceLink $region (ConceptNode \"UrbanRegion\")) $region)")
    ]
    
    for description, query in queries:
        print(f"\n{description}:")
        print(f"  Query: {query}")
        results = manager.query(query)
        print(f"  Results: {results}")


def test_atomspace_stats():
    """Test atomspace statistics"""
    print("\n" + "="*60)
    print("TEST 5: AtomSpace Statistics")
    print("="*60)
    
    manager = get_atomspace_manager()
    stats = manager.get_stats()
    
    print(f"\nAtomSpace Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  MINIMAL METTA CIVIC ALLOCATION DOMAIN TESTS")
    print("  Following eval, chain, and match principles")
    print("="*70)
    
    try:
        test_minimal_eval()
        test_chain_eval()
        test_civic_queries()
        test_match_queries()
        test_atomspace_stats()
        
        print("\n" + "="*70)
        print("  ALL TESTS COMPLETED")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
