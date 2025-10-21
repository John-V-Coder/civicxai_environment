"""
Data Source Management Views
Handles CRUD operations for PDFs and website links used by AI
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from .models import DataSource
from .permissions import IsAdminOnly
from .serializers import (
    DataSourceSerializer,
    DataSourceListSerializer,
    DataSourceCreateSerializer
)


class DataSourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing data sources (PDFs, URLs)
    
    list: Get all data sources
    retrieve: Get a specific data source
    create: Add a new data source
    update: Update a data source
    destroy: Delete a data source
    """
    queryset = DataSource.objects.all()
    permission_classes = [IsAdminOnly]  # Only admins can access
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'tags', 'author']
    ordering_fields = ['created_at', 'usage_count', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return DataSourceListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DataSourceCreateSerializer
        return DataSourceSerializer
    
    def perform_create(self, serializer):
        """Set the user who added the data source"""
        # If user is authenticated, set added_by
        if self.request.user.is_authenticated:
            serializer.save(added_by=self.request.user)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active data sources"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get data sources grouped by category"""
        category = request.query_params.get('category')
        if not category:
            return Response(
                {'error': 'Category parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            category=category,
            is_active=True
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get data sources by type (pdf, url, document)"""
        source_type = request.query_params.get('type')
        if not source_type:
            return Response(
                {'error': 'Type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            source_type=source_type,
            is_active=True
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search_sources(self, request):
        """
        Search data sources by query
        Query params: q (search query), category, type
        """
        query = request.query_params.get('q', '')
        category = request.query_params.get('category')
        source_type = request.query_params.get('type')
        
        queryset = self.get_queryset().filter(is_active=True)
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query) |
                Q(summary__icontains=query) |
                Q(key_points__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category=category)
        
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def increment_usage(self, request, pk=None):
        """Increment usage counter when AI uses this source"""
        data_source = self.get_object()
        data_source.increment_usage()
        
        return Response({
            'success': True,
            'usage_count': data_source.usage_count,
            'last_used': data_source.last_used
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about data sources"""
        total = self.get_queryset().count()
        active = self.get_queryset().filter(is_active=True).count()
        inactive = total - active
        
        by_type = {}
        for source_type, _ in DataSource.SOURCE_TYPE_CHOICES:
            count = self.get_queryset().filter(source_type=source_type, is_active=True).count()
            by_type[source_type] = count
        
        by_category = {}
        for category, _ in DataSource.CATEGORY_CHOICES:
            count = self.get_queryset().filter(category=category, is_active=True).count()
            by_category[category] = count
        
        most_used = self.get_queryset().filter(is_active=True).order_by('-usage_count')[:5]
        most_used_serializer = DataSourceListSerializer(most_used, many=True)
        
        return Response({
            'total': total,
            'active': active,
            'inactive': inactive,
            'by_type': by_type,
            'by_category': by_category,
            'most_used': most_used_serializer.data
        })
