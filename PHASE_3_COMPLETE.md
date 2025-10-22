# 🎉 Phase 3: Advanced Reasoning - COMPLETE!

## What Was Implemented

Phase 3 adds **advanced reasoning capabilities** with PLN (Probabilistic Logic Networks), confidence scoring, and reasoning chain visualization - your system can now explain *why* and *how* it reached conclusions!

---

## ✅ Components Delivered

### 1. **PLN Rules Engine** (`cognitive/pln_rules.py`)

**Purpose:** Probabilistic logic-based reasoning with truth values

**Capabilities:**
- ✅ Truth values (strength + confidence)
- ✅ PLN deduction, abduction, induction
- ✅ Conjunction, disjunction, negation
- ✅ Domain-specific rules
- ✅ Rule application with confidence
- ✅ Multi-hop reasoning chains

**Example Usage:**
```python
from cognitive.pln_rules import get_pln_engine, TruthValue

pln = get_pln_engine()

# Create truth values
tv1 = TruthValue(0.9, 0.8)  # strength=0.9, confidence=0.8
tv2 = TruthValue(0.8, 0.9)

# Apply PLN deduction
result = pln.deduction(tv1, tv2)
print(f"Result: {result}")  # TV(0.720, 0.720)

# Apply domain rule
evidence = {'High_Poverty_Region': True}
rule_result = pln.apply_rule('poverty_implies_priority', evidence)
print(rule_result['conclusion'])  # 'High_Priority'
```

**Built-in PLN Rules:**
- `poverty_implies_priority` - High poverty → High priority (TV: 0.85, 0.90)
- `impact_boosts_priority` - High impact → Increased priority (TV: 0.80, 0.85)
- `corruption_reduces_allocation` - High corruption → Reduced allocation (TV: 0.75, 0.80)
- `deforestation_needs_intervention` - High deforestation → Intervention needed (TV: 0.80, 0.85)

---

### 2. **Confidence Scorer** (`cognitive/confidence_scorer.py`)

**Purpose:** Calculate confidence scores for reasoning and decisions

**Capabilities:**
- ✅ Score reasoning chains
- ✅ Score evidence quality
- ✅ Score decisions
- ✅ Compare alternatives
- ✅ Multi-factor confidence calculation

**Example Usage:**
```python
from cognitive.confidence_scorer import get_confidence_scorer

scorer = get_confidence_scorer()

# Score a reasoning chain
chain_data = [
    {'truth_value': TruthValue(0.9, 0.8)},
    {'truth_value': TruthValue(0.8, 0.7)}
]
score = scorer.score_reasoning_chain(chain_data)

print(f"Confidence: {score.overall_score:.2f}")  # 0.78
print(f"Level: {score.level}")  # 'high'
print(f"Percentage: {score.overall_score * 100:.1f}%")  # 78.0%
```

**Confidence Levels:**
- `very_high` - 0.9+ (90%+)
- `high` - 0.7-0.9 (70-90%)
- `medium` - 0.5-0.7 (50-70%)
- `low` - 0.3-0.5 (30-50%)
- `very_low` - <0.3 (<30%)

---

### 3. **Reasoning Chain Visualizer** (`cognitive/reasoning_chain.py`)

**Purpose:** Create structured, visualizable reasoning chains

**Capabilities:**
- ✅ Step-by-step reasoning chains
- ✅ Text explanations
- ✅ Graph visualization data
- ✅ Confidence tracking per step
- ✅ Evidence linking

**Example Usage:**
```python
from cognitive.reasoning_chain import get_chain_builder
from cognitive.pln_rules import TruthValue

builder = get_chain_builder()

# Start chain
chain = builder.start_chain("High priority allocation")

# Add reasoning steps
builder.add_deduction(
    premise="Region has poverty index 0.8",
    conclusion="Region classified as High Poverty",
    truth_value=TruthValue(0.9, 0.85),
    evidence=["Poverty threshold is 0.7"]
)

builder.add_deduction(
    premise="Region classified as High Poverty",
    conclusion="Region receives high priority",
    truth_value=TruthValue(0.85, 0.90),
    evidence=["Policy: Poverty Rule"]
)

# Get summary
result = builder.finalize()
print(result['confidence'])
```

