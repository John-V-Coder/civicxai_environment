from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from explainable_ai.models import (
    Region, Workgroup, Proposal, Event, DashboardMetrics
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('🚀 Starting to populate sample data...\n')
        
        # Create sample users
        self.create_users()
        
        # Create regions
        self.create_regions()
        
        # Create workgroups
        self.create_workgroups()
        
        # Create proposals
        self.create_proposals()
        
        # Create events
        self.create_events()
        
        # Calculate dashboard metrics
        DashboardMetrics.calculate_today_metrics()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data populated successfully!'))
    
    def create_users(self):
        """Create sample users with different roles"""
        self.stdout.write('Creating users...')
        
        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@civicxai.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User',
                'bio': 'System Administrator',
                'contribution_score': 100
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'  ✓ Created admin user (password: admin123)')
        
        # Create contributors
        contributors = [
            ('0xkenichi', 'Ken', 'Nakamoto', 'contributor', 85),
            ('ayomishu', 'Ayomi', 'Shu', 'contributor', 72),
            ('cardano_wolf', 'Cardano', 'Wolf', 'contributor', 68),
            ('dukepeter', 'Duke', 'Peter', 'contributor', 55),
        ]
        
        for username, first, last, role, score in contributors:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@civicxai.com',
                    'role': role,
                    'first_name': first,
                    'last_name': last,
                    'bio': f'Core contributor focused on governance and civic tech',
                    'contribution_score': score,
                    'is_online': random.choice([True, False])
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  ✓ Created {username}')
        
        # Create regular citizens
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                username=f'citizen{i}',
                defaults={
                    'email': f'citizen{i}@civicxai.com',
                    'role': 'citizen',
                    'first_name': f'Citizen',
                    'last_name': f'{i}',
                    'bio': 'Active community member',
                    'contribution_score': random.randint(5, 30)
                }
            )
            if created:
                user.set_password('password123')
                user.save()
    
    def create_regions(self):
        """Create sample regions with various metrics"""
        self.stdout.write('Creating regions...')
        
        regions_data = [
            ('KAK001', 'Kakamega', 'Kakamega County', 2200000, 3050.3, 0.81, 0.75, 0.92),
            ('TUR001', 'Turkana', 'Turkana County', 926000, 68680.0, 0.89, 0.85, 0.45),
            ('NAI001', 'Nairobi', 'Nairobi County', 4400000, 696.1, 0.35, 0.05, 0.95),
            ('MOM001', 'Mombasa', 'Mombasa County', 1200000, 219.9, 0.48, 0.22, 0.88),
            ('KIS001', 'Kisumu', 'Kisumu County', 1155000, 2085.9, 0.62, 0.45, 0.76),
            ('NYE001', 'Nyeri', 'Nyeri County', 759000, 2361.0, 0.44, 0.68, 0.82),
            ('KIL001', 'Kilifi', 'Kilifi County', 1450000, 12609.7, 0.71, 0.58, 0.65),
            ('UAS001', 'Uasin Gishu', 'Uasin Gishu County', 1163000, 3345.2, 0.52, 0.35, 0.78),
        ]
        
        for region_id, name, county, pop, area, poverty, deforest, impact in regions_data:
            region, created = Region.objects.get_or_create(
                region_id=region_id,
                defaults={
                    'name': name,
                    'county': county,
                    'population': pop,
                    'area_sq_km': area,
                    'poverty_index': poverty,
                    'unemployment_rate': random.uniform(0.2, 0.7),
                    'education_index': random.uniform(0.3, 0.8),
                    'health_index': random.uniform(0.3, 0.8),
                    'deforestation_rate': deforest,
                    'air_quality_index': random.uniform(0.2, 0.8),
                    'water_scarcity': random.uniform(0.2, 0.8),
                    'project_impact_score': impact,
                    'infrastructure_need': random.uniform(0.4, 0.9),
                    'corruption_risk': random.uniform(0.1, 0.4),
                }
            )
            if created:
                region.calculate_priority()
                self.stdout.write(f'  ✓ Created {name} region')
    
    def create_workgroups(self):
        """Create sample workgroups"""
        self.stdout.write('Creating workgroups...')
        
        workgroups_data = [
            ('Infrastructure Development', 'infrastructure-dev', 'infrastructure', 
             'Working on road, water, and electricity infrastructure projects'),
            ('Environmental Protection', 'environmental-protection', 'environment',
             'Focus on reforestation, conservation, and climate action'),
            ('Education Improvement', 'education-improvement', 'education',
             'Improving access to quality education in underserved areas'),
            ('Healthcare Access', 'healthcare-access', 'health',
             'Ensuring universal healthcare coverage and facility improvement'),
            ('Economic Development', 'economic-development', 'economy',
             'Supporting SMEs, job creation, and economic empowerment'),
            ('Governance & Transparency', 'governance-transparency', 'governance',
             'Promoting transparent governance and citizen participation'),
        ]
        
        contributors = User.objects.filter(role='contributor')
        
        for name, slug, category, description in workgroups_data:
            workgroup, created = Workgroup.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': description,
                    'category': category,
                    'status': random.choice(['active', 'active', 'inactive']),
                    'budget_allocated': random.uniform(100000, 5000000)
                }
            )
            
            if created:
                # Add random members and leads
                members = random.sample(list(contributors), k=min(3, len(contributors)))
                for member in members:
                    workgroup.members.add(member)
                
                if members:
                    workgroup.leads.add(members[0])
                
                self.stdout.write(f'  ✓ Created {name} workgroup')
    
    def create_proposals(self):
        """Create sample proposals"""
        self.stdout.write('Creating proposals...')
        
        contributors = User.objects.filter(role='contributor')
        workgroups = Workgroup.objects.all()
        regions = Region.objects.all()
        
        proposals_data = [
            ('Q3 2025 Infrastructure Budget', 'quarterly', 'in_review',
             'Quarterly budget allocation report for infrastructure projects'),
            ('Reforestation Initiative in Kakamega', 'project', 'in_review',
             'Large-scale tree planting project to combat deforestation'),
            ('Healthcare Center Construction', 'allocation', 'in_review',
             'Funding for new healthcare centers in underserved regions'),
            ('Digital Literacy Program', 'project', 'voting',
             'Providing computers and internet to rural schools'),
            ('Water Resource Management Policy', 'policy', 'approved',
             'New policy framework for sustainable water resource management'),
            ('SME Support Fund', 'budget', 'draft',
             'Creating a fund to support small and medium enterprises'),
            ('Road Network Expansion', 'project', 'in_review',
             'Expanding and improving road connectivity in rural areas'),
            ('Anti-Corruption Measures', 'policy', 'voting',
             'Implementation of transparent procurement and audit systems'),
        ]
        
        for title, p_type, status, description in proposals_data:
            proposal, created = Proposal.objects.get_or_create(
                title=title,
                defaults={
                    'description': description,
                    'proposal_type': p_type,
                    'author': random.choice(contributors) if contributors else User.objects.first(),
                    'workgroup': random.choice(workgroups) if workgroups else None,
                    'related_region': random.choice(regions) if regions else None,
                    'requested_amount': random.uniform(50000, 2000000) if p_type in ['allocation', 'budget', 'project'] else None,
                    'status': status,
                    'priority': random.randint(1, 10),
                    'votes_for': random.randint(0, 20) if status in ['voting', 'approved'] else 0,
                    'votes_against': random.randint(0, 10) if status in ['voting', 'approved'] else 0,
                    'quorum_required': 3,
                    'review_deadline': timezone.now() + timedelta(days=30) if status == 'in_review' else None,
                    'voting_deadline': timezone.now() + timedelta(days=7) if status == 'voting' else None,
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created proposal: {title}')
    
    def create_events(self):
        """Create sample calendar events"""
        self.stdout.write('Creating events...')
        
        events_data = [
            ('Q3 Reports & Q4 Budgets Deadline', 'deadline', 0, True),
            ('Review & Comment Window Closes', 'review', 3, True),
            ('Editing Locked: Consent Opens', 'deadline', 3, True),
            ('Consent Deadline', 'deadline', 6, False),
            ('Quarterly Governance Meeting', 'meeting', 10, False),
            ('Infrastructure Working Group Session', 'meeting', 12, False),
            ('Environmental Impact Assessment Due', 'report', 15, True),
            ('Community Feedback Session', 'meeting', 20, False),
        ]
        
        admin_user = User.objects.filter(role='admin').first()
        
        for title, event_type, days_from_now, high_priority in events_data:
            event, created = Event.objects.get_or_create(
                title=title,
                defaults={
                    'description': f'Important {event_type} event for governance process',
                    'event_type': event_type,
                    'start_date': timezone.now() + timedelta(days=days_from_now),
                    'end_date': timezone.now() + timedelta(days=days_from_now + 1) if event_type == 'meeting' else None,
                    'is_high_priority': high_priority,
                    'created_by': admin_user,
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created event: {title}')
