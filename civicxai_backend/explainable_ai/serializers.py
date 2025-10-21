from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import (
    User, Region, Allocation, Workgroup, Proposal, 
    Vote, Event, DashboardMetrics, DataSource
)

User = get_user_model()


# =====================================================
# Authentication Serializers
# =====================================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user info"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['role'] = user.role
        token['user_id'] = str(user.user_id)
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra user data to response
        data['user'] = {
            'id': self.user.id,
            'user_id': str(self.user.user_id),
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'profile_image': self.user.profile_image,
            'contribution_score': self.user.contribution_score,
        }
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'bio'
        ]
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profiles"""
    
    workgroups_member_count = serializers.SerializerMethodField()
    workgroups_lead_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'user_id', 'username', 'email', 'first_name', 'last_name',
            'role', 'profile_image', 'bio', 'contribution_score',
            'proposals_created', 'votes_cast', 'is_online', 'last_activity',
            'joined_date', 'workgroups_member_count', 'workgroups_lead_count'
        ]
        read_only_fields = ['user_id', 'contribution_score', 'proposals_created', 'votes_cast']
    
    def get_workgroups_member_count(self, obj):
        return obj.workgroups_member.count()
    
    def get_workgroups_lead_count(self, obj):
        return obj.workgroups_lead.count()


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for user lists"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image', 'role', 'is_online']


# =====================================================
# Region & Allocation Serializers
# =====================================================

class RegionSerializer(serializers.ModelSerializer):
    """Full region serializer with all metrics"""
    
    allocation_count = serializers.SerializerMethodField()
    latest_allocation = serializers.SerializerMethodField()
    
    class Meta:
        model = Region
        fields = '__all__'
        read_only_fields = ['priority_score', 'created_at', 'updated_at']
    
    def get_allocation_count(self, obj):
        return obj.allocations.count()
    
    def get_latest_allocation(self, obj):
        latest = obj.allocations.first()
        if latest:
            return {
                'amount': latest.amount,
                'fiscal_year': latest.fiscal_year,
                'quarter': latest.quarter,
                'status': latest.status
            }
        return None


class RegionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for region lists"""
    
    class Meta:
        model = Region
        fields = [
            'id', 'region_id', 'name', 'county', 'population',
            'priority_score', 'current_allocation'
        ]


