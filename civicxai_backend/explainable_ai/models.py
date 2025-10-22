from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, Avg
import uuid


# =====================================================
# Authentication & User Management
# =====================================================

class User(AbstractUser):
    """Extended user model for CivicXAI governance system"""
    
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('contributor', 'Core Contributor'),
        ('admin', 'Administrator'),
        ('analyst', 'Data Analyst'),
    ]
    
    # Profile Information
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    profile_image = models.URLField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Governance Participation
    contribution_score = models.IntegerField(default=0)
    proposals_created = models.IntegerField(default=0)
    votes_cast = models.IntegerField(default=0)
    
    # Activity Tracking
    last_activity = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)
    joined_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-contribution_score', '-date_joined']
        
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def update_contribution_score(self):
        """Calculate and update user's contribution score"""
        # Count leads and member workgroups dynamically
        leads_count = self.workgroups_lead.count() if hasattr(self, 'workgroups_lead') else 0
        members_count = self.workgroups_member.count() if hasattr(self, 'workgroups_member') else 0
        
        self.contribution_score = (
            self.proposals_created * 10 +
            self.votes_cast * 2 +
            leads_count * 20 +
            members_count * 5
        )
        self.save()


# =====================================================
# Regional Data & Allocation Models
# =====================================================

class Region(models.Model):
    """Represents a geographical region for resource allocation"""
    
    region_id = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    county = models.CharField(max_length=100, blank=True)
    population = models.IntegerField(validators=[MinValueValidator(0)])
    area_sq_km = models.FloatField(validators=[MinValueValidator(0)])
    
    # Socio-Economic Indicators (0-1 scale)
    poverty_index = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    unemployment_rate = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    education_index = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    health_index = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Environmental Indicators (0-1 scale)
    deforestation_rate = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    air_quality_index = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    water_scarcity = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Project Impact Metrics
    project_impact_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0.5)
    infrastructure_need = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0.5)
    
    # Governance Risk
    corruption_risk = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0.3)
    
    # Calculated Fields
    priority_score = models.FloatField(default=0, editable=False)
    current_allocation = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_assessment = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority_score', 'name']
        indexes = [
            models.Index(fields=['priority_score']),
            models.Index(fields=['region_id']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.region_id})"
    
    def calculate_priority(self):
        """Calculate priority score using weighted factors"""
        poverty_weight = 0.40
        impact_weight = 0.30
        environment_weight = 0.20
        corruption_penalty = 0.10
        
        self.priority_score = (
            self.poverty_index * poverty_weight +
            self.project_impact_score * impact_weight +
            self.deforestation_rate * environment_weight -
            self.corruption_risk * corruption_penalty
        )
        self.save()
        return self.priority_score


