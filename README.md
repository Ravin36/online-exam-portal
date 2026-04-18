# Online Examination Portal

A full-stack web application for managing online examinations with fee-based eligibility system.

## Features

- **Role-based Authentication** (Student, Admin, Teacher)
- **Fee Payment System** with admin verification
- **Exam Management** with MCQ-based questions
- **Timer-based Examination** with auto-submission
- **Automated Evaluation** and results
- **Notification System** for payment reminders
- **Responsive Design**

## Technology Stack

- **Backend:** FastAPI (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL
- **Authentication:** JWT

## Installation

### Prerequisites

- Python 3.8+
- MySQL Server
- Modern web browser

### Backend Setup

Option 1: Run from the repository root
```powershell
cd backend
python -m venv env
.\env\Scripts\Activate.ps1     # PowerShell
# or .\env\Scripts\activate.bat  # Command Prompt
pip install -r requirements.txt
.\env\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Option 2: Run directly from the repository root without changing folders
```powershell
.\backend\env\Scripts\Activate.ps1
pip install -r backend\requirements.txt
.\backend\env\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Database Setup

1. Create the MySQL database:
```sql
CREATE DATABASE exam_portal;
```

2. Import the schema and sample data from `database/schema.sql`.

3. Use these sample login accounts:
   - Admin: `admin` / `admin@123`
   - Teacher: `teacher1` / `admin123`
   - Student: `student1` / `student123`

4. If you already imported the database and your admin account is not working, update the stored password hash:
```sql
USE exam_portal;
UPDATE users
SET password = '$2b$12$R3wV0WIMCCMLA3n8.L3OzOw60I.UDttkscWav4HmjK0Sr8Lx6GWhS'
WHERE username = 'admin';
```

5. If MySQL requires a password, create a `.env` file in `backend` with:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=exam_portal
```

> Note: `./env/Scripts/activate` fails from the repository root because the virtual environment is located under `backend\env`, not `env` at the root.
