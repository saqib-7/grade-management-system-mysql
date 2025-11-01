# Grade Management System - MongoDB to MySQL Migration Analysis

## Executive Summary
This is a **FastAPI-based** grade management system with a React frontend. The application manages faculty assignments, student enrollments, and grade tracking across multiple classes and subjects. Currently uses MongoDB as the database, requiring migration to MySQL.

---

## 1. Backend Framework: FastAPI

### Framework Details
- **Framework**: FastAPI 0.110.1
- **Web Server**: Uvicorn 0.25.0
- **Language**: Python
- **API Type**: RESTful
- **Authentication**: JWT + HTTPBearer

### Key Dependencies
- **fastapi==0.110.1** - Web framework
- **motor==3.3.1** - Async MongoDB driver
- **pydantic==2.12.0** - Data validation
- **python-jose==3.5.0** - JWT handling
- **passlib==1.7.4** - Password hashing
- **bcrypt==4.1.3** - Password encryption
- **uvicorn==0.25.0** - ASGI server

### Architecture Characteristics
- Asynchronous request handling
- CORS enabled for all origins
- Bearer token authentication
- Pydantic models for request/response validation
- Database interaction via Motor (async MongoDB driver)

---

## 2. Files Interacting with MongoDB

### Backend Files
- **`backend/server.py`** - **ONLY backend file** (Single monolithic file)
  - All database operations
  - All API endpoints
  - Authentication logic
  - Sample data initialization

### MongoDB Collections Referenced
1. `db.faculties` - Faculty/instructor accounts
2. `db.students` - Student records
3. `db.marks` - Grade records

### Direct MongoDB Operations in server.py
- **Lines 26-27**: MongoDB client initialization
- **Line 114**: `db.faculties.find_one()` - Faculty lookup by email
- **Line 128**: `db.faculties.find_one()` - Startup check
- **Line 170**: `db.faculties.insert_many()` - Sample data
- **Line 242**: `db.students.insert_many()` - Sample data
- **Lines 293-296**: `db.students.find()` - Query students by class and subject
- **Lines 302-306**: `db.marks.find_one()` - Query marks
- **Lines 350-354**: `db.marks.find_one()` - Check existing marks
- **Lines 369-377**: `db.marks.update_one()` and `db.marks.insert_one()` - Upsert marks

---

## 3. Data Models and Schemas

### Pydantic Models (lines 39-96)

#### 1. **Assignment** (Embedded Model)
```python
class Assignment(BaseModel):
    class_name: str          # e.g., "Class 10A"
    subject: str             # e.g., "Mathematics"
```

#### 2. **Faculty** (lines 44-52)
```python
class Faculty(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))  # UUID
    name: str                # Faculty name
    email: str               # Email (used as login)
    employee_id: str         # Employee ID
    assignments: List[Assignment]  # List of class-subject pairs
```

#### 3. **Student** (lines 54-62)
```python
class Student(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))  # UUID
    name: str                # Student name
    student_id: str          # Student ID (e.g., "10A001")
    class_name: str          # Class (e.g., "Class 10A")
    enrolled_subjects: List[str]  # Subjects enrolled in
```

#### 4. **Marks** (lines 64-76)
```python
class Marks(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))  # UUID
    student_id: str          # Reference to student
    class_name: str          # Class name
    subject: str             # Subject name
    faculty_email: str       # Faculty who entered marks
    ct1: Optional[float]     # Class Test 1 (0-30)
    insem: Optional[float]   # In-semester (0-30)
    ct2: Optional[float]     # Class Test 2 (0-70)
    total: Optional[float]   # Total (0-130)
```

#### 5. **LoginRequest** (lines 78-80)
```python
class LoginRequest(BaseModel):
    email: str
    password: str
```

#### 6. **LoginResponse** (lines 82-84)
```python
class LoginResponse(BaseModel):
    token: str
    faculty: Faculty
```

#### 7. **MarksUpdate** (lines 86-92)
```python
class MarksUpdate(BaseModel):
    student_id: str
    class_name: str
    subject: str
    ct1: Optional[float]
    insem: Optional[float]
    ct2: Optional[float]
```

#### 8. **StudentWithMarks** (lines 94-96)
```python
class StudentWithMarks(BaseModel):
    student: Student
    marks: Optional[Marks] = None
```

---

## 4. Current MongoDB Database Structure

### MongoDB Database Name
- `grade_management_db`

