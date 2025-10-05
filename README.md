# Alerting Platform

Minimal scaffold for the alerting-platform project.

- Django project: `alerting_platform`
- App: `alerts`

To run:

1. python -m venv .venv
2. .\.venv\Scripts\Activate.ps1
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py runserver

Using Upstash Redis for Celery (managed Redis)
---------------------------------------------
If you use Upstash (a managed Redis provider), set the environment variable `UPSTASH_REDIS_URL`
to the provided `rediss://...` URL. Example in `.env`:

UPSTASH_REDIS_URL=rediss://:<token>@us1-upstash-redis.upstash.io:port

Then run Celery as usual (no local Redis required):

celery -A alerting_platform worker --pool=solo -l info

If your Upstash URL uses rediss:// (TLS), the Django settings will configure Celery to use
SSL with permissive cert verification. For production, consider using proper CA verification.
