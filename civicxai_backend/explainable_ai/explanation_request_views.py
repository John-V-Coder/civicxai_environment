"""
API Views for Explanation Requests
Manages explanation requests submitted through AI Gateway
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from .models import ExplanationRequest


class ExplanationRequestPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class ExplanationRequestListView(APIView):
    """
    List all explanation requests
    GET /api/explanation-requests/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Get query parameters
        status_filter = request.query_params.get('status')
        region_id = request.query_params.get('region_id')
        
        # Base queryset
        queryset = ExplanationRequest.objects.all()
        
        # Apply filters
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if region_id:
            queryset = queryset.filter(region_id=region_id)
        
        # Paginate
        paginator = ExplanationRequestPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        # Serialize
        data = [
            {
                'id': str(req.request_id),
                'region_id': req.region_id,
                'region_name': req.region_name,
                'status': req.status,
                'language': req.language,
                'allocation_data': req.allocation_data,
                'context': req.context,
                'notes': req.notes,
                'explanation_text': req.explanation_text,
                'key_points': req.key_points,
                'policy_implications': req.policy_implications,
                'transparency_score': req.transparency_score,
                'files_attached': req.files_attached,
                'created_at': req.created_at.isoformat(),
                'completed_at': req.completed_at.isoformat() if req.completed_at else None,
            }
            for req in page
        ]
        
        return paginator.get_paginated_response(data)


class ExplanationRequestCreateView(APIView):
    """
    Create a new explanation request
    POST /api/explanation-requests/create/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Extract data
            data = request.data
            
            # Create explanation request
            explanation_request = ExplanationRequest.objects.create(
                region_id=data.get('region_id', ''),
                region_name=data.get('region_name', data.get('region_id', '')),
                allocation_data=data.get('allocation_data', {}),
                context=data.get('context', ''),
                language=data.get('language', 'simple'),
                notes=data.get('notes', ''),
                files_attached=data.get('files_attached', 0),
                file_paths=data.get('file_paths', []),
                status='pending'
            )
            
            # If user is authenticated, link it
            if request.user.is_authenticated:
                explanation_request.submitted_by = request.user
                explanation_request.save()
            
            return Response({
                'success': True,
                'request_id': str(explanation_request.request_id),
                'message': 'Explanation request created successfully',
                'data': {
                    'id': str(explanation_request.request_id),
                    'region_id': explanation_request.region_id,
                    'region_name': explanation_request.region_name,
                    'status': explanation_request.status,
                    'created_at': explanation_request.created_at.isoformat(),
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Failed to create explanation request'
            }, status=status.HTTP_400_BAD_REQUEST)


class ExplanationRequestDetailView(APIView):
    """
    Get, update, or delete a specific explanation request
    GET/PUT/DELETE /api/explanation-requests/<request_id>/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, request_id):
        try:
            explanation_request = ExplanationRequest.objects.get(request_id=request_id)
            
            return Response({
                'success': True,
                'data': {
                    'id': str(explanation_request.request_id),
                    'region_id': explanation_request.region_id,
                    'region_name': explanation_request.region_name,
                    'status': explanation_request.status,
                    'language': explanation_request.language,
                    'allocation_data': explanation_request.allocation_data,
                    'context': explanation_request.context,
                    'notes': explanation_request.notes,
                    'explanation_text': explanation_request.explanation_text,
                    'key_points': explanation_request.key_points,
                    'policy_implications': explanation_request.policy_implications,
                    'transparency_score': explanation_request.transparency_score,
                    'files_attached': explanation_request.files_attached,
                    'created_at': explanation_request.created_at.isoformat(),
                    'completed_at': explanation_request.completed_at.isoformat() if explanation_request.completed_at else None,
                }
            }, status=status.HTTP_200_OK)
            
        except ExplanationRequest.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Explanation request not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, request_id):
        """Update explanation request with AI results"""
        try:
            explanation_request = ExplanationRequest.objects.get(request_id=request_id)
            data = request.data
            
            # Update fields
            if 'status' in data:
                explanation_request.status = data['status']
            if 'explanation_text' in data:
                explanation_request.explanation_text = data['explanation_text']
            if 'key_points' in data:
                explanation_request.key_points = data['key_points']
            if 'policy_implications' in data:
                explanation_request.policy_implications = data['policy_implications']
            if 'transparency_score' in data:
                explanation_request.transparency_score = float(data['transparency_score'])
            
            # Mark as completed if explanation provided
            if explanation_request.status == 'pending' and explanation_request.explanation_text:
                explanation_request.status = 'completed'
                explanation_request.completed_at = timezone.now()
            
            explanation_request.save()
            
            return Response({
                'success': True,
                'message': 'Explanation request updated successfully'
            }, status=status.HTTP_200_OK)
            
        except ExplanationRequest.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Explanation request not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, request_id):
        """Delete an explanation request"""
        try:
            explanation_request = ExplanationRequest.objects.get(request_id=request_id)
            explanation_request.delete()
            
            return Response({
                'success': True,
                'message': 'Explanation request deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except ExplanationRequest.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Explanation request not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ExplanationRequestStatsView(APIView):
    """
    Get statistics about explanation requests
    GET /api/explanation-requests/stats/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        total = ExplanationRequest.objects.count()
        pending = ExplanationRequest.objects.filter(status='pending').count()
        processing = ExplanationRequest.objects.filter(status='processing').count()
        completed = ExplanationRequest.objects.filter(status='completed').count()
        approved = ExplanationRequest.objects.filter(status='approved').count()
        
        return Response({
            'success': True,
            'stats': {
                'total': total,
                'pending': pending,
                'processing': processing,
                'completed': completed,
                'approved': approved,
                'by_status': {
                    'pending': pending,
                    'processing': processing,
                    'completed': completed,
                    'approved': approved,
                }
            }
        }, status=status.HTTP_200_OK)
