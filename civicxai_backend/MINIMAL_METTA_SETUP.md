# Minimal MeTTa Setup for Civic Allocation Domain

## Overview

This implementation follows **Minimal MeTTa** principles for the Civic Allocation domain, providing precise control over evaluation and reasoning about resource allocation in civic governance.

## Minimal MeTTa Principles Implemented

### 1. **eval** - One-Step Evaluation
```python
manager.minimal_eval("(get-poverty Region_Nairobi)")
# Returns one evaluation step: searches for (= (get-poverty Region_Nairobi) $body)
# Returns $body or NotReducible
```

**Key behaviors:**
- Searches for pattern `(= ARG $body)` in atomspace
- Returns unified `$body` if match found
- Returns `NotReducible` if no match
- Returns `Empty` if match succeeds with no bindings
- Executes grounded functions directly

### 2. **chain** - Multi-Step Evaluation
```python
manager.chain_eval("(foo)", max_steps=10)
# Chains eval steps: foo -> bar -> baz -> final_value
# Stops at NotReducible, Empty, Error, or max_steps
```

**Implementation:**
- Manually chains `eval` calls
- Detects terminal states (NotReducible, Empty, Error)
- Prevents infinite loops with max_steps

### 3. **match** - Pattern Matching Queries
```python
query = "!(match &self (EvaluationLink (PredicateNode \"hasHighPoverty\") $region) $region)"
results = manager.metta.run(query)
# Finds all regions with high poverty
```

## Civic Allocation Domain Integration

### Knowledge Base: `civic_allocation.metta`

The knowledge base is automatically loaded on initialization:

```python
manager = AtomSpaceManager(load_civic_kb=True)
```

**Structure:**
- **ConceptNodes**: Poverty, Infrastructure, Education, Healthcare, etc.
- **PredicateNodes**: hasHighPoverty, requiresInvestment, hasLowCorruption
- **EvaluationLinks**: Facts with truth values `<tv: strength confidence>`
- **ImplicationLinks**: Reasoning rules
- **SimilarityLinks**: Domain relationships
- **InheritanceLinks**: Taxonomic hierarchies

### Domain-Specific Queries

#### Query Region Allocation Data
```python
result = manager.query_civic_allocation('Region_Nairobi')
# Returns:
# {
#     'region': 'Region_Nairobi',
#     'has_high_poverty': True,
#     'requires_investment': True,
#     'corruption_level': 'low',
#     'priority': 'high'
# }
```

#### Get All Regions
```python
regions = manager.get_all_regions()
# Returns: ['Region_Nairobi', 'Region_Mombasa', 'Region_Kisumu', ...]
```

## Example Usage

### Basic Minimal MeTTa Operations

```python
from cognitive.atoms.atomspace_manager import get_atomspace_manager

# Get singleton instance (loads civic_allocation.metta automatically)
manager = get_atomspace_manager()

# Add equality rule
manager.add_atom("(= (get-region) Region_Nairobi)")

# One-step eval
result = manager.minimal_eval("(get-region)")
# Returns: Region_Nairobi

# Chained eval
manager.add_atom("(= (level-1) (level-2))")
manager.add_atom("(= (level-2) final)")
result = manager.chain_eval("(level-1)")
# Returns: final

# Check for undefined
result = manager.minimal_eval("(undefined)")
# Returns: NotReducible
```

### Civic Domain Queries

```python
# Find regions with high poverty
query = "!(match &self (EvaluationLink (PredicateNode \"hasHighPoverty\") (ListLink (ConceptNode $region))) $region)"
regions = manager.query(query)

# Query specific region data
nairobi_data = manager.query_civic_allocation('Region_Nairobi')
print(f"Nairobi poverty level: {nairobi_data['has_high_poverty']}")
print(f"Investment needed: {nairobi_data['requires_investment']}")

# Get atomspace statistics
stats = manager.get_stats()
print(f"Total regions: {stats['total_regions']}")
print(f"Civic KB loaded: {stats['civic_kb_loaded']}")
```

## Minimal MeTTa vs Standard MeTTa

| Operation | Minimal MeTTa | Standard MeTTa |
|-----------|---------------|----------------|
| `(foo)` | `(foo)` - not evaluated | Evaluated automatically |
| `!(eval (foo))` | `(bar)` - one step only | `(bar)` if reduces, else kept |
| `!(eval (baz))` | `NotReducible` | `(eval (baz))` kept unreduced |
| Chaining | Manual via chain_eval | Automatic by interpreter |
| Grounded functions | Via eval | Direct execution |

## Special Results Handling

The implementation properly handles special Minimal MeTTa results:

- **NotReducible**: No reduction rule found
- **Empty**: Match succeeded but no bindings
- **Error**: Runtime error in grounded function
  ```python
  # Example from documentation
  !(eval (pow-math 2 200000000000000))
  # Returns: (Error (pow-math 2 200000000000000) power argument is too big...)
  ```

## Testing

Run comprehensive tests:
```bash
cd civicxai_backend/cognitive/atoms
python test_minimal_metta.py
```

Tests cover:
1. Minimal eval - one step evaluation
2. Chain eval - multi-step reduction
3. Civic allocation queries
4. Match pattern queries
5. AtomSpace statistics

## Architecture

```
AtomSpaceManager
├── __init__(load_civic_kb=True)          # Initialize with civic KB
├── _load_civic_knowledge_base()          # Load civic_allocation.metta
├── minimal_eval(expr)                    # One-step eval
├── chain_eval(expr, max_steps)           # Multi-step eval with chaining
├── query_civic_allocation(region)        # Domain-specific queries
├── get_all_regions()                     # List all civic regions
└── Standard operations (add_atom, query, etc.)
```

## References

- **MeTTa Documentation**: https://metta-lang.dev/docs/learn/tutorials/eval_intro/main_concepts.html
- **Minimal MeTTa**: Core instructions (eval, chain, unify)
- **Civic Allocation KB**: `metta_files/civic_allocation.metta`

## Best Practices

1. **Use minimal_eval** for precise one-step control
2. **Use chain_eval** for full reduction with safety limits
3. **Use query** for high-level pattern matching
4. **Handle special results** (NotReducible, Empty, Error)
5. **Load civic KB** on initialization for domain knowledge
6. **Query civic_allocation** for pre-built domain queries
7. **Check stats** to verify KB loaded successfully

---

**Implementation Status**: ✅ Complete  
**Domain**: Civic Resource Allocation  
**Compliance**: Minimal MeTTa Specification
