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
- **Database:** None configured
- **Authentication:** JWT

## Installation

### Prerequisites

- Python 3.8+
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

> Note: `./env/Scripts/activate` fails from the repository root because the virtual environment is located under `backend\env`, not `env` at the root.
