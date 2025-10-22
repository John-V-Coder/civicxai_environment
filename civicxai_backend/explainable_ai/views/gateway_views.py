"""
Gateway Integration Views
Handles communication with uagents gateway API for AI-powered allocation analysis
"""
import os
import httpx
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from dotenv import load_dotenv

load_dotenv()


# Gateway configuration
UAGENTS_GATEWAY_URL = os.getenv("UAGENTS_GATEWAY_URL")
GATEWAY_API_URL = UAGENTS_GATEWAY_URL  # Alias for consistent usage


class GatewayAllocationRequestView(APIView):
    """
    Send allocation request to uagents gateway with optional PDF/file uploads
    POST /api/gateway/allocation/request/
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Submit allocation request to gateway
        
        Expected form data:
        - region_id: str
        - poverty_index: float (0-1)
        - project_impact: float (0-1)
        - environmental_score: float (0-1)
        - corruption_risk: float (0-1)
        - notes: str (optional)
        - urls: JSON string array (optional)
        - files: file uploads (optional, PDFs, images, etc.)
        """
        try:
            # Prepare form data
            form_data = {
                'region_id': request.data.get('region_id'),
                'poverty_index': float(request.data.get('poverty_index', 0)),
                'project_impact': float(request.data.get('project_impact', 0)),
                'environmental_score': float(request.data.get('environmental_score', 0)),
                'corruption_risk': float(request.data.get('corruption_risk', 0)),
            }
            
            # Optional fields
            if request.data.get('notes'):
                form_data['notes'] = request.data.get('notes')
            
            if request.data.get('urls'):
                form_data['urls'] = request.data.get('urls')  # Should be JSON string
            
            # Prepare files
            files = []
            for file_key in request.FILES:
                file_obj = request.FILES[file_key]
                files.append(('files', (file_obj.name, file_obj.read(), file_obj.content_type)))
            
            # Send to gateway
            with httpx.Client(timeout=30.0) as client:
                if files:
                    response = client.post(
                        f"{GATEWAY_API_URL}/allocation/request",
                        data=form_data,
                        files=files
                    )
                else:
                    response = client.post(
                        f"{GATEWAY_API_URL}/allocation/request",
                        data=form_data
                    )
                
                response.raise_for_status()
                result = response.json()
                
                return Response({
                    'success': True,
                    'request_id': result.get('request_id'),
                    'status': result.get('status'),
                    'data': result.get('data'),
                    'message': 'Allocation request submitted to gateway'
                }, status=status.HTTP_200_OK)
                
        except httpx.ConnectError as e:
            # Fallback to local MeTTa calculation
            try:
                from ...metta.metta_service import calculate_priority
                
                priority_score = calculate_priority(
                    poverty_index=form_data['poverty_index'],
                    project_impact=form_data['project_impact'],
                    environmental_score=form_data['environmental_score'],
                    corruption_risk=form_data['corruption_risk']
                )
                
                return Response({
                    'success': True,
                    'request_id': f"local_{form_data['region_id']}",
                    'status': 'completed',
                    'data': {
                        'priority_score': priority_score,
                        'recommendation': 'high' if priority_score > 0.7 else 'medium' if priority_score > 0.4 else 'low',
                        'mode': 'local_metta'
                    },
                    'message': 'Gateway unavailable - used local MeTTa calculation',
                    'warning': f'uAgents Gateway is not running at {GATEWAY_API_URL}. Start it with: python run_uagents.py'
                }, status=status.HTTP_200_OK)
                
            except Exception as fallback_error:
                return Response({
                    'error': 'Gateway is not running and local fallback failed',
                    'detail': f'Cannot connect to uAgents gateway at {GATEWAY_API_URL}',
                    'solution': 'Start the gateway: python run_uagents.py',
                    'gateway_url': GATEWAY_API_URL,
                    'fallback_error': str(fallback_error)
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except httpx.HTTPStatusError as e:
            return Response({
                'error': 'Gateway request failed',
                'details': str(e),
                'gateway_response': e.response.text if hasattr(e, 'response') else None
            }, status=status.HTTP_502_BAD_GATEWAY)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR in GatewayAllocationRequestView: {error_details}")
            return Response({
                'error': 'Failed to submit allocation request',
                'details': str(e),
                'type': type(e).__name__,
                'traceback': error_details if status.HTTP_500_INTERNAL_SERVER_ERROR else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GatewayExplanationRequestView(APIView):
    """
    Request explanation from uagents gateway
    POST /api/gateway/explanation/request/
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Request allocation explanation
        
        Expected form data:
        - region_id: str
        - allocation_data: JSON string
        - context: str (optional)
        - language: str (default: 'en')
        - notes: str (optional)
        - urls: JSON string array (optional)
        - files: file uploads (optional)
        """
        try:
            # Prepare form data
            form_data = {
                'region_id': request.data.get('region_id'),
                'allocation_data': request.data.get('allocation_data'),  # JSON string
                'context': request.data.get('context', ''),
                'language': request.data.get('language', 'en'),
            }
            
            # Optional fields
            if request.data.get('notes'):
                form_data['notes'] = request.data.get('notes')
            
            if request.data.get('urls'):
                form_data['urls'] = request.data.get('urls')
            
            # Prepare files
            files = []
            for file_key in request.FILES:
                file_obj = request.FILES[file_key]
                files.append(('files', (file_obj.name, file_obj.read(), file_obj.content_type)))
            
            # Send to gateway
            with httpx.Client(timeout=30.0) as client:
                if files:
                    response = client.post(
                        f"{GATEWAY_API_URL}/explanation/request",
                        data=form_data,
                        files=files
                    )
                else:
                    response = client.post(
                        f"{GATEWAY_API_URL}/explanation/request",
                        data=form_data
                    )
                
                response.raise_for_status()
                result = response.json()
                
                return Response({
                    'success': True,
                    'request_id': result.get('request_id'),
                    'status': result.get('status'),
                    'data': result.get('data'),
                    'message': 'Explanation request submitted to gateway'
                }, status=status.HTTP_200_OK)
                
        except httpx.ConnectError as e:
            # Fallback to local explanation generation
            try:
                from ...metta.metta_service import generate_explanation_from_data
                import json
                
                # Parse allocation_data
                try:
                    allocation_data = json.loads(form_data.get('allocation_data', '{}'))
                except json.JSONDecodeError:
                    allocation_data = {}
                
                # Generate local explanation
                explanation_result = generate_explanation_from_data(
                    region_id=form_data.get('region_id', 'Unknown'),
                    allocation_data=allocation_data,
                    context=form_data.get('context', ''),
                    language=form_data.get('language', 'en')
                )
                
                return Response({
                    'success': True,
                    'request_id': f"local_explanation_{form_data.get('region_id')}",
                    'status': 'completed',
                    'data': explanation_result,
                    'message': 'Gateway unavailable - used local explanation generation',
                    'warning': f'uAgents Gateway is not running at {GATEWAY_API_URL}. Using local generation.'
                }, status=status.HTTP_200_OK)
                
            except Exception as fallback_error:
                return Response({
                    'error': 'Gateway is not running and local fallback failed',
                    'detail': f'Cannot connect to uAgents gateway at {GATEWAY_API_URL}',
                    'solution': 'Start the gateway: python run_uagents.py',
                    'gateway_url': GATEWAY_API_URL,
                    'fallback_error': str(fallback_error)
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except httpx.HTTPStatusError as e:
            return Response({
                'error': 'Gateway request failed',
                'details': str(e),
                'gateway_response': e.response.text if hasattr(e, 'response') else None
            }, status=status.HTTP_502_BAD_GATEWAY)
            
        except Exception as e:
            return Response({
                'error': 'Failed to submit explanation request',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GatewayStatusView(APIView):
    """
    Check status of a gateway request
    GET /api/gateway/status/<request_id>/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, request_id):
        """Poll gateway for request status and results"""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{GATEWAY_API_URL}/status/{request_id}")
                response.raise_for_status()
                result = response.json()
                
                return Response({
                    'success': True,
                    'request_id': result.get('request_id'),
                    'status': result.get('status'),
                    'data': result.get('data'),
                    'timestamp': result.get('timestamp')
                }, status=status.HTTP_200_OK)
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return Response({
                    'error': 'Request not found',
                    'request_id': request_id
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'error': 'Failed to check status',
                'details': str(e)
            }, status=status.HTTP_502_BAD_GATEWAY)
            
        except Exception as e:
            return Response({
                'error': 'Status check failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GatewayHealthView(APIView):
    """
    Check gateway health status
    GET /api/gateway/health/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Check if gateway is healthy and operational"""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{GATEWAY_API_URL}/health")
                response.raise_for_status()
                result = response.json()
                
                return Response({
                    'success': True,
                    'gateway_status': result.get('status'),
                    'agent_active': result.get('agent_active'),
                    'cache_stats': result.get('cache_stats'),
                    'timestamp': result.get('timestamp')
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gateway is not reachable',
                'details': str(e),
                'gateway_url': GATEWAY_API_URL
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class GatewayMetricsView(APIView):
    """
    Get gateway metrics and statistics
    GET /api/gateway/metrics/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Retrieve gateway performance metrics"""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{GATEWAY_API_URL}/metrics")
                response.raise_for_status()
                result = response.json()
                
                return Response({
                    'success': True,
                    'metrics': result
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve metrics',
                'details': str(e)
            }, status=status.HTTP_502_BAD_GATEWAY)
