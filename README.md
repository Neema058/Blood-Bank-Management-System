# Blood Bank Management System

## Setup Instructions

### 1. Create Database
Run `create_database.sql` in phpMyAdmin (or MySQL client) to create the database.

### 2. Configure Database
Edit `blood_bank/settings.py` and update the DATABASES section with your MySQL credentials.

### 3. Run Setup
Double-click `setup.bat` (Windows) or run manually:
```
pip install -r requirements.txt
python manage.py makemigrations accounts donors donations inventory patients blood_requests reports dashboard
python manage.py migrate
```

Then create your admin user:
```
python manage.py createsuperuser
```

### 4. Start Server
```
python manage.py runserver
```
Open: http://127.0.0.1:8000

---

## User Roles & Access

| Role | Access |
|------|--------|
| **Admin** | Full access — dashboard, donors, donations, inventory, patients, blood requests (approve/reject), reports, manage users |
| **Receptionist** | Dashboard, donors, donations, inventory, patients, blood requests (create only), no reports |
| **Lab Technician** | Dashboard, donors, donations, inventory, blood requests (view only), reports |
| **Patient** | Personal portal only — view their profile, submit blood requests, track request status |

## How to Create a Patient Login
1. First register the patient under **Patients → Add Patient**
2. Go to **Admin → Manage Users → Add User**
3. Select Role = **Patient** and link to the patient record
4. Give them a username and password
5. Patient can now log in at the main login page and will be directed to their personal portal

---

## Modules
- **Donors** — Registration, eligibility tracking, CNIC-based ID
- **Donations** — Blood test results (HIV, Hep B/C, Malaria, Syphilis), auto blood unit creation
- **Inventory** — Real-time stock, expiry tracking, rare blood group alerts
- **Blood Requests** — Patient requests, emergency alerts, FIFO unit issuance
- **Patients** — Patient records, request history
- **Reports** — Monthly donation charts, inventory reports, PDF export
- **Patient Portal** — Self-service portal for patients to submit and track requests
## commented line 