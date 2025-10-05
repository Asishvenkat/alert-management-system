from abc import ABC, abstractmethod
from django.utils import timezone
from .models import Alert, User, NotificationDelivery, UserAlertPreference


# ==================== Strategy Pattern for Notification Channels ====================

class NotificationStrategy(ABC):
    """Base Notification Strategy"""
    
    @abstractmethod
    def send(self, user, alert):
        """Send notification to user"""
        pass


class InAppNotificationStrategy(NotificationStrategy):
    """In-App Notification Strategy"""
    
    def send(self, user, alert):
        """Send in-app notification"""
        print(f"[InApp] Sending alert '{alert.title}' to user {user.email}")
        
        return {
            'success': True,
            'channel': 'InApp',
            'user_id': user.id,
            'alert_id': alert.id,
            'sent_at': timezone.now()
        }


class EmailNotificationStrategy(NotificationStrategy):
    """Email Notification Strategy"""
    
    def send(self, user, alert):
        """Send email notification"""
        print(f"[Email] Would send alert '{alert.title}' to {user.email}")
        
        # TODO: Integrate with Django email backend or SendGrid
        # from django.core.mail import send_mail
        # send_mail(
        #     subject=alert.title,
        #     message=alert.message,
        #     from_email='noreply@alertplatform.com',
        #     recipient_list=[user.email],
        # )
        
        return {
            'success': True,
            'channel': 'Email',
            'user_id': user.id,
            'alert_id': alert.id,
            'sent_at': timezone.now()
        }


class SMSNotificationStrategy(NotificationStrategy):
    """SMS Notification Strategy"""
    
    def send(self, user, alert):
        """Send SMS notification"""
        print(f"[SMS] Would send alert '{alert.title}' to user {user.email}")
        
        # TODO: Integrate with Twilio or AWS SNS
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # client.messages.create(
        #     body=f"{alert.title}: {alert.message}",
        #     from_='+1234567890',
        #     to=user.phone_number
        # )
        
        return {
            'success': True,
            'channel': 'SMS',
            'user_id': user.id,
            'alert_id': alert.id,
            'sent_at': timezone.now()
        }


# ==================== Factory Pattern ====================

class NotificationStrategyFactory:
    """Factory to create notification strategies"""
    
    @staticmethod
    def get_strategy(delivery_type):
        """Get appropriate strategy based on delivery type"""
        strategies = {
            'InApp': InAppNotificationStrategy,
            'Email': EmailNotificationStrategy,
            'SMS': SMSNotificationStrategy,
        }
        
        strategy_class = strategies.get(delivery_type, InAppNotificationStrategy)
        return strategy_class()


# ==================== Notification Service ====================

class NotificationService:
    """Service to handle notification logic"""
    
    def get_target_users(self, alert):
        """Get all users who should receive this alert"""
        users = []
        
        if alert.visibility_type == 'Organization':
            users = User.objects.filter(
                organization=alert.target_organization,
                is_active=True
            )
        
        elif alert.visibility_type == 'Team':
            users = User.objects.filter(
                team__in=alert.target_teams.all(),
                is_active=True
            ).distinct()
        
        elif alert.visibility_type == 'User':
            users = alert.target_users.filter(is_active=True)
        
        return users
    
    def send_to_user(self, alert, user, is_reminder=False):
        """Send alert to specific user"""
        try:
            # Get or create user preference
            preference, created = UserAlertPreference.objects.get_or_create(
                user=user,
                alert=alert
            )
            
            # Check if user has snoozed this alert
            if is_reminder and preference.is_snoozed_now():
                print(f"User {user.email} has snoozed alert {alert.title}")
                return {'success': False, 'reason': 'snoozed'}
            
            # Check if enough time has passed for reminder
            if is_reminder and not preference.should_receive_reminder(alert.reminder_frequency_hours):
                print(f"Not enough time passed for reminder to {user.email}")
                return {'success': False, 'reason': 'too_soon'}
            
            # Get the appropriate notification strategy
            strategy = NotificationStrategyFactory.get_strategy(alert.delivery_type)
            
            # Send the notification
            result = strategy.send(user, alert)
            
            if result['success']:
                # Log the delivery
                NotificationDelivery.objects.create(
                    alert=alert,
                    user=user,
                    delivery_type=alert.delivery_type,
                    status='sent',
                    sent_at=timezone.now(),
                    is_reminder=is_reminder,
                    reminder_count=1 if is_reminder else 0
                )
                
                # Update preference
                preference.last_reminder_sent_at = timezone.now()
                preference.save()
            
            return result
        
        except Exception as e:
            print(f"Error sending notification to {user.email}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_alert(self, alert_id, is_reminder=False):
        """Send alert to all target users"""
        try:
            alert = Alert.objects.select_related('created_by').prefetch_related(
                'target_teams', 'target_users'
            ).get(id=alert_id)
            
            if not alert.is_active or alert.is_archived:
                return {'success': False, 'reason': 'Alert not active'}
            
            # Check if alert should send reminders
            if not alert.should_send_reminder():
                return {'success': False, 'reason': 'Alert expired or reminders disabled'}
            
            users = self.get_target_users(alert)
            
            results = {
                'total': users.count(),
                'sent': 0,
                'failed': 0,
                'snoozed': 0,
                'details': []
            }
            
            for user in users:
                result = self.send_to_user(alert, user, is_reminder)
                
                if result['success']:
                    results['sent'] += 1
                elif result.get('reason') == 'snoozed':
                    results['snoozed'] += 1
                else:
                    results['failed'] += 1
                
                results['details'].append({
                    'user_id': user.id,
                    'email': user.email,
                    **result
                })
            
            return results
        
        except Alert.DoesNotExist:
            return {'success': False, 'reason': 'Alert not found'}
        except Exception as e:
            print(f"Error in send_alert: {str(e)}")
            raise
    
    def process_reminders(self):
        """Process all active alerts for reminders"""
        now = timezone.now()
        
        # Find all alerts that should send reminders
        alerts = Alert.objects.filter(
            is_active=True,
            is_archived=False,
            reminder_enabled=True,
            start_time__lte=now,
            expiry_time__gt=now
        )
        
        print(f"Processing reminders for {alerts.count()} active alerts")
        
        results = []
        for alert in alerts:
            result = self.send_alert(alert.id, is_reminder=True)
            results.append({
                'alert_id': alert.id,
                'alert_title': alert.title,
                **result
            })
        
        return results