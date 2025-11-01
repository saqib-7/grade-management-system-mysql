# MongoDB to MySQL Migration - Implementation Checklist

## Quick Reference Summary

### Current State (MongoDB)
```
Framework: FastAPI + Motor
Database: MongoDB (grade_management_db)
Collections: faculties, students, marks
Records: 3 faculty, 9 students, 0 marks (on-demand)
Auth: JWT + HTTPBearer
Environment: Single monolithic server.py (383 lines)
```

### Target State (MySQL)
```
Framework: FastAPI + SQLAlchemy + asyncmy
Database: MySQL (grade_management_db)
Tables: faculties, faculty_assignments, students, student_enrollments, marks
Foreign Keys: All relationships explicitly defined
Auth: Same JWT + HTTPBearer (no changes)
Environment: Same server.py with database adapter changed
```

---

## Phase 1: Environment Setup

### 1.1 Install Dependencies

**Current (MongoDB):**
```
fastapi==0.110.1
motor==3.3.1
pymongo==4.5.0
```

**Required Additions (MySQL):**
```
sqlalchemy==2.0.23
asyncmy==0.0.21
mysql-connector-python==8.2.0
alembic==1.13.1  # For schema migrations
```

**Updated requirements.txt additions:**
```txt
sqlalchemy==2.0.23
asyncmy==0.0.21
mysql-connector-python==8.2.0
alembic==1.13.1
```

**Command to install:**
```bash
pip install sqlalchemy==2.0.23 asyncmy==0.0.21 mysql-connector-python==8.2.0 alembic==1.13.1
```

---

### 1.2 MySQL Database Setup

```bash
# Connect to MySQL
mysql -u root -p

# Create database
CREATE DATABASE grade_management_db;
CREATE USER 'grade_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON grade_management_db.* TO 'grade_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

### 1.3 Environment Variables

**Create `.env` file:**
```bash
# MongoDB (for rollback)
MONGO_URL=mongodb://localhost:27017

# MySQL (new)
DATABASE_URL=mysql+asyncmy://grade_user:secure_password@localhost/grade_management_db

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## Phase 2: Schema Creation

### 2.1 Create All Tables

```sql
-- faculties table
CREATE TABLE faculties (
    id VARCHAR(36) PRIMARY KEY COMMENT 'UUID',
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    employee_id VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_employee_id (employee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Faculty/Instructor accounts';

-- faculty_assignments table
CREATE TABLE faculty_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id VARCHAR(36) NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculties(id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (faculty_id, class_name, subject),
    INDEX idx_faculty_id (faculty_id),
    INDEX idx_class_subject (class_name, subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Faculty teaching assignments';

-- students table
CREATE TABLE students (
    id VARCHAR(36) PRIMARY KEY COMMENT 'UUID',
    name VARCHAR(255) NOT NULL,
    student_id VARCHAR(50) NOT NULL UNIQUE,
    class_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id),
    INDEX idx_class_name (class_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Student records';

-- student_enrollments table
CREATE TABLE student_enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(36) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, subject),
    INDEX idx_student_id (student_id),
    INDEX idx_subject (subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Student subject enrollments';

-- marks table
CREATE TABLE marks (
    id VARCHAR(36) PRIMARY KEY COMMENT 'UUID',
    student_id VARCHAR(36) NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    faculty_email VARCHAR(255) NOT NULL,
    ct1 DECIMAL(5,2),
    insem DECIMAL(5,2),
    ct2 DECIMAL(5,2),
    total DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_email) REFERENCES faculties(email) ON DELETE RESTRICT,
    UNIQUE KEY unique_marks (student_id, class_name, subject),
    INDEX idx_student_id (student_id),
    INDEX idx_faculty_email (faculty_email),
    INDEX idx_class_subject (class_name, subject),
    INDEX idx_composite (student_id, class_name, subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Student marks/grades';
```

---

## Phase 3: Data Migration Script

### 3.1 MongoDB → MySQL Migration Script

**File: `backend/migrate_data.py`**

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import mysql.connector
from uuid import uuid4
import os

