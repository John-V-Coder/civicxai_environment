from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from ..serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    DashboardMetricsSerializer,
    UserListSerializer
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


class RequestPasswordResetView(APIView):
    """Request password reset - sends email with reset token"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link (frontend URL)
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
            reset_link = f"{frontend_url}/reset-password/{uid}/{token}"
            
            # Send email (in production, use proper email templates)
            try:
                send_mail(
                    subject='CivicXAI - Password Reset Request',
                    message=f'Click the link below to reset your password:\n\n{reset_link}\n\nThis link will expire in 24 hours.\n\nIf you did not request this reset, please ignore this email.',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@civicxai.com'),
                    recipient_list=[email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                # Log error but don't expose to user
                print(f"Email send error: {e}")
                email_sent = False
            
            return Response({
                'success': True,
                'message': 'If an account with that email exists, a password reset link has been sent.',
                'reset_link': reset_link if not email_sent else None  # Include link for dev/testing
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Don't reveal if user exists or not (security)
            return Response({
                'success': True,
                'message': 'If an account with that email exists, a password reset link has been sent.'
            }, status=status.HTTP_200_OK)


class VerifyPasswordResetTokenView(APIView):
    """Verify if password reset token is valid"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        
        if not uid or not token:
            return Response({
                'success': False,
                'error': 'UID and token are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                return Response({
                    'success': True,
                    'message': 'Token is valid',
                    'email': user.email
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid or expired reset token'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'success': False,
                'error': 'Invalid reset token'
            }, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """Reset password using token"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not uid or not token or not new_password:
            return Response({
                'success': False,
                'error': 'UID, token, and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({
                'success': False,
                'error': 'Password must be at least 8 characters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                
                return Response({
                    'success': True,
                    'message': 'Password has been reset successfully'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid or expired reset token'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'success': False,
                'error': 'Invalid reset token'
            }, status=status.HTTP_400_BAD_REQUEST)


# =====================================================
#  User Management Views
# =====================================================


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
