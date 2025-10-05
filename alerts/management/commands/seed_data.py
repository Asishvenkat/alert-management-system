from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from alerts.models import User, Team, Alert


class Command(BaseCommand):
    help = 'Seed database with initial data'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Clear existing data
        User.objects.filter(is_superuser=False).delete()
        Team.objects.all().delete()
        Alert.objects.all().delete()
        
        # Create Teams
        engineering = Team.objects.create(
            name='Engineering',
            description='Software development team',
            organization='default-org'
        )
        
        marketing = Team.objects.create(
            name='Marketing',
            description='Marketing and growth team',
            organization='default-org'
        )
        
        sales = Team.objects.create(
            name='Sales',
            description='Sales team',
            organization='default-org'
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Created 3 teams'))
        
        # Create Admin User
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            first_name='Admin',
            last_name='User',
            role='admin',
            organization='default-org'
        )
        
        # Create Engineering Users
        john = User.objects.create_user(
            username='john',
            email='john@example.com',
            password='password123',
            first_name='John',
            last_name='Engineer',
            role='user',
            team=engineering,
            organization='default-org'
        )
        
        sarah = User.objects.create_user(
            username='sarah',
            email='sarah@example.com',
            password='password123',
            first_name='Sarah',
            last_name='Developer',
            role='user',
            team=engineering,
            organization='default-org'
        )
        
        # Create Marketing Users
        mike = User.objects.create_user(
            username='mike',
            email='mike@example.com',
            password='password123',
            first_name='Mike',
            last_name='Marketer',
            role='user',
            team=marketing,
            organization='default-org'
        )
        
        lisa = User.objects.create_user(
            username='lisa',
            email='lisa@example.com',
            password='password123',
            first_name='Lisa',
            last_name='Content',
            role='user',
            team=marketing,
            organization='default-org'
        )
        
        # Create Sales User
        tom = User.objects.create_user(
            username='tom',
            email='tom@example.com',
            password='password123',
            first_name='Tom',
            last_name='Sales',
            role='user',
            team=sales,
            organization='default-org'
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Created 6 users (1 admin, 5 regular users)'))
        
        # Create Sample Alerts
        now = timezone.now()
        tomorrow = now + timedelta(days=1)
        next_week = now + timedelta(days=7)
        
        # Organization-wide alert
        alert1 = Alert.objects.create(
            title='System Maintenance Scheduled',
            message='The system will undergo maintenance tomorrow from 2 AM to 4 AM. Please save your work.',
            severity='Warning',
            delivery_type='InApp',
            visibility_type='Organization',
            target_organization='default-org',
            reminder_enabled=True,
            reminder_frequency_hours=2,
            expiry_time=tomorrow,
            created_by=admin
        )
        
        # Team-specific alert (Engineering)
        alert2 = Alert.objects.create(
            title='Code Review Required',
            message='Please review the pending pull requests in the main repository.',
            severity='Info',
            delivery_type='InApp',
            visibility_type='Team',
            reminder_enabled=True,
            reminder_frequency_hours=2,
            expiry_time=next_week,
            created_by=admin
        )
        alert2.target_teams.add(engineering)
        
        # Critical alert for Marketing team
        alert3 = Alert.objects.create(
            title='Campaign Launch Deadline',
            message='The new marketing campaign must be finalized by end of day tomorrow!',
            severity='Critical',
            delivery_type='InApp',
            visibility_type='Team',
            reminder_enabled=True,
            reminder_frequency_hours=2,
            expiry_time=tomorrow,
            created_by=admin
        )
        alert3.target_teams.add(marketing)
        
        # User-specific alert
        alert4 = Alert.objects.create(
            title='Performance Review Reminder',
            message='Your quarterly performance review is scheduled for next week. Please prepare your self-assessment.',
            severity='Info',
            delivery_type='InApp',
            visibility_type='User',
            reminder_enabled=True,
            reminder_frequency_hours=2,
            expiry_time=next_week,
            created_by=admin
        )
        alert4.target_users.add(john)
        
        # Create Sample Alerts summary and output
        self.stdout.write(self.style.SUCCESS('✓ Created 4 sample alerts'))

        self.stdout.write(self.style.SUCCESS('\n========== Seed Data Summary =========='))
        self.stdout.write('Teams Created:')
        self.stdout.write(f'  - Engineering (ID: {engineering.id})')
        self.stdout.write(f'  - Marketing (ID: {marketing.id})')
        self.stdout.write(f'  - Sales (ID: {sales.id})')
        self.stdout.write('\nUsers Created:')
        self.stdout.write('  Admin:')
        self.stdout.write('    - admin@example.com / password123')
        self.stdout.write('  Engineering Team:')
        self.stdout.write('    - john@example.com / password123')
        self.stdout.write('    - sarah@example.com / password123')
        self.stdout.write('  Marketing Team:')
        self.stdout.write('    - mike@example.com / password123')
        self.stdout.write('    - lisa@example.com / password123')
        self.stdout.write('  Sales Team:')
        self.stdout.write('    - tom@example.com / password123')
        self.stdout.write('\nAlerts Created: 4')
        self.stdout.write('  - 1 Organization-wide')
        self.stdout.write('  - 2 Team-specific')
        self.stdout.write('  - 1 User-specific')
        self.stdout.write('=======================================\n')

        self.stdout.write(self.style.SUCCESS('✓ Database seeded successfully!'))