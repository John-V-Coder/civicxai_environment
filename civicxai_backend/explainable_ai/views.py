from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Region, Allocation, Workgroup, Proposal, Vote, Event
from .serializers import (
    RegionSerializer, RegionListSerializer,
    AllocationSerializer, AllocationCreateSerializer,
    WorkgroupSerializer, WorkgroupListSerializer,
    ProposalSerializer, ProposalListSerializer,
    VoteSerializer, EventSerializer, EventListSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsContributorOrReadOnly
from metta.metta_engine import metta_engine
from agents.asi1_governance import ASIExplainAgent

User = get_user_model()


# =====================================================
# MeTTa / Explanation API
# =====================================================

class CalculatePriorityView(APIView):
    """Calculate priority using MeTTa engine"""
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            poverty = request.data.get('poverty_index', 0)
            impact = request.data.get('project_impact', 0)
            environment = request.data.get('deforestation', 0)
            corruption = request.data.get('corruption_risk', 0)

            if not metta_engine.validate_inputs(poverty, impact, environment, corruption):
                return Response({'error': 'All values must be between 0 and 1'}, status=status.HTTP_400_BAD_REQUEST)

            priority_score = metta_engine.calculate_priority(poverty, impact, environment, corruption)
            total_budget = 50_000_000
            allocation = priority_score * total_budget

            return Response({
                'success': True,
                'priority_score': priority_score,
                'allocation': allocation,
                'allocation_millions': round(allocation / 1_000_000, 2),
                'factors': {
                    'poverty_index': poverty,
                    'project_impact': impact,
                    'deforestation': environment,
                    'corruption_risk': corruption
                },
                'explanation': f"Priority score {priority_score:.3f} calculated using MeTTa policy engine"
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """Check if MeTTa engine is working"""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            test_score = metta_engine.calculate_priority(0.8, 0.9, 0.4, 0.3)
            return Response({'status': 'healthy', 'metta_engine': 'operational', 'test_calculation': test_score})
        except Exception as e:
            return Response({'status': 'unhealthy', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateExplanationAPIView(APIView):
    """Generate explanations using ASIExplainAgent"""
    permission_classes = [AllowAny]

    def post(self, request):
        region_id = request.data.get('region_id')
        if not region_id:
            return Response({"error": "Region ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Dummy region data
        region_data = {
            "region_name": f"County {region_id}",
            "poverty_index": 0.81,
            "project_impact_score": 0.92,
            "deforestation": 0.75,
            "rainfall": 0.80
        }
        predicted_priority_score = 0.88
        feature_importance_factors = {
            "poverty_index": 0.40,
            "deforestation": 0.30,
            "project_impact_score": 0.15,
            "rainfall": 0.05
        }
        policy_feedback = "Complies with high-need region policy based on poverty index."

        try:
            explain_agent = ASIExplainAgent()
            explanation = explain_agent.generate_explanation(
                region_data={"region_name": region_data["region_name"], "priority_score": predicted_priority_score},
                factors=feature_importance_factors,
                policy_feedback=policy_feedback
            )
            return Response({"explanation": explanation, "region_name": region_data["region_name"]}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": f"Configuration error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Failed to generate explanation: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =====================================================
# Region ViewSet
# =====================================================

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'region_id', 'county']
    ordering_fields = ['priority_score', 'population', 'current_allocation']
    ordering = ['-priority_score']

    def get_serializer_class(self):
        return RegionListSerializer if self.action == 'list' else RegionSerializer

    @action(detail=True, methods=['post'])
    def calculate_priority(self, request, pk=None):
        region = self.get_object()
        score = region.calculate_priority()
        return Response({
            'success': True,
            'region': region.name,
            'priority_score': score,
            'factors': {
                'poverty_index': region.poverty_index,
                'project_impact': region.project_impact_score,
                'deforestation': region.deforestation_rate,
                'corruption_risk': region.corruption_risk
            }
        })


# =====================================================
# Allocation ViewSet
# =====================================================

class AllocationViewSet(viewsets.ModelViewSet):
    queryset = Allocation.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['region__name', 'allocation_id']
    ordering = ['-created_at']

    def get_serializer_class(self):
        return AllocationCreateSerializer if self.action == 'create' else AllocationSerializer

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def approve(self, request, pk=None):
        allocation = self.get_object()
        if allocation.status != 'pending':
            return Response({'error': 'Only pending allocations can be approved'}, status=status.HTTP_400_BAD_REQUEST)

        allocation.status = 'approved'
        allocation.approved_by = request.user
        allocation.approved_at = timezone.now()
        allocation.save()

        allocation.region.current_allocation = allocation.amount
        allocation.region.save()

        return Response({'success': True, 'allocation': AllocationSerializer(allocation).data})

    @action(detail=True, methods=['post'])
    def disburse(self, request, pk=None):
        allocation = self.get_object()
        if allocation.status != 'approved':
            return Response({'error': 'Only approved allocations can be disbursed'}, status=status.HTTP_400_BAD_REQUEST)

        allocation.status = 'disbursed'
        allocation.disbursed_at = timezone.now()
        allocation.save()

        return Response({'success': True, 'allocation': AllocationSerializer(allocation).data})


# =====================================================
# Workgroup ViewSet
# =====================================================

class WorkgroupViewSet(viewsets.ModelViewSet):
    queryset = Workgroup.objects.all()
    permission_classes = [IsContributorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['category', 'name']

    def get_serializer_class(self):
        return WorkgroupListSerializer if self.action == 'list' else WorkgroupSerializer

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        workgroup = self.get_object()
        workgroup.members.add(request.user)
        return Response({'success': True, 'message': f'Joined {workgroup.name}'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        workgroup = self.get_object()
        workgroup.members.remove(request.user)
        return Response({'success': True, 'message': f'Left {workgroup.name}'})


# =====================================================
# Proposal ViewSet
# =====================================================

class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'author__username']
    ordering = ['-created_at']

    def get_serializer_class(self):
        return ProposalListSerializer if self.action == 'list' else ProposalSerializer

    def perform_create(self, serializer):
        proposal = serializer.save(author=self.request.user)
        self.request.user.proposals_created += 1
        self.request.user.save()
        if proposal.workgroup:
            proposal.workgroup.update_metrics()


# =====================================================
# Vote ViewSet
# =====================================================

class VoteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]


# =====================================================
# Event ViewSet
# =====================================================

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering = ['start_date']

    def get_serializer_class(self):
        return EventListSerializer if self.action == 'list' else EventSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)