**Chain Output:**
```
**Reasoning Chain: High priority allocation**

**Step 1:** Region has poverty index 0.8
  ↓ (using: Deduction)
  → Region classified as High Poverty
  Confidence: 0.85
  Evidence: Poverty threshold is 0.7

**Step 2:** Region classified as High Poverty
  ↓ (using: Deduction)
  → Region receives high priority
  Confidence: 0.90
  Evidence: Policy: Poverty Rule

**Overall Confidence:** high (0.82)
```

---

### 4. **Enhanced Reasoner** (Updated `cognitive/reasoner.py`)

**New Methods:**

#### `reason_with_pln(premises, goal)`
PLN-based reasoning from premises to goal
```python
reasoner = get_reasoner()

premises = [
    {'statement': 'High poverty', 'conclusion': 'Needs resources', 'strength': 0.9, 'confidence': 0.8},
    {'statement': 'Needs resources', 'conclusion': 'Gets priority', 'strength': 0.85, 'confidence': 0.9}
]

result = reasoner.reason_with_pln(premises, "High Priority")
```

#### `explain_with_chain(region_id)`
Full explanation with reasoning chain
```python
result = reasoner.explain_with_chain("Region_Nairobi")
print(result['text_explanation'])
print(result['confidence'])
```

#### `compare_with_confidence(region1, region2)`
Compare regions with confidence scores
```python
result = reasoner.compare_with_confidence("Region_A", "Region_B")
print(result['confidence'])
print(result['explanation'])
```

#### `multi_hop_inference(start, goal, max_hops)`
Multi-hop reasoning from start to goal
```python
result = reasoner.multi_hop_inference("Poverty", "High_Priority", max_hops=3)
print(result['steps'])
```

---

### 5. **API Endpoints** (Added to `cognitive/views.py`)

**New Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/cognitive/reason/pln/` | POST | PLN-based reasoning |
| `/api/cognitive/reason/explain-chain/` | POST | Explanation with chain |
| `/api/cognitive/reason/compare-confidence/` | POST | Compare with confidence |
| `/api/cognitive/reason/multi-hop/` | POST | Multi-hop inference |

---

## 📡 API Usage Examples

### PLN Reasoning
```bash
curl -X POST http://localhost:8000/api/cognitive/reason/pln/ \
  -H "Content-Type: application/json" \
  -d '{
    "premises": [
      {
        "statement": "Region has high poverty",
        "conclusion": "Region needs resources",
        "strength": 0.9,
        "confidence": 0.8
      },
      {
        "statement": "Region needs resources",
        "conclusion": "Region gets priority",
        "strength": 0.85,
        "confidence": 0.9
      }
    ],
    "goal": "High Priority Allocation"
  }'
```

**Response:**
```json
{
  "success": true,
  "goal": "High Priority Allocation",
  "total_steps": 2,
  "confidence": {
    "overall_score": 0.78,
    "level": "high",
    "percentage": 78.0
  },
  "steps": [
    {
      "step": 1,
      "premise": "Region has high poverty",
      "conclusion": "Region needs resources",
      "rule": "PLN Deduction",
      "truth_value": {"strength": 0.9, "confidence": 0.8}
    }
  ]
}
```

### Explain with Chain
```bash
curl -X POST http://localhost:8000/api/cognitive/reason/explain-chain/ \
  -H "Content-Type: application/json" \
  -d '{
    "region_id": "Region_Nairobi"
  }'
```

**Response:**
```json
{
  "success": true,
  "goal": "Priority decision for Region_Nairobi",
  "total_steps": 2,
  "confidence": {
    "overall_score": 0.82,
    "level": "high"
  },
  "text_explanation": "**Reasoning Chain: Priority decision for Region_Nairobi**\n\n**Step 1:** Region_Nairobi is classified as High_Poverty_Region\n  ↓ (using: Domain Rule: Poverty Classification)\n  → Region has urgent need\n  Confidence: 0.85\n\n**Step 2:** Region has urgent need\n  ↓ (using: PLN Rule: poverty_implies_priority)\n  → Region receives high priority\n  Confidence: 0.90\n\n**Overall Confidence:** high (0.82)"
}
```

### Multi-Hop Inference
```bash
curl -X POST http://localhost:8000/api/cognitive/reason/multi-hop/ \
  -H "Content-Type: application/json" \
  -d '{
    "start": "Poverty",
    "goal": "High_Priority",
    "max_hops": 3
  }'
