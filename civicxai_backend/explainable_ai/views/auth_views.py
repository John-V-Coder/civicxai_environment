from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import transaction
from ..serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    DashboardMetricsSerializer
)
from ..models import DashboardMetrics

User = get_user_model()


# =====================================================
# Authentication Views
# =====================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT login view with additional user info"""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    """User registration view"""
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Registration successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Logout view that blacklists the refresh token"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Update user online status
            request.user.is_online = False
            request.user.save()
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for getting and updating user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        # Update user's online status
        request.user.is_online = True
        request.user.save()
        
        return super().update(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """View for changing user password"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({
                'success': False,
                'error': 'Both old and new passwords are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            return Response({
                'success': False,
                'error': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({
                'success': False,
                'error': 'New password must be at least 8 characters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        # Generate new tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Password changed successfully',
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)


# =====================================================
#  User Management Views
# =====================================================

from ..serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    DashboardMetricsSerializer,
    UserListSerializer
)


class UserListView(generics.ListAPIView):
    """View for listing users (contributors)"""
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.filter(is_active=True)
        
        # Filter by role if specified
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by online status
        online = self.request.query_params.get('online')
        if online == 'true':
            queryset = queryset.filter(is_online=True)
        
        # Filter by workgroup membership
        workgroup_id = self.request.query_params.get('workgroup')
        if workgroup_id:
            queryset = queryset.filter(workgroups_member__id=workgroup_id)
        
        return queryset.order_by('-contribution_score')


class UpdateUserRoleView(APIView):
    """Admin view for updating user roles"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        # Check if requesting user is admin
        if request.user.role != 'admin':
            return Response({
                'success': False,
                'error': 'Only administrators can change user roles'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
            new_role = request.data.get('role')
            
            if new_role not in ['citizen', 'contributor', 'admin', 'analyst']:
                return Response({
                    'success': False,
                    'error': 'Invalid role specified'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.role = new_role
            user.save()
            
            return Response({
                'success': True,
                'message': f'User role updated to {new_role}',
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)


# =====================================================
# Dashboard Views
# =====================================================

class DashboardOverviewView(APIView):
    """Main dashboard overview with all metrics"""
    permission_classes = [AllowAny]  # Changed to AllowAny for debugging

    def get(self, request):
        try:
            # Get or calculate today's metrics
            metrics = DashboardMetrics.calculate_today_metrics()

            # Get recent events
            from ..models import Event, User, Proposal
            from datetime import datetime, timedelta

            recent_events = Event.objects.filter(
                start_date__gte=datetime.now() - timedelta(days=30)
            )[:5]

            # Get active contributors
            active_contributors = User.objects.filter(
                is_online=True
            ).order_by('-contribution_score')[:10]

            # Get recent proposals
            recent_proposals = Proposal.objects.filter(
                status='in_review'
            )[:4]

            return Response({
                'metrics': DashboardMetricsSerializer(metrics).data,
                'recent_events': [{
                    'id': e.id,
                    'title': e.title,
                    'type': e.event_type,
                    'date': e.start_date.strftime('%b %d'),
                    'high_priority': e.is_high_priority
                } for e in recent_events],
                'active_contributors': [{
                    'id': u.id,
                    'username': u.username,
                    'profile_image': u.profile_image,
                    'role': u.role,
                    'online': u.is_online
                } for u in active_contributors],
                'recent_proposals': [{
                    'id': p.id,
                    'title': p.title,
                    'status': p.status,
                    'type': p.proposal_type,
                    'date': p.created_at.strftime('%m/%d/%Y')
                } for p in recent_proposals],
                'quick_actions': {
                    'can_create_proposal': request.user.is_authenticated and request.user.role in ['contributor', 'admin'],
                    'can_vote': request.user.is_authenticated and request.user.role != 'citizen',
                    'pending_votes': Proposal.objects.filter(
                        status='voting'
                    ).exclude(
                        votes__voter=request.user
                    ).count() if request.user.is_authenticated else 0
                }
            })
        except Exception as e:
            import traceback
            return Response({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth_status(request):
    """Check if user is authenticated and return user info"""
    return Response({
        'authenticated': True,
        'user': UserProfileSerializer(request.user).data
    })
