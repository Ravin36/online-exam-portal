from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

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

# SQLAlchemy Database Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.student)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    fee = Column(Float)
    duration_minutes = Column(Integer)
    total_marks = Column(Integer)
    passing_marks = Column(Integer)
    exam_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.pending)
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.pending)
    transaction_id = Column(String, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    question_text = Column(Text)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_answer = Column(String)
    marks = Column(Integer, default=1)

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer = Column(String)
    is_correct = Column(Boolean)
    marks_obtained = Column(Float, default=0)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

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