from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    student = "student"
    admin = "admin"
    teacher = "teacher"

class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    verified = "verified"
    rejected = "rejected"

class ApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

# User Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.student

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    full_name: str

# Exam Models
class ExamCreate(BaseModel):
    title: str
    description: str
    fee: float
    duration_minutes: int
    total_marks: int
    passing_marks: int
    exam_date: datetime

class ExamResponse(BaseModel):
    id: int
    title: str
    description: str
    fee: float
    duration_minutes: int
    total_marks: int
    passing_marks: int
    exam_date: datetime
    is_active: bool

# Application Models
class ApplicationCreate(BaseModel):
    exam_id: int

class PaymentUpdate(BaseModel):
    transaction_id: str

class ApplicationApproval(BaseModel):
    application_id: int
    status: ApprovalStatus

# Question Models
class QuestionCreate(BaseModel):
    exam_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    marks: int = 1

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    marks: int

# Answer Models
class AnswerSubmit(BaseModel):
    exam_id: int
    answers: List[dict]  # [{"question_id": 1, "answer": "A"}, ...]

# Notification Models
class NotificationCreate(BaseModel):
    recipient_id: int
    message: str
    type: str = "general"