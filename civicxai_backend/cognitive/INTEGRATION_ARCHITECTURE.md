"""
Cognitive Integration Views
Connects cognitive module with Gateway/MeTTa/ASI agents
"""
import os
import httpx
import logging
from typing import Dict, Any, Optional
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings

from cognitive.orchestrator.orchestrator import get_orchestrator
from cognitive.core.hybrid_responder import get_hybrid_responder
from cognitive.reasoner.reasoner import get_reasoner
from cognitive.knowledge.knowledge_store import get_knowledge_store

logger = logging.getLogger(__name__)

# Configuration
UAGENTS_GATEWAY_URL = os.getenv("UAGENTS_GATEWAY_URL", "http://localhost:8001")


class HybridQueryView(APIView):
    """
    Intelligent query routing using cognitive orchestrator
    POST /api/cognitive/query/hybrid/
    
    Routes queries to:
    1. MeTTa (simple calculations)
    2. Cognitive Reasoner (knowledge-based reasoning)
    3. Gateway/ASI Agents (complex AI analysis)
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Process query with intelligent routing
        
        Body:
        {
            "query": "What is the poverty impact in Nairobi?",
            "region_id": "Region_Nairobi",
            "context": {...},
            "files": [...],
            "force_mode": "auto|metta|cognitive|gateway"
        }
        """
        try:
            query = request.data.get('query')
            region_id = request.data.get('region_id')
            context = request.data.get('context', {})
            force_mode = request.data.get('force_mode', 'auto')
            
            if not query:
                return Response({
                    'error': 'Query is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            orchestrator = get_orchestrator()
            
            # Analyze and route query
            routing_decision = orchestrator.analyze_query(query, context)
            
            # Override if force_mode specified
            if force_mode != 'auto':
                routing_decision['recommended_system'] = force_mode
            
            # Execute based on routing decision
            result = self._execute_query(
                query=query,
                region_id=region_id,
                context=context,
                routing=routing_decision,
                files=request.FILES
            )
            
            return Response({
                'success': True,
                'query': query,
                'routing': routing_decision,
                'result': result,
                'mode': routing_decision['recommended_system']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Hybrid query error: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _execute_query(self, query: str, region_id: str, context: dict, 
                      routing: dict, files) -> Dict[str, Any]:
        """Execute query based on routing decision"""
        
        system = routing['recommended_system']
        
        if system == 'metta':
            return self._query_metta(query, context)
        elif system == 'cognitive':
            return self._query_cognitive(query, region_id, context)
        elif system == 'gateway':
            return self._query_gateway(query, region_id, context, files)
        else:
            # Hybrid: Combine multiple systems
            return self._query_hybrid(query, region_id, context, files)
    
    def _query_metta(self, query: str, context: dict) -> Dict[str, Any]:
        """Use local MeTTa calculation"""
        try:
            from metta.metta_service import calculate_priority
            
            # Extract metrics from context
            metrics = context.get('metrics', {})
            
            priority_score = calculate_priority(
                poverty_index=metrics.get('poverty_index', 0.5),
                project_impact=metrics.get('project_impact', 0.5),
                environmental_score=metrics.get('environmental_score', 0.5),
                corruption_risk=metrics.get('corruption_risk', 0.5)
            )
            
            return {
                'type': 'metta_calculation',
                'priority_score': priority_score,
                'explanation': f'Calculated priority score: {priority_score:.2f}',
                'processing_time_ms': 5
            }
        except Exception as e:
            logger.error(f"MeTTa query error: {e}")
            return {'error': str(e)}
    
    def _query_cognitive(self, query: str, region_id: str, context: dict) -> Dict[str, Any]:
        """Use cognitive reasoning engine"""
        try:
            reasoner = get_reasoner()
            knowledge = get_knowledge_store()
            
            # Extract key concepts from query
            if 'poverty' in query.lower():
                result = reasoner.reason_about_region(region_id, 'poverty')
            elif 'allocation' in query.lower():
                result = reasoner.reason_about_region(region_id, 'allocation')
            else:
                # Generic reasoning
                result = reasoner.reason_with_context(query, context)
            
            return {
                'type': 'cognitive_reasoning',
                'reasoning_result': result,
                'knowledge_used': True,
                'confidence': result.get('confidence', 0.0)
            }
        except Exception as e:
            logger.error(f"Cognitive query error: {e}")
            return {'error': str(e)}
    
    def _query_gateway(self, query: str, region_id: str, context: dict, files) -> Dict[str, Any]:
        """Use Gateway/ASI agents"""
        try:
            # Prepare request for gateway
            form_data = {
                'region_id': region_id or 'QUERY_REGION',
                'poverty_index': context.get('metrics', {}).get('poverty_index', 0.5),
                'project_impact': context.get('metrics', {}).get('project_impact', 0.5),
                'environmental_score': context.get('metrics', {}).get('environmental_score', 0.5),
                'corruption_risk': context.get('metrics', {}).get('corruption_risk', 0.5),
                'notes': query
            }
            
            # Prepare files
            file_list = []
            if files:
                for file_key in files:
                    file_obj = files[file_key]
                    file_list.append(('files', (file_obj.name, file_obj.read(), file_obj.content_type)))
            
            # Send to gateway
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{UAGENTS_GATEWAY_URL}/allocation/request",
                    data=form_data,
                    files=file_list if file_list else None
                )
                response.raise_for_status()
                result = response.json()
                
                # Poll for completion
                request_id = result.get('request_id')
                if request_id:
                    return self._poll_gateway_result(client, request_id)
                
                return result
                
        except httpx.ConnectError:
            logger.warning("Gateway not available, falling back to cognitive")
            return self._query_cognitive(query, region_id, context)
        except Exception as e:
            logger.error(f"Gateway query error: {e}")
            return {'error': str(e)}
    
    def _query_hybrid(self, query: str, region_id: str, context: dict, files) -> Dict[str, Any]:
        """Combine multiple AI systems for best result"""
        try:
            hybrid_responder = get_hybrid_responder()
            
            # Get results from multiple systems
            metta_result = self._query_metta(query, context)
            cognitive_result = self._query_cognitive(query, region_id, context)
            
            # Try gateway (but don't fail if unavailable)
            try:
                gateway_result = self._query_gateway(query, region_id, context, files)
            except:
                gateway_result = None
            
            # Combine results using hybrid responder
            combined = hybrid_responder.combine_results(
                metta_result=metta_result,
                cognitive_result=cognitive_result,
                gateway_result=gateway_result,
                query=query,
                context=context
            )
            
            return {
                'type': 'hybrid_response',
                'combined_result': combined,
                'sources': {
                    'metta': bool(metta_result and 'error' not in metta_result),
                    'cognitive': bool(cognitive_result and 'error' not in cognitive_result),
                    'gateway': bool(gateway_result and 'error' not in gateway_result)
                }
            }
        except Exception as e:
            logger.error(f"Hybrid query error: {e}")
            return {'error': str(e)}
    
    def _poll_gateway_result(self, client: httpx.Client, request_id: str, max_attempts: int = 30) -> Dict[str, Any]:
        """Poll gateway for result"""
        import time
        
        for attempt in range(max_attempts):
            try:
                response = client.get(f"{UAGENTS_GATEWAY_URL}/status/{request_id}")
                data = response.json()
                
                if data.get('status') == 'completed':
                    return {
                        'type': 'gateway_result',
                        'data': data.get('data'),
                        'request_id': request_id,
                        'attempts': attempt + 1
                    }
                elif data.get('status') == 'failed':
                    return {
                        'error': 'Gateway processing failed',
                        'request_id': request_id
                    }
                
                time.sleep(2)  # Wait 2 seconds between polls
                
            except Exception as e:
                logger.error(f"Polling error: {e}")
                break
        
        return {
            'error': 'Gateway request timeout',
            'request_id': request_id,
            'status': 'timeout'
        }


class CognitiveRegionAnalysisView(APIView):
    """
    Analyze region using cognitive reasoning + knowledge base
    POST /api/cognitive/region/analyze/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Analyze a region with cognitive AI
        
        Body:
        {
            "region_id": "Region_Nairobi",
            "analysis_type": "poverty|allocation|comprehensive",
            "include_causal": true,
            "include_reasoning_chain": true
        }
        """
        try:
            region_id = request.data.get('region_id')
            analysis_type = request.data.get('analysis_type', 'comprehensive')
            include_causal = request.data.get('include_causal', True)
            include_chain = request.data.get('include_reasoning_chain', True)
            
            if not region_id:
                return Response({
                    'error': 'region_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            reasoner = get_reasoner()
            knowledge = get_knowledge_store()
            
            # Perform analysis
            if analysis_type == 'poverty':
                result = reasoner.reason_about_region(region_id, 'poverty')
            elif analysis_type == 'allocation':
                result = reasoner.reason_about_region(region_id, 'allocation')
            else:
                # Comprehensive analysis
                result = self._comprehensive_analysis(region_id, reasoner, knowledge)
            
            # Add causal analysis if requested
            if include_causal:
                from cognitive.pipline.causal_inference import get_causal_inference
                causal = get_causal_inference()
                result['causal_relationships'] = causal.discover_causal_relationships(
                    [region_id], 
                    max_relationships=10
                )
            
            # Add reasoning chain if requested
            if include_chain and 'reasoning_chain' not in result:
                result['reasoning_chain'] = self._build_reasoning_chain(result)
            
            return Response({
                'success': True,
                'region_id': region_id,
                'analysis_type': analysis_type,
                'result': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Region analysis error: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _comprehensive_analysis(self, region_id: str, reasoner, knowledge) -> Dict[str, Any]:
        """Perform comprehensive region analysis"""
        
        # Get all knowledge about region
        region_data = knowledge.get_region_info(region_id) if hasattr(knowledge, 'get_region_info') else {}
        
        # Multiple reasoning passes
        poverty_analysis = reasoner.reason_about_region(region_id, 'poverty')
        allocation_analysis = reasoner.reason_about_region(region_id, 'allocation')
        
        return {
            'region_data': region_data,
            'poverty_analysis': poverty_analysis,
            'allocation_analysis': allocation_analysis,
            'knowledge_base_size': knowledge.get_knowledge_stats(),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def _build_reasoning_chain(self, result: dict) -> list:
        """Build human-readable reasoning chain"""
        chain = []
        
        if 'inferences' in result:
            for i, inference in enumerate(result['inferences'], 1):
                chain.append({
                    'step': i,
                    'description': inference.get('conclusion', 'Unknown'),
                    'confidence': inference.get('confidence', 0.0)
                })
        
        return chain


class CognitiveKnowledgeIngestView(APIView):
    """
    Ingest knowledge from documents into cognitive system
    POST /api/cognitive/ingest/
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Ingest PDF or text into knowledge base
        
        Form data:
        - file: PDF file upload
        - text: Text content (if no file)
        - source_id: Unique identifier for source
        - category: Document category
        """
        try:
            from cognitive.pipline.ingestion_pipeline import get_ingestion_pipeline
            
            pipeline = get_ingestion_pipeline()
            source_id = request.data.get('source_id', f'DOC_{__import__("time").time()}')
            
            # Handle file upload
            if 'file' in request.FILES:
                file_obj = request.FILES['file']
                
                # Save temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    for chunk in file_obj.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name
                
                # Process PDF
                result = pipeline.process_pdf_file(tmp_path, source_id)
                
                # Cleanup
                __import__('os').unlink(tmp_path)
                
            # Handle text content
            elif 'text' in request.data:
                text = request.data.get('text')
                result = pipeline.process_text(text, source_id)
            else:
                return Response({
                    'error': 'Either file or text is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'success': result.get('success', False),
                'source_id': source_id,
                'atoms_created': result.get('atoms_created', 0),
                'concepts_extracted': result.get('concepts_extracted', 0),
                'key_topics': result.get('key_topics', []),
                'message': 'Knowledge ingested successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Knowledge ingest error: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
