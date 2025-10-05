from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom User Model"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    organization = models.CharField(max_length=100, default='default-org')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['organization']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class Team(models.Model):
    """Team/Department Model"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    organization = models.CharField(max_length=100, default='default-org')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teams'
        unique_together = ['name', 'organization']
        indexes = [
            models.Index(fields=['organization']),
        ]
    
    def __str__(self):
        return self.name


class Alert(models.Model):
    """Alert Model"""
    SEVERITY_CHOICES = [
        ('Info', 'Info'),
        ('Warning', 'Warning'),
        ('Critical', 'Critical'),
    ]
    
    DELIVERY_CHOICES = [
        ('InApp', 'In-App'),
        ('Email', 'Email'),
        ('SMS', 'SMS'),
    ]
    
    VISIBILITY_CHOICES = [
        ('Organization', 'Organization'),
        ('Team', 'Team'),
        ('User', 'User'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='Info')
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='InApp')
    visibility_type = models.CharField(max_length=20, choices=VISIBILITY_CHOICES)
    
    # Target audience
    target_organization = models.CharField(max_length=100, blank=True)
    target_teams = models.ManyToManyField(Team, blank=True, related_name='alerts')
    target_users = models.ManyToManyField(User, blank=True, related_name='targeted_alerts')
    
    # Reminder settings
    reminder_enabled = models.BooleanField(default=True)
    reminder_frequency_hours = models.IntegerField(default=2)
    
    # Timing
    start_time = models.DateTimeField(default=timezone.now)
    expiry_time = models.DateTimeField()
    
    # Status
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_alerts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alerts'
        indexes = [
            models.Index(fields=['is_active', 'expiry_time']),
            models.Index(fields=['visibility_type']),
            models.Index(fields=['severity']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.severity})"
    
    @property
    def is_expired(self):
        """Check if alert is expired"""
        return self.expiry_time < timezone.now()
    
    def should_send_reminder(self):
        """Check if alert should send reminders"""
        now = timezone.now()
        return (
            self.is_active and
            not self.is_archived and
            self.reminder_enabled and
            self.start_time <= now and
            self.expiry_time > now
        )


class NotificationDelivery(models.Model):
    """Notification Delivery Log"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ]
    
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='deliveries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    delivery_type = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    
    is_reminder = models.BooleanField(default=False)
    reminder_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_deliveries'
        indexes = [
            models.Index(fields=['alert', 'user']),
            models.Index(fields=['user', 'status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Delivery: {self.alert.title} to {self.user.username}"


class UserAlertPreference(models.Model):
    """User Alert Preferences (Read/Snooze State)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_preferences')
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='user_preferences')
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    is_snoozed = models.BooleanField(default=False)
    snoozed_at = models.DateTimeField(null=True, blank=True)
    snooze_until = models.DateTimeField(null=True, blank=True)
    
    last_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_alert_preferences'
        unique_together = ['user', 'alert']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['is_snoozed', 'snooze_until']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.alert.title}"
    
    def is_snoozed_now(self):
        """Check if snooze is still active"""
        if not self.is_snoozed or not self.snooze_until:
            return False
        return self.snooze_until > timezone.now()
    
    def snooze_for_day(self):
        """Snooze alert until end of day"""
        end_of_day = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        self.is_snoozed = True
        self.snoozed_at = timezone.now()
        self.snooze_until = end_of_day
        self.save()
    
    def mark_as_read(self):
        """Mark alert as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def should_receive_reminder(self, reminder_frequency_hours=2):
        """Check if user should receive reminder"""
        if self.is_snoozed_now():
            return False
        
        if not self.last_reminder_sent_at:
            return True
        
        time_since_last = timezone.now() - self.last_reminder_sent_at
        return time_since_last.total_seconds() / 3600 >= reminder_frequency_hours