```

---

## 🎯 Real-World Example

**Scenario:** User uploads "Kenya Poverty Assessment 2024.pdf" and asks:
"Why should Nairobi get high priority?"

**System Response (Phase 3):**

```
**Reasoning Chain: Priority Decision for Nairobi**

**Step 1:** Nairobi classified as High_Poverty_Region
  ↓ (using: Poverty Index Classification)
  → Poverty index 0.82 exceeds threshold 0.7
  Confidence: 0.90
  Evidence: Kenya Poverty Assessment 2024.pdf (page 15)

**Step 2:** High_Poverty_Region status confirmed
  ↓ (using: PLN Rule: poverty_implies_priority)
  → Region requires high priority allocation
  Confidence: 0.85
  Evidence: County Allocation Act 2024 §3.1

**Step 3:** Additional factors considered
  ↓ (using: Multi-factor Analysis)
  → Population density and impact potential assessed
  Confidence: 0.78
  Evidence: World Bank Development Indicators

**Conclusion:** Nairobi receives HIGH PRIORITY

**Overall Confidence:** High (82%)

📚 **Supporting Evidence:**
1. Kenya Poverty Assessment 2024 (Policy Document)
2. County Allocation Act 2024 §3.1 (Legal Framework)
3. World Bank Development Indicators (Data Source)

**Confidence Breakdown:**
- Data quality: 0.85 (high)
- Reasoning chain: 0.82 (high)
- Evidence support: 0.80 (high)
```

---

## 📊 What Phase 3 Enables

### Before Phase 3:
```
User: "Why does Nairobi get high priority?"
System: "Nairobi has high priority because poverty is high."
```

### With Phase 3:
```
User: "Why does Nairobi get high priority?"
System: 
"Nairobi receives high priority through the following reasoning:

STEP 1: Poverty Classification (Confidence: 90%)
  Nairobi's poverty index (0.82) exceeds the high poverty 
  threshold (0.7), classifying it as a High Poverty Region.
  Evidence: Kenya Poverty Assessment 2024, page 15

STEP 2: Policy Application (Confidence: 85%)
  Per County Allocation Act 2024 §3.1, High Poverty Regions 
  receive high priority allocation.
  Evidence: County Allocation Act 2024

STEP 3: Validation (Confidence: 78%)
  Historical data shows 85% success rate for similar 
  allocations in comparable regions (Mombasa 2022, Kisumu 2023).
  Evidence: Historical allocation records

OVERALL CONFIDENCE: High (82%)

This decision is strongly supported by policy, data, and 
historical precedent."
```

---

## 🧪 Testing Phase 3

```bash
# Run Phase 3 tests
cd civicxai_backend
python cognitive/tests/test_phase3_reasoning.py
```

**Expected Output:**
```
============================================================
🧠 PHASE 3: ADVANCED REASONING TEST SUITE
============================================================

✅ PASS - PLN Engine Initialization
    Loaded 4 PLN rules

✅ PASS - Truth Value Operations
    Deduction result: TV(0.560, 0.720)

✅ PASS - PLN Conjunction
    A ∧ B = TV(0.720, 0.800)

✅ PASS - PLN Rule Application
    Rule applied: High_Priority

✅ PASS - Confidence Scoring
    Score: 0.78, Level: high

✅ PASS - Evidence Scoring
    Evidence score: 0.82

✅ PASS - Reasoning Chain Creation
    Created chain with 1 steps

✅ PASS - Chain Confidence Calculation
    Overall confidence: 0.78

✅ PASS - Chain Text Explanation
    Generated 245 characters of explanation

✅ PASS - Chain Graph Visualization
    Generated 4 nodes, 3 edges

✅ PASS - Enhanced Reasoner Stats
    Phase 3, 4 PLN rules

✅ PASS - PLN Reasoning Integration
    Reasoning succeeded

