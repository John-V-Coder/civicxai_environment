# 🚀 Phase 3: Quick Start Guide

## Test Phase 3 (2 minutes)

```bash
cd civicxai_backend

# Run Phase 3 tests
python cognitive/tests/test_phase3_reasoning.py

# Expected: ✅ 12/12 tests passed
```

---

## Try PLN Reasoning (1 minute)

```bash
# Start server
python manage.py runserver

# In another terminal, test PLN reasoning
curl -X POST http://localhost:8000/api/cognitive/reason/pln/ \
  -H "Content-Type: application/json" \
  -d '{
    "premises": [
      {
        "statement": "Region has high poverty",
        "conclusion": "Region needs resources",
        "strength": 0.9,
        "confidence": 0.8
      }
    ],
    "goal": "High Priority Allocation"
  }'
```

**Response:**
```json
{
  "success": true,
  "confidence": {
    "overall_score": 0.78,
    "level": "high"
  }
}
```

---

## Get Explanation with Chain (30 seconds)

First, add a test region:
```bash
curl -X POST http://localhost:8000/api/cognitive/region/ \
  -H "Content-Type: application/json" \
  -d '{
    "region_id": "Region_Test",
    "region_data": {"poverty_index": 0.8}
  }'
```

Then get explanation:
```bash
curl -X POST http://localhost:8000/api/cognitive/reason/explain-chain/ \
  -H "Content-Type: application/json" \
  -d '{
    "region_id": "Region_Test"
  }'
```

---

## Use in Python (1 minute)

```python
from cognitive import get_reasoner
from cognitive.pln_rules import TruthValue

reasoner = get_reasoner()

# PLN reasoning
premises = [
    {
        'statement': 'High poverty',
        'conclusion': 'Needs resources',
        'strength': 0.9,
        'confidence': 0.8
    }
]
result = reasoner.reason_with_pln(premises, "High Priority")
print(f"Confidence: {result['confidence']}")

# Explain with chain
explanation = reasoner.explain_with_chain("Region_Test")
print(explanation['text_explanation'])
```

---

## Key Features

### 1. PLN Reasoning
```python
from cognitive.pln_rules import get_pln_engine, TruthValue

pln = get_pln_engine()
tv1 = TruthValue(0.9, 0.8)
tv2 = TruthValue(0.8, 0.9)
result = pln.deduction(tv1, tv2)
```

### 2. Confidence Scoring
```python
from cognitive.confidence_scorer import get_confidence_scorer

scorer = get_confidence_scorer()
score = scorer.score_reasoning_chain(chain_data)
print(f"Confidence: {score.level} ({score.overall_score:.0%})")
```

### 3. Reasoning Chains
```python
from cognitive.reasoning_chain import get_chain_builder

builder = get_chain_builder()
chain = builder.start_chain("Goal")
chain.add_step("Premise", "Conclusion", "Rule", TruthValue(0.9, 0.8))
summary = chain.get_chain_summary()
```

---

## Verify Everything Works

```bash
# Check stats (should show Phase 3)
curl http://localhost:8000/api/cognitive/stats/

# Should see:
# "reasoning_engine": "PLN + Pattern Matching (Phase 3)"
# "phase": 3
# "pln_rules_count": 4
```

---

## What You Can Do Now

✅ **PLN-based reasoning** with truth values  
✅ **Confidence scoring** for all decisions  
✅ **Reasoning chains** with step-by-step explanations  
✅ **Multi-hop inference** across concepts  
✅ **Enhanced explanations** with evidence  

---

## Troubleshooting

### Tests fail?
```bash
# Make sure Phase 1 & 2 pass first
python cognitive/tests/test_cognitive_system.py
python cognitive/tests/test_ingestion_pipeline.py
```

### API not working?
```bash
# Check health
curl http://localhost:8000/api/cognitive/health/

# Check stats
curl http://localhost:8000/api/cognitive/stats/
```

---

## Next Steps

1. ✅ Phase 1: Foundation
2. ✅ Phase 2: Knowledge Ingestion  
3. ✅ Phase 3: Advanced Reasoning
4. **→ Phase 4: Chat Integration**

**Phase 3 Complete! 🎉** Your system now reasons with confidence!
