# 🚀 Phase 4: Quick Start Guide

## Test Phase 4 (2 minutes)

```bash
cd civicxai_backend

# Run Phase 4 tests
python cognitive/tests/test_phase4_integration.py

# Expected: ✅ 12/12 tests passed
```

---

## Try Document Query (Key Deliverable!)

```bash
# Start server
python manage.py runserver

# In another terminal, test document query
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What documents mention poverty?"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "**Document Search Results**\n\nFound **X documents** mentioning: poverty...",
  "intent": "search"
}
```

---

## Test Intelligent Routing (1 minute)

### Simple Query → MeTTa
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate priority score"}'
```

### Complex Query → Cognitive
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain why poverty leads to priority with evidence"}'
```

### Hybrid Query → MeTTa + OpenCog
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate priority for poverty 0.8 and explain"}'
```

---

## Use in Python

```python
from cognitive import get_orchestrator, get_hybrid_responder

# Analyze and route query
orchestrator = get_orchestrator()
routing = orchestrator.route_query("What documents mention poverty?")

print(f"Routes to: {routing['routing'].value}")
print(f"Rationale: {routing['rationale']}")

# Get hybrid response
responder = get_hybrid_responder()
enhanced = responder.combine_metta_with_reasoning(
    metta_result, query, context
)
```

---

## Test All Query Types

```bash
# Document queries
curl -X POST http://localhost:8000/api/chat/ \
  -d '{"message": "What documents mention poverty?"}'

curl -X POST http://localhost:8000/api/chat/ \
  -d '{"message": "Find sources about allocation"}'

# Simple calculations
curl -X POST http://localhost:8000/api/chat/ \
  -d '{"message": "Calculate priority"}'

# Complex reasoning
curl -X POST http://localhost:8000/api/chat/ \
  -d '{"message": "Why does poverty lead to priority?"}'

# Hybrid queries
curl -X POST http://localhost:8000/api/chat/ \
  -d '{"message": "Calculate and explain with evidence"}'
```

---

## Check Orchestrator Stats

```python
from cognitive import get_orchestrator

orchestrator = get_orchestrator()
stats = orchestrator.get_stats()

print(f"Total queries: {stats['total_queries']}")
print(f"MeTTa: {stats['percentages']['metta']:.1f}%")
print(f"Cognitive: {stats['percentages']['cognitive']:.1f}%")
print(f"Hybrid: {stats['percentages']['hybrid']:.1f}%")
```

---

## Verify Everything Works

```bash
# Run all tests
python cognitive/tests/test_cognitive_system.py      # Phase 1: 12/12
python cognitive/tests/test_ingestion_pipeline.py    # Phase 2: 12/12
python cognitive/tests/test_phase3_reasoning.py      # Phase 3: 12/12
python cognitive/tests/test_phase4_integration.py    # Phase 4: 12/12

# Total: 48/48 tests should pass ✅
```

---

## Troubleshooting

### Tests fail?
```bash
# Make sure all previous phases pass
python cognitive/tests/test_cognitive_system.py
python cognitive/tests/test_ingestion_pipeline.py
python cognitive/tests/test_phase3_reasoning.py
```

### Document queries return empty?
```bash
# Initialize domain knowledge first
curl -X POST http://localhost:8000/api/cognitive/ingest/initialize/

# Upload some test documents
curl -X POST http://localhost:8000/api/cognitive/ingest/pdf/ \
  -F "file=@test_document.pdf"
```

### Routing not working?
```bash
# Check chat API is accessible
curl http://localhost:8000/api/chat/ -X OPTIONS

# Check cognitive health
curl http://localhost:8000/api/cognitive/health/
```

---

## What You Can Do Now

✅ **Document Queries:** "What documents mention X?"  
✅ **Intelligent Routing:** Automatic system selection  
✅ **Hybrid Responses:** Combined MeTTa + OpenCog  
✅ **Reasoning Chains:** Step-by-step explanations  
✅ **Source Citation:** Automatic document references  
✅ **Confidence Scoring:** All responses scored  

---

## Complete System Test

```bash
# 1. Initialize knowledge
curl -X POST http://localhost:8000/api/cognitive/ingest/initialize/

# 2. Upload a document
curl -X POST http://localhost:8000/api/cognitive/ingest/pdf/ \
  -F "file=@policy_document.pdf"

# 3. Query the document
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What documents mention allocation?"}'

# 4. Get complex explanation
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain allocation priorities with evidence"}'

# ✅ All should work!
```

---

## Next Steps

1. ✅ Phase 1: Foundation - Complete
2. ✅ Phase 2: Knowledge Ingestion - Complete
3. ✅ Phase 3: Advanced Reasoning - Complete
4. ✅ Phase 4: Chat Integration - Complete

**🎉 Your Cognitive AI System is Complete!**

**Production Checklist:**
- [ ] All 48 tests pass
- [ ] Upload your real documents
- [ ] Test all query types
- [ ] Configure for production environment
- [ ] Deploy!

---

**Phase 4 Complete!** 🚀 Your system can now intelligently route queries, search documents with reasoning, and provide hybrid responses!
