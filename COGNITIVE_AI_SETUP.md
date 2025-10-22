# 🧠 Cognitive AI Phase 1: Installation & Setup Guide

## Overview

Phase 1 implements the **foundation layer** for OpenCog Cognitive AI integration:
- ✅ AtomSpace manager for knowledge storage
- ✅ Knowledge store with domain-specific methods
- ✅ Basic reasoning engine with pattern matching
- ✅ REST API endpoints for cognitive operations
- ✅ Test suite to verify functionality

---

## 📋 Prerequisites

### System Requirements
- Python 3.9 or higher
- Windows 10/11 (your current environment)
- 4GB RAM minimum (8GB recommended)
- Django 5.1+ (already installed)

---

## 🚀 Installation Steps

### Step 1: Install Dependencies

```bash
cd civicxai_backend

# Install cognitive AI packages
pip install opencog==0.1.4
pip install hyperon==0.1.12
pip install spacy==3.7.2
pip install sentence-transformers==2.3.1
pip install celery==5.3.6
pip install redis==5.0.1
pip install cython==3.0.8

# Download spaCy language model
python -m spacy download en_core_web_sm
```

**Or install all at once:**
```bash
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
# Test if Hyperon/MeTTa is working
python -c "from hyperon import *; print('✅ Hyperon installed successfully')"

# Test spaCy
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ spaCy installed successfully')"
```

### Step 3: Run Tests

```bash
# Run the cognitive system test suite
python cognitive/tests/test_cognitive_system.py
```

**Expected Output:**
```
============================================================
🧠 COGNITIVE AI SYSTEM TEST SUITE
============================================================

✅ PASS - AtomSpace Initialization
    Backend: Hyperon/MeTTa

✅ PASS - Add Simple Node

✅ PASS - Add Link Between Nodes

✅ PASS - Query Concepts
    Found X concepts

... (more tests)

============================================================
📊 TEST SUMMARY: 12/12 tests passed
============================================================
✅ All tests passed! Cognitive system is working correctly.
```

---

## 🔧 Configuration

### Optional: Redis Setup (for Background Jobs - Phase 2)

```bash
# Install Redis (if not already installed)
# Windows: Download from https://github.com/microsoftarchive/redis/releases

# Start Redis server
redis-server
```

---

## 📡 API Endpoints

Once your Django server is running (`python manage.py runserver`), you can access:

### 1. Health Check
```http
GET http://localhost:8000/api/cognitive/health/
```

**Response:**
```json
{
  "status": "healthy",
  "atomspace": {
    "total_concepts": 0,
    "status": "active",
    "backend": "Hyperon/MeTTa"
  },
  "knowledge_base": {
    "regions": 0,
    "policies": 0,
    "data_sources": 0
  },
  "message": "Cognitive AI system is operational"
}
```

### 2. Add Concept
```http
POST http://localhost:8000/api/cognitive/concept/
Content-Type: application/json

{
  "concept_name": "Poverty",
  "concept_type": "ConceptNode",
  "properties": {
    "description": "Economic hardship condition"
  }
}
```

### 3. Add Region
```http
POST http://localhost:8000/api/cognitive/region/
Content-Type: application/json

{
  "region_id": "Region_Nairobi",
  "region_data": {
    "name": "Nairobi",
    "poverty_index": 0.8,
    "deforestation": 0.3,
    "population": 4500000
  }
}
```

### 4. Query Concepts
```http
GET http://localhost:8000/api/cognitive/concepts/
GET http://localhost:8000/api/cognitive/concepts/?concept=Poverty
```

### 5. Reasoning Operations
```http
POST http://localhost:8000/api/cognitive/reason/
Content-Type: application/json

{
  "operation": "explain_priority",
  "parameters": {
    "region_id": "Region_Nairobi"
  }
}
```

**Supported Operations:**
- `explain_priority` - Explain why a region has certain priority
- `compare_regions` - Compare two regions
- `find_evidence` - Find evidence for a decision
- `generate_recommendation` - Generate recommendation for a query

### 6. Knowledge Statistics
```http
GET http://localhost:8000/api/cognitive/stats/
```

---

## 🧪 Testing with curl/Postman

### Test 1: Health Check
```bash
curl http://localhost:8000/api/cognitive/health/
```

### Test 2: Add a Region
```bash
curl -X POST http://localhost:8000/api/cognitive/region/ \
  -H "Content-Type: application/json" \
  -d '{
    "region_id": "Region_Test",
    "region_data": {
      "name": "Test Region",
      "poverty_index": 0.7
    }
  }'
```

### Test 3: Explain Priority
```bash
curl -X POST http://localhost:8000/api/cognitive/reason/ \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "explain_priority",
    "parameters": {
      "region_id": "Region_Test"
    }
  }'
```

---

## 🐍 Python Integration Example

```python
# In your Django views or scripts
from cognitive.atomspace_manager import get_atomspace_manager
from cognitive.knowledge_store import get_knowledge_store
from cognitive.reasoner import get_reasoner

# Get singleton instances
atomspace = get_atomspace_manager()
knowledge = get_knowledge_store()
reasoner = get_reasoner()

# Add a region to knowledge base
region_data = {
    'name': 'Nairobi',
    'poverty_index': 0.8,
    'deforestation': 0.3
}
knowledge.add_region('Region_Nairobi', region_data)

# Explain priority
explanation = reasoner.explain_priority('Region_Nairobi')
print(explanation)

# Get statistics
stats = knowledge.get_knowledge_stats()
print(f"Total concepts: {stats['total_concepts']}")
```