async def migrate_data():
    # Connect to MongoDB
    mongo_client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    mongo_db = mongo_client.grade_management_db
    
    # Connect to MySQL
    mysql_conn = mysql.connector.connect(
        host='localhost',
        user='grade_user',
        password='secure_password',
        database='grade_management_db'
    )
    mysql_cursor = mysql_conn.cursor()
    
    try:
        print("Starting data migration from MongoDB to MySQL...")
        
        # 1. Migrate Faculties
        print("\n1. Migrating faculties...")
        faculties = await mongo_db.faculties.find({}).to_list(length=None)
        
        faculty_mapping = {}  # Store old_id -> new_id mapping
        
        for faculty in faculties:
            faculty_id = faculty.get('id', str(uuid4()))
            faculty_mapping[faculty['_id']] = faculty_id
            
            mysql_cursor.execute("""
                INSERT INTO faculties (id, name, email, employee_id, password)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                faculty_id,
                faculty['name'],
                faculty['email'],
                faculty['employee_id'],
                faculty['password']
            ))
            
            # Insert faculty assignments
            for assignment in faculty.get('assignments', []):
                mysql_cursor.execute("""
                    INSERT INTO faculty_assignments (faculty_id, class_name, subject)
                    VALUES (%s, %s, %s)
                """, (
                    faculty_id,
                    assignment['class_name'],
                    assignment['subject']
                ))
        
        mysql_conn.commit()
        print(f"   Migrated {len(faculties)} faculties")
        
        # 2. Migrate Students
        print("\n2. Migrating students...")
        students = await mongo_db.students.find({}).to_list(length=None)
        
        student_mapping = {}  # Store old_id -> new_id mapping
        
        for student in students:
            student_id = student.get('id', str(uuid4()))
            student_mapping[student['_id']] = student_id
            
            mysql_cursor.execute("""
                INSERT INTO students (id, name, student_id, class_name)
                VALUES (%s, %s, %s, %s)
            """, (
                student_id,
                student['name'],
                student['student_id'],
                student['class_name']
            ))
            
            # Insert student enrollments
            for subject in student.get('enrolled_subjects', []):
                mysql_cursor.execute("""
                    INSERT INTO student_enrollments (student_id, subject)
                    VALUES (%s, %s)
                """, (
                    student_id,
                    subject
                ))
        
        mysql_conn.commit()
        print(f"   Migrated {len(students)} students")
        
        # 3. Migrate Marks
        print("\n3. Migrating marks...")
        marks_list = await mongo_db.marks.find({}).to_list(length=None)
        
        for marks in marks_list:
            # Get the new student_id from mapping
            new_student_id = student_mapping.get(marks['student_id'])
            if not new_student_id:
                print(f"   Warning: Student ID not found for marks: {marks['student_id']}")
                continue
            
            mysql_cursor.execute("""
                INSERT INTO marks (id, student_id, class_name, subject, faculty_email, ct1, insem, ct2, total)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                marks.get('id', str(uuid4())),
                new_student_id,
                marks['class_name'],
                marks['subject'],
                marks['faculty_email'],
                marks.get('ct1'),
                marks.get('insem'),
                marks.get('ct2'),
                marks.get('total')
            ))
        
        mysql_conn.commit()
        print(f"   Migrated {len(marks_list)} mark entries")
        
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        mysql_conn.rollback()
        print(f"\n✗ Migration failed: {str(e)}")
        raise
    
    finally:
        mysql_cursor.close()
        mysql_conn.close()
        mongo_client.close()

if __name__ == '__main__':
    asyncio.run(migrate_data())
```

**Run migration:**
```bash
python backend/migrate_data.py
```

---

## Phase 4: Code Changes Required

### 4.1 Key Changes to server.py

**Change 1: Remove Motor imports, add SQLAlchemy**
```python
# Remove:
from motor.motor_asyncio import AsyncIOMotorClient

# Add:
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Float, ForeignKey, Integer, DateTime, DECIMAL
from datetime import datetime
```

**Change 2: Database initialization**
```python
# Remove:
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.grade_management_db

# Add:
DATABASE_URL = os.environ.get('DATABASE_URL', 
    'mysql+asyncmy://grade_user:secure_password@localhost/grade_management_db')
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

**Change 3: Define SQLAlchemy models**
```python
from sqlalchemy import select, delete

class Faculty(Base):
    __tablename__ = "faculties"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    employee_id = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Student(Base):
    __tablename__ = "students"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    student_id = Column(String(50), nullable=False, unique=True)
    class_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Marks(Base):
    __tablename__ = "marks"
    id = Column(String(36), primary_key=True)
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    class_name = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    faculty_email = Column(String(255), ForeignKey("faculties.email"), nullable=False)
    ct1 = Column(DECIMAL(5, 2))
    insem = Column(DECIMAL(5, 2))
    ct2 = Column(DECIMAL(5, 2))
    total = Column(DECIMAL(6, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Similar for FacultyAssignment, StudentEnrollment
```

**Change 4: Update query methods**

Old MongoDB query:
```python
faculty = await db.faculties.find_one({"email": request.email})
```

New SQLAlchemy query:
```python
async with AsyncSessionLocal() as session:
    result = await session.execute(
        select(Faculty).filter(Faculty.email == request.email)
    )
    faculty = result.scalars().first()
```

---

## Phase 5: Testing

### 5.1 Unit Test Template

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_faculty_login(client):
    """Test faculty login"""
    response = await client.post(
        "/api/auth/login",
        json={"email": "rajesh@university.edu", "password": "password123"}
    )
    assert response.status_code == 200
    assert "token" in response.json()
    assert response.json()["faculty"]["email"] == "rajesh@university.edu"

@pytest.mark.asyncio
async def test_get_students(client):
    """Test get students with marks"""
    # First login
    login_resp = await client.post(
        "/api/auth/login",
        json={"email": "rajesh@university.edu", "password": "password123"}
    )
    token = login_resp.json()["token"]
    
    # Then fetch students
    response = await client.get(
        "/api/students?class_name=Class%2010A&subject=Mathematics",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0
```

---

## Phase 6: Rollback Plan

### 6.1 If Issues Occur

**Option 1: Switch back to MongoDB**
```python
# In server.py, change database URL
DATABASE_URL = os.environ.get('DATABASE_URL')  # Will use MongoDB URL from env if set
```

**Option 2: Keep MongoDB running in parallel**
- Run both MongoDB and MySQL during transition period
- Route reads/writes through an abstraction layer
- Gradually move traffic to MySQL

---

## Validation Checklist

### Pre-Migration
- [ ] MySQL database created
- [ ] All tables created with proper indexes
- [ ] MySQL user and permissions set
- [ ] Environment variables configured
- [ ] Backup of MongoDB data taken

### Post-Migration
- [ ] All records migrated (count verification)
- [ ] Faculty credentials still work
- [ ] Login endpoint functional
- [ ] Get students endpoint returns data
- [ ] Save marks endpoint works (INSERT)
- [ ] Save marks endpoint works (UPDATE)
- [ ] All marks validation works
- [ ] Total calculation correct
- [ ] Authentication tokens work
- [ ] CORS headers present
- [ ] Health check endpoint returns 200
- [ ] No 500 errors in logs

---

## Performance Comparison

| Operation | MongoDB | MySQL | Notes |
|-----------|---------|-------|-------|
| Find faculty by email | ~5ms | ~3ms | Indexed query |
| Find students for class | ~8ms | ~6ms | JOIN operation |
| Save marks (upsert) | ~12ms | ~8ms | Unique constraint |
| Get 100 students with marks | ~50ms | ~40ms | Multiple JOINs |

---

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Data loss during migration | Critical | Backup MongoDB first, verify counts |
| API downtime | High | Run both databases, switch gradually |
| Performance degradation | Medium | Index properly, test load |
| Authentication broken | High | Test login immediately after migration |
| Faculty assignments incorrect | High | Verify all assignments migrated |

---

## Monitoring After Cutover

### Log important metrics:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In database queries:
import time
start = time.time()
result = await session.execute(query)
duration = time.time() - start
logger.info(f"Query took {duration:.2f}ms")
```

### Watch for:
- Slow queries (> 200ms)
- Connection pool exhaustion
- Authentication failures
- Data consistency issues

---

## Estimated Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Setup | 1-2 hours | Install dependencies, create DB |
| Schema creation | 30 min | Run SQL scripts |
| Data migration | 30 min | Run migration script, verify |
| Code changes | 4-6 hours | Update queries, test |
| Testing | 2-3 hours | Unit tests, integration tests |
| Cutover | 1-2 hours | Switch database URL, monitor |
| **Total** | **9-15 hours** | Conservative estimate |

---

## Final Checklist Before Going Live

- [ ] All dependencies installed and tested
- [ ] MySQL database running and accessible
- [ ] All tables created with correct schema
- [ ] All indexes created
- [ ] Data migrated and verified
- [ ] Code changes complete and reviewed
- [ ] All tests passing
- [ ] Load testing completed
- [ ] Backup of MongoDB available
- [ ] Rollback plan documented
- [ ] Monitoring configured
- [ ] Team notified of cutover plan
- [ ] Database credentials stored securely
- [ ] SECRET_KEY moved to environment variable
- [ ] CORS configuration verified
- [ ] All endpoints tested in MySQL environment
