Radisist Backend
================

Backend API for a radiology workflow with role-based access (patients, radiologists, admin), scan uploads, AI-assisted predictions, and radiology reports. Built with Django REST Framework, JWT auth, and Djoser.

Features
--------
- Custom user model with roles: PATIENT, RADIOLOGIST, ADMIN
- Patient and radiologist profiles
- Scan upload with AI prediction on create (or manual rerun)
- Report generation and permissions (patients see impressions, radiologists edit full content)
- JWT authentication and token blacklist logout
- CORS/CSRF configuration for frontend integrations

Tech Stack
----------
- Django 6.0
- Django REST Framework
- Djoser + SimpleJWT
- PostgreSQL (via `DATABASE_URL`)
- External AI service (HTTP endpoint)

Project Structure
-----------------
- backend/           Django project settings
- apps/users/        Custom user model, serializers, views
- apps/radiology/    Scan + report models, AI service, viewsets
- media/             Uploaded scans

Quick Start
-----------
1) Create and activate a virtual environment
2) Install dependencies
3) Configure environment variables
4) Run migrations and start the server

Example (Windows PowerShell):

```
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000

DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME

EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=app-password

AI_SERVICE_URL=https://your-ai-service.example.com
DOMAIN=localhost:3000
SITE_NAME=Radisist
```

Run migrations and start the server:

```
python manage.py migrate
python manage.py runserver
```

Authentication
--------------
JWT endpoints from Djoser:
- POST /api/auth/jwt/create/   (login)
- POST /api/auth/jwt/refresh/  (refresh)
- POST /api/auth/jwt/verify/   (verify)

Logout (token blacklist):
- POST /api/auth/logout/

Users API
---------
User endpoints are served via a router:
- /api/auth/users/
- /api/auth/users/{id}/

User creation uses a custom serializer that accepts role-specific fields.

Radiology API
-------------
Base path: /api/radiology/

Scans:
- GET /api/radiology/scans/
- POST /api/radiology/scans/
- GET /api/radiology/scans/{id}/
- PATCH /api/radiology/scans/{id}/
- DELETE /api/radiology/scans/{id}/
- POST /api/radiology/scans/{id}/rerun_ai/

Reports:
- GET /api/radiology/reports/
- POST /api/radiology/reports/
- GET /api/radiology/reports/{id}/
- PATCH /api/radiology/reports/{id}/
- DELETE /api/radiology/reports/{id}/

Permissions
-----------
- Patients see their own scans and report impressions only
- Radiologists can create/update reports
- Admin/staff can access all scans

AI Service
----------
The backend calls an external AI prediction service when a new scan is saved. Configure the URL with `AI_SERVICE_URL`. The service is expected to accept:
- POST {AI_SERVICE_URL}/predict
- Multipart file with field `file`
- Query param `model_name`

The response should be JSON with:
- predicted_class
- confidence
- benign_probability
- malignant_probability

Notes
-----
- Media uploads are served from `/media/` in development.
- For production, configure a proper static/media server and secure environment variables.
