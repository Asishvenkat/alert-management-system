from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Team, Alert, NotificationDelivery, UserAlertPreference


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'team', 'organization', 'is_active']
    list_filter = ['role', 'is_active', 'organization']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'team', 'organization')}),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'is_active', 'created_at']
    list_filter = ['organization', 'is_active']
    search_fields = ['name', 'description']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'visibility_type', 'is_active', 'expiry_time', 'created_by']
    list_filter = ['severity', 'visibility_type', 'is_active', 'is_archived']
    search_fields = ['title', 'message']
    date_hierarchy = 'created_at'
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = ['alert', 'user', 'delivery_type', 'status', 'is_reminder', 'sent_at']
    list_filter = ['status', 'delivery_type', 'is_reminder']
    search_fields = ['alert__title', 'user__username']
    date_hierarchy = 'created_at'
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserAlertPreference)
class UserAlertPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'alert', 'is_read', 'is_snoozed', 'snooze_until']
    list_filter = ['is_read', 'is_snoozed']
    search_fields = ['user__username', 'alert__title']
    
    readonly_fields = ['created_at', 'updated_at']