class Allocation(models.Model):
    """Records resource allocation decisions with explanations"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    allocation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='allocations')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fiscal_year = models.IntegerField()
    quarter = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    
    priority_score_snapshot = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    explanation = models.TextField()
    explanation_factors = models.JSONField(default=dict)
    policy_compliance = models.TextField(blank=True)
    suggested_actions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['region', 'fiscal_year', 'quarter']]
    
    def __str__(self):
        return f"{self.region.name} - Q{self.quarter}/{self.fiscal_year} - ${self.amount:,.2f}"


# =====================================================
# Workgroups & Governance
# =====================================================

class Workgroup(models.Model):
    """Represents working groups focused on specific governance areas"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    CATEGORY_CHOICES = [
        ('infrastructure', 'Infrastructure'),
        ('environment', 'Environment'),
        ('education', 'Education'),
        ('health', 'Health'),
        ('economy', 'Economy'),
        ('governance', 'Governance'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    proposals_count = models.IntegerField(default=0)
    completed_tasks = models.IntegerField(default=0)
    budget_allocated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    members = models.ManyToManyField(User, related_name='workgroups_member', blank=True)
    leads = models.ManyToManyField(User, related_name='workgroups_lead', blank=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def update_metrics(self):
        self.proposals_count = self.proposals.count()
        self.save()


# =====================================================
# Proposals & Voting
# =====================================================

class Proposal(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('voting', 'Voting'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
        ('expired', 'Expired'),
    ]
    
    TYPE_CHOICES = [
        ('allocation', 'Resource Allocation'),
        ('policy', 'Policy Change'),
        ('project', 'New Project'),
        ('budget', 'Budget Adjustment'),
        ('quarterly', 'Quarterly Report'),
    ]
    
    proposal_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    proposal_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_proposals')
    workgroup = models.ForeignKey(Workgroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='proposals')
    related_region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    votes_for = models.IntegerField(default=0)
    votes_against = models.IntegerField(default=0)
    quorum_required = models.IntegerField(default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    review_deadline = models.DateTimeField(null=True, blank=True)
    voting_deadline = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    ai_risk_score = models.FloatField(null=True, blank=True)
    ai_recommendation = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def calculate_approval(self):
        total_votes = self.votes_for + self.votes_against
        if total_votes >= self.quorum_required:
            return self.votes_for > self.votes_against
        return False


class Vote(models.Model):
    VOTE_CHOICES = [
        ('for', 'For'),
        ('against', 'Against'),
        ('abstain', 'Abstain'),
    ]
    
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    vote = models.CharField(max_length=10, choices=VOTE_CHOICES)
    comment = models.TextField(blank=True)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['proposal', 'voter']]
        ordering = ['-voted_at']
    
    def __str__(self):
        return f"{self.voter.username} - {self.proposal.title} ({self.vote})"


# =====================================================
# Events & Calendar
# =====================================================

class Event(models.Model):
    EVENT_TYPES = [
        ('deadline', 'Deadline'),
        ('meeting', 'Meeting'),
        ('report', 'Report Due'),
        ('voting', 'Voting Period'),
        ('review', 'Review Window'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    
    related_proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, null=True, blank=True)
    related_workgroup = models.ForeignKey(Workgroup, on_delete=models.CASCADE, null=True, blank=True)
    
    is_high_priority = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%Y-%m-%d')}"


# =====================================================
# Analytics & Metrics
# =====================================================

class DashboardMetrics(models.Model):
    date = models.DateField(unique=True)
    
    total_workgroups = models.IntegerField(default=0)
    active_workgroups = models.IntegerField(default=0)
    inactive_workgroups = models.IntegerField(default=0)
    
    total_members = models.IntegerField(default=0)
    active_members = models.IntegerField(default=0)
    new_members_month = models.IntegerField(default=0)
    
    total_proposals = models.IntegerField(default=0)
    proposals_in_review = models.IntegerField(default=0)
    proposals_approved = models.IntegerField(default=0)
    proposals_rejected = models.IntegerField(default=0)
    
    total_allocated = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_disbursed = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    regions_funded = models.IntegerField(default=0)
    average_priority_score = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Metrics for {self.date}"
    
    @classmethod
    def calculate_today_metrics(cls):
        today = timezone.now().date()
        metrics, _ = cls.objects.get_or_create(date=today)
        
        metrics.total_workgroups = Workgroup.objects.count()
        metrics.active_workgroups = Workgroup.objects.filter(status='active').count()
        metrics.inactive_workgroups = Workgroup.objects.filter(status='inactive').count()
        
        metrics.total_members = User.objects.filter(is_active=True).count()
        metrics.active_members = User.objects.filter(last_activity__gte=timezone.now() - timezone.timedelta(days=30)).count()
        
        metrics.total_proposals = Proposal.objects.count()
        metrics.proposals_in_review = Proposal.objects.filter(status='in_review').count()
        metrics.proposals_approved = Proposal.objects.filter(status='approved').count()
        metrics.proposals_rejected = Proposal.objects.filter(status='rejected').count()
        
        metrics.total_allocated = Allocation.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        metrics.total_disbursed = Allocation.objects.filter(status='disbursed').aggregate(Sum('amount'))['amount__sum'] or 0
        
        metrics.regions_funded = Region.objects.filter(current_allocation__gt=0).count()
        metrics.average_priority_score = Region.objects.aggregate(Avg('priority_score'))['priority_score__avg'] or 0
        
        metrics.save()
        return metrics


# =====================================================
# AI Data Sources
# =====================================================

class DataSource(models.Model):
    """Store PDFs and website links for AI agent to use as knowledge base"""
    
    SOURCE_TYPE_CHOICES = [
        ('pdf', 'PDF Document'),
        ('url', 'Website Link'),
        ('document', 'Text Document'),
    ]
    
    CATEGORY_CHOICES = [
        ('policy', 'Policy Document'),
        ('research', 'Research Paper'),
        ('data', 'Data Source'),
        ('guideline', 'Guideline'),
        ('report', 'Report'),
        ('reference', 'Reference Material'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='reference')
    
    # Source Location
    url = models.URLField(max_length=500, blank=True, null=True, help_text="URL for websites or online documents")
    file = models.FileField(upload_to='data_sources/', blank=True, null=True, help_text="Upload PDF or document")
    
    # Metadata
    author = models.CharField(max_length=255, blank=True)
    published_date = models.DateField(blank=True, null=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Content Summary (for quick reference)
    summary = models.TextField(blank=True, help_text="AI-generated or manual summary of content")
    key_points = models.TextField(blank=True, help_text="Key takeaways, one per line")
    
    # Usage Tracking
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0, help_text="Number of times referenced by AI")
    last_used = models.DateTimeField(blank=True, null=True)
    
    # Admin
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='data_sources_added')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_type', 'category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_source_type_display()})"
    
    def increment_usage(self):
        """Track when this source is used"""
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])
    
    def get_content_preview(self):
        """Get a preview of the content"""
        if self.summary:
            return self.summary[:200] + '...' if len(self.summary) > 200 else self.summary
        return self.description[:200] + '...' if len(self.description) > 200 else self.description
    
    @property
    def source_location(self):
        """Return the actual location of the source"""
        if self.url:
            return self.url
        elif self.file:
            return self.file.url
        return None


