"""
Cognitive AI URL Configuration
"""
from django.urls import path
from .views import (
    CognitiveHealthView,
    AddConceptView,
    AddRegionView,
    QueryConceptsView,
    ReasoningView,
    KnowledgeStatsView,
    # Phase 2: Ingestion
    IngestPDFView,
    IngestTextView,
    InitializeDomainKnowledgeView,
    # Phase 3: Advanced Reasoning
    PLNReasoningView,
    ExplainWithChainView,
    CompareWithConfidenceView,
    MultiHopInferenceView,
    # Phase 5: Advanced Reasoning & Learning
    AdvancedPLNView,
    CausalInferenceView,
    LearningLoopView,
    KnowledgeGraphView
)

app_name = 'cognitive'

urlpatterns = [
    # Health check
    path('health/', CognitiveHealthView.as_view(), name='cognitive_health'),
    
    # Knowledge management (Phase 1)
    path('concept/', AddConceptView.as_view(), name='add_concept'),
    path('region/', AddRegionView.as_view(), name='add_region'),
    path('concepts/', QueryConceptsView.as_view(), name='query_concepts'),
    path('stats/', KnowledgeStatsView.as_view(), name='knowledge_stats'),
    
    # Reasoning (Phase 1)
    path('reason/', ReasoningView.as_view(), name='reasoning'),
    
    # Knowledge Ingestion (Phase 2)
    path('ingest/pdf/', IngestPDFView.as_view(), name='ingest_pdf'),
    path('ingest/text/', IngestTextView.as_view(), name='ingest_text'),
    path('ingest/initialize/', InitializeDomainKnowledgeView.as_view(), name='initialize_domain'),
    
    # Advanced Reasoning (Phase 3)
    path('reason/pln/', PLNReasoningView.as_view(), name='pln_reasoning'),
    path('reason/explain-chain/', ExplainWithChainView.as_view(), name='explain_with_chain'),
    path('reason/compare-confidence/', CompareWithConfidenceView.as_view(), name='compare_with_confidence'),
    path('reason/multi-hop/', MultiHopInferenceView.as_view(), name='multi_hop_inference'),
    
    # Advanced Reasoning & Learning (Phase 5)
    path('reason/advanced-pln/', AdvancedPLNView.as_view(), name='advanced_pln'),
    path('causal/', CausalInferenceView.as_view(), name='causal_inference'),
    path('learn/', LearningLoopView.as_view(), name='learning_loop'),
    path('graph/', KnowledgeGraphView.as_view(), name='knowledge_graph'),
]
