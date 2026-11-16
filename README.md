# MallWay &bull; Smart Mall Navigation & Management System

A full-stack Django web application designed for modern shopping mall exploration, directory navigation, tenant management, and role-based operations.

Built with **Full Stack Django** (Django backend and Django templates) and backed by **PostgreSQL / Supabase**.

---

## 🚀 Key Features

### 1. Account Registration & Authentication
- **Registration Form**: Validates required fields, valid email format, unique username and email, matching passwords, and role selection (**Customer** or **Mall Administrator**).
- **Password Security**: Passwords are cryptographically hashed using Django's built-in authentication system (PBKDF2 SHA-256).
- **Flexible Sign-In**: Users can log in using either their **username** or their **email address**.
- **Session Management**: Secure login and logout with user feedback messages.
- **Route Protection**: Protected views are strictly secured using `@login_required(login_url='login')`.

### 2. Role-Based User Dashboards
- **Customer Dashboard (Shopper Guide)**:
  - Welcome hero banner with personalized greeting.
  - Interactive mall directory with live category filter chips (*Fashion, Dining, Tech, Cinema, Wellness, Groceries*).
  - Rewards points, saved stores, and flash deals overview.
  - Mall facilities and guest comfort amenities guide.
- **Mall Administrator Dashboard (Operations Center)**:
  - Real-time mall KPIs: Total Stores, Occupancy Rate (92.3%), Daily Footfall, and Registered Accounts.
  - Tenant and store directory table with live search filtering, unit codes, and lease status badges.
  - Mall broadcast announcements management.
  - Quick administrative tools and floor plan shortcuts.
- **Strict Cross-Role URL Protection**:
  - Customers cannot open the Administrator Dashboard by typing its URL; unauthorized attempts are immediately blocked and redirected to the Customer Dashboard with an **Access Denied** alert.
  - Administrators attempting to access the Customer Dashboard URL are similarly bounced back to the Operations Console.

### 3. User Profile Management
- **View Profile**: Logged-in users can view their profile details, contact number, role badge, account timeline, and uploaded avatar.
- **Update Profile**: Users can update their first name, last name, email (with duplicate checks), contact number, and upload a profile photo with instant image preview.
- **Ownership Privacy**: Strict scoping ensures users can only view and edit their own profile.

### 4. Soothing, Professional UI Design
- Calming color palette with soft canvas tones (`#f7f9fc`), restful pastel accents (mint sage, soft sky, gentle lavender, warm honey), and pure-white cards with diffusion shadows.
- Typography using **Plus Jakarta Sans** and **Inter** for comfortable legibility without visual fatigue.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Django 6.1
- **Frontend**: Django Templates, HTML5, Modern CSS3, Vanilla JavaScript
- **Database**: PostgreSQL / Supabase
- **Image Processing**: Pillow 13.0
- **Environment Management**: Python-dotenv

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
Copy `.env.example` to `.env` and fill in your Supabase / PostgreSQL database credentials:
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
The repository includes 17 comprehensive unit and integration tests:
```powershell
python manage.py test accounts --keepdb
```

### 7. Start the Development Server
```powershell
python manage.py runserver 8001
```
Open [http://127.0.0.1:8001/](http://127.0.0.1:8001/) in your web browser.

---

## 📄 License & Credits
Developed by **Miles Angela Pinatil (G2)** for **MallWay**. All rights reserved.