---

## 📂 Project Structure

```
civicxai_backend/
├── cognitive/                      # NEW: Cognitive AI module
│   ├── __init__.py
│   ├── atomspace_manager.py       # AtomSpace wrapper
│   ├── knowledge_store.py         # Domain knowledge interface
│   ├── reasoner.py                # Reasoning engine
│   ├── views.py                   # REST API endpoints
│   ├── urls.py                    # URL routing
│   └── tests/
│       └── test_cognitive_system.py  # Test suite
│
├── explainable_ai/
│   ├── urls.py                    # MODIFIED: Added cognitive routes
│   └── ...
│
└── requirements.txt               # MODIFIED: Added cognitive dependencies
```

---

## ✅ Verification Checklist

After installation, verify:

- [ ] All dependencies installed without errors
- [ ] Test suite passes (12/12 tests)
- [ ] Health endpoint returns `"status": "healthy"`
- [ ] Can add concepts via API
- [ ] Can add regions via API
- [ ] Can query concepts
- [ ] Can perform reasoning operations
- [ ] AtomSpace manager is accessible
- [ ] Knowledge store is functional
- [ ] Reasoner produces explanations

---

## 🎯 What You Can Do Now

### 1. Add Knowledge
```python
# Add concepts
knowledge.add_concept_similarity('Poverty', 'Economic_Hardship', 0.9)
knowledge.add_causal_relationship('High_Poverty', 'Requires_Allocation', 0.85)

# Add regions from your database
from explainable_ai.models import Region

for region in Region.objects.all():
    knowledge.add_region(f'Region_{region.region_id}', {
        'name': region.name,
        'poverty_index': region.poverty_index,
        'deforestation': region.deforestation_rate,
        'population': region.population
    })
```

### 2. Perform Basic Reasoning
```python
# Explain priority
explanation = reasoner.explain_priority('Region_Nairobi')
print(explanation['reasoning_chain'])

# Compare regions
comparison = reasoner.compare_regions('Region_A', 'Region_B')
print(comparison['recommendation'])

# Find related concepts
related = reasoner.find_related_concepts('Poverty', depth=2)
print(related)
```

### 3. Query Knowledge
```python
# Get all concepts
concepts = atomspace.get_all_concepts()

# Get statistics
stats = knowledge.get_knowledge_stats()

# Find high poverty regions
high_poverty_regions = knowledge.get_regions_by_poverty_level('high')
```

---

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'hyperon'"

**Solution:**
```bash
pip install opencog hyperon
```

### Issue: "Can't find spaCy model 'en_core_web_sm'"

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: "AtomSpace initialization failed"

**Solution:**
1. Check if Hyperon is properly installed
2. Verify Python version (3.9+)
3. Try reinstalling: `pip uninstall hyperon && pip install hyperon`

### Issue: Tests fail with import errors

**Solution:**
```bash
# Make sure Django is set up
export DJANGO_SETTINGS_MODULE=civicxai_backend.settings
# Or on Windows:
set DJANGO_SETTINGS_MODULE=civicxai_backend.settings

python cognitive/tests/test_cognitive_system.py
```

---

## 📊 Performance Notes

### Current Capabilities (Phase 1)
- ✅ Basic knowledge storage and retrieval
- ✅ Simple pattern matching
- ✅ Direct relationship queries
- ✅ Basic reasoning with 1-2 hop inference
- ⚡ Fast for < 1000 concepts

### Limitations (To be addressed in Phase 2+)
- ❌ No multi-hop reasoning (3+ hops)
- ❌ No probabilistic inference yet
- ❌ No automatic knowledge extraction from PDFs
- ❌ No background learning

---

## 🚀 Next Steps (Phase 2)

Once Phase 1 is working:

1. **Knowledge Ingestion Pipeline**
   - Automatic PDF text extraction
   - NLP concept extraction
   - Batch import of existing data sources

2. **Enhanced Reasoning**
   - Multi-hop causal inference
   - Probabilistic Logic Networks (PLN)
   - Confidence scoring

3. **Integration with Chat**
   - Cognitive orchestrator
   - Route complex queries to reasoning engine
   - Generate explanations with evidence

4. **Background Workers**
   - Celery tasks for async processing
   - Periodic knowledge base building
   - Automatic relationship discovery

---

## 📝 Notes

- Phase 1 provides the **foundation** - basic storage and retrieval
- The system is **read-heavy** - optimized for queries over writes
- AtomSpace is **in-memory** - consider persistence for production
- All operations are **synchronous** in Phase 1

---

## 🆘 Getting Help

If you encounter issues:

1. Check test output: `python cognitive/tests/test_cognitive_system.py`
2. Verify health endpoint: `curl http://localhost:8000/api/cognitive/health/`
3. Check Django logs for errors
4. Ensure all dependencies are installed: `pip list | grep -E "hyperon|opencog|spacy"`

---

## ✨ Success Criteria

Phase 1 is complete when:

✅ All 12 tests pass  
✅ Health endpoint returns healthy status  
✅ Can add and query concepts via API  
✅ Basic reasoning operations work  
✅ No import or dependency errors  

**You're now ready to move to Phase 2!** 🎉
