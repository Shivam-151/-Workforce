# WorkforceOS — Group 10

**Workforce Shift, Timesheet & Expense Reconciliation System**

A local, full-stack demonstration application for employee/manager workflows. It uses Python's standard library (`http.server`, `sqlite3`) and a responsive HTML/CSS/JavaScript frontend. No framework or database server installation is required.

## Run

1. Install Python 3.10 or later.
2. Extract this ZIP.
3. Open a terminal in this folder.
4. Run `python app.py` (Windows: `py app.py`).
5. Open `http://127.0.0.1:8000` in a browser.

The SQLite database `workforce.db` is created automatically on first launch and seeded with demonstration records.

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@group10.local | admin123 |
| Manager | manager@group10.local | manager123 |
| Employee | aarav@group10.local | employee123 |
| Employee | neha@group10.local | employee123 |
| Employee | kabir@group10.local | employee123 |

Use the Admin account to add team members and schedule shifts. Use Manager to review timesheets and expense claims. Employees can view their own shifts, submit timesheets and expenses, and see their own records.

## Main functionality

- Role-aware login (admin, manager, employee)
- Dashboard with workforce counts, pending approvals, month-to-date hours and approved expense total
- Team directory and employee creation (admin)
- Shift scheduling (admin/manager)
- Timesheet submission with hours and overtime calculation (overtime is hours above 8 per submitted workday)
- Expense claims with category, amount and optional receipt filename
- Manager/admin approval and rejection of timesheets and expenses
- Search/filter tables and persistent SQLite storage

## Important project limitations / demo assumptions

- This is an academic local-network prototype, not a production payroll or HR system.
- Passwords are hashed for the demonstration, but the hashing method and in-memory session store are not production-grade. Use HTTPS, a modern password KDF, CSRF protection, persistent secure sessions, audit logging and role-specific policy review before real deployment.
- Receipt upload is represented by a receipt filename field; binary file upload/storage is not implemented.
- Shift overlap, leave management, payroll disbursement, multi-location time zones and statutory overtime rules are outside the current scope.
- A timesheet is one record per employee per work date. If clock-out is omitted, the record remains at zero hours until a later version adds an edit/clock-out action.

## Project structure

```
app.py                 HTTP server, API, business logic and SQLite schema
static/index.html      Application shell
static/style.css       Responsive interface styling
static/app.js          Frontend interactions and API calls
workforce.db           Created automatically at runtime
docs/                  PBL diagrams and supporting material
tests/test_logic.py    Unit tests for hour calculation
PBL_Report_Group10.docx  Completed PBL report
```

## API overview

- `POST /api/login`, `POST /api/logout`
- `GET /api/me`, `GET /api/health`, `GET /api/dashboard`
- `GET/POST /api/employees`
- `GET/POST /api/shifts`
- `GET/POST /api/timesheets`, `PATCH /api/timesheets/{id}`
- `GET/POST /api/expenses`, `PATCH /api/expenses/{id}`

All protected endpoints require a logged-in session. Manager/admin permissions are enforced server-side.
