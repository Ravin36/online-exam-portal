import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime, timedelta

from models import *
from database import execute_query, execute_single
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)

app = FastAPI(title="Online Examination Portal API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def ensure_admin_user():
    """Ensure default admin user exists with known credentials."""
    admin_username = "admin"
    admin_password = "admin@123"
    admin_email = "admin@exam.com"
    admin_full_name = "System Administrator"
    
    try:
        existing_admin = execute_single(
            "SELECT id FROM users WHERE username = %s",
            (admin_username,)
        )

        hashed_password = get_password_hash(admin_password)

        if not existing_admin:
            execute_query(
                "INSERT INTO users (username, email, password, role, full_name) VALUES (%s, %s, %s, %s, %s)",
                (admin_username, admin_email, hashed_password, 'admin', admin_full_name)
            )
    except Exception:
        pass

# ============== AUTHENTICATION ENDPOINTS ==============

@app.post("/api/register")
async def register(user: UserCreate):
    """Register new user"""
    # Check if user exists
    existing = execute_single(
        "SELECT id FROM users WHERE username = %s OR email = %s",
        (user.username, user.email)
    )
    
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Insert user
    user_id = execute_query(
        """INSERT INTO users (username, email, password, role, full_name) 
           VALUES (%s, %s, %s, %s, %s)""",
        (user.username, user.email, hashed_password, user.role.value, user.full_name)
    )
    
    if user_id:
        return {"message": "Registration successful", "user_id": user_id}
    else:
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/login")
async def login(credentials: UserLogin):
    """User login"""
    user = execute_single(
        "SELECT * FROM users WHERE username = %s",
        (credentials.username,)
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    stored_password = user['password']
    password_ok = False

    if isinstance(stored_password, str) and stored_password.startswith('$2'):
        password_ok = verify_password(credentials.password, stored_password)
    else:
        password_ok = credentials.password == stored_password
        if not password_ok:
            password_ok = credentials.password.lower() == stored_password.lower()

    if not password_ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token_data = {
        "user_id": user['id'],
        "username": user['username'],
        "role": user['role']
    }
    token = create_access_token(token_data)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "role": user['role'],
            "full_name": user['full_name']
        }
    }

# ============== STUDENT ENDPOINTS ==============

@app.get("/api/student/exams")
async def get_available_exams(current_user: dict = Depends(get_current_user)):
    """Get all available exams"""
    exams = execute_query(
        "SELECT * FROM exams WHERE is_active = 1 ORDER BY exam_date DESC",
        fetch=True
    )
    return exams or []

@app.post("/api/student/apply")
async def apply_for_exam(application: ApplicationCreate, current_user: dict = Depends(get_current_user)):
    """Apply for an exam"""
    if current_user['role'] != 'student':
        raise HTTPException(status_code=403, detail="Only students can apply")
    
    # Check if already applied
    existing = execute_single(
        "SELECT id FROM exam_applications WHERE student_id = %s AND exam_id = %s",
        (current_user['user_id'], application.exam_id)
    )
    
    if existing:
        raise HTTPException(status_code=400, detail="Already applied for this exam")
    
    # Create application
    app_id = execute_query(
        """INSERT INTO exam_applications (student_id, exam_id) 
           VALUES (%s, %s)""",
        (current_user['user_id'], application.exam_id)
    )
    
    return {"message": "Application submitted successfully", "application_id": app_id}

@app.get("/api/student/applications")
async def get_my_applications(current_user: dict = Depends(get_current_user)):
    """Get student's applications"""
    applications = execute_query(
        """SELECT ea.*, e.title, e.fee, e.exam_date, e.duration_minutes
           FROM exam_applications ea
           JOIN exams e ON ea.exam_id = e.id
           WHERE ea.student_id = %s
           ORDER BY ea.application_date DESC""",
        (current_user['user_id'],),
        fetch=True
    )
    return applications or []

