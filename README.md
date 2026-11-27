# MallWay &bull; Smart Mall Navigation & Management System

A modern full-stack Django web application designed for shopping mall exploration, directory navigation, tenant management, and role-based operations.

Built with **Full Stack Django** (Django backend and Django templates) and backed by **PostgreSQL / Supabase**.

Developed by **Miles Angela Pinatil (G2)** for **CSIT327 – Information Management 2**.

---

## 🏬 Project Development 2 — Core Feature: Mall Directory Management (Vertical Slice)

In this increment (**Project Development 2**), the primary core feature of MallWay—**Mall Directory Management & Destination Navigation**—has been built as a full working vertical slice across all application layers:

- **Database Layer**: Models and migrations for `Destination` stored in **PostgreSQL / Supabase** with owner tracking (`ForeignKey` to `auth.User`), category choices, floor, unit location, operating hours, featured flag, archived flag, and optional image upload.
- **Backend Layer**: Django forms (`DestinationForm`) with strict clean validation, URL routes, and views handling all CRUD operations with role-based access control and flash message alerts.
- **Frontend Layer**: Calming, responsive Django templates (`admin_directory.html`, `destination_form.html`, `destination_delete.html`, `destination_archive.html`, `directory.html`, `destination_detail.html`) styled with custom CSS and Plus Jakarta Sans typography.

### Core Feature Capabilities

| Feature Layer | Mall Administrator Capabilities | Customer / Shopper Capabilities |
| :--- | :--- | :--- |
| **Create (C)** | Add new destinations with name, category, floor, unit location, hours, description, photo upload, and featured status | N/A (Restricted to Admin) |
| **Read (R)** | View complete directory table with live search, category filter, and status filter (All, Active, Featured, Archived) | Browse active destinations, live search by name, filter by category and floor, view featured highlights, inspect destination details |
| **Update (U)** | Edit destination information, change unit/floor, upload replacement image, toggle featured status on/off | N/A (Restricted to Admin) |
| **Delete (D)** | **Permanent Delete** with confirmation modal & **Archive (Soft Delete)** / Restore toggle to hide from shoppers without losing data | N/A (Restricted to Admin) |

### Key Business Rules & Security

1. **Role-Based Access Control (RBAC)**: All administrative directory views (`/accounts/admin-panel/*`) strictly verify administrator privileges. Customers attempting to access admin URLs are redirected with an **Access Denied** alert.
2. **Account Ownership Integration**: Newly created destinations automatically link to the logged-in administrator (`destination.created_by = request.user`).
3. **Data Integrity & Soft Deletes**: Archived destinations are excluded from shopper queries (`archived=False`), ensuring historical accuracy while keeping the public directory clean.
4. **Input Validation**: Required fields (`name`, `category`, `floor`, `location`) are validated server-side, rejecting blank or whitespace-only inputs with field-level error messages.

---

## 🛡️ Standard Features (Project Development 1 — Still 100% Working)

1. **Account Registration**: Complete with unique username/email validation, role assignment (Customer or Mall Administrator), and PBKDF2 SHA-256 password hashing.
2. **Authentication (Login / Logout)**: Dual sign-in via username or email; secure session termination with feedback messages.
3. **Role-Based User Dashboards**:
   - **Customer Guide**: Personalized welcome hero, featured store cards, mall perks, and amenities guide.
   - **Admin Operations Center**: Real-time KPI tiles (Total Stores, Occupancy, Footfall), tenant directory, and announcements.
   - **Bidirectional Route Protection**: Cross-role dashboard access attempts are strictly blocked.
4. **User Profile Management**: View profile details, edit personal info, upload avatar photos, and maintain strict ownership privacy.

---

## 🛡️ Project Development 3 — Hardening of Core & Standard Features

In **Project Development 3 (PD3)**, MallWay's core feature (**Mall Directory Management**) and standard features were hardened for reliability, security, and data integrity:

- **PD2 Issues Fixed**: Added role-specific **Manage Directory** (admin) and **Mall Directory** (customer) navigation links in `templates/base.html`, wired dashboard action buttons in `admin_dashboard.html` and `customer_dashboard.html`, and read `DEBUG` / `SECRET_KEY` from `.env`.
- **Server-Side Validation & Business Rules**: `DestinationForm` enforces minimum lengths, whitespace normalization, uploaded image type/size/PIL verification (`validate_uploaded_image`), and prevents duplicate active destinations at the same floor and unit location. Restoring an archived destination into an occupied unit is also blocked.
- **Security & Access Control**: Every view enforces `@login_required` and role checks; `_get_owned_destination_or_403()` prevents admins from viewing or modifying another admin's records by ID (`403 Forbidden`); `@require_POST` is enforced on `destination_toggle_featured_view`; CSRF tokens are required on all POST forms; no raw SQL or `|safe` on user input.
- **Custom Error Pages**: Custom `404.html`, `403.html`, and `500.html` templates wired via `handler404`, `handler403`, and `handler500` in `mallway/urls.py` when `DEBUG=False`.
- **Data Integrity**: Added `MinLengthValidator(2)` and `UniqueConstraint(fields=['name', 'floor', 'location'])` in migration `0005`, `transaction.atomic()` around multi-step saves/deletes, `select_related('created_by')` on directory queries, and explicit confirmation modals before delete/archive.

