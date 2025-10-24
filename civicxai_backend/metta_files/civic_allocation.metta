; ================================================================
; Civic Allocation Knowledge Base in MeTTa
; Based on OpenCog Hyperon and MeTTa Language Documentation
; ================================================================
; 
; Key Concepts from MeTTa Documentation:
; 1. Atomspace - Knowledge database with query engine
; 2. Atoms - Fundamental building blocks (nodes or links)
; 3. Knowledge Graphs - Atoms connected via links
; 4. Truth Values - Probabilistic reasoning with <tv: strength confidence>
;
; Reference: https://metta-lang.dev/docs/learn/tutorials/eval_intro/main_concepts.html
; ================================================================

; ================================================================
; CONCEPT NODES - Define key civic concepts
; ================================================================

; Resource allocation domains
(: Poverty ConceptNode)
(: Infrastructure ConceptNode)
(: Education ConceptNode)
(: Healthcare ConceptNode)
(: Environment ConceptNode)
(: Corruption ConceptNode)
(: ProjectImpact ConceptNode)

; Allocation priorities
(: HighPriority ConceptNode)
(: MediumPriority ConceptNode)
(: LowPriority ConceptNode)

; Risk levels
(: HighRisk ConceptNode)
(: MediumRisk ConceptNode)
(: LowRisk ConceptNode)

; ================================================================
; REGION NODES - Kenya regions
; ================================================================

(: Region_Nairobi ConceptNode)
(: Region_Mombasa ConceptNode)
(: Region_Kisumu ConceptNode)
(: Region_Nakuru ConceptNode)
(: Region_Eldoret ConceptNode)

; Region types
(: UrbanRegion ConceptNode)
(: RuralRegion ConceptNode)

; ================================================================
; PREDICATE NODES - Define relationships
; ================================================================

; Poverty-related
(: hasHighPoverty PredicateNode)
(: hasModeratePoverty PredicateNode)
(: hasLowPoverty PredicateNode)

; Investment-related
(: requiresInvestment PredicateNode)
(: requiresUrgentIntervention PredicateNode)
(: hasGoodInfrastructure PredicateNode)

; Risk-related
(: hasHighCorruption PredicateNode)
(: hasLowCorruption PredicateNode)
(: hasHighRisk PredicateNode)

; Impact-related
(: hasHighImpact PredicateNode)
(: hasEnvironmentalBenefit PredicateNode)

; ================================================================
; EVALUATION LINKS - Facts about regions
; Format: (EvaluationLink <tv: strength confidence> predicate target)
; strength = belief (0.0-1.0)
; confidence = certainty (0.0-1.0)
; ================================================================

; Nairobi - Urban region with high poverty but high impact potential
(EvaluationLink <tv: 0.85 0.95>
  (PredicateNode "hasHighPoverty")
  (ListLink
    (ConceptNode "Region_Nairobi")
  )
)

(EvaluationLink <tv: 0.90 0.98>
  (PredicateNode "hasHighImpact")
  (ListLink
    (ConceptNode "Region_Nairobi")
    (ConceptNode "Healthcare")
  )
)

(EvaluationLink <tv: 0.75 0.88>
  (PredicateNode "hasHighImpact")
  (ListLink
    (ConceptNode "Region_Nairobi")
    (ConceptNode "Education")
  )
)

(EvaluationLink <tv: 0.30 0.85>
  (PredicateNode "hasLowCorruption")
  (ListLink
    (ConceptNode "Region_Nairobi")
  )
)

(EvaluationLink <tv: 0.65 0.90>
  (PredicateNode "hasGoodInfrastructure")
  (ListLink
    (ConceptNode "Region_Nairobi")
  )
)

; Mombasa - Coastal region with moderate conditions
(EvaluationLink <tv: 0.70 0.92>
  (PredicateNode "hasModeratePoverty")
  (ListLink
    (ConceptNode "Region_Mombasa")
  )
)

(EvaluationLink <tv: 0.80 0.95>
  (PredicateNode "hasHighImpact")
  (ListLink
    (ConceptNode "Region_Mombasa")
    (ConceptNode "Infrastructure")
  )
)

(EvaluationLink <tv: 0.55 0.88>
  (PredicateNode "hasLowCorruption")
  (ListLink
    (ConceptNode "Region_Mombasa")
  )
)

; Kisumu - Rural region requiring intervention
(EvaluationLink <tv: 0.92 0.97>
  (PredicateNode "hasHighPoverty")
  (ListLink
    (ConceptNode "Region_Kisumu")
  )
)

(EvaluationLink <tv: 0.85 0.93>
  (PredicateNode "requiresUrgentIntervention")
  (ListLink
    (ConceptNode "Region_Kisumu")
  )
)

