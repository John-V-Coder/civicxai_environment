from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CalculatePriorityView,
    HealthCheckView,
    GenerateExplanationAPIView,
    RegionViewSet,
    AllocationViewSet,
    WorkgroupViewSet,
    ProposalViewSet,
    EventViewSet,
    VoteViewSet
)
from .auth_views import (
    CustomTokenObtainPairView,
    RegisterView,
    LogoutView,
    UserProfileView,
    ChangePasswordView,
    UserListView,
    UpdateUserRoleView,
    DashboardOverviewView,
    check_auth_status
)
from .gateway_views import (
    GatewayAllocationRequestView,
    GatewayExplanationRequestView,
    GatewayStatusView,
    GatewayHealthView,
    GatewayMetricsView
)

# =====================================================
# DRF Router for ViewSets
# =====================================================
router = DefaultRouter()
router.register(r'regions', RegionViewSet, basename='region')
router.register(r'allocations', AllocationViewSet, basename='allocation')
router.register(r'workgroups', WorkgroupViewSet, basename='workgroup')
router.register(r'proposals', ProposalViewSet, basename='proposal')
router.register(r'events', EventViewSet, basename='event')
router.register(r'votes', VoteViewSet, basename='vote')

# =====================================================
# URL Patterns
# =====================================================
urlpatterns = [
    # ===== Authentication =====
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/status/', check_auth_status, name='auth_status'),

    # ===== User Management =====
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('user/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/role/', UpdateUserRoleView.as_view(), name='update_user_role'),

    # ===== Dashboard =====
    path('dashboard/', DashboardOverviewView.as_view(), name='dashboard_overview'),

    # ===== MeTTa / Explainable AI =====
    path('metta/calculate-priority/', CalculatePriorityView.as_view(), name='calculate-priority'),
    path('metta/health/', HealthCheckView.as_view(), name='health-check'),
    path('metta/explain/', GenerateExplanationAPIView.as_view(), name='generate_explanation'),

    # ===== uAgents Gateway Integration =====
    path('gateway/allocation/request/', GatewayAllocationRequestView.as_view(), name='gateway_allocation_request'),
    path('gateway/explanation/request/', GatewayExplanationRequestView.as_view(), name='gateway_explanation_request'),
    path('gateway/status/<str:request_id>/', GatewayStatusView.as_view(), name='gateway_status'),
    path('gateway/health/', GatewayHealthView.as_view(), name='gateway_health'),
    path('gateway/metrics/', GatewayMetricsView.as_view(), name='gateway_metrics'),

    # ===== Include ViewSet Routers =====
    path('', include(router.urls)),
]