### Collection 1: `faculties`
**Sample Document:**
```json
{
  "_id": ObjectId(...),
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Dr. Rajesh Kumar",
  "email": "rajesh@university.edu",
  "employee_id": "FAC001",
  "password": "$2b$12$[bcrypt_hash]",
  "assignments": [
    {
      "class_name": "Class 10A",
      "subject": "Mathematics"
    },
    {
      "class_name": "Class 10B",
      "subject": "Mathematics"
    }
  ]
}
```

**Fields:**
- `_id`: MongoDB ObjectId (auto-generated)
- `id`: UUID string (application-level ID)
- `name`: string
- `email`: string (unique, used for login)
- `employee_id`: string
- `password`: string (bcrypt hashed)
- `assignments`: array of objects
  - `class_name`: string
  - `subject`: string

**Current Sample Data:** 3 faculty members

### Collection 2: `students`
**Sample Document:**
```json
{
  "_id": ObjectId(...),
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Aarav Patel",
  "student_id": "10A001",
  "class_name": "Class 10A",
  "enrolled_subjects": [
    "Mathematics",
    "Physics",
    "Chemistry"
  ]
}
```

**Fields:**
- `_id`: MongoDB ObjectId (auto-generated)
- `id`: UUID string (application-level ID)
- `name`: string
- `student_id`: string (unique student ID)
- `class_name`: string
- `enrolled_subjects`: array of strings

**Current Sample Data:**
- Class 10A: 5 students
- Class 10B: 4 students
- Total: 9 students

### Collection 3: `marks`
**Sample Document:**
```json
{
  "_id": ObjectId(...),
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "class_name": "Class 10A",
  "subject": "Mathematics",
  "faculty_email": "rajesh@university.edu",
  "ct1": 25.5,
  "insem": 28.0,
  "ct2": 65.0,
  "total": 118.5
}
```

**Fields:**
- `_id`: MongoDB ObjectId (auto-generated)
- `id`: UUID string (application-level ID)
- `student_id`: string (FK to students.id)
- `class_name`: string
- `subject`: string
- `faculty_email`: string (FK to faculties.email)
- `ct1`: float or null (0-30 range)
- `insem`: float or null (0-30 range)
- `ct2`: float or null (0-70 range)
- `total`: float or null (auto-calculated, 0-130 range)

**Indexes Needed:**
- Composite index: `(student_id, class_name, subject)` - for upsert operations
- Index on `student_id` - for lookups
- Index on `faculty_email` - for faculty queries
- Index on `class_name` - for filtering

**Current Sample Data:** Empty (populated on first run)

---

## 5. API Endpoints

### Authentication Endpoints

#### 1. **POST /api/auth/login**
**Purpose**: Faculty login endpoint
**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```
**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "faculty": {
    "id": "uuid",
    "name": "string",
    "email": "string",
    "employee_id": "string",
    "assignments": [
      {
        "class_name": "string",
        "subject": "string"
      }
    ]
  }
}
```
**Error Responses:**
- 401: Invalid email or password
**Line**: 251-268

---

### Faculty Endpoints

#### 2. **GET /api/faculty/me**
**Purpose**: Get current logged-in faculty information
**Authentication**: Bearer Token (required)
**Response (200 OK):**
```json
{
  "id": "uuid",
  "name": "string",
  "email": "string",
  "employee_id": "string",
  "assignments": [
    {
      "class_name": "string",
      "subject": "string"
    }
  ]
}
```
**Error Responses:**
- 401: Invalid/expired token
**Line**: 270-272

---

### Student Endpoints

#### 3. **GET /api/students**
**Purpose**: Get students with marks for a specific class-subject combination
**Authentication**: Bearer Token (required)
**Query Parameters:**
- `class_name`: string (required)
- `subject`: string (required)

**Response (200 OK):**
```json
[
  {
    "student": {
      "id": "uuid",
      "name": "string",
      "student_id": "string",
      "class_name": "string",
      "enrolled_subjects": ["string"]
    },
    "marks": {
      "id": "uuid",
      "student_id": "uuid",
      "class_name": "string",
      "subject": "string",
      "faculty_email": "string",
      "ct1": 25.5,
      "insem": 28.0,
      "ct2": 65.0,
      "total": 118.5
    } // or null if no marks
  }
]
```
**Error Responses:**
- 401: Invalid/expired token
- 403: Faculty not assigned to this class-subject combination
**Line**: 274-313

---

### Grades/Marks Endpoints

#### 4. **POST /api/marks**
**Purpose**: Save or update marks for a student
**Authentication**: Bearer Token (required)
**Request Body:**
```json
{
  "student_id": "uuid",
  "class_name": "string",
  "subject": "string",
  "ct1": null or float,
  "insem": null or float,
  "ct2": null or float
}
```
**Response (200 OK):**
```json
{
  "message": "Marks saved successfully",
  "marks": {
    "id": "uuid",
    "student_id": "uuid",
    "class_name": "string",
    "subject": "string",
    "faculty_email": "string",
    "ct1": 25.5,
    "insem": 28.0,
    "ct2": 65.0,
    "total": 118.5
  }
}
```
**Validation:**
- CT1: 0-30 range
- Insem: 0-30 range
- CT2: 0-70 range
- Total: Auto-calculated sum

**Error Responses:**
- 400: Invalid marks range
- 401: Invalid/expired token
- 403: Faculty not assigned to this class-subject combination
**Line**: 315-379

---

### Health Check Endpoint

#### 5. **GET /api/health**
**Purpose**: Application health check
**Response (200 OK):**
```json
{
  "status": "healthy"
}
```
**Line**: 381-383

---

## 6. Authentication & Security

### JWT Configuration (lines 32-37)
```python
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
```

### Password Hashing (line 30)
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

### Token Creation (lines 99-104)
- Creates JWT with faculty email as subject
- 24-hour expiration
- HS256 algorithm

### Authentication Dependency (lines 106-122)
- Validates JWT token
- Checks token expiration
- Verifies faculty exists in database
- Raises 401 errors for invalid/expired tokens

---

## 7. Frontend-Backend Integration

### API Base URL (App.js:4)
```javascript
const API_URL = process.env.REACT_APP_BACKEND_URL || '';
```

### Frontend API Calls
1. **POST /api/auth/login** - Faculty authentication
2. **GET /api/students** - Fetch students and marks
3. **POST /api/marks** - Save/update marks
4. **GET /api/health** - Health check (implicit)

### Authentication Flow
- Token stored in localStorage
- Token included in Authorization header: `Bearer {token}`
- Session persists across page reloads
- Logout clears token and faculty data

---

## 8. Migration Considerations

### Key Points for MySQL Migration

1. **ID Strategy**
   - Current: UUID strings (application-generated)
   - MySQL Approach: Keep UUID or switch to AUTO_INCREMENT
   - Recommendation: Keep UUID for consistency

2. **Unique Constraints**
   - `faculties.email` must be UNIQUE
   - `students.student_id` should be UNIQUE
   - Composite index on `marks(student_id, class_name, subject)`

3. **Relationships**
   - Faculties → Assignments (embedded array → separate table)
   - Students → enrolled_subjects (embedded array → separate table)
   - Marks → Students (FK relationship)
   - Marks → Faculties (via faculty_email FK)

4. **Data Types**
   - Strings: VARCHAR
   - Floats: DECIMAL(5,2) for marks
   - Passwords: VARCHAR (already hashed)
   - Arrays: Separate junction tables

5. **No Current Indexes**
   - MongoDB doesn't have explicit indexes in code
   - MySQL will need proper indexing strategy

6. **Async Operations**
   - Current: Motor (async MongoDB driver)
   - Required for MySQL: `aiomysql` or `asyncmy`
   - Alternative: `SQLAlchemy` with async support

---

## 9. Summary Statistics

| Metric | Value |
|--------|-------|
| Total Backend Files | 1 |
| Total MongoDB Collections | 3 |
| Total API Endpoints | 5 |
| Sample Faculty Records | 3 |
| Sample Student Records | 9 |
| Sample Mark Records | 0 (generated on demand) |
| Frontend Components | React (SPA) |
| Authentication Type | JWT + Bearer |
| Code Language | Python (Backend), JavaScript (Frontend) |

---

## 10. Configuration

### Environment Variables Used
```
MONGO_URL=mongodb://localhost:27017
```

### Default Values
- MongoDB URL: `mongodb://localhost:27017`
- Database: `grade_management_db`
- JWT Secret: `your-secret-key-change-in-production` (⚠️ Should be environment variable)
- JWT Algorithm: HS256
- Token Expiration: 1440 minutes (24 hours)

---

## Next Steps for Migration

1. Design MySQL schema with proper normalization
2. Replace Motor with MySQL async driver (SQLAlchemy + asyncmy)
3. Update database connection strings
4. Create migration scripts for sample data
5. Update environment configuration
6. Test all API endpoints with MySQL backend
7. Performance testing and indexing optimization