(EvaluationLink <tv: 0.78 0.91>
  (PredicateNode "hasLowCorruption")
  (ListLink
    (ConceptNode "Region_Kisumu")
  )
)

(EvaluationLink <tv: 0.88 0.95>
  (PredicateNode "hasHighImpact")
  (ListLink
    (ConceptNode "Region_Kisumu")
    (ConceptNode "Education")
  )
)

; ================================================================
; IMPLICATION LINKS - Reasoning rules for allocation
; Format: (ImplicationLink <tv> condition consequence)
; ================================================================

; Rule 1: High poverty + Low corruption → Requires investment
(ImplicationLink <tv: 0.90 0.95>
  (AndLink
    (EvaluationLink
      (PredicateNode "hasHighPoverty")
      (VariableNode "$region")
    )
    (EvaluationLink
      (PredicateNode "hasLowCorruption")
      (VariableNode "$region")
    )
  )
  (EvaluationLink
    (PredicateNode "requiresInvestment")
    (VariableNode "$region")
  )
)

; Rule 2: High poverty + Urgent intervention → High priority
(ImplicationLink <tv: 0.95 0.98>
  (AndLink
    (EvaluationLink
      (PredicateNode "hasHighPoverty")
      (VariableNode "$region")
    )
    (EvaluationLink
      (PredicateNode "requiresUrgentIntervention")
      (VariableNode "$region")
    )
  )
  (EvaluationLink
    (PredicateNode "hasHighPriority")
    (VariableNode "$region")
  )
)

; Rule 3: High corruption → High risk
(ImplicationLink <tv: 0.85 0.90>
  (EvaluationLink
    (PredicateNode "hasHighCorruption")
    (VariableNode "$region")
  )
  (EvaluationLink
    (PredicateNode "hasHighRisk")
    (VariableNode "$region")
  )
)

; Rule 4: High impact + Low corruption → Good investment
(ImplicationLink <tv: 0.88 0.93>
  (AndLink
    (EvaluationLink
      (PredicateNode "hasHighImpact")
      (ListLink
        (VariableNode "$region")
        (VariableNode "$domain")
      )
    )
    (EvaluationLink
      (PredicateNode "hasLowCorruption")
      (VariableNode "$region")
    )
  )
  (EvaluationLink
    (PredicateNode "requiresInvestment")
    (VariableNode "$region")
  )
)

; ================================================================
; SIMILARITY LINKS - Common-sense relationships
; Based on: Use Case: Common-sense inference (Image 3)
; ================================================================

; Healthcare and Education are similar domains
(SimilarityLink <tv: 0.80 0.90>
  (ConceptNode "Healthcare")
  (ConceptNode "Education")
)

; Infrastructure and Environment are related
(SimilarityLink <tv: 0.70 0.85>
  (ConceptNode "Infrastructure")
  (ConceptNode "Environment")
)

; Urban and Rural regions have different needs
(SimilarityLink <tv: 0.40 0.80>
  (ConceptNode "UrbanRegion")
  (ConceptNode "RuralRegion")
)

; ================================================================
; INHERITANCE LINKS - Taxonomic relationships
; ================================================================

; Nairobi is an urban region
(InheritanceLink
  (ConceptNode "Region_Nairobi")
  (ConceptNode "UrbanRegion")
)

; Mombasa is an urban region
(InheritanceLink
  (ConceptNode "Region_Mombasa")
  (ConceptNode "UrbanRegion")
)

; Kisumu is a rural region
(InheritanceLink
  (ConceptNode "Region_Kisumu")
  (ConceptNode "RuralRegion")
)

; Nakuru is a rural region
(InheritanceLink
  (ConceptNode "Region_Nakuru")
  (ConceptNode "RuralRegion")
)

; ================================================================
; CONTEXT LINKS - Contextual information for semantic inference
; Based on: Use Case: Semantic visual inference (Image 4)
; ================================================================

(ContextLink <tv: 0.90 0.92>
  (ConceptNode "Region_Nairobi")
  (ConceptNode "RequiresUrbanPlanning")
)

(ContextLink <tv: 0.85 0.88>
  (ConceptNode "Region_Kisumu")
  (ConceptNode "RequiresRuralDevelopment")
)

; ================================================================
; QUERIES - Example queries for allocation reasoning
; ================================================================

; To use in Python:
; 
; # Find all regions with high poverty
; query = "(match &space (EvaluationLink (PredicateNode \"hasHighPoverty\") $region) $region)"
; results = metta.run(query)
;
; # Find regions requiring investment
; query = "(match &space (EvaluationLink (PredicateNode \"requiresInvestment\") $region) $region)"
; results = metta.run(query)
;
; # Find all urban regions
; query = "(match &space (InheritanceLink $region (ConceptNode \"UrbanRegion\")) $region)"
; results = metta.run(query)

; ================================================================
; END OF KNOWLEDGE BASE
; ================================================================
