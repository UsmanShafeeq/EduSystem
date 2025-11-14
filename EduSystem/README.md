# EduSystem API

**EduSystem** is a full-featured **Django REST Framework** application for managing students, staff, courses, admissions, enrollments, attendance, exams, grades, fees, and notifications.
It includes JWT authentication, role-based permissions, bulk create/update endpoints, dashboard statistics, and API documentation with Swagger & ReDoc.

---

## Table of Contents

* [Features](#features)
* [Tech Stack](#tech-stack)
* [Installation](#installation)
* [Environment Setup](#environment-setup)
* [Running the Server](#running-the-server)
* [API Documentation](#api-documentation)
* [Authentication](#authentication)
* [Endpoints Overview](#endpoints-overview)
* [Testing API](#testing-api)
* [Pagination](#pagination)
* [Role-Based Permissions](#role-based-permissions)
* [Bulk Operations](#bulk-operations)
* [Dashboard](#dashboard)

---

## Features

* JWT Authentication with `access` & `refresh` tokens
* Role-based access control (`Admin`, `Staff`, `Student`)
* CRUD APIs for:

  * Departments, Programs, Courses, Designations
  * Students, Staff, Admissions, Enrollments, Attendance
  * Exams, Grades, Fees, Notifications
* Bulk create/update endpoints for Students & Courses
* Dashboard statistics with date filters (`today`, `week`, `month`, `custom`)
* Search, filter, ordering, and pagination for all endpoints
* API documentation using Swagger (`/swagger/`) and ReDoc (`/redoc/`)
* Actions:

  * Deactivate Student/Staff
  * Mark Fee as Paid
  * Mark Notification as Read

---

## Tech Stack

* Python 3.11+
* Django 5.x
* Django REST Framework
* Django Filters
* Simple JWT (`djangorestframework-simplejwt`)
* SQLite (default, can switch to PostgreSQL/MySQL)
* Swagger & ReDoc (`drf-yasg`)
* CORS headers for React/Vite frontend

---

## Installation

Clone the repository:

```bash
git clone <your-repo-url>
cd backend
```

Create a virtual environment:

```bash
python -m venv env
source env/bin/activate      # Linux / Mac
env\Scripts\activate       # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Setup

Create `.env` file (optional):

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Update `settings.py` to use environment variables if desired.

---

## Running the Server

Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create superuser:

```bash
python manage.py createsuperuser
```

Run server:

```bash
python manage.py runserver
```

Access:

* Admin: `http://127.0.0.1:8000/admin/`
* Swagger: `http://127.0.0.1:8000/swagger/`
* ReDoc: `http://127.0.0.1:8000/redoc/`

---

## API Documentation

* **Swagger UI:** `/swagger/`
* **ReDoc:** `/redoc/`

Swagger supports JWT authentication. Click **Authorize**, then enter:

```
Bearer <access_token>
```

---

## Authentication

* Obtain tokens:

```http
POST /api/token/
{
    "username": "admin",
    "password": "admin123"
}
```

* Refresh token:

```http
POST /api/token/refresh/
{
    "refresh": "<refresh_token>"
}
```

* Include access token in headers:

```
Authorization: Bearer <access_token>
```

---

## Endpoints Overview

| Resource     | Endpoint              | Methods                | Roles Allowed         |
| ------------ | --------------------- | ---------------------- | --------------------- |
| Department   | `/api/departments/`   | GET, POST, PUT, DELETE | Admin, Staff          |
| Program      | `/api/programs/`      | GET, POST, PUT, DELETE | Admin, Staff          |
| Course       | `/api/courses/`       | GET, POST, PUT, DELETE | Admin, Staff          |
| Designation  | `/api/designations/`  | GET, POST, PUT, DELETE | Admin                 |
| Student      | `/api/students/`      | GET, POST, PUT, DELETE | Admin, Staff, Student |
| Staff        | `/api/staff/`         | GET, POST, PUT, DELETE | Admin                 |
| Admission    | `/api/admissions/`    | GET, POST, PUT, DELETE | Admin, Staff          |
| Enrollment   | `/api/enrollments/`   | GET, POST, PUT, DELETE | Admin, Staff, Student |
| Attendance   | `/api/attendances/`   | GET, POST, PUT, DELETE | Admin, Staff          |
| Exam         | `/api/exams/`         | GET, POST, PUT, DELETE | Admin, Staff          |
| Grade        | `/api/grades/`        | GET, POST, PUT, DELETE | Admin, Staff, Student |
| Fee          | `/api/fees/`          | GET, POST, PUT, DELETE | Admin, Staff, Student |
| Notification | `/api/notifications/` | GET, POST, PUT, DELETE | Admin, Staff, Student |
| Student Bulk | `/api/students/bulk/` | POST, PUT              | Admin, Staff          |
| Course Bulk  | `/api/courses/bulk/`  | POST, PUT              | Admin, Staff          |
| Dashboard    | `/api/dashboard/`     | GET                    | Admin, Staff          |

---

## Testing API

* Use Swagger UI or **Postman** to test all endpoints.
* Use sample JSON input for **CRUD** operations.
* Bulk operations allow multiple records in one request.
* Dashboard supports filters: `today`, `week`, `month`, `custom`.

---

## Pagination

* Default page size: `10`
* Query param: `?page=1&?page_size=20`

---

## Role-Based Permissions

* **Admin:** Full access
* **Staff:** Limited to assigned modules
* **Student:** Can view own data, grades, attendance, notifications

---

## Bulk Operations

* **Students:** `/api/students/bulk/`
* **Courses:** `/api/courses/bulk/`

Supports **POST** (create) and **PUT** (update) with transaction rollback.

---

## Dashboard

* `/api/dashboard/?filter=today|week|month|custom&start=YYYY-MM-DD&end=YYYY-MM-DD`
* Returns counts for all resources filtered by date.

Example response:

```json
{
  "total_students": 10,
  "total_staff": 5,
  "total_admissions": 8,
  "total_enrollments": 12,
  "total_attendance": 50,
  "total_exams": 3,
  "total_grades": 25,
  "total_fees": 20,
  "total_notifications": 7,
  "filter_info": {
    "filter_type": "today",
    "start_date": "2025-11-14",
    "end_date": "2025-11-15"
  }
}
```

---

## Notes

* Supports **SQLite** by default; can switch to PostgreSQL/MySQL.
* Ensure `drf_yasg` and `rest_framework_simplejwt` are installed for Swagger and JWT.
* Frontend (React/Vite) can consume APIs via CORS (`http://localhost:3000`, `http://localhost:5173`).

---

## License

MIT License © 2025
