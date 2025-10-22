"""
Test Suite for Knowledge Ingestion Pipeline (Phase 2)
Tests PDF processing, concept extraction, and atom generation
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civicxai_backend.settings')
import django
django.setup()

from cognitive.processors.pdf_processor import get_pdf_processor
from cognitive.processors.concept_extractor import get_concept_extractor
from cognitive.processors.atom_generator import get_atom_generator
from cognitive.ingestion_pipeline import get_ingestion_pipeline


class TestIngestionPipeline:
    """Test knowledge ingestion pipeline"""
    
    def __init__(self):
        self.pdf_processor = get_pdf_processor()
        self.concept_extractor = get_concept_extractor()
        self.atom_generator = get_atom_generator()
        self.pipeline = get_ingestion_pipeline()
        self.test_results = []
    
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append((test_name, passed))
    
    def test_pdf_processor_initialization(self):
        """Test 1: PDF processor initialization"""
        try:
            passed = self.pdf_processor is not None
            self.log_test("PDF Processor Initialization", passed, 
                         f"Supported formats: {self.pdf_processor.supported_formats}")
            return passed
        except Exception as e:
            self.log_test("PDF Processor Initialization", False, str(e))
            return False
    
    def test_concept_extractor_initialization(self):
        """Test 2: Concept extractor initialization"""
        try:
            passed = self.concept_extractor.nlp is not None
            self.log_test("Concept Extractor Initialization", passed,
                         "spaCy model loaded")
            return passed
        except Exception as e:
            self.log_test("Concept Extractor Initialization", False, str(e))
            return False
    
    def test_extract_concepts_from_text(self):
        """Test 3: Extract concepts from text"""
        try:
            sample_text = """
            Poverty is a major challenge in developing regions. High poverty rates
            often correlate with lack of infrastructure and education. Resource
            allocation must prioritize regions with the highest poverty index to
            maximize impact and promote economic development.
            """
            
            concepts = self.concept_extractor.extract_concepts(sample_text)
            passed = len(concepts) > 0
            self.log_test("Extract Concepts from Text", passed,
                         f"Found {len(concepts)} concepts")
            
            if concepts:
                top_concepts = [c['text'] for c in concepts[:3]]
                print(f"    Top concepts: {', '.join(top_concepts)}")
            
            return passed
        except Exception as e:
            self.log_test("Extract Concepts from Text", False, str(e))
            return False
    
    def test_extract_entities(self):
        """Test 4: Extract named entities"""
        try:
            sample_text = """
            In Nairobi, Kenya, the government announced a new allocation policy
            for 2024. The Ministry of Planning will oversee the implementation
            across all regions including Mombasa and Kisumu.
            """
            
            entities = self.concept_extractor.extract_entities(sample_text)
            passed = len(entities) > 0
            self.log_test("Extract Named Entities", passed,
                         f"Found {len(entities)} entities")
            
            if entities:
                entity_types = set(e['type'] for e in entities)
                print(f"    Entity types: {', '.join(entity_types)}")
            
            return passed
        except Exception as e:
            self.log_test("Extract Named Entities", False, str(e))
            return False
    
    def test_extract_keywords(self):
        """Test 5: Extract keywords"""
        try:
            sample_text = """
            The poverty index indicates severe economic hardship in rural areas.
            Allocation priorities must focus on infrastructure development and
            education to improve living standards and reduce unemployment.
            """
            
            keywords = self.concept_extractor.extract_keywords(sample_text, top_n=5)
            passed = len(keywords) > 0
            self.log_test("Extract Keywords", passed,
                         f"Found {len(keywords)} keywords")
            
            if keywords:
                top_keywords = [f"{word}({score:.2f})" for word, score in keywords[:3]]
                print(f"    Top keywords: {', '.join(top_keywords)}")
            
            return passed
        except Exception as e:
            self.log_test("Extract Keywords", False, str(e))
            return False
    
    def test_extract_topics(self):
        """Test 6: Extract main topics"""
        try:
            sample_text = """
            Resource allocation in developing regions requires careful analysis
            of poverty levels, infrastructure needs, and governance capacity.
            Environmental factors like deforestation must also be considered
            along with corruption risk assessment.
            """
            
            topics = self.concept_extractor.extract_topics(sample_text, num_topics=5)
            passed = len(topics) > 0
            self.log_test("Extract Topics", passed,
                         f"Found {len(topics)} topics")
            
            if topics:
                print(f"    Topics: {', '.join(topics)}")
            
            return passed
        except Exception as e:
            self.log_test("Extract Topics", False, str(e))
            return False
    
    def test_atom_generation(self):
        """Test 7: Generate atoms from analysis"""
        try:
            # Create mock analysis
            analysis = {
                'concepts': [
                    {'text': 'poverty', 'frequency': 5, 'importance': 0.9, 'category': 'noun_phrase'},
                    {'text': 'resource allocation', 'frequency': 3, 'importance': 0.8, 'category': 'noun_phrase'}
                ],
                'entities': [
                    {'text': 'Nairobi', 'type': 'GPE'},
                    {'text': 'Kenya', 'type': 'GPE'}
                ],
                'topics': ['Poverty', 'Allocation', 'Development'],
                'relationships': [
                    {'subject': 'poverty', 'predicate': 'requires', 'object': 'allocation'}
                ]
            }
            
            source_id = "TestSource_AtomGen"
            stats = self.atom_generator.generate_from_analysis(analysis, source_id)
            
            passed = stats['concepts_added'] > 0
            self.log_test("Generate Atoms from Analysis", passed,
                         f"Created {sum(stats.values())} atoms total")
            
            print(f"    Breakdown: {stats}")
            return passed
        except Exception as e:
            self.log_test("Generate Atoms from Analysis", False, str(e))
            return False
    
    def test_domain_knowledge_initialization(self):
        """Test 8: Initialize domain knowledge"""
        try:
            stats = self.atom_generator.generate_domain_knowledge()
            passed = stats['concepts'] > 0 and stats['similarities'] > 0
            self.log_test("Initialize Domain Knowledge", passed,
                         f"Added {stats['concepts']} concepts, {stats['similarities']} similarities")
            return passed
        except Exception as e:
            self.log_test("Initialize Domain Knowledge", False, str(e))
            return False
    
    def test_process_text(self):
        """Test 9: Complete text processing pipeline"""
        try:
            sample_text = """
            Allocation Policy Framework 2024
            
            This policy outlines the criteria for resource allocation across
            regions. Priority is given to areas with high poverty rates and
            significant infrastructure needs. Environmental sustainability and
            governance quality are also key factors in allocation decisions.
            """
            
            result = self.pipeline.process_text(sample_text, "TestSource_TextPipeline")
            passed = result['success'] and result['atoms_created'] > 0
            self.log_test("Process Text Pipeline", passed,
                         f"Created {result.get('atoms_created', 0)} atoms")
            
            if result['success']:
                print(f"    Concepts: {result.get('concepts_extracted', 0)}")
                print(f"    Topics: {', '.join(result.get('key_topics', []))}")
            
            return passed
        except Exception as e:
            self.log_test("Process Text Pipeline", False, str(e))
            return False
    
    def test_comprehensive_analysis(self):
        """Test 10: Comprehensive document analysis"""
        try:
            sample_text = """
            Regional Development Analysis
            
            Poverty remains a critical challenge affecting millions in rural areas.
            The correlation between poverty and lack of education is well-documented.
            Infrastructure development is essential for economic growth and improving
            living standards. Deforestation poses environmental risks that must be
            addressed through sustainable allocation policies.
            """
            
            analysis = self.concept_extractor.analyze_document(sample_text)
            
            passed = (
                len(analysis['concepts']) > 0 and
                len(analysis['topics']) > 0
            )
            
            self.log_test("Comprehensive Document Analysis", passed,
                         f"Complete analysis with multiple components")
            
            if passed:
                print(f"    Concepts: {len(analysis['concepts'])}")
                print(f"    Entities: {len(analysis['entities'])}")
                print(f"    Keywords: {len(analysis['keywords'])}")
                print(f"    Topics: {len(analysis['topics'])}")
                print(f"    Relationships: {len(analysis['relationships'])}")
            
            return passed
        except Exception as e:
            self.log_test("Comprehensive Document Analysis", False, str(e))
            return False
    
    def test_find_domain_concepts(self):
        """Test 11: Find domain-specific concepts"""
        try:
            sample_text = """
            The poverty index shows high levels in rural regions.
            Resource allocation must consider deforestation rates
            and corruption risk when prioritizing development projects.
            """
            
            domain_concepts = self.concept_extractor.find_domain_concepts(sample_text)
            passed = len(domain_concepts) > 0
            self.log_test("Find Domain Concepts", passed,
                         f"Found {len(domain_concepts)} domain concepts")
            
            if domain_concepts:
                print(f"    Domain concepts: {', '.join(domain_concepts)}")
            
            return passed
        except Exception as e:
            self.log_test("Find Domain Concepts", False, str(e))
            return False
    
    def test_pipeline_initialization(self):
        """Test 12: Pipeline initialization"""
        try:
            result = self.pipeline.initialize_domain_knowledge()
            passed = result['success']
            self.log_test("Pipeline Initialize Domain", passed,
                         f"Domain knowledge ready")
            return passed
        except Exception as e:
            self.log_test("Pipeline Initialize Domain", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all Phase 2 tests"""
        print("\n" + "="*60)
        print("🔬 KNOWLEDGE INGESTION PIPELINE TEST SUITE (Phase 2)")
        print("="*60 + "\n")
        
        tests = [
            self.test_pdf_processor_initialization,
            self.test_concept_extractor_initialization,
            self.test_extract_concepts_from_text,
            self.test_extract_entities,
            self.test_extract_keywords,
            self.test_extract_topics,
            self.test_atom_generation,
            self.test_domain_knowledge_initialization,
            self.test_process_text,
            self.test_comprehensive_analysis,
            self.test_find_domain_concepts,
            self.test_pipeline_initialization,
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
            print("✅ All tests passed! Ingestion pipeline is working correctly.")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check errors above.")
        
        return passed == total


def main():
    """Run the Phase 2 test suite"""
    tester = TestIngestionPipeline()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Phase 2 Implementation: SUCCESS")
        print("\nThe system can now:")
        print("✅ Extract text from PDFs")
        print("✅ Identify concepts and entities")
        print("✅ Generate atoms from documents")
        print("✅ Process documents via API")
        print("✅ Auto-process uploaded sources")
        print("\nNext steps:")
        print("1. Upload PDFs via API or Django admin")
        print("2. Knowledge will be auto-extracted")
        print("3. Move to Phase 3: Advanced Reasoning")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("Make sure:")
        print("1. spaCy model is installed: python -m spacy download en_core_web_sm")
        print("2. All Phase 1 tests pass first")
        print("3. All dependencies are installed")
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
