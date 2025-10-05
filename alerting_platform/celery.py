import os
import ssl
from celery import Celery
from decouple import config
from django.conf import settings

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alerting_platform.settings')

# Create Celery app
app = Celery('alerting_platform')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Prefer Django settings if they have CELERY_BROKER_URL/CELERY_RESULT_BACKEND
broker = getattr(settings, 'CELERY_BROKER_URL', None) or config('REDIS_URL', default=None)
result_backend = getattr(settings, 'CELERY_RESULT_BACKEND', None) or broker

if broker and broker.startswith('rediss://'):
    # Upstash Redis with SSL — use ssl constants. For production set CERT_REQUIRED.
    app.conf.update(
        broker_url=broker,
        result_backend=result_backend,
        broker_use_ssl={
            'ssl_cert_reqs': ssl.CERT_NONE
        },
        redis_backend_use_ssl={
            'ssl_cert_reqs': ssl.CERT_NONE
        },
        broker_connection_retry_on_startup=True,
    )
elif broker:
    app.conf.update(
        broker_url=broker,
        result_backend=result_backend,
    )
else:
    # No broker configured — rely on whatever settings object has (this will surface an error)
    pass

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')