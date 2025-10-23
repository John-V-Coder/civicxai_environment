"""
API Views for Allocation Requests
Manages allocation requests submitted through AI Gateway
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from ..models import AllocationRequest


class AllocationRequestPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class AllocationRequestListView(APIView):
    """
    List all allocation requests
    GET /api/allocation-requests/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Get query parameters
        status_filter = request.query_params.get('status')
        region_id = request.query_params.get('region_id')
        
        # Base queryset
        queryset = AllocationRequest.objects.all()
        
        # Apply filters
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if region_id:
            queryset = queryset.filter(region_id=region_id)
        
        # Paginate
        paginator = AllocationRequestPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        # Serialize
        data = [
            {
                'id': str(req.request_id),
                'pk': req.pk,
                'region_id': req.region_id,
                'region_name': req.region_name,
                'status': req.status,
                'priority_level': req.priority_level,
                'confidence_score': req.confidence_score,
                'recommended_allocation_percentage': req.recommended_allocation_percentage,
                'metrics': req.get_metrics_dict(),
                'notes': req.notes,
                'key_findings': req.key_findings,
                'recommendations': req.recommendations,
                'files_attached': req.files_attached,
                'created_at': req.created_at.isoformat(),
                'analyzed_at': req.analyzed_at.isoformat() if req.analyzed_at else None,
            }
            for req in page
        ]
        
        return paginator.get_paginated_response(data)


class AllocationRequestCreateView(APIView):
    """
    Create a new allocation request
    POST /api/allocation-requests/create/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Extract data
            data = request.data
            
            # Validate required fields
            required_fields = ['region_id', 'poverty_index', 'project_impact', 
                             'environmental_score', 'corruption_risk']
            missing_fields = [field for field in required_fields if field not in data or data.get(field) == '']
            
            if missing_fields:
                return Response({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}',
                    'message': 'Please provide all required fields'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate numeric ranges (0-1)
            numeric_fields = ['poverty_index', 'project_impact', 'environmental_score', 'corruption_risk']
            for field in numeric_fields:
                try:
                    value = float(data.get(field))
                    if value < 0 or value > 1:
                        return Response({
                            'success': False,
                            'error': f'{field} must be between 0 and 1, got {value}',
                            'message': 'Invalid field value'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except (ValueError, TypeError) as e:
                    return Response({
                        'success': False,
                        'error': f'Invalid value for {field}: {data.get(field)}',
                        'message': 'Field must be a valid number'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create allocation request
            allocation_request = AllocationRequest.objects.create(
                region_id=data.get('region_id'),
                region_name=data.get('region_name', data.get('region_id')),  # Fallback to ID if name not provided
                poverty_index=float(data.get('poverty_index')),
                project_impact=float(data.get('project_impact')),
                environmental_score=float(data.get('environmental_score')),
                corruption_risk=float(data.get('corruption_risk')),
                notes=data.get('notes', ''),
                urls=data.get('urls', ''),
                files_attached=data.get('files_attached', 0),
                file_paths=data.get('file_paths', []),
                status=data.get('status', 'pending')  # Accept status from request or default to pending
            )
            
            # If user is authenticated, link it
            if request.user.is_authenticated:
                allocation_request.submitted_by = request.user
                allocation_request.save()
            
            return Response({
                'success': True,
                'request_id': str(allocation_request.request_id),
                'message': 'Allocation request created successfully',
                'data': {
                    'id': str(allocation_request.request_id),
                    'region_id': allocation_request.region_id,
                    'region_name': allocation_request.region_name,
                    'status': allocation_request.status,
                    'created_at': allocation_request.created_at.isoformat(),
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            return Response({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'message': 'Failed to create allocation request',
                'received_data': request.data  # Include received data for debugging
            }, status=status.HTTP_400_BAD_REQUEST)


class AllocationRequestDetailView(APIView):
    """
    Get, update, or delete a specific allocation request
    GET/PUT/DELETE /api/allocation-requests/<request_id>/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, pk=None, request_id=None):
        try:
            # Support both integer pk and UUID request_id
            if pk is not None:
                allocation_request = AllocationRequest.objects.get(pk=pk)
            else:
                allocation_request = AllocationRequest.objects.get(request_id=request_id)

            return Response({
                'success': True,
                'data': {
                    'id': str(allocation_request.request_id),
                    'pk': allocation_request.pk,
                    'region_id': allocation_request.region_id,
                    'region_name': allocation_request.region_name,
                    'status': allocation_request.status,
                    'metrics': allocation_request.get_metrics_dict(),
                    'notes': allocation_request.notes,
                    'urls': allocation_request.urls.split('\n') if allocation_request.urls else [],
                    'priority_level': allocation_request.priority_level,
                    'confidence_score': allocation_request.confidence_score,
                    'recommended_allocation_percentage': allocation_request.recommended_allocation_percentage,
                    'ai_recommendation': allocation_request.ai_recommendation,
                    'key_findings': allocation_request.key_findings,
                    'recommendations': allocation_request.recommendations,
                    'files_attached': allocation_request.files_attached,
                    'created_at': allocation_request.created_at.isoformat(),
                    'analyzed_at': allocation_request.analyzed_at.isoformat() if allocation_request.analyzed_at else None,
                }
            }, status=status.HTTP_200_OK)

        except AllocationRequest.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Allocation request not found',
                'pk': pk,
                'request_id': request_id
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            return Response({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, pk=None, request_id=None):
        """Update allocation request with AI analysis results"""
        try:
            # Support both integer pk and UUID request_id
            if pk is not None:
                allocation_request = AllocationRequest.objects.get(pk=pk)
            else:
                allocation_request = AllocationRequest.objects.get(request_id=request_id)
            data = request.data
            
            # Update fields
            if 'status' in data:
                allocation_request.status = data['status']
            if 'priority_level' in data:
                allocation_request.priority_level = data['priority_level']
            if 'confidence_score' in data:
                allocation_request.confidence_score = float(data['confidence_score'])
            if 'recommended_allocation_percentage' in data:
                allocation_request.recommended_allocation_percentage = float(data['recommended_allocation_percentage'])
            if 'ai_recommendation' in data:
                allocation_request.ai_recommendation = data['ai_recommendation']
            if 'key_findings' in data:
                allocation_request.key_findings = data['key_findings']
            if 'recommendations' in data:
                allocation_request.recommendations = data['recommendations']
            
            # Mark as analyzed if results provided
            if allocation_request.status == 'pending' and allocation_request.priority_level:
                allocation_request.status = 'analyzed'
                allocation_request.analyzed_at = timezone.now()
            
            allocation_request.save()
            
            return Response({
                'success': True,
                'message': 'Allocation request updated successfully'
            }, status=status.HTTP_200_OK)
            
        except AllocationRequest.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Allocation request not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None, request_id=None):
        """Delete an allocation request"""
        try:
            # Support both integer pk and UUID request_id
            if pk is not None:
                allocation_request = AllocationRequest.objects.get(pk=pk)
            else:
                allocation_request = AllocationRequest.objects.get(request_id=request_id)
            allocation_request.delete()
            
            return Response({
                'success': True,
                'message': 'Allocation request deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except AllocationRequest.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Allocation request not found'
            }, status=status.HTTP_404_NOT_FOUND)


class AllocationRequestStatsView(APIView):
    """
    Get statistics about allocation requests
    GET /api/allocation-requests/stats/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        total = AllocationRequest.objects.count()
        pending = AllocationRequest.objects.filter(status='pending').count()
        processing = AllocationRequest.objects.filter(status='processing').count()
        analyzed = AllocationRequest.objects.filter(status='analyzed').count()
        approved = AllocationRequest.objects.filter(status='approved').count()
        
        return Response({
            'success': True,
            'stats': {
                'total': total,
                'pending': pending,
                'processing': processing,
                'analyzed': analyzed,
                'approved': approved,
                'by_status': {
                    'pending': pending,
                    'processing': processing,
                    'analyzed': analyzed,
                    'approved': approved,
                }
            }
        }, status=status.HTTP_200_OK)
