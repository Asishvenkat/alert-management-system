from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Team, Alert, NotificationDelivery, UserAlertPreference


class UserSerializer(serializers.ModelSerializer):
    """User Serializer"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'role', 'team', 'team_name', 'organization', 'is_active']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    """User Registration Serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 
                  'role', 'team', 'organization']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Login Serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            # Django's authenticate uses username by default
            # We need to get user by email first
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
            except User.DoesNotExist:
                user = None
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            data['user'] = user
            return data
        else:
            raise serializers.ValidationError('Must include email and password')


class TeamSerializer(serializers.ModelSerializer):
    """Team Serializer"""
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'organization', 
                  'is_active', 'member_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()


class AlertSerializer(serializers.ModelSerializer):
    """Alert Serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    target_teams_names = serializers.SerializerMethodField()
    target_users_names = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_target_teams_names(self, obj):
        return [team.name for team in obj.target_teams.all()]
    
    def get_target_users_names(self, obj):
        return [user.get_full_name() or user.username for user in obj.target_users.all()]
    
    def validate(self, data):
        """Validate alert data"""
        # Ensure expiry time is in the future
        from django.utils import timezone
        if data.get('expiry_time') and data['expiry_time'] <= timezone.now():
            raise serializers.ValidationError("Expiry time must be in the future")
        
        # Validate visibility type
        visibility_type = data.get('visibility_type')
        if visibility_type == 'Organization' and not data.get('target_organization'):
            raise serializers.ValidationError("Target organization is required for Organization visibility")
        
        return data


class AlertListSerializer(serializers.ModelSerializer):
    """Simplified Alert Serializer for Lists"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Alert
        fields = ['id', 'title', 'message', 'severity', 'visibility_type', 
                  'is_active', 'is_archived', 'expiry_time', 'created_by_name', 
                  'created_at', 'is_expired']


class UserAlertSerializer(serializers.ModelSerializer):
    """Alert Serializer for User View (includes user preferences)"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_read = serializers.SerializerMethodField()
    is_snoozed = serializers.SerializerMethodField()
    snooze_until = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = ['id', 'title', 'message', 'severity', 'delivery_type',
                  'expiry_time', 'created_by_name', 'created_at',
                  'is_read', 'is_snoozed', 'snooze_until']
    
    def get_is_read(self, obj):
        user = self.context.get('user')
        if user:
            pref = UserAlertPreference.objects.filter(user=user, alert=obj).first()
            return pref.is_read if pref else False
        return False
    
    def get_is_snoozed(self, obj):
        user = self.context.get('user')
        if user:
            pref = UserAlertPreference.objects.filter(user=user, alert=obj).first()
            return pref.is_snoozed_now() if pref else False
        return False
    
    def get_snooze_until(self, obj):
        user = self.context.get('user')
        if user:
            pref = UserAlertPreference.objects.filter(user=user, alert=obj).first()
            return pref.snooze_until if pref and pref.is_snoozed_now() else None
        return None


class NotificationDeliverySerializer(serializers.ModelSerializer):
    """Notification Delivery Serializer"""
    alert_title = serializers.CharField(source='alert.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = NotificationDelivery
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserAlertPreferenceSerializer(serializers.ModelSerializer):
    """User Alert Preference Serializer"""
    alert_title = serializers.CharField(source='alert.title', read_only=True)
    
    class Meta:
        model = UserAlertPreference
        fields = '__all__'
        read_only_fields = ['id', 'user', 'alert', 'created_at', 'updated_at']