# =====================================================
# AI Gateway Allocation Requests
# =====================================================

class AllocationRequest(models.Model):
    """
    Stores allocation requests submitted through AI Gateway
    Displays in dashboard as proposals
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('processing', 'Being Processed'),
        ('analyzed', 'Analysis Complete'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Request identification
    request_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    region_id = models.CharField(max_length=100, db_index=True)
    region_name = models.CharField(max_length=200, help_text="Human-readable region name")
    
    # Metrics submitted
    poverty_index = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    project_impact = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    environmental_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    corruption_risk = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Additional context
    notes = models.TextField(blank=True)
    urls = models.TextField(blank=True, help_text="Reference URLs, one per line")
    
    # AI Analysis Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority_score = models.FloatField(null=True, blank=True)
    priority_level = models.CharField(max_length=50, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    recommended_allocation_percentage = models.FloatField(null=True, blank=True)
    
    # AI Recommendations
    ai_recommendation = models.TextField(blank=True)
    key_findings = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    
    # Files attached
    files_attached = models.IntegerField(default=0)
    file_paths = models.JSONField(default=list, blank=True)
    
    # Tracking
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['region_id']),
        ]
    
    def __str__(self):
        return f"{self.region_name} - {self.region_id} ({self.get_status_display()})"
    
    def get_metrics_dict(self):
        """Return metrics as dictionary for display"""
        return {
            'poverty_index': self.poverty_index,
            'project_impact': self.project_impact,
            'environmental_score': self.environmental_score,
            'corruption_risk': self.corruption_risk,
        }
    
    def update_from_gateway_result(self, result_data):
        """Update with results from Gateway API"""
        if not result_data:
            return
        
        recommendation = result_data.get('recommendation', {})
        self.status = 'analyzed'
        self.analyzed_at = timezone.now()
        
        self.priority_level = recommendation.get('priority_level', '')
        self.confidence_score = recommendation.get('confidence_score', 0)
        self.recommended_allocation_percentage = recommendation.get('recommended_allocation_percentage', 0)
        self.ai_recommendation = recommendation.get('rationale', '')
        self.key_findings = recommendation.get('key_findings', [])
        self.recommendations = recommendation.get('recommendations', [])
        
        self.save()


class ExplanationRequest(models.Model):
    """
    Stores explanation requests submitted through AI Gateway
    Displays in dashboard alongside allocation requests
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending Generation'),
        ('processing', 'Being Processed'),
        ('completed', 'Explanation Ready'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    LANGUAGE_CHOICES = [
        ('technical', 'Technical'),
        ('simple', 'Simple'),
        ('policy', 'Policy-focused'),
    ]
    
    # Request identification
    request_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    region_id = models.CharField(max_length=100, db_index=True)
    region_name = models.CharField(max_length=200, help_text="Human-readable region name", blank=True)
    
    # Request details
    allocation_data = models.JSONField(default=dict, blank=True, help_text="Allocation data to explain")
    context = models.TextField(blank=True, help_text="Additional context for explanation")
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='simple')
    notes = models.TextField(blank=True)
    
    # AI Generated Explanation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    explanation_text = models.TextField(blank=True, help_text="Generated explanation")
    key_points = models.JSONField(default=list, blank=True)
    policy_implications = models.JSONField(default=list, blank=True)
    transparency_score = models.FloatField(null=True, blank=True)
    
    # Files attached
    files_attached = models.IntegerField(default=0)
    file_paths = models.JSONField(default=list, blank=True)
    
    # Tracking
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['region_id']),
        ]
    
    def __str__(self):
        return f"Explanation for {self.region_name or self.region_id} ({self.get_status_display()})"
    
    def update_from_gateway_result(self, result_data):
        """Update with results from Gateway API"""
        if not result_data:
            return
        
        explanation = result_data.get('explanation', {})
        self.status = 'completed'
        self.completed_at = timezone.now()
        
        self.explanation_text = explanation.get('text', '')
        self.key_points = explanation.get('key_points', [])
        self.policy_implications = explanation.get('policy_implications', [])
        self.transparency_score = explanation.get('transparency_score', 0)
        
        self.save()