@app.put("/api/student/payment/{application_id}")
async def update_payment(
    application_id: int, 
    payment: PaymentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update payment status"""
    execute_query(
        """UPDATE exam_applications 
           SET payment_status = 'paid', payment_date = NOW(), transaction_id = %s
           WHERE id = %s AND student_id = %s""",
        (payment.transaction_id, application_id, current_user['user_id'])
    )
    
    return {"message": "Payment updated successfully"}

@app.get("/api/student/exam/{exam_id}/questions")
async def get_exam_questions(exam_id: int, current_user: dict = Depends(get_current_user)):
    """Get exam questions for student"""
    # Check if student has approved application and paid
    application = execute_single(
        """SELECT admin_approval, payment_status 
           FROM exam_applications 
           WHERE student_id = %s AND exam_id = %s""",
        (current_user['user_id'], exam_id)
    )
    
    if not application or application['admin_approval'] != 'approved':
        raise HTTPException(status_code=403, detail="Exam not approved or not applied")
    
    questions = execute_query(
        """SELECT q.id, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d
           FROM questions q
           WHERE q.exam_id = %s
           ORDER BY q.id""",
        (exam_id,),
        fetch=True
    )
    return questions or []

@app.post("/api/student/submit-exam")
async def submit_exam(submission: ExamSubmission, current_user: dict = Depends(get_current_user)):
    """Submit exam answers"""
    if current_user['role'] != 'student':
        raise HTTPException(status_code=403, detail="Only students can submit exams")
    
    total_marks = 0
    obtained_marks = 0
    
    for answer in submission.answers:
        # Get correct answer
        correct_answer = execute_single(
            "SELECT correct_answer FROM questions WHERE id = %s",
            (answer.question_id,)
        )
        
        is_correct = answer.selected_answer == correct_answer['correct_answer']
        
        # Insert student answer
        execute_query(
            """INSERT INTO student_answers (student_id, exam_id, question_id, selected_answer, is_correct)
               VALUES (%s, %s, %s, %s, %s)""",
            (current_user['user_id'], submission.exam_id, answer.question_id, answer.selected_answer, is_correct)
        )
        
        if is_correct:
            obtained_marks += 1
        total_marks += 1
    
    percentage = (obtained_marks / total_marks) * 100 if total_marks > 0 else 0
    status = "pass" if percentage >= 40 else "fail"
    
    # Insert result
    execute_query(
        """INSERT INTO results (student_id, exam_id, obtained_marks, total_marks, percentage, status)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (current_user['user_id'], submission.exam_id, obtained_marks, total_marks, percentage, status)
    )
    
    return {
        "message": "Exam submitted successfully",
        "obtained_marks": obtained_marks,
        "total_marks": total_marks,
        "percentage": percentage,
        "status": status
    }

@app.get("/api/student/results")
async def get_my_results(current_user: dict = Depends(get_current_user)):
    """Get student results"""
    results = execute_query(
        """SELECT r.*, e.title
           FROM results r
           JOIN exams e ON r.exam_id = e.id
           WHERE r.student_id = %s
           ORDER BY r.submission_date DESC""",
        (current_user['user_id'],),
        fetch=True
    )
    return results or []

# ============== ADMIN ENDPOINTS ==============

@app.get("/api/admin/applications")
async def get_all_applications(current_user: dict = Depends(get_current_user)):
    """Get all exam applications (Admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    applications = execute_query(
        """SELECT ea.*, u.full_name, u.email, u.username, e.title, e.fee
           FROM exam_applications ea
           JOIN users u ON ea.student_id = u.id
           JOIN exams e ON ea.exam_id = e.id
           ORDER BY ea.application_date DESC""",
        fetch=True
    )
    return applications or []

@app.put("/api/admin/approve")
async def approve_application(approval: ApprovalUpdate, current_user: dict = Depends(get_current_user)):
    """Approve or reject application"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get application details
    app = execute_single(
        "SELECT student_id, payment_status FROM exam_applications WHERE id = %s",
        (approval.application_id,)
    )
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if approval.status == ApprovalStatus.approved and app['payment_status'] != 'paid':
        raise HTTPException(status_code=400, detail="Cannot approve unpaid application")
    
    # Update application
    execute_query(
        """UPDATE exam_applications 
           SET admin_approval = %s, admin_id = %s, approval_date = NOW()
           WHERE id = %s""",
        (approval.status.value, current_user['user_id'], approval.application_id)
    )
    
    # Send notification
    message = f"Your exam application has been {approval.status.value}d"
    execute_query(
        """INSERT INTO notifications (user_id, sender_id, message, type)
           VALUES (%s, %s, %s, %s)""",
        (app['student_id'], current_user['user_id'], message, 'approval' if approval.status == ApprovalStatus.approved else 'rejection')
    )
    
    return {"message": f"Application {approval.status.value}d successfully"}

