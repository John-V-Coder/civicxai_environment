# Setting Up MeTTa for CivicXAI

## 🚀 Quick Start

MeTTa (Meta Type Talk) is already integrated into CivicXAI! This guide shows how to use and extend it.

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Install Hyperon (MeTTa's Python Implementation)

```bash
# Install the Hyperon library
pip install hyperon

# Or if you have issues, try:
pip install git+https://github.com/singnet/hyperon.git
```

## 🧪 Test the Installation

```bash
cd civicxai_backend/metta

# Run the example (no dependencies required)
python example_usage.py

# If Hyperon is installed, run the full test
python test_metta.py
```

## 📝 MeTTa Files in This Project

### 1. **civic_policies.metta** - Basic Rules
Simple weighted scoring system:
```metta
(: poverty_weight Float)
(= poverty_weight 0.40)

(: calculate_priority (-> Float Float Float Float Float))
(= (calculate_priority $poverty $impact $environment $corruption)
   ...)
```

### 2. **civic_policies_enhanced.metta** - Advanced Rules
Comprehensive symbolic reasoning:
- Emergency overrides
- Environmental bonuses
- Risk classifications
- Explanation generation
- Meta-reasoning capabilities

### 3. **metta_engine_enhanced.py** - Python Integration
Enhanced engine with:
- Result caching
- Fallback mechanisms
- Comprehensive analysis
- Region comparison
- Custom query support

## 🔧 Basic Usage

### Python Code
```python
from metta_engine_enhanced import EnhancedCivicMeTTaEngine

# Initialize the engine
engine = EnhancedCivicMeTTaEngine()

# Calculate priority for a region
score = engine.calculate_priority(
    poverty=0.8,      # High poverty
    impact=0.6,       # Medium impact
    environment=0.5,  # Average environment
    corruption=0.3    # Some corruption risk
)

print(f"Priority Score: {score}")
print(f"Budget Allocation: {score * 100}%")
```

### Expected Output
```
Priority Score: 0.5700
Budget Allocation: 57.00%
```

## 🎯 Advanced Usage

### Comprehensive Analysis
```python
analysis = engine.analyze_allocation(
    poverty=0.75,
    impact=0.65,
    environment=0.55,
    corruption=0.35
)

print(f"Score: {analysis['score']}")
print(f"Priority: {analysis['priority_level']}")
print(f"Risk: {analysis['risk_assessment']}")
print(f"Allocation: {analysis['allocation_percentage']}%")
```

### Compare Regions
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
print(f"Recommended: {comparison['recommended_priority']}")
```

## 🔍 Writing MeTTa Rules

### Basic Rule Structure
```metta
;; Define a type
(: MyRule Type)

;; Define a constant
(: MY_CONSTANT Number)
(= MY_CONSTANT 0.5)

;; Define a function
(: my_function (-> Number Number Number))
(= (my_function $input1 $input2)
   (+ (* $input1 MY_CONSTANT) $input2))

;; Pattern matching
(= (classify $value)
   (if (> $value 0.7) high
       (if (> $value 0.3) medium
           low)))
```

### Adding New Rules

1. Edit `civic_policies_enhanced.metta`
2. Add your rule:
```metta
;; New rule for population density factor
(: population_density_bonus (-> Number Number))
(= (population_density_bonus $density)
   (if (> $density 0.8) 0.05 0.0))
```

3. Use in Python:
```python
result = engine.run_custom_query("!(population_density_bonus 0.9)")
```

## 🛠️ Troubleshooting

### Import Error: No module named 'hyperon'
```bash
# Solution: Install Hyperon
pip install hyperon

# Alternative: Use the example without Hyperon
python example_usage.py
```

### MeTTa Syntax Error
- Check parentheses balance
- Verify type declarations
- Ensure all variables start with $

### Performance Issues
- Enable caching in metta_engine_enhanced.py
- Use fallback calculations for non-critical operations
- Consider batch processing for multiple calculations

## 📚 Resources

### Official Documentation
- **MeTTa Language**: https://metta-lang.dev/
- **Tutorial**: https://metta-lang.dev/tutorials/
- **Examples**: https://github.com/singnet/hyperon/tree/main/python/tests

### SingularityNET
- **Website**: https://singularitynet.io/
- **GitHub**: https://github.com/singnet
- **AGI Research**: https://agi.singularitynet.io/

### Academic Papers
- "MeTTa: A Language for AGI" - SingularityNET Foundation
- "Symbolic AI for Transparent Decision Making" - Various authors

## 🎓 Learning Path

1. **Start Simple**: Run `example_usage.py` to understand concepts
2. **Test Basic**: Try `test_metta.py` with Hyperon installed
3. **Explore Rules**: Read `civic_policies_enhanced.metta`
4. **Modify Rules**: Add your own policy rules
5. **Integrate**: Use in Django views for API endpoints

## 🔮 Advanced Topics

### Combining with Machine Learning
```python
# Use MeTTa for feature engineering
features = engine.analyze_allocation(...)

# Feed to ML model
ml_model.predict(features['score'], features['priority_level'])
```

### Multi-Agent Systems
```python
# Create multiple MeTTa agents
agent1 = EnhancedCivicMeTTaEngine('policy1.metta')
agent2 = EnhancedCivicMeTTaEngine('policy2.metta')

# Consensus mechanism
score1 = agent1.calculate_priority(...)
score2 = agent2.calculate_priority(...)
consensus = (score1 + score2) / 2
```

## ✅ Verification

Run this to verify MeTTa is working:

```python
from metta_engine_enhanced import EnhancedCivicMeTTaEngine

engine = EnhancedCivicMeTTaEngine()
score = engine.calculate_priority(0.5, 0.5, 0.5, 0.5)

if 0.3 <= score <= 0.4:
    print("✅ MeTTa is working correctly!")
else:
    print("❌ Check MeTTa configuration")
```

## 💡 Tips

1. **Keep rules simple**: Complex rules are harder to debug
2. **Use comments**: Document your MeTTa rules thoroughly
3. **Test incrementally**: Test each rule before adding more
4. **Cache results**: Use the caching feature for performance
5. **Provide fallbacks**: Always have Python fallbacks

---

**MeTTa brings transparent, explainable AI to CivicXAI's fund allocation decisions!**
