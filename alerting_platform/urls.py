from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from alerts import views

# Router for ViewSets
router = DefaultRouter()
router.register(r'admin/alerts', views.AdminAlertViewSet, basename='admin-alerts')
router.register(r'user/alerts', views.UserAlertViewSet, basename='user-alerts')
router.register(r'teams', views.TeamViewSet, basename='teams')

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/auth/register/', views.RegisterView.as_view(), name='register'),
    path('api/auth/register', views.RegisterView.as_view(), name='register-no-slash'),
    path('api/auth/login/', views.LoginView.as_view(), name='login'),
    path('api/auth/login', views.LoginView.as_view(), name='login-no-slash'),
    path('api/auth/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('api/auth/me', views.CurrentUserView.as_view(), name='current-user-no-slash'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/auth/refresh', TokenRefreshView.as_view(), name='token-refresh-no-slash'),
    
    # Analytics
    path('api/analytics/', views.system_analytics, name='system-analytics'),
    path('api/analytics', views.system_analytics, name='system-analytics-no-slash'),
    path('api/analytics/alerts/<int:alert_id>/', views.alert_analytics, name='alert-analytics'),
    path('api/analytics/alerts/<int:alert_id>', views.alert_analytics, name='alert-analytics-no-slash'),
    
    # Router URLs (includes all viewsets)
    path('api/', include(router.urls)),
]