---

## 🌿 Git Branching Strategy & Workflow

This project adheres to the required Git branching strategy:
- `main`: Production/stable branch. No direct commits.
- `develop`: Integration branch created from `main`.
- `feature/<feature-name>`: Dedicated feature branches branched from `develop` and merged via Pull Requests.

```
main ─────────────────────────────────────────────────────────────● (Release PD2)
       \                                                         /
develop ──●───────────────────────────●──────────●──────────────●
            \                       /   \       /
feature/directory-management ──────●     \     /
(Admin CRUD, Models, Migrations)          \   /
                                           \ /
feature/customer-directory ─────────────────●
(Customer Directory, Detail, 29 Tests)
```

### Pull Requests

1. **PR #1**: `feature/directory-management` &rarr; `develop`
   - *Contents*: Destination model enhancements (`created_by`, `image`, `created_at`), migration `0004`, `DestinationForm`, admin directory views, and administrative templates (`admin_directory.html`, `destination_form.html`, `destination_delete.html`, `destination_archive.html`).
2. **PR #2**: `feature/customer-directory` &rarr; `develop`
   - *Contents*: Customer directory browsing, live search, category and floor filtering, destination detail view, customer dashboard integration, and 12 core automated tests.
3. **PR #3**: `develop` &rarr; `main`
   - *Contents*: Project Development 2 increment release with complete documentation, passing test suite, and completion report.
4. **PR #4**: `fix/pd2-navigation-and-issues` &rarr; `develop`
   - *Contents*: Fixed missing Manage Directory / Mall Directory navbar links, dashboard quick action links, and UTF-8 encoding.
5. **PR #5**: `hardening/validation-security-integrity` &rarr; `develop`
   - *Contents*: Server-side validation, business rules, ownership checks (`_get_owned_destination_or_403`), atomic transactions, `.env` `DEBUG`, and custom `403`/`404`/`500` error pages.
6. **PR #6**: `test/hardening-core-tests` &rarr; `develop`
   - *Contents*: Added 12 `MallDirectoryHardeningTests` covering validation, RBAC, ownership, CSRF enforcement, and error pages.
7. **PR #7**: `develop` &rarr; `main`
   - *Contents*: Project Development 3 increment release with hardened Mall Directory core feature, 41 passing automated tests, and PD3 Hardening Report.

---

## 🧪 Comprehensive Automated Test Suite (41 Tests)

The repository includes **41 automated unit and integration tests** with **100% pass rate**:
- **17 Tests**: Account registration, authentication, role isolation, and user profile management (PD1).
- **12 Tests**: Destination CRUD operations, input validation, soft-delete archiving, category/floor filtering, and role-based route security (PD2).
- **12 Tests**: Hardening tests (`MallDirectoryHardeningTests`) verifying duplicate unit rejection, image upload validation, ownership isolation (`403`), `POST`-only toggles (`405`), `get_object_or_404` (`404`), custom 404 page with `DEBUG=False`, restore conflict checks, and CSRF enforcement (PD3).

To run the complete test suite:
```powershell
python manage.py test
```

Output:
```
Ran 41 tests in 59.507s
OK
```

---

## 🔑 Test Accounts

| Role | Username / Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Mall Administrator** | `admin_clara` / `clara@mallway.com` | `ClaraPassword123!` | Admin Operations & Directory Management |
| **Customer (Shopper)** | `shopper_dan` / `dan@example.com` | `DanPassword123!` | Shopper Guide & Public Mall Directory |

---

## ⚙️ Setup & Installation Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/milescitrine17/MallWay-Pinatil-Miles_Angela-G2.git
cd MallWay-Pinatil-Miles_Angela-G2
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your Supabase / PostgreSQL credentials:
```powershell
cp .env.example .env
```

Ensure `.env` contains:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True

DB_NAME=postgres
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_HOST=aws-0-ap-northeast-1.pooler.supabase.com
DB_PORT=5432
```

### 5. Run Database Migrations
```powershell
python manage.py migrate
```

### 6. Run the Test Suite
```powershell
python manage.py test
```
> **Note**: When running `manage.py test`, Django automatically uses an isolated in-memory SQLite database so tests run reliably without requiring external database access.

### 7. Start the Development Server
```powershell
python manage.py runserver 8001
```
Open [http://127.0.0.1:8001/](http://127.0.0.1:8001/) in your browser.

---

## 📄 Implementation & Hardening Reports
The official Project Development reports are committed under `docs/`:
- `docs/MallWay-Pinatil-Miles_Angela-G2-PD3.pdf` (Project Development 3 Hardening Report)
- `docs/MallWay-Pinatil-Miles_Angela-G2-PD3.docx`
- `docs/MallWay-Pinatil-Miles_Angela-G2-PD2.pdf` (Project Development 2 Completion Report)
- `docs/MallWay-Pinatil-Miles_Angela-G2-PD2.docx`

---

## 📜 License & Credits
Developed by **Miles Angela Pinatil (G2)** for **MallWay**. All rights reserved.