============================================================
📊 TEST SUMMARY: 12/12 tests passed
============================================================
✅ All tests passed! Phase 3 reasoning is working correctly.
```

---

## 📁 New Files Created

```
✅ cognitive/pln_rules.py                 # PLN engine
✅ cognitive/confidence_scorer.py         # Confidence scoring
✅ cognitive/reasoning_chain.py           # Chain visualization
✅ cognitive/reasoner.py                  # ENHANCED with Phase 3 methods
✅ cognitive/views.py                     # ENHANCED with Phase 3 endpoints
✅ cognitive/urls.py                      # ENHANCED with Phase 3 routes
✅ cognitive/tests/test_phase3_reasoning.py  # Phase 3 tests
✅ PHASE_3_COMPLETE.md                    # This file
```

---

## 🎓 Key Concepts

### Truth Values
Combine **strength** (how true) and **confidence** (how sure):
- `TruthValue(0.9, 0.8)` = 90% true, 80% confident

### PLN Inference Rules
- **Deduction:** If A→B and B→C, then A→C
- **Abduction:** If A→B and B observed, then A likely
- **Induction:** Multiple instances → generalization

### Confidence Levels
- **Chain length:** Shorter chains = higher confidence
- **Truth values:** Higher TVs = higher confidence
- **Evidence:** More evidence = higher confidence

---

## 🚀 Integration Example

**In your chat system:**
```python
from cognitive import get_reasoner

reasoner = get_reasoner()

# User asks: "Why prioritize Region X?"
result = reasoner.explain_with_chain("Region_X")

# Return explanation with confidence
chat_response = f"""
{result['text_explanation']}

**Confidence Level:** {result['confidence']['level']}
**Confidence Score:** {result['confidence']['overall_score']:.0%}

📊 This explanation is based on:
- {len(result['steps'])} reasoning steps
- PLN-verified logic
- Evidence from {len(result.get('evidence', []))} sources
"""
```

---

## ✅ Verification Checklist

Before moving to Phase 4:

- [ ] Phase 1 tests pass (12/12)
- [ ] Phase 2 tests pass (12/12)
- [ ] Phase 3 tests pass (12/12)
- [ ] Can perform PLN reasoning via API
- [ ] Reasoning chains generate correctly
- [ ] Confidence scores calculate properly
- [ ] Multi-hop inference works
- [ ] Explanations include confidence levels

---

## 🎯 Success Metrics

**Phase 3 is complete when:**

✅ All 12 Phase 3 tests pass  
✅ PLN rules apply correctly  
✅ Confidence scoring works  
✅ Reasoning chains visualize  
✅ Multi-hop inference succeeds  
✅ API endpoints respond correctly  

---

## 📖 API Reference

### POST /api/cognitive/reason/pln/
**Perform PLN-based reasoning**

**Request:**
```json
{
  "premises": [
    {
      "statement": "premise text",
      "conclusion": "conclusion text",
      "strength": 0.9,
      "confidence": 0.8
    }
  ],
  "goal": "Goal statement"
}
```

**Response:** Reasoning chain with confidence

### POST /api/cognitive/reason/explain-chain/
**Get explanation with reasoning chain**

**Request:**
```json
{
  "region_id": "Region_Nairobi"
}
```

**Response:** Full reasoning chain with steps

### POST /api/cognitive/reason/multi-hop/
**Multi-hop inference**

**Request:**
```json
{
  "start": "Poverty",
  "goal": "High_Priority",
  "max_hops": 3
}
```

**Response:** Inference path with intermediate steps

---

## 🎉 Phase 3 Achievements

| Feature | Phase 1 | Phase 2 | Phase 3 |
|---------|---------|---------|---------|
| **Knowledge Storage** | ✅ Manual | ✅ Automatic | ✅ Automatic |
| **Reasoning** | Basic | Basic | **Advanced PLN** |
| **Confidence** | None | None | **Full scoring** |
| **Explanations** | Simple | Simple | **With chains** |
| **Multi-hop** | No | No | **✅ Yes** |
| **Evidence** | Basic | Auto-extracted | **Confidence-scored** |

---

## 🚀 Next: Phase 4

**Chat Integration:**
- Cognitive orchestrator (smart query routing)
- Auto-cite sources in responses
- Real-time knowledge updates
- Enhanced user experience

---

**🎉 Phase 3 Complete!** Your system now reasons like an expert, explains its thinking, and provides confidence scores! Ready for Phase 4? 🚀
