from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, RegisterView, LoginView, CurrentUserView, system_analytics, alert_analytics

router = DefaultRouter()
router.register('alerts', AlertViewSet)

urlpatterns = [
    # Auth endpoints (accept both with and without trailing slash)
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/register', RegisterView.as_view()),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/login', LoginView.as_view()),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('auth/me', CurrentUserView.as_view()),

    # Analytics
    path('analytics/', system_analytics, name='system-analytics'),
    path('analytics', system_analytics),
    path('analytics/alerts/<int:alert_id>/', alert_analytics, name='alert-analytics'),
    path('analytics/alerts/<int:alert_id>', alert_analytics),

    # Router URLs
    path('', include(router.urls)),
]
