from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, Team, Alert, NotificationDelivery, UserAlertPreference
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer,
    TeamSerializer, AlertSerializer, AlertListSerializer,
    UserAlertSerializer, NotificationDeliverySerializer,
    UserAlertPreferenceSerializer
)
from .services import NotificationService
from .permissions import IsAdminUser


# ==================== Authentication Views ====================

class RegisterView(generics.CreateAPIView):
    """User Registration"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': UserSerializer(user).data,
                'token': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """User Login"""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': UserSerializer(user).data,
                'token': str(refresh.access_token),
                'refresh': str(refresh)
            }
        })


class CurrentUserView(generics.RetrieveAPIView):
    """Get Current User"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


# ==================== Admin Alert Views ====================

class AdminAlertViewSet(viewsets.ModelViewSet):
    """Admin Alert Management ViewSet"""
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['severity', 'visibility_type', 'is_active', 'is_archived']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AlertListSerializer
        return AlertSerializer
    
    def get_queryset(self):
        queryset = Alert.objects.filter(is_archived=False)
        
        # Filter by status (active/expired)
        status_param = self.request.query_params.get('status')
        if status_param == 'active':
            queryset = queryset.filter(
                is_active=True,
                expiry_time__gt=timezone.now()
            )
        elif status_param == 'expired':
            queryset = queryset.filter(expiry_time__lte=timezone.now())
        
        return queryset.select_related('created_by').prefetch_related('target_teams', 'target_users')
    
    def perform_create(self, serializer):
        alert = serializer.save(created_by=self.request.user)
        
        # Send alert immediately
        notification_service = NotificationService()
        notification_service.send_alert(alert.id, is_reminder=False)
    
    def perform_update(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['delete'])
    def archive(self, request, pk=None):
        """Archive an alert"""
        alert = self.get_object()
        alert.is_archived = True
        alert.is_active = False
        alert.save()
        
        return Response({
            'success': True,
            'message': 'Alert archived successfully'
        })
    
    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        """Manually trigger an alert"""
        alert = self.get_object()
        
        notification_service = NotificationService()
        result = notification_service.send_alert(alert.id, is_reminder=False)
        
        return Response({
            'success': True,
            'message': 'Alert triggered successfully',
            'data': result
        })


# ==================== User Alert Views ====================

class UserAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """User Alert ViewSet"""
    serializer_class = UserAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        now = timezone.now()
        
        # Build query for alerts visible to this user
        query = Q(
            is_active=True,
            is_archived=False,
            start_time__lte=now,
            expiry_time__gt=now
        )
        
        # Organization-wide alerts
        org_query = Q(
            visibility_type='Organization',
            target_organization=user.organization
        )
        
        # Team-specific alerts
        team_query = Q(
            visibility_type='Team',
            target_teams=user.team
        ) if user.team else Q(pk=None)
        
        # User-specific alerts
        user_query = Q(
            visibility_type='User',
            target_users=user
        )
        
        queryset = Alert.objects.filter(
            query & (org_query | team_query | user_query)
        ).distinct().select_related('created_by').order_by('-severity', '-created_at')
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
    
    @action(detail=True, methods=['put'])
    def mark_read(self, request, pk=None):
        """Mark alert as read"""
        alert = self.get_object()
        user = request.user
        
        # Get or create preference
        preference, created = UserAlertPreference.objects.get_or_create(
            user=user,
            alert=alert
        )
        
        preference.mark_as_read()
        
        # Update delivery status
        NotificationDelivery.objects.filter(
            user=user,
            alert=alert,
            status='sent'
        ).update(status='read', read_at=timezone.now())
        
        return Response({
            'success': True,
            'message': 'Alert marked as read'
        })
    
    @action(detail=True, methods=['put'])
    def mark_unread(self, request, pk=None):
        """Mark alert as unread"""
        alert = self.get_object()
        user = request.user
        
        try:
            preference = UserAlertPreference.objects.get(user=user, alert=alert)
            preference.is_read = False
            preference.read_at = None
            preference.save()
            
            return Response({
                'success': True,
                'message': 'Alert marked as unread'
            })
        except UserAlertPreference.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Alert preference not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def snooze(self, request, pk=None):
        """Snooze alert for the day"""
        alert = self.get_object()
        user = request.user
        
        # Get or create preference
        preference, created = UserAlertPreference.objects.get_or_create(
            user=user,
            alert=alert
        )
        
        preference.snooze_for_day()
        
        return Response({
            'success': True,
            'message': 'Alert snoozed until end of day',
            'data': UserAlertPreferenceSerializer(preference).data
        })
    
    @action(detail=False, methods=['get'])
    def snoozed(self, request):
        """Get snoozed alerts"""
        user = request.user
        now = timezone.now()
        
        snoozed_prefs = UserAlertPreference.objects.filter(
            user=user,
            is_snoozed=True,
            snooze_until__gt=now
        ).select_related('alert', 'alert__created_by')
        
        data = []
        for pref in snoozed_prefs:
            alert_data = UserAlertSerializer(pref.alert, context={'user': user}).data
            alert_data['snoozed_at'] = pref.snoozed_at
            data.append(alert_data)
        
        return Response({
            'success': True,
            'data': data
        })


# ==================== Analytics Views ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def system_analytics(request):
    """Get system-wide analytics"""
    from django.db.models import Count
    
    # Overview metrics
    total_alerts = Alert.objects.filter(is_archived=False).count()
    active_alerts = Alert.objects.filter(
        is_active=True,
        is_archived=False,
        expiry_time__gt=timezone.now()
    ).count()
    expired_alerts = Alert.objects.filter(
        is_archived=False,
        expiry_time__lte=timezone.now()
    ).count()
    
    total_delivered = NotificationDelivery.objects.count()
    total_read = NotificationDelivery.objects.filter(status='read').count()
    total_snoozed = UserAlertPreference.objects.filter(
        is_snoozed=True,
        snooze_until__gt=timezone.now()
    ).count()
    
    read_rate = (total_read / total_delivered * 100) if total_delivered > 0 else 0
    
    # Severity breakdown
    severity_breakdown = Alert.objects.filter(
        is_archived=False
    ).values('severity').annotate(count=Count('id'))
    
    # Delivery type breakdown
    delivery_breakdown = Alert.objects.filter(
        is_archived=False
    ).values('delivery_type').annotate(count=Count('id'))
    
    # Visibility breakdown
    visibility_breakdown = Alert.objects.filter(
        is_archived=False
    ).values('visibility_type').annotate(count=Count('id'))
    
    # Recent activity (last 7 days)
    from datetime import timedelta
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    recent_alerts = Alert.objects.filter(
        created_at__gte=seven_days_ago,
        is_archived=False
    ).extra(select={'date': 'DATE(created_at)'}).values('date').annotate(count=Count('id')).order_by('date')
    
    return Response({
        'success': True,
        'data': {
            'overview': {
                'totalAlerts': total_alerts,
                'activeAlerts': active_alerts,
                'expiredAlerts': expired_alerts,
                'totalDelivered': total_delivered,
                'totalRead': total_read,
                'totalSnoozed': total_snoozed,
                'readRate': round(read_rate, 2)
            },
            'breakdowns': {
                'severity': list(severity_breakdown),
                'deliveryType': list(delivery_breakdown),
                'visibility': list(visibility_breakdown)
            },
            'recentActivity': list(recent_alerts)
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def alert_analytics(request, alert_id):
    """Get analytics for specific alert"""
    try:
        alert = Alert.objects.get(id=alert_id)
    except Alert.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Alert not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Delivery metrics
    total_deliveries = NotificationDelivery.objects.filter(alert=alert).count()
    read_count = NotificationDelivery.objects.filter(alert=alert, status='read').count()
    snoozed_count = UserAlertPreference.objects.filter(
        alert=alert,
        is_snoozed=True,
        snooze_until__gt=timezone.now()
    ).count()
    reminder_count = NotificationDelivery.objects.filter(alert=alert, is_reminder=True).count()
    
    read_rate = (read_count / total_deliveries * 100) if total_deliveries > 0 else 0
    
    # Status breakdown
    status_breakdown = NotificationDelivery.objects.filter(
        alert=alert
    ).values('status').annotate(count=Count('id'))
    
    return Response({
        'success': True,
        'data': {
            'alert': {
                'id': alert.id,
                'title': alert.title,
                'severity': alert.severity,
                'createdAt': alert.created_at
            },
            'metrics': {
                'totalDeliveries': total_deliveries,
                'readCount': read_count,
                'snoozedCount': snoozed_count,
                'reminderCount': reminder_count,
                'readRate': round(read_rate, 2)
            },
            'statusBreakdown': list(status_breakdown)
        }
    })


# ==================== Team Views ====================

class TeamViewSet(viewsets.ModelViewSet):
    """Team Management ViewSet"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Team.objects.filter(organization=user.organization)
    