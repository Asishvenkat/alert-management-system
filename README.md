# 🚀 Alerting & Notification Platform

A lightweight, extensible alerting and notification system built with **Django REST Framework**, featuring admin configurability, user control, and clean **OOP design patterns**.

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture--design-patterns)
- [Installation](#️-installation)
- [Deployment](#-deployment)   
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [How It Works](#-how-it-works)
- [Future Scope](#-future-scope)
- [Troubleshooting](#-troubleshooting)
- [Security Notes](#-security-notes)
- [License](#-license)

---

## 🎯 Overview
A scalable platform for managing organizational alerts and notifications.
- **Admins:** Create, configure, and monitor alerts with visibility control.  
- **Users:** Receive, snooze, and track alerts.  
- **System:** Sends automatic 2-hour reminders until snoozed or expired.  
- **Analytics:** Provides insights into alert delivery and engagement.


### 🌐 Live Demo
- **Frontend:** [https://alert-management-ui.vercel.app/login](https://alert-management-ui.vercel.app/login)  
- **Backend API:** [https://alert-management-system-1.onrender.com](https://alert-management-system-1.onrender.com)  

### 🔑 Test Credentials
**Admin Account:**
- Email: `admin@example.com`
- Password: `password123`

**Regular User Account:**
- Email: `user@example.com`
- Password: `password123`

## 🧪 Notes & Feature Info

**Test the backend:** Easily try all APIs using **Postman** or **cURL**.  
Example base URL: `https://alert-management-system-1.onrender.com/api`

**Frontend Login:** May take a few seconds initially due to server startup and API response time.

**Feature Availability:**  
- **Frontend:** Most main features are ready; some actions are only available via the backend API.  
- **Backend:** All features are fully implemented and testable via API.

---

## ✨ Features

### 👨‍💼 Admin
- Create alerts (**Info / Warning / Critical**)
- Define visibility: **Organization / Team / User**
- Configure start, expiry, and reminder frequency
- Archive, update, and filter alerts
- View analytics (delivery & engagement)

### 👤 User
- Receive alerts relevant to them
- Mark alerts as **read/unread**
- **Snooze alerts** (resets daily)
- View snooze history

### ⚙️ System
- Automated 2-hour reminders via **Celery**
- Daily snooze reset
- Cloud task queue (**Upstash Redis**)
- In-app notifications (MVP)

 ## 🖼️ Screenshots

<table>
  <tr>
    <td align="center">
      <a href="https://drive.google.com/file/d/1L_RFW0QcDriAHaCaU25Arq763GEgggPm/view?usp=sharing" target="_blank">
        <img src="https://drive.google.com/uc?export=view&id=1L_RFW0QcDriAHaCaU25Arq763GEgggPm" width="450"/>
      </a>
      <br/>Admin: Create Alert
    </td>
    <td align="center">
      <a href="https://drive.google.com/file/d/1GHykLPmqVpE9M3OZwnXQbx_nrltyxuNL/view?usp=sharing" target="_blank">
        <img src="https://drive.google.com/uc?export=view&id=1GHykLPmqVpE9M3OZwnXQbx_nrltyxuNL" width="450"/>
      </a>
      <br/>User: View Alerts
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="https://drive.google.com/file/d/1i622EkZSGNqY-KKP1UDCKWW4TSPSwIlG/view?usp=sharing" target="_blank">
        <img src="https://drive.google.com/uc?export=view&id=1i622EkZSGNqY-KKP1UDCKWW4TSPSwIlG" width="450"/>
      </a>
      <br/>Analytics Dashboard
    </td>
    <td align="center">
      <a href="https://drive.google.com/file/d/1UWwPe_Eay2RobtTwOzO1tAecctcNtqFL/view?usp=sharing" target="_blank">
        <img src="https://drive.google.com/uc?export=view&id=1UWwPe_Eay2RobtTwOzO1tAecctcNtqFL" width="450"/>
      </a>
      <br/>Admin: View Alerts
    </td>
  </tr>
</table>


---

## 🛠️ Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend** | Django 4.2, DRF 3.14 |
| **Database** | MySQL 8.0 |
| **Queue** | Celery 5.3 + Redis (Upstash) |
| **Authentication** | JWT (SimpleJWT) |
| **Language** | Python 3.8+ |

---

## 🧱 Architecture & Design Patterns

1. **Strategy Pattern** – Encapsulates notification delivery (InApp, Email, SMS).  
2. **Factory Pattern** – Centralized strategy creation for extensibility.  
3. **Service Layer Pattern** – Separates business logic from views for clean, testable code.

**OOP Principles:** Encapsulation, Abstraction, Inheritance, Polymorphism, SRP, Open/Closed Principle.

---


## ⚙️ Installation

### Prerequisites
- Python 3.8+
 - MySQL 8.0
 - Upstash Redis (Free tier)

### Steps

# Clone and setup
  ```git clone <repo-url>
 
  cd backend
  
  python -m venv venv
  
  venv\Scripts\activate  # Windows
  
  pip install -r requirements.txt
```

# Setup .env file
  ```SECRET_KEY=your-secret
 
   DEBUG=True
  
   DB_NAME=alerting_platform
  
   DB_USER=root
 
   DB_PASSWORD=your_password
  
   DB_HOST=localhost
 
   REDIS_URL=rediss://default:your-password@your-redis-url.upstash.io:6379
  ```

## ⚙️ Setup Database

### 1. Login to MySQL
   
     mysql -u root -p

### 2. Create database
   
     CREATE DATABASE alerting_platform;

 ### 3. Apply migrations

     python manage.py migrate

### 4. Seed initial data

     python manage.py seed_data


## 🚀 Run Application

 ### Terminal 1: Run Django server
    
    python manage.py runserver

 ### Terminal 2: Start Celery worker
     celery -A alerting_platform worker --pool=solo -l info

 ### Terminal 3: Start Celery beat scheduler
    celery -A alerting_platform beat -l info

---

## 🚀 Deployment

This project is fully deployed and accessible online. Below are the details:

### Backend
- **Platform:** Render
- **URL:** [https://alert-management-system-1.onrender.com](https://alert-management-system-1.onrender.com)
- **Database:** Aiven MySQL (online hosted database)
- **Authentication:** JWT-based authentication
- **Background tasks:** Redis + Celery for reminders and notifications

### Frontend
- **Platform:** Vercel
- **URL:** [https://your-frontend.vercel.app](https://your-frontend.vercel.app)
- **Connected to backend:** via Render API

### Notes
- The backend and frontend communicate via REST API
- JWT tokens are required for accessing protected endpoints
- Sample credentials (for testing):
  - Email: `test@example.com`
  - Password: `Password123`


## 📚 API Endpoints

**Base URL:** `http://localhost:8000/api`

### 🔐 Auth
| Method | Endpoint       | Description         |
|--------|----------------|-------------------|
| POST   | /auth/login/   | Login (JWT)       |
| GET    | /auth/me/      | Current user info |

### 🧑‍💼 Admin
| Method | Endpoint                      | Description                    |
|--------|-------------------------------|--------------------------------|
| POST   | /admin/alerts/                | Create alert                  |
| GET    | /admin/alerts/                | List alerts (filter by severity/status) |
| PUT    | /admin/alerts/{id}/           | Update alert                  |
| DELETE | /admin/alerts/{id}/archive/   | Archive alert                 |
| POST   | /admin/alerts/{id}/trigger/   | Trigger alert manually        |

### 👥 User
| Method | Endpoint                        | Description            |
|--------|---------------------------------|-----------------------|
| GET    | /user/alerts/                   | View alerts           |
| PUT    | /user/alerts/{id}/mark_read/    | Mark as read          |
| POST   | /user/alerts/{id}/snooze/       | Snooze alert          |
| GET    | /user/alerts/snoozed/           | View snoozed alerts   |

### 📊 Analytics
| Method | Endpoint                     | Description        |
|--------|------------------------------|------------------|
| GET    | /analytics/                  | System metrics    |
| GET    | /analytics/alerts/{id}/      | Alert metrics     |

---

## 📁 Project Structure

```text
backend/
├── alerting_platform/
│   ├── settings.py
│   ├── celery.py
│   └── urls.py
│
├── alerts/
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── tasks.py
│   └── management/commands/seed_data.py
│
├── requirements.txt
├── manage.py
└── .env
```
---

## 🧪 Testing

### 1. Login

   curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}'


### 2. Create alert
 curl -X POST http://localhost:8000/api/admin/alerts/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Alert","message":"Testing","severity":"Info"}'


---

## 🔄 How It Works

### Celery Beat:
 - Schedules process_reminders() every 2 hours

 - Runs reset_expired_snoozes() daily

### Celery Worker:
 - Sends alerts

 - Logs deliveries

 - Skips snoozed users

### Visibility levels:
 - Organization / Team / User targeting

---

## 🚀 Future Scope

 - Email & SMS channels (Twilio / AWS SNS)
 - Custom reminder frequency
 - Scheduled & recurring alerts
 - Escalation rules (auto-upgrade severity)
 - Push notifications
 - Alert templates

---

## 🐛 Troubleshooting

 Issue                 Fix
 
 Redis not connecting  Verify REDIS_URL starts with rediss://
 
 MySQL errors          Ensure MySQL is running, recreate DB
 
 Celery not running    Check all 3 processes (Django, Worker, Beat)

---

## 🔐 Security Notes

 - Change SECRET_KEY & disable DEBUG in production
 - Store credentials in .env
 - Enforce HTTPS & JWT rotation
 - Implement rate limiting
 - Use strong database credentials

---

## 📝 License

## Educational demo showcasing:
 - Strategy

 - Factory

 - Service Layer

 - Celery

 - REST API
- Clean Architecture

## Built using Django, Celery, and solid OOP design principles.

