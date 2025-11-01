from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
import os
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_mysql import AsyncSessionLocal, Faculty, FacultyAssignment, Student, StudentEnrollment, Marks, init_db

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

security = HTTPBearer()

# Pydantic Models (Kept as-is for API compatibility)
class Assignment(BaseModel):
    class_name: str
    subject: str

class Faculty(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    email: str
    employee_id: str
    assignments: List[Assignment]
    
    class Config:
        from_attributes = True

class Student(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    student_id: str
    class_name: str
    enrolled_subjects: List[str]
    
    class Config:
        from_attributes = True

class Marks(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    student_id: str
    class_name: str
    subject: str
    faculty_email: str
    ct1: Optional[float] = None
    insem: Optional[float] = None
    ct2: Optional[float] = None
    total: Optional[float] = None
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    faculty: Faculty

class MarksUpdate(BaseModel):
    student_id: str
    class_name: str
    subject: str
    ct1: Optional[float] = None
    insem: Optional[float] = None
    ct2: Optional[float] = None

class StudentWithMarks(BaseModel):
    student: Student
    marks: Optional[Marks] = None

# Helper Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_faculty(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(lambda: AsyncSessionLocal())
):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Query faculty by email with assignments
        result = await session.execute(
            select(FacultyModel).filter(FacultyModel.email == email)
        )
        faculty_obj = result.scalars().first()
        
        if faculty_obj is None:
            raise HTTPException(status_code=401, detail="Faculty not found")
        
        # Convert to Pydantic model with nested assignments
        assignments_list = [
            Assignment(class_name=a.class_name, subject=a.subject)
            for a in faculty_obj.assignments
        ]
        
        faculty = Faculty(
            id=faculty_obj.id,
            name=faculty_obj.name,
            email=faculty_obj.email,
            employee_id=faculty_obj.employee_id,
            assignments=assignments_list
        )
        
        return faculty
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Database session dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Initialize Sample Data (Startup event replacement)
@app.on_event("startup")
async def startup_event():
    # This is now handled by database_setup.sql
    # Tables are created and populated via SQL script
    print("Application started. Ensure database_setup.sql has been executed.")

# API Endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(FacultyModel).filter(FacultyModel.email == request.email)
    )
    faculty_obj = result.scalars().first()
    
    if not faculty_obj:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not pwd_context.verify(request.password, faculty_obj.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": faculty_obj.email})
    
    # Convert to Pydantic model with nested assignments
    assignments_list = [
        Assignment(class_name=a.class_name, subject=a.subject)
        for a in faculty_obj.assignments
    ]
    
    faculty = Faculty(
        id=faculty_obj.id,
        name=faculty_obj.name,
        email=faculty_obj.email,
        employee_id=faculty_obj.employee_id,
        assignments=assignments_list
    )
    
    return LoginResponse(token=token, faculty=faculty)

@app.get("/api/faculty/me", response_model=Faculty)
async def get_faculty_info(current_faculty: Faculty = Depends(get_current_faculty)):
    return current_faculty

@app.get("/api/students", response_model=List[StudentWithMarks])
async def get_students_with_marks(
    class_name: str,
    subject: str,
    current_faculty: Faculty = Depends(get_current_faculty),
    session: AsyncSession = Depends(get_db)
):
    # Check if faculty is assigned to this class-subject combination
    is_assigned = any(
        a.class_name == class_name and a.subject == subject 
        for a in current_faculty.assignments
    )
    
    if not is_assigned:
        raise HTTPException(
            status_code=403, 
            detail="You are not assigned to teach this subject in this class"
        )
    
    # Get students enrolled in this subject for this class
    result = await session.execute(
        select(StudentModel).filter(
            StudentModel.class_name == class_name,
            StudentModel.enrollments.any(StudentEnrollmentModel.subject == subject)
        )
    )
    students_list = result.scalars().all()
    
    # Get marks for these students
    result_list = []
    for student in students_list:
        marks_result = await session.execute(
            select(MarksModel).filter(
                MarksModel.student_id == student.id,
                MarksModel.class_name == class_name,
                MarksModel.subject == subject
            )
        )
        marks_obj = marks_result.scalars().first()
        
        # Convert student to Pydantic model
        enrolled_subjects = [e.subject for e in student.enrollments]
        student_pydantic = Student(
            id=student.id,
            name=student.name,
            student_id=student.student_id,
            class_name=student.class_name,
            enrolled_subjects=enrolled_subjects
        )
        
        # Convert marks to Pydantic model if exists
        marks_pydantic = None
        if marks_obj:
            marks_pydantic = Marks(
                id=marks_obj.id,
                student_id=marks_obj.student_id,
                class_name=marks_obj.class_name,
                subject=marks_obj.subject,
                faculty_email=marks_obj.faculty_email,
                ct1=float(marks_obj.ct1) if marks_obj.ct1 else None,
                insem=float(marks_obj.insem) if marks_obj.insem else None,
                ct2=float(marks_obj.ct2) if marks_obj.ct2 else None,
                total=float(marks_obj.total) if marks_obj.total else None
            )
        
        result_list.append(StudentWithMarks(student=student_pydantic, marks=marks_pydantic))
    
    return result_list

@app.post("/api/marks")
async def save_marks(
    marks_update: MarksUpdate,
    current_faculty: Faculty = Depends(get_current_faculty),
    session: AsyncSession = Depends(get_db)
):
    # Check if faculty is assigned to this class-subject combination
    is_assigned = any(
        a.class_name == marks_update.class_name and a.subject == marks_update.subject 
        for a in current_faculty.assignments
    )
    
    if not is_assigned:
        raise HTTPException(
            status_code=403, 
            detail="You are not assigned to teach this subject in this class"
        )
    
    # Validate marks
    if marks_update.ct1 is not None and (marks_update.ct1 < 0 or marks_update.ct1 > 30):
        raise HTTPException(status_code=400, detail="CT1 marks must be between 0 and 30")
    if marks_update.insem is not None and (marks_update.insem < 0 or marks_update.insem > 30):
        raise HTTPException(status_code=400, detail="Insem marks must be between 0 and 30")
    if marks_update.ct2 is not None and (marks_update.ct2 < 0 or marks_update.ct2 > 70):
        raise HTTPException(status_code=400, detail="CT2 marks must be between 0 and 70")
    
    # Calculate total
    total = 0
    if marks_update.ct1 is not None:
        total += marks_update.ct1
    if marks_update.insem is not None:
        total += marks_update.insem
    if marks_update.ct2 is not None:
        total += marks_update.ct2
    
    # Check if marks already exist
    existing_marks_result = await session.execute(
        select(MarksModel).filter(
            MarksModel.student_id == marks_update.student_id,
            MarksModel.class_name == marks_update.class_name,
            MarksModel.subject == marks_update.subject
        )
    )
    existing_marks = existing_marks_result.scalars().first()
    
    marks_data = {
        "student_id": marks_update.student_id,
        "class_name": marks_update.class_name,
        "subject": marks_update.subject,
        "faculty_email": current_faculty.email,
        "ct1": marks_update.ct1,
        "insem": marks_update.insem,
        "ct2": marks_update.ct2,
        "total": total
    }
    
    if existing_marks:
        # Update existing marks
        existing_marks.ct1 = marks_update.ct1
        existing_marks.insem = marks_update.insem
        existing_marks.ct2 = marks_update.ct2
        existing_marks.total = total
        await session.commit()
        marks_data["id"] = existing_marks.id
    else:
        # Create new marks entry
        marks_data["id"] = str(uuid4())
        new_marks = MarksModel(**marks_data)
        session.add(new_marks)
        await session.commit()
    
    return {"message": "Marks saved successfully", "marks": marks_data}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Import models with different names to avoid conflict with Pydantic models
from db_mysql import Faculty as FacultyModel
from db_mysql import Student as StudentModel
from db_mysql import StudentEnrollment as StudentEnrollmentModel
from db_mysql import Marks as MarksModel