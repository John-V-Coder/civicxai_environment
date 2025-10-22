# MeTTa Symbolic AI Integration Documentation

## 🧠 What is MeTTa?

**MeTTa** (Meta Type Talk) is a programming language designed for Artificial General Intelligence (AGI) research, developed by [SingularityNET](https://singularitynet.io/). It combines symbolic AI with modern programming paradigms to create transparent, explainable AI systems.

**Official Documentation**: https://metta-lang.dev/

## 🎯 Purpose in CivicXAI

In CivicXAI, MeTTa serves as the **symbolic reasoning engine** that ensures:
- **Transparent** fund allocation decisions
- **Rule-based** priority calculations
- **Explainable** AI outputs
- **Policy compliance** enforcement

## 📚 Core Concepts

### 1. **Atoms and Types**
MeTTa uses atoms as fundamental units of computation:
```metta
(: poverty-index (-> Number Number))
(: Region Type)
```

### 2. **Rules and Functions**
Define symbolic rules for decision-making:
```metta
(= (calculate-priority $poverty $impact $environment $corruption)
   (- (+ (* $poverty 0.4) (* $impact 0.3) (* $environment 0.2))
      (* $corruption 0.1)))
```

### 3. **Pattern Matching**
MeTTa excels at pattern matching for complex reasoning:
```metta
(= (classify-priority $score)
   (if (>= $score 0.7) critical
       (if (>= $score 0.4) high
           (if (>= $score 0.2) medium low))))
```

## 🏗️ Architecture

```
civicxai_backend/metta/
├── civic_policies.metta           # Basic policy rules
├── civic_policies_enhanced.metta  # Advanced symbolic rules
├── metta_engine.py                # Basic MeTTa integration
├── metta_engine_enhanced.py      # Enhanced engine with caching
└── test_metta.py                  # Test suite and examples
```

## 📝 Policy Rules Implementation

### Weight-Based Scoring System

The MeTTa engine implements a weighted scoring system:

| Factor | Weight | Description |
|--------|--------|-------------|
| **Poverty Index** | 40% | Socioeconomic need indicator |
| **Project Impact** | 30% | Expected community benefit |
| **Environmental Score** | 20% | Sustainability rating |
| **Corruption Risk** | -10% | Risk penalty (negative weight) |

### MeTTa Rule Definition
```metta
;;;; Weight Constants ;;;;
(: POVERTY_WEIGHT Number)
(= POVERTY_WEIGHT 0.40)

(: IMPACT_WEIGHT Number)
(= IMPACT_WEIGHT 0.30)

(: ENVIRONMENT_WEIGHT Number)
(= ENVIRONMENT_WEIGHT 0.20)

(: CORRUPTION_PENALTY Number)
(= CORRUPTION_PENALTY 0.10)
```

## 🔧 Python Integration

### Basic Usage
```python
from metta_engine_enhanced import EnhancedCivicMeTTaEngine

# Initialize engine
engine = EnhancedCivicMeTTaEngine()

# Calculate priority
score = engine.calculate_priority(
    poverty=0.8,
    impact=0.6,
    environment=0.5,
    corruption=0.3
)
print(f"Priority Score: {score}")
```

### Comprehensive Analysis
```python
# Perform full analysis
analysis = engine.analyze_allocation(
    poverty=0.75,
    impact=0.65,
    environment=0.55,
    corruption=0.35
)

print(f"Score: {analysis['score']}")
print(f"Priority Level: {analysis['priority_level']}")
print(f"Risk Assessment: {analysis['risk_assessment']}")
print(f"Allocation: {analysis['allocation_percentage']}%")
```

### Region Comparison
```python
region1 = {
    "name": "Northern Region",
    "poverty": 0.85,
    "impact": 0.60,
    "environment": 0.45,
    "corruption": 0.40
}

region2 = {
    "name": "Central Region",
    "poverty": 0.55,
    "impact": 0.80,
    "environment": 0.70,
    "corruption": 0.25
}

comparison = engine.compare_regions(region1, region2)
print(f"Recommended Priority: {comparison['recommended_priority']}")
```

## 🎯 Advanced Features

### 1. **Emergency Override**
Automatically prioritizes regions with extreme poverty:
```metta
(= (emergency-override $poverty)
   (> $poverty 0.8))
```

### 2. **Environmental Bonus**
Rewards projects with excellent environmental scores:
```metta
(= (environmental-bonus $env-score)
   (if (> $env-score 0.8) 0.1 0.0))
```

### 3. **Risk Classification**
Categorizes corruption risk levels:
```metta
(= (assess-corruption-risk $corruption)
   (if (> $corruption 0.7) high-risk
       (if (> $corruption 0.4) medium-risk
           low-risk)))
```

### 4. **Explanation Generation**
Generates human-readable explanations:
```metta
(= (explain-factor poverty $value)
   (if (> $value 0.7)
       "Critical poverty level requiring immediate intervention"
       "Moderate poverty level"))
```

## 🧪 Testing

Run the test suite to verify MeTTa integration:

```bash
cd civicxai_backend/metta
python test_metta.py
```

Expected output:
```
============================================================
  Basic Priority Calculation
============================================================

Region: Kampala - High Poverty
  Inputs: P=0.8, I=0.6, E=0.5, C=0.3
  Priority Score: 0.5700
  Allocation: 57.00%

Region: Gulu - Balanced Factors
  Inputs: P=0.5, I=0.7, E=0.8, C=0.2
  Priority Score: 0.5500
  Allocation: 55.00%
```

## 🔍 Direct MeTTa Queries

You can run custom MeTTa queries:

```python
# Get policy weights
result = engine.run_custom_query("!(get-weights)")

# Classify a score
result = engine.run_custom_query("!(classify-priority 0.75)")

# Check emergency status
result = engine.run_custom_query("!(emergency-override 0.85)")
```

## 🚀 Performance Optimizations

### 1. **Result Caching**
The enhanced engine caches frequently used calculations:
```python
self._cache = {}  # In-memory cache for calculations
```

### 2. **Fallback Mechanisms**
If MeTTa execution fails, Python fallbacks ensure continuity:
```python
def _fallback_calculation(self, poverty, impact, environment, corruption):
    return (poverty * 0.40 + impact * 0.30 + 
            environment * 0.20 - corruption * 0.10)
```

### 3. **Input Validation**
All inputs are validated before processing:
```python
def validate_inputs(self, *values):
    return all(0 <= v <= 1 for v in values)
```

## 📊 MeTTa vs Traditional Approaches

| Aspect | MeTTa (Symbolic AI) | Traditional ML |
|--------|-------------------|----------------|
| **Transparency** | ✅ Fully explainable rules | ❌ Black box |
| **Interpretability** | ✅ Human-readable logic | ❌ Complex matrices |
| **Auditability** | ✅ Clear decision paths | ❌ Opaque processes |
| **Flexibility** | ✅ Easy rule modification | ❌ Requires retraining |
| **Speed** | ✅ Instant execution | ❌ Training time needed |

## 🔗 API Integration

The MeTTa engine integrates with Django views:

```python
# In views.py
from metta.metta_engine_enhanced import get_metta_engine

def calculate_allocation(request):
    engine = get_metta_engine()
    
    # Extract parameters
    poverty = float(request.data.get('poverty_index'))
    impact = float(request.data.get('project_impact'))
    environment = float(request.data.get('environmental_score'))
    corruption = float(request.data.get('corruption_risk'))
    
    # Use MeTTa for calculation
    analysis = engine.analyze_allocation(
        poverty, impact, environment, corruption
    )
    
    return Response(analysis)
```

## 🎓 Learning Resources

1. **MeTTa Official Docs**: https://metta-lang.dev/
2. **SingularityNET**: https://singularitynet.io/
3. **Hyperon Framework**: https://github.com/singnet/hyperon
4. **AGI Research**: https://agi.singularitynet.io/

## 🔮 Future Enhancements

1. **Machine Learning Integration**
   - Use MeTTa for feature engineering
   - Combine symbolic rules with neural networks

2. **Dynamic Rule Learning**
   - Adjust weights based on outcomes
   - Learn new rules from data patterns

3. **Multi-Agent Reasoning**
   - Distributed MeTTa agents
   - Consensus mechanisms for decisions

4. **Advanced Explanations**
   - Natural language generation
   - Visual reasoning graphs

## 📌 Key Takeaways

- MeTTa provides **transparent, rule-based** decision making
- All allocation decisions are **fully explainable**
- The system can be **audited and verified**
- Rules can be **modified without retraining**
- Combines the best of **symbolic AI and modern programming**

---

**MeTTa ensures that CivicXAI's fund allocation decisions are transparent, fair, and explainable - essential qualities for public governance systems.**