class AllocationSerializer(serializers.ModelSerializer):
    """Allocation serializer with nested region data"""
    
    region_name = serializers.CharField(source='region.name', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    
    class Meta:
        model = Allocation
        fields = '__all__'
        read_only_fields = ['allocation_id', 'created_at', 'approved_at', 'disbursed_at']


class AllocationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating allocations"""
    
    class Meta:
        model = Allocation
        fields = [
            'region', 'amount', 'fiscal_year', 'quarter',
            'priority_score_snapshot', 'explanation',
            'explanation_factors', 'policy_compliance', 'suggested_actions'
        ]
    
    def create(self, validated_data):
        # Get current priority score from region
        region = validated_data['region']
        validated_data['priority_score_snapshot'] = region.priority_score
        
        return super().create(validated_data)


# =====================================================
# Workgroup Serializers
# =====================================================

class WorkgroupSerializer(serializers.ModelSerializer):
    """Full workgroup serializer"""
    
    members_count = serializers.SerializerMethodField()
    leads = UserListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Workgroup
        fields = '__all__'
        read_only_fields = ['created_at', 'last_activity', 'proposals_count']
    
    def get_members_count(self, obj):
        return obj.members.count()


class WorkgroupListSerializer(serializers.ModelSerializer):
    """Lightweight workgroup list serializer"""
    
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workgroup
        fields = [
            'id', 'name', 'slug', 'category', 'status',
            'members_count', 'proposals_count'
        ]
    
    def get_members_count(self, obj):
        return obj.members.count()


# =====================================================
# Proposal & Voting Serializers
# =====================================================

class ProposalSerializer(serializers.ModelSerializer):
    """Full proposal serializer"""
    
    author_username = serializers.CharField(source='author.username', read_only=True)
    workgroup_name = serializers.CharField(source='workgroup.name', read_only=True)
    region_name = serializers.CharField(source='related_region.name', read_only=True)
    vote_count = serializers.SerializerMethodField()
    user_has_voted = serializers.SerializerMethodField()
    
    class Meta:
        model = Proposal
        fields = '__all__'
        read_only_fields = [
            'proposal_id', 'votes_for', 'votes_against',
            'created_at', 'submitted_at', 'approved_at'
        ]
    
    def get_vote_count(self, obj):
        return obj.votes.count()
    
    def get_user_has_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.votes.filter(voter=request.user).exists()
        return False


class ProposalListSerializer(serializers.ModelSerializer):
    """Lightweight proposal list serializer"""
    
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'id', 'proposal_id', 'title', 'proposal_type', 'status',
            'priority', 'author_username', 'created_at',
            'votes_for', 'votes_against'
        ]


class VoteSerializer(serializers.ModelSerializer):
    """Vote serializer"""
    
    voter_username = serializers.CharField(source='voter.username', read_only=True)
    proposal_title = serializers.CharField(source='proposal.title', read_only=True)
    
    class Meta:
        model = Vote
        fields = '__all__'
        read_only_fields = ['voted_at']
    
    def create(self, validated_data):
        # Update proposal vote counts
        proposal = validated_data['proposal']
        vote_type = validated_data['vote']
        
        if vote_type == 'for':
            proposal.votes_for += 1
        elif vote_type == 'against':
            proposal.votes_against += 1
        
        proposal.save()
        return super().create(validated_data)


# =====================================================
# Event Serializers
# =====================================================

class EventSerializer(serializers.ModelSerializer):
    """Event serializer"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['created_at']


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight event list serializer"""
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'event_type', 'start_date',
            'end_date', 'is_high_priority'
        ]


# =====================================================
# Dashboard Metrics Serializer
# =====================================================

class DashboardMetricsSerializer(serializers.ModelSerializer):
    """Dashboard metrics serializer"""
    
    class Meta:
        model = DashboardMetrics
        fields = '__all__'
        read_only_fields = ['created_at']


class DashboardSummarySerializer(serializers.Serializer):
    """Summary serializer for dashboard overview"""
    
    workgroups = serializers.DictField()
    members = serializers.DictField()
    proposals = serializers.DictField()
    financials = serializers.DictField()
    recent_events = EventListSerializer(many=True)
    active_contributors = UserListSerializer(many=True)


# =====================================================
# Data Source Serializers
# =====================================================

class DataSourceSerializer(serializers.ModelSerializer):
    """Full data source serializer"""
    
    added_by_username = serializers.CharField(source='added_by.username', read_only=True)
    source_location = serializers.ReadOnlyField()
    content_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = DataSource
        fields = [
            'id', 'title', 'description', 'source_type', 'category',
            'url', 'file', 'author', 'published_date', 'tags',
            'summary', 'key_points', 'is_active', 'usage_count',
            'last_used', 'added_by', 'added_by_username', 'created_at',
            'updated_at', 'source_location', 'content_preview'
        ]
        read_only_fields = ['usage_count', 'last_used', 'created_at', 'updated_at']
    
    def get_content_preview(self, obj):
        return obj.get_content_preview()


class DataSourceListSerializer(serializers.ModelSerializer):
    """Lightweight list serializer"""
    
    source_location = serializers.ReadOnlyField()
    
    class Meta:
        model = DataSource
        fields = [
            'id', 'title', 'source_type', 'category', 'is_active',
            'usage_count', 'created_at', 'source_location'
        ]


class DataSourceCreateSerializer(serializers.ModelSerializer):
    """Create/Update serializer"""
    
    class Meta:
        model = DataSource
        fields = [
            'title', 'description', 'source_type', 'category',
            'url', 'file', 'author', 'published_date', 'tags',
            'summary', 'key_points', 'is_active'
        ]
    
    def validate(self, data):
        """Ensure either URL or file is provided"""
        if not data.get('url') and not data.get('file'):
            raise serializers.ValidationError("Either URL or file must be provided")
        return data
