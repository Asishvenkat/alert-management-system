🚀 Alerting & Notification Platform

A lightweight, extensible alerting and notification system built with Django REST Framework, featuring admin configurability, user control, and clean OOP design patterns.

📋 Table of Contents

Overview

Features

Tech Stack

Architecture

Installation

API Endpoints

Project Structure

Testing

Future Scope

Troubleshooting

Security Notes

🎯 Overview

A scalable platform for managing organizational alerts and notifications.

Admins: Create, configure, and monitor alerts with visibility control.

Users: Receive, snooze, and track alerts.

System: Sends automatic 2-hour reminders until snoozed or expired.

Analytics: Provides insights into alert delivery and engagement.

✨ Features
Admin

Create alerts (Info/Warning/Critical)

Define visibility: Organization / Team / User

Configure start, expiry, reminder frequency

Archive, update, and filter alerts

View analytics (delivery & engagement)

User

Receive alerts relevant to them

Mark as read/unread

Snooze alerts (resets daily)

View snooze history

System

Automated 2-hour reminders via Celery

Daily snooze reset

Cloud task queue (Upstash Redis)

In-app notifications (MVP)

🛠️ Tech Stack
Component	Technology
Backend	Django 4.2, DRF 3.14
DB	MySQL 8.0
Queue	Celery 5.3 + Redis (Upstash)
Auth	JWT (SimpleJWT)
Language	Python 3.8+
🧱 Architecture & Design Patterns

1. Strategy Pattern (Notification Channels)
Encapsulates notification delivery (InApp, Email, SMS).

2. Factory Pattern (Channel Selection)
Centralized strategy creation for extensibility.

3. Service Layer Pattern (Business Logic)
Separates business logic from views for cleaner, testable code.

OOP Principles: Encapsulation, Abstraction, Inheritance, Polymorphism, SRP, Open/Closed Principle.

⚙️ Installation
Prerequisites

Python 3.8+

MySQL 8.0

Upstash Redis (Free tier)

Steps
# Clone and setup
git clone <repo-url>
cd backend
python -m venv venv
venv\Scripts\activate  # Windows

pip install -r requirements.txt


Create .env:

SECRET_KEY=your-secret
DEBUG=True

DB_NAME=alerting_platform
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost

REDIS_URL=rediss://default:your-password@your-redis-url.upstash.io:6379


Setup DB:

mysql -u root -p
CREATE DATABASE alerting_platform;
python manage.py migrate
python manage.py seed_data


Run:

# Terminal 1
python manage.py runserver

# Terminal 2
celery -A alerting_platform worker --pool=solo -l info

# Terminal 3
celery -A alerting_platform beat -l info

📚 API Endpoints

Base URL: http://localhost:8000/api

Auth

POST /auth/login/ → Login (JWT)

GET /auth/me/ → Current user

Admin

POST /admin/alerts/ → Create alert

GET /admin/alerts/ → List alerts (filter by severity/status)

PUT /admin/alerts/{id}/ → Update

DELETE /admin/alerts/{id}/archive/ → Archive

POST /admin/alerts/{id}/trigger/ → Trigger manually

User

GET /user/alerts/ → View alerts

PUT /user/alerts/{id}/mark_read/ → Mark read

POST /user/alerts/{id}/snooze/ → Snooze

GET /user/alerts/snoozed/ → Snoozed alerts

Analytics

GET /analytics/ → System metrics

GET /analytics/alerts/{id}/ → Alert metrics

📁 Project Structure
backend/
├── alerting_platform/
│   ├── settings.py / celery.py / urls.py
│
├── alerts/
│   ├── models.py / views.py / services.py / tasks.py
│   └── management/commands/seed_data.py
│
├── requirements.txt
├── manage.py
└── .env

🧪 Testing
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}'

# 2. Create alert
curl -X POST http://localhost:8000/api/admin/alerts/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Alert","message":"Testing","severity":"Info"}'

🔄 How It Works

Celery Beat: schedules process_reminders() every 2 hours, reset_expired_snoozes() daily.

Celery Worker: sends alerts, logs deliveries, skips snoozed users.

Visibility: organization / team / user targeting.

🚀 Future Scope

Email & SMS channels (Twilio/AWS SNS)

Custom reminder frequency

Scheduled & recurring alerts

Escalation rules (auto-upgrade severity)

Push notifications

Alert templates

🐛 Troubleshooting
Issue	Fix
Redis not connecting	Verify REDIS_URL starts with rediss://
MySQL errors	Ensure MySQL is running, recreate DB
Celery not running	Check all 3 processes (Django, worker, beat)
🔐 Security Notes

Change SECRET_KEY & disable DEBUG in production

Store credentials in .env

Enforce HTTPS & JWT rotation

Implement rate limiting

Use strong database credentials

📝 License

Educational demo showcasing:
Strategy • Factory • Service Layer • Celery • REST API • Clean Architecture

Built with ❤️ using Django, Celery, and OOP Design Principles.