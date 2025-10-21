from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    User, Region, Allocation, Workgroup, Proposal, 
    Vote, Event, DashboardMetrics, DataSource
)


# =====================================================
# User Admin
# =====================================================

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Enhanced admin interface for User model"""
    
    list_display = [
        'username', 'email', 'role', 'contribution_score', 
        'is_online_indicator', 'proposals_created', 'votes_cast'
    ]
    list_filter = ['role', 'is_online', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-contribution_score', '-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('CivicXAI Profile', {
            'fields': ('role', 'profile_image', 'bio', 'contribution_score')
        }),
        ('Activity', {
            'fields': ('proposals_created', 'votes_cast', 'is_online', 'last_activity')
        }),
        # Workgroups are now through Workgroup model
    )
    
    def is_online_indicator(self, obj):
        if obj.is_online:
            return format_html('<span style="color: green;">●</span> Online')
        return format_html('<span style="color: gray;">○</span> Offline')
    is_online_indicator.short_description = 'Status'


# =====================================================
# Region Admin
# =====================================================

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'region_id', 'county', 'population',
        'priority_score_display', 'current_allocation_display'
    ]
    list_filter = ['county', 'priority_score']
    search_fields = ['name', 'region_id', 'county']
    ordering = ['-priority_score']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('region_id', 'name', 'county', 'population', 'area_sq_km')
        }),
        ('Socio-Economic Indicators', {
            'fields': ('poverty_index', 'unemployment_rate', 'education_index', 'health_index')
        }),
        ('Environmental Indicators', {
            'fields': ('deforestation_rate', 'air_quality_index', 'water_scarcity')
        }),
        ('Impact & Governance', {
            'fields': ('project_impact_score', 'infrastructure_need', 'corruption_risk')
        }),
        ('Allocation', {
            'fields': ('priority_score', 'current_allocation', 'last_assessment'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['priority_score']
    
    def priority_score_display(self, obj):
        color = 'green' if obj.priority_score > 0.7 else 'orange' if obj.priority_score > 0.4 else 'red'
        return format_html('<span style="color: {};">{:.3f}</span>', color, obj.priority_score)
    priority_score_display.short_description = 'Priority'
    
    def current_allocation_display(self, obj):
        return format_html('${:,.2f}', obj.current_allocation)
    current_allocation_display.short_description = 'Allocation'
    
    actions = ['calculate_priorities']
    
    def calculate_priorities(self, request, queryset):
        for region in queryset:
            region.calculate_priority()
        self.message_user(request, f"Calculated priorities for {queryset.count()} regions.")
    calculate_priorities.short_description = "Recalculate priority scores"


# =====================================================
# Allocation Admin
# =====================================================

@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = [
        'region', 'fiscal_year', 'quarter', 'amount_display',
        'status', 'priority_score_snapshot', 'created_at'
    ]
    list_filter = ['status', 'fiscal_year', 'quarter']
    search_fields = ['region__name', 'allocation_id']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Allocation Details', {
            'fields': ('allocation_id', 'region', 'amount', 'fiscal_year', 'quarter', 'priority_score_snapshot')
        }),
        ('Status', {
            'fields': ('status', 'approved_by', 'approved_at', 'disbursed_at')
        }),
        ('AI Explanation', {
            'fields': ('explanation', 'explanation_factors', 'policy_compliance', 'suggested_actions'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['allocation_id', 'priority_score_snapshot', 'created_at']
    
    def amount_display(self, obj):
        return format_html('${:,.2f}', obj.amount)
    amount_display.short_description = 'Amount'


# =====================================================
# Workgroup Admin
# =====================================================

@admin.register(Workgroup)
class WorkgroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'status', 'members_count', 'proposals_count', 'budget_display']
    list_filter = ['status', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    filter_horizontal = ['members', 'leads']
    
    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = 'Members'
    
    def budget_display(self, obj):
        return format_html('${:,.2f}', obj.budget_allocated)
    budget_display.short_description = 'Budget'


# =====================================================
#  Proposal Admin
# =====================================================

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['title', 'proposal_type', 'status', 'author', 'votes_display', 'priority', 'created_at']
    list_filter = ['status', 'proposal_type', 'priority']
    search_fields = ['title', 'description', 'author__username']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('proposal_id', 'title', 'description', 'proposal_type', 'author', 'workgroup')
        }),
        ('Financial', {
            'fields': ('requested_amount', 'approved_amount', 'related_region')
        }),
        ('Status & Voting', {
            'fields': ('status', 'priority', 'votes_for', 'votes_against', 'quorum_required', 'review_deadline', 'voting_deadline')
        }),
        ('AI Analysis', {
            'fields': ('ai_risk_score', 'ai_recommendation'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['proposal_id', 'votes_for', 'votes_against']
    
    def votes_display(self, obj):
        total = obj.votes_for + obj.votes_against
        if total > 0:
            approval_rate = (obj.votes_for / total) * 100
            color = 'green' if approval_rate > 60 else 'orange' if approval_rate > 40 else 'red'
            return format_html('<span style="color: {};">👍 {} / 👎 {} ({:.0f}%)</span>',
                               color, obj.votes_for, obj.votes_against, approval_rate)
        return "No votes yet"
    votes_display.short_description = 'Votes'


# =====================================================
# Vote Admin
# =====================================================

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['proposal', 'voter', 'vote', 'voted_at']
    list_filter = ['vote', 'voted_at']
    search_fields = ['proposal__title', 'voter__username']
    ordering = ['-voted_at']
    date_hierarchy = 'voted_at'


# =====================================================
# Event Admin
# =====================================================

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'is_high_priority', 'created_by']
    list_filter = ['event_type', 'is_high_priority']
    search_fields = ['title', 'description']
    ordering = ['start_date']
    date_hierarchy = 'start_date'


# =====================================================
# Dashboard Metrics Admin
# =====================================================

@admin.register(DashboardMetrics)
class DashboardMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_workgroups', 'active_workgroups', 'total_members', 'total_proposals', 'total_allocated_display']
    ordering = ['-date']
    date_hierarchy = 'date'
    
    readonly_fields = [
        'date', 'total_workgroups', 'active_workgroups', 'inactive_workgroups',
        'total_members', 'active_members', 'new_members_month',
        'total_proposals', 'proposals_in_review', 'proposals_approved',
        'proposals_rejected', 'total_allocated', 'total_disbursed',
        'regions_funded', 'average_priority_score'
    ]
    
    def total_allocated_display(self, obj):
        return format_html('${:,.2f}', obj.total_allocated)
    total_allocated_display.short_description = 'Total Allocated'
    
    actions = ['recalculate_metrics']
    
    def recalculate_metrics(self, request, queryset):
        for metric in queryset:
            DashboardMetrics.calculate_today_metrics()
        self.message_user(request, "Metrics recalculated successfully.")
    recalculate_metrics.short_description = "Recalculate selected metrics"


# =====================================================
# Data Source Admin
# =====================================================

@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    """Admin interface for AI Data Sources"""
    
    list_display = [
        'title', 'source_type', 'category', 'is_active', 
        'usage_count', 'added_by', 'created_at'
    ]
    list_filter = ['source_type', 'category', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'tags', 'author', 'summary']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'source_type', 'category', 'is_active')
        }),
        ('Source Location', {
            'fields': ('url', 'file')
        }),
        ('Metadata', {
            'fields': ('author', 'published_date', 'tags')
        }),
        ('Content Summary', {
            'fields': ('summary', 'key_points'),
            'classes': ('collapse',)
        }),
        ('Usage Tracking', {
            'fields': ('usage_count', 'last_used', 'added_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['usage_count', 'last_used', 'added_by']
    
    actions = ['activate_sources', 'deactivate_sources', 'reset_usage_count']
    
    def activate_sources(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"Activated {count} data source(s).")
    activate_sources.short_description = "Activate selected sources"
    
    def deactivate_sources(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {count} data source(s).")
    deactivate_sources.short_description = "Deactivate selected sources"
    
    def reset_usage_count(self, request, queryset):
        count = queryset.update(usage_count=0, last_used=None)
        self.message_user(request, f"Reset usage count for {count} source(s).")
    reset_usage_count.short_description = "Reset usage counters"
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
