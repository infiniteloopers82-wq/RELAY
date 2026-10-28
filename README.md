# RELAY — Trusted Resource Sharing Network

RELAY is a working full-stack resource-sharing platform for institutions. It includes server-enforced eligibility, booking conflicts, owner approvals, lifecycle condition reports, incidents, fair waitlisting, dashboards, and audit history.

## Prerequisites

- Windows 10/11 PowerShell
- Python 3.13 (SQLAlchemy 2.0.36 is pinned for Windows compatibility)
- Node.js 20+ and npm
- Git

## Backend setup (PowerShell)

```powershell
cd c:\Users\OM\OneDrive\RELAY
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
cd backend
python seed.py
python app.py
```

The API runs at `http://localhost:5000/api`. Seed is non-destructive: it does nothing if users already exist. To start with an isolated demo database, use a fresh `backend\relay.db`.

## Frontend setup

In a second PowerShell window:

```powershell
cd c:\Users\OM\OneDrive\RELAY\frontend
npm.cmd install
npm.cmd run dev
```

Open `http://localhost:5173`.

## Tests and build

```powershell
cd c:\Users\OM\OneDrive\RELAY\backend
..\.venv\Scripts\python.exe -m pytest -q

cd ..\frontend
npm.cmd run build
```

## Demo accounts

All passwords are `Relay123!`.

| Role | Email |
|---|---|
| Student with relevant training | student@relay.demo |
| Student lacking training | untrained@relay.demo |
| Owner | owner@relay.demo |
| Administrator | admin@relay.demo |

Public registration always creates a student account. Owner and administrator roles must be provisioned by trusted administrators outside this public flow.

## Booking lifecycle

`pending` / `waitlisted` → `approved` → `checked_in` → `returned`; pending, waitlisted, or approved requests may become `cancelled`; pending or waitlisted requests may become `rejected`. Invalid transitions are rejected by the API. Waitlisted requests are deterministic FIFO by request creation time, then booking ID. A waitlisted booking is not an approval.

Approval is denied for an ineligible requester, an owner approving their own request, a time conflict with an approved/active booking, an unauthorized personnel member, or a configured usage limit. Current limits default to three active bookings per user and can be configured with `MAX_ACTIVE_BOOKINGS_PER_USER`.

## API overview

- Health: `GET /api/health`
- Auth: register, login, logout, current user
- Resources: discover, create, update, deactivate
- Bookings: create, inspect, approve, reject, cancel, check in, return
- Incidents: report, review, resolve
- Dashboards: student, owner, administrator
- Audit: administrator-only audit log

## Architecture

The Flask application factory (`backend/app.py`) initializes SQLAlchemy and Flask-Migrate. Domain models are separated under `backend/models`; HTTP routes under `backend/routes`; eligibility, allocation, audit, and booking logic under `backend/services`. The React application uses React Router, a central API client, cookie-based session authentication, role-aware routes, and a responsive shared shell.

## Security and limitations

- Passwords are hashed using Werkzeug's secure password hashing.
- Private routes require a server-side session; roles are read from the database, not supplied by the frontend.
- CORS allows only configured origins. Keep `SECRET_KEY`, cookies, and HTTPS settings production-safe.
- SQLite is suitable for local demonstration. Set `DATABASE_URL` to PostgreSQL for production and run migrations rather than relying only on `db.create_all`.
- Incidents are recorded for human review; the system never automatically declares a person guilty of damage.
- This demonstration uses an HTTP cookie session, which requires HTTPS and secure cookie configuration in production.
- Image references are stored as strings; actual object/image storage is a deployment integration.

## Environment

Copy `.env.example` to `.env` as a template. Never commit real secrets or the demo database. Deployment must set a random `SECRET_KEY`, production `DATABASE_URL`, HTTPS origins, and `SESSION_COOKIE_SECURE=true`.