@app.get("/api/admin/unpaid-students")
async def get_unpaid_students(current_user: dict = Depends(get_current_user)):
    """Get list of students with pending payments"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    students = execute_query(
        """SELECT ea.id, u.id as student_id, u.full_name, u.email, u.username, 
                  e.title, e.fee, ea.application_date
           FROM exam_applications ea
           JOIN users u ON ea.student_id = u.id
           JOIN exams e ON ea.exam_id = e.id
           WHERE ea.admin_approval = 'approved' AND ea.payment_status = 'pending'
           ORDER BY ea.application_date DESC""",
        fetch=True
    )
    return students or []

@app.post("/api/admin/notify-teacher")
async def notify_teacher_about_unpaid(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Notify teacher about unpaid students"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get teacher
    teacher = execute_single(
        "SELECT id FROM users WHERE role = 'teacher' LIMIT 1"
    )
    
    if not teacher:
        raise HTTPException(status_code=404, detail="No teacher found")
    
    # Send notification
    execute_query(
        """INSERT INTO notifications (user_id, sender_id, message, type)
           VALUES (%s, %s, %s, %s)""",
        (teacher['id'], current_user['user_id'], data['message'], 'payment_reminder')
    )
    
    return {"message": "Teacher notified successfully"}

@app.post("/api/admin/create-exam")
async def create_exam(exam: ExamCreate, current_user: dict = Depends(get_current_user)):
    """Create new exam (Admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    exam_id = execute_query(
        """INSERT INTO exams (title, description, fee, exam_date, duration_minutes, total_questions, is_active)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (exam.title, exam.description, exam.fee, exam.exam_date, exam.duration_minutes, exam.total_questions, exam.is_active)
    )
    
    return {"message": "Exam created successfully", "exam_id": exam_id}

@app.post("/api/admin/add-question")
async def add_question(question: QuestionCreate, current_user: dict = Depends(get_current_user)):
    """Add question to exam (Admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    question_id = execute_query(
        """INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (question.exam_id, question.question_text, question.option_a, question.option_b, question.option_c, question.option_d, question.correct_answer)
    )
    
    return {"message": "Question added successfully", "question_id": question_id}

# ============== TEACHER ENDPOINTS ==============

@app.get("/api/teacher/unpaid-students")
async def teacher_get_unpaid(current_user: dict = Depends(get_current_user)):
    """Get unpaid students list for teacher"""
    if current_user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail="Teacher access required")
    
    students = execute_query(
        """SELECT ea.id, u.id as student_id, u.full_name, u.email, u.username,
                  e.title, e.fee, ea.application_date
           FROM exam_applications ea
           JOIN users u ON ea.student_id = u.id
           JOIN exams e ON ea.exam_id = e.id
           WHERE ea.admin_approval = 'approved' AND ea.payment_status = 'pending'
           ORDER BY ea.application_date DESC""",
        fetch=True
    )
    return students or []

@app.post("/api/teacher/send-reminder")
async def send_payment_reminder(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send payment reminder to student"""
    if current_user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail="Teacher access required")
    
    # Send notification
    execute_query(
        """INSERT INTO notifications (user_id, sender_id, message, type)
           VALUES (%s, %s, %s, %s)""",
        (data['student_id'], current_user['user_id'], data['message'], 'payment_reminder')
    )
    
    return {"message": "Reminder sent successfully"}

from mangum import Mangum

handler = Mangum(app)