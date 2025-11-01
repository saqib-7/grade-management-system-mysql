import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Float, ForeignKey, Integer, DateTime, DECIMAL, UniqueConstraint, Index
from datetime import datetime
from typing import List, Optional

# Database URL from environment or default
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'mysql+asyncmy://grade_user:password123@localhost/grade_management_db'
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=0
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


class Faculty(Base):
    __tablename__ = "faculties"
    
    id = Column(String(36), primary_key=True, comment="UUID")
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    employee_id = Column(String(50), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = relationship("FacultyAssignment", back_populates="faculty", cascade="all, delete-orphan")
    marks = relationship("Marks", back_populates="faculty_obj")


class FacultyAssignment(Base):
    __tablename__ = "faculty_assignments"
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    faculty_id = Column(String(36), ForeignKey("faculties.id", ondelete="CASCADE"), nullable=False, index=True)
    class_name = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint for assignment combination
    __table_args__ = (
        UniqueConstraint('faculty_id', 'class_name', 'subject', name='unique_assignment'),
        Index('idx_class_subject', 'class_name', 'subject'),
    )
    
    # Relationships
    faculty = relationship("Faculty", back_populates="assignments")


class Student(Base):
    __tablename__ = "students"
    
    id = Column(String(36), primary_key=True, comment="UUID")
    name = Column(String(255), nullable=False)
    student_id = Column(String(50), nullable=False, unique=True, index=True)
    class_name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = relationship("StudentEnrollment", back_populates="student", cascade="all, delete-orphan")
    marks = relationship("Marks", back_populates="student_obj")


class StudentEnrollment(Base):
    __tablename__ = "student_enrollments"
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint for enrollment
    __table_args__ = (
        UniqueConstraint('student_id', 'subject', name='unique_enrollment'),
        Index('idx_subject', 'subject'),
    )
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")


class Marks(Base):
    __tablename__ = "marks"
    
    id = Column(String(36), primary_key=True, comment="UUID")
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    class_name = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    faculty_email = Column(String(255), ForeignKey("faculties.email", ondelete="RESTRICT"), nullable=False, index=True)
    ct1 = Column(DECIMAL(5, 2), nullable=True)
    insem = Column(DECIMAL(5, 2), nullable=True)
    ct2 = Column(DECIMAL(5, 2), nullable=True)
    total = Column(DECIMAL(6, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint for marks
    __table_args__ = (
        UniqueConstraint('student_id', 'class_name', 'subject', name='unique_marks'),
        Index('idx_composite', 'student_id', 'class_name', 'subject'),
        Index('idx_class_subject', 'class_name', 'subject'),
    )
    
    # Relationships
    student_obj = relationship("Student", back_populates="marks")
    faculty_obj = relationship("Faculty", back_populates="marks", foreign_keys=[faculty_email])


async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


