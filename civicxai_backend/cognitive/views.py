"""
Cognitive AI API Views
REST API endpoints for cognitive operations
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import JsonResponse

# Lazy imports - imported within methods to avoid loading heavy dependencies during Django startup


class CognitiveHealthView(APIView):
    """
    Check cognitive system health
    GET /api/cognitive/health/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            from .atoms.atomspace_manager import get_atomspace_manager
            from .knowledge.knowledge_store import get_knowledge_store
            from .reasoner.reasoner import get_reasoner
            
            atomspace = get_atomspace_manager()
            knowledge = get_knowledge_store()
            reasoner = get_reasoner()
            
            stats = atomspace.get_stats()
            knowledge_stats = knowledge.get_knowledge_stats()
            reasoning_stats = reasoner.get_reasoning_stats()
            
            return Response({
                'status': 'healthy',
                'atomspace': stats,
                'knowledge_base': knowledge_stats,
                'reasoning_engine': reasoning_stats,
                'message': 'Cognitive AI system is operational'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'error': str(e),
                'message': 'Cognitive system is not available'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddConceptView(APIView):
    """
    Add a concept to the knowledge base
    POST /api/cognitive/concept/
    
    Body:
    {
        "concept_name": "Poverty",
        "concept_type": "ConceptNode",
        "properties": {"description": "Economic hardship"}
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            concept_name = request.data.get('concept_name')
            concept_type = request.data.get('concept_type', 'ConceptNode')
            properties = request.data.get('properties', {})
            
            if not concept_name:
                return Response({
                    'error': 'concept_name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from .atoms.atomspace_manager import get_atomspace_manager
            atomspace = get_atomspace_manager()
            
            # Add node
            success = atomspace.add_node(concept_type, concept_name)
            
            # Add properties if provided
            if properties:
                success = atomspace.add_concept_with_properties(concept_name, properties)
            
            if success:
                return Response({
                    'success': True,
                    'concept': concept_name,
                    'message': f'Concept {concept_name} added successfully'
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': 'Failed to add concept'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddRegionView(APIView):
    """
    Add a region to the knowledge base
    POST /api/cognitive/region/
    
    Body:
    {
        "region_id": "Region_Nairobi",
        "region_data": {
            "name": "Nairobi",
            "poverty_index": 0.8,
            "deforestation": 0.3
        }
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            region_id = request.data.get('region_id')
            region_data = request.data.get('region_data', {})
            
            if not region_id:
                return Response({
                    'error': 'region_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from .knowledge.knowledge_store import get_knowledge_store
            knowledge = get_knowledge_store()
            success = knowledge.add_region(region_id, region_data)
            
            if success:
                return Response({
                    'success': True,
                    'region_id': region_id,
                    'message': f'Region {region_id} added to knowledge base'
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': 'Failed to add region'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QueryConceptsView(APIView):
    """
    Query concepts in the knowledge base
    GET /api/cognitive/concepts/?concept=Poverty
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            concept = request.query_params.get('concept')
            
            from .atoms.atomspace_manager import get_atomspace_manager
            atomspace = get_atomspace_manager()
            
            if concept:
                # Find related concepts
                related = atomspace.get_related_concepts(concept)
                return Response({
                    'concept': concept,
                    'related_concepts': related,
                    'count': len(related)
                }, status=status.HTTP_200_OK)
            else:
                # Get all concepts
                all_concepts = atomspace.get_all_concepts()
                return Response({
                    'concepts': all_concepts,
                    'count': len(all_concepts)
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReasoningView(APIView):
    """
    Perform reasoning operations
    POST /api/cognitive/reason/
    
    Body:
    {
        "operation": "explain_priority",
        "parameters": {
            "region_id": "Region_Nairobi"
        }
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            operation = request.data.get('operation')
            parameters = request.data.get('parameters', {})
            
            if not operation:
                return Response({
                    'error': 'operation is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from .reasoner.reasoner import get_reasoner
            reasoner = get_reasoner()
            
            # Route to appropriate reasoning operation
            if operation == 'explain_priority':
                region_id = parameters.get('region_id')
                if not region_id:
                    return Response({
                        'error': 'region_id is required for explain_priority'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                result = reasoner.explain_priority(region_id)
                return Response(result, status=status.HTTP_200_OK)
            
            elif operation == 'compare_regions':
                region1 = parameters.get('region1')
                region2 = parameters.get('region2')
                if not region1 or not region2:
                    return Response({
                        'error': 'Both region1 and region2 are required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                result = reasoner.compare_regions(region1, region2)
                return Response(result, status=status.HTTP_200_OK)
            
            elif operation == 'find_evidence':
                decision = parameters.get('decision')
                context = parameters.get('context', {})
                
                result = reasoner.find_evidence_for_decision(decision, context)
                return Response({
                    'evidence': result,
                    'count': len(result)
                }, status=status.HTTP_200_OK)
            
            elif operation == 'generate_recommendation':
                query = parameters.get('query')
                context = parameters.get('context', {})
                
                if not query:
                    return Response({
                        'error': 'query is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                result = reasoner.generate_recommendation(query, context)
                return Response(result, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    'error': f'Unknown operation: {operation}',
                    'supported_operations': [
                        'explain_priority',
                        'compare_regions',
                        'find_evidence',
                        'generate_recommendation'
                    ]
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KnowledgeStatsView(APIView):
    """
    Get knowledge base statistics
    GET /api/cognitive/stats/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            from .knowledge.knowledge_store import get_knowledge_store
            knowledge = get_knowledge_store()
            stats = knowledge.get_knowledge_stats()
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== Phase 2: Knowledge Ingestion Views =====

class IngestPDFView(APIView):
    """
    Ingest knowledge from PDF file
    POST /api/cognitive/ingest/pdf/
    
    Body (multipart/form-data):
    - file: PDF file
    - source_id: Unique identifier for this source
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Get uploaded file
            if 'file' not in request.FILES:
                return Response({
                    'error': 'No file provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            uploaded_file = request.FILES['file']
            source_id = request.data.get('source_id', f"Source_{uploaded_file.name}")
            
            # Read file bytes
            pdf_bytes = uploaded_file.read()
            
            # Process PDF
            from .pipline.ingestion_pipeline import get_ingestion_pipeline
            pipeline = get_ingestion_pipeline()
            result = pipeline.process_pdf_bytes(pdf_bytes, uploaded_file.name, source_id)
            
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IngestTextView(APIView):
    """
    Ingest knowledge from plain text
    POST /api/cognitive/ingest/text/
    
    Body:
    {
        "text": "Document text content",
        "source_id": "Source_123"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            text = request.data.get('text')
            source_id = request.data.get('source_id')
            
            if not text:
                return Response({
                    'error': 'text is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not source_id:
                return Response({
                    'error': 'source_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process text
            from .pipline.ingestion_pipeline import get_ingestion_pipeline
            pipeline = get_ingestion_pipeline()
            result = pipeline.process_text(text, source_id)
            
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InitializeDomainKnowledgeView(APIView):
    """
    Initialize knowledge base with domain-specific concepts
    POST /api/cognitive/ingest/initialize/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            from .pipline.ingestion_pipeline import get_ingestion_pipeline
            pipeline = get_ingestion_pipeline()
            result = pipeline.initialize_domain_knowledge()
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== Phase 3: Advanced Reasoning Views =====

class PLNReasoningView(APIView):
    """
    Perform PLN-based reasoning
    POST /api/cognitive/reason/pln/
    
    Body:
    {
        "premises": [
            {"statement": "...", "conclusion": "...", "strength": 0.9, "confidence": 0.8}
        ],
        "goal": "Goal statement"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            premises = request.data.get('premises', [])
            goal = request.data.get('goal')
            
            if not goal:
                return Response({
                    'error': 'goal is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from .reasoner.reasoner import get_reasoner
            reasoner = get_reasoner()
            result = reasoner.reason_with_pln(premises, goal)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExplainWithChainView(APIView):
    """
    Get explanation with reasoning chain
    POST /api/cognitive/reason/explain-chain/
    
    Body:
    {
        "region_id": "Region_Nairobi"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            region_id = request.data.get('region_id')
            
            if not region_id:
                return Response({
                    'error': 'region_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from .reasoner.reasoner import get_reasoner
            reasoner = get_reasoner()
            result = reasoner.explain_with_chain(region_id)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompareWithConfidenceView(APIView):
    """
    Compare regions with confidence scoring
    POST /api/cognitive/reason/compare-confidence/
    
    Body:
    {
        "region1": "Region_A",
        "region2": "Region_B"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            region1 = request.data.get('region1')
            region2 = request.data.get('region2')
            
            if not region1 or not region2:
                return Response({
                    'error': 'Both region1 and region2 are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from .reasoner.reasoner import get_reasoner
            reasoner = get_reasoner()
            result = reasoner.compare_with_confidence(region1, region2)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MultiHopInferenceView(APIView):
    """
    Perform multi-hop inference
    POST /api/cognitive/reason/multi-hop/
    
    Body:
    {
        "start": "Poverty",
        "goal": "High_Priority",
        "max_hops": 3
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            start = request.data.get('start')
            goal = request.data.get('goal')
            max_hops = request.data.get('max_hops', 3)
            
            if not start or not goal:
                return Response({
                    'error': 'Both start and goal are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from .reasoner.reasoner import get_reasoner
            reasoner = get_reasoner()
            result = reasoner.multi_hop_inference(start, goal, max_hops)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== Phase 5: Advanced Reasoning Views =====

class AdvancedPLNView(APIView):
    """
    Advanced PLN reasoning with forward/backward chaining
    POST /api/cognitive/reason/advanced-pln/
    
    Body:
    {
        "method": "forward" or "backward",
        "premises": [...],
        "goal": "..." (for backward chaining)
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            from cognitive.pln.advanced_pln import get_advanced_pln
            from cognitive.pln.pln_rules import TruthValue
            
            method = request.data.get('method', 'forward')
            premises_data = request.data.get('premises', [])
            goal = request.data.get('goal')
            
            pln = get_advanced_pln()
            
            if method == 'forward':
                # Forward chaining
                premises = [(p['statement'], TruthValue(p['strength'], p['confidence'])) 
                           for p in premises_data]
                results = pln.forward_chaining(premises)
                
                return Response({
                    'method': 'forward_chaining',
                    'results': [r.to_dict() for r in results]
                }, status=status.HTTP_200_OK)
            
            elif method == 'backward':
                # Backward chaining
                if not goal:
                    return Response({
                        'error': 'goal is required for backward chaining'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                known_facts = {p['statement']: TruthValue(p['strength'], p['confidence']) 
                             for p in premises_data}
                result = pln.backward_chaining(goal, known_facts)
                
                return Response({
                    'method': 'backward_chaining',
                    'result': result.to_dict() if result else None
                }, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    'error': 'method must be "forward" or "backward"'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CausalInferenceView(APIView):
    """
    Causal inference operations
    POST /api/cognitive/causal/
    
    Body:
    {
        "operation": "add_relation" | "estimate_effect" | "explain" | "counterfactual",
        "params": {...}
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            from cognitive.pipline.causal_inference import get_causal_inference
            
            operation = request.data.get('operation')
            params = request.data.get('params', {})
            
            causal = get_causal_inference()
            
            if operation == 'add_relation':
                causal.add_causal_relation(
                    params['cause'],
                    params['effect'],
                    params.get('strength', 0.8),
                    params.get('confidence', 0.7),
                    params.get('evidence', [])
                )
                return Response({'success': True}, status=status.HTTP_200_OK)
            
            elif operation == 'estimate_effect':
                result = causal.estimate_causal_effect(
                    params['cause'],
                    params['effect'],
                    params.get('intervention')
                )
                return Response(result, status=status.HTTP_200_OK)
            
            elif operation == 'explain':
                result = causal.explain_with_causality(
                    params['outcome'],
                    params.get('context', {})
                )
                return Response(result, status=status.HTTP_200_OK)
            
            elif operation == 'counterfactual':
                result = causal.counterfactual_reasoning(
                    params['actual_outcome'],
                    params['counterfactual_intervention']
                )
                return Response(result, status=status.HTTP_200_OK)
            
            elif operation == 'get_graph':
                graph = causal.get_causal_graph()
                return Response(graph, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    'error': 'Invalid operation'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LearningLoopView(APIView):
    """
    Learning loop operations
    POST /api/cognitive/learn/
    
    Body:
    {
        "operation": "feedback" | "performance" | "suggestions" | "stats"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            from cognitive.core.learning_loop import get_learning_loop
            
            operation = request.data.get('operation')
            learning = get_learning_loop()
            
            if operation == 'feedback':
                learning.record_feedback(
                    query=request.data.get('query'),
                    response=request.data.get('response'),
                    routing_decision=request.data.get('routing'),
                    feedback_score=request.data.get('score'),
                    user_rating=request.data.get('user_rating'),
                    response_time=request.data.get('response_time', 0.0)
                )
                return Response({'success': True}, status=status.HTTP_200_OK)
            
            elif operation == 'performance':
                performance = learning.get_routing_performance()
                return Response(performance, status=status.HTTP_200_OK)
            
            elif operation == 'suggestions':
                suggestions = learning.suggest_improvements()
                return Response({'suggestions': suggestions}, status=status.HTTP_200_OK)
            
            elif operation == 'stats':
                stats = learning.get_learning_stats()
                return Response(stats, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    'error': 'Invalid operation'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KnowledgeGraphView(APIView):
    """
    Knowledge graph visualization
    GET /api/cognitive/graph/
    
    Query params:
    - type: full | subgraph | causal | domain | reasoning_path
    - center: (for subgraph)
    - start, end: (for reasoning_path)
    - domain: (for domain graph)
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            from cognitive.knowledge.knowledge_graph_viz import get_kg_visualizer
            
            graph_type = request.query_params.get('type', 'full')
            viz = get_kg_visualizer()
            
            if graph_type == 'full':
                max_nodes = int(request.query_params.get('max_nodes', 100))
                graph = viz.generate_full_graph(max_nodes)
            
            elif graph_type == 'subgraph':
                center = request.query_params.get('center')
                if not center:
                    return Response({
                        'error': 'center parameter required for subgraph'
                    }, status=status.HTTP_400_BAD_REQUEST)
                depth = int(request.query_params.get('depth', 2))
                graph = viz.generate_subgraph(center, depth)
            
            elif graph_type == 'causal':
                graph = viz.generate_causal_graph()
            
            elif graph_type == 'domain':
                domain = request.query_params.get('domain', 'allocation')
                graph = viz.generate_domain_graph(domain)
            
            elif graph_type == 'reasoning_path':
                start = request.query_params.get('start')
                end = request.query_params.get('end')
                if not start or not end:
                    return Response({
                        'error': 'start and end parameters required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                graph = viz.generate_reasoning_path_graph(start, end)
            
            else:
                return Response({
                    'error': 'Invalid graph type'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Export to Cytoscape format if requested
            if request.query_params.get('format') == 'cytoscape':
                graph = viz.export_to_cytoscape(graph)
            
            return Response(graph, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
