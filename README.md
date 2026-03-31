# INGO

INGO is a full-stack tenant management MVP focused on structured onboarding, role-based access, and property assignment.

## Stack

- Backend: Django 4.2, Django REST Framework, SimpleJWT
- Database: PostgreSQL via `DATABASE_URL`, with SQLite fallback for development
- Frontend: Vue 3, Vite, vanilla CSS
- PWA: `vite-plugin-pwa`

## Roles

- `super_admin`: created manually with a Django command
- `landlord`: created by the super admin
- `caretaker`: created by a landlord
- `tenant`: created by a landlord or caretaker, activated through OTP onboarding

## Local Setup

### Backend

1. Copy [`backend/.env.example`](/S:/PersonalProjects/ingov2/backend/.env.example) to `backend/.env` and adjust values if needed.
2. Install dependencies:

```bash
cd backend
python -m pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Create the super admin:

```bash
python manage.py create_super_admin --name "System Owner" --email owner@example.com --password "ChangeMe123!"
```

5. Start the API:

```bash
python manage.py runserver
```

### Frontend

1. Copy [`frontend/.env.example`](/S:/PersonalProjects/ingov2/frontend/.env.example) to `frontend/.env`.
2. Install dependencies:

```bash
cd frontend
npm install
```

3. Start the web app:

```bash
npm run dev
```

The frontend expects the API at `http://127.0.0.1:8000/api` by default.

## Core Flows

### Staff login

- Super admin, landlord, and caretaker sign in with email and password.

### Tenant onboarding

1. A landlord or caretaker creates a tenant with name and phone number.
2. The backend creates an inactive tenant account and a secure 6-digit OTP.
3. The OTP stays visible in landlord and caretaker dashboards until activation.
4. The tenant verifies their name and OTP from the public activation screen.
5. The tenant sets a password and can optionally update the phone number once.
6. The OTP is burned, the account becomes active, and future logins use phone plus password.

## Important API Routes

- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`
- `GET /api/auth/dashboard/`
- `GET|POST /api/auth/users/`
- `GET|POST /api/properties/`
- `POST /api/properties/<property_id>/assign-caretaker/`
- `GET|POST /api/tenants/`
- `GET /api/tenants/<tenant_id>/otp/`
- `POST /api/tenants/activation/verify/`
- `POST /api/tenants/activation/complete/`

## Verification

- Backend checks: `python manage.py check`
- Backend tests: `python manage.py test`
- Frontend build: `npm run build`
