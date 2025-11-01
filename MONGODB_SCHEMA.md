# MongoDB to MySQL Schema Migration Guide

## Visual MongoDB Collections Structure

### Current MongoDB Document Model

```
┌─────────────────────────────────────────────────────────┐
│ Database: grade_management_db                           │
└─────────────────────────────────────────────────────────┘
         │
         ├─── Collection: faculties
         │       ├─ _id: ObjectId
         │       ├─ id: UUID (String)
         │       ├─ name: String
         │       ├─ email: String (UNIQUE)
         │       ├─ employee_id: String
         │       ├─ password: String (hashed)
         │       └─ assignments: Array<Object>
         │           ├─ class_name: String
         │           └─ subject: String
         │
         ├─── Collection: students
         │       ├─ _id: ObjectId
         │       ├─ id: UUID (String)
         │       ├─ name: String
         │       ├─ student_id: String (UNIQUE)
         │       ├─ class_name: String
         │       └─ enrolled_subjects: Array<String>
         │
         └─── Collection: marks
                 ├─ _id: ObjectId
                 ├─ id: UUID (String)
                 ├─ student_id: String (FK → students.id)
                 ├─ class_name: String
                 ├─ subject: String
                 ├─ faculty_email: String (FK → faculties.email)
                 ├─ ct1: Float (0-30)
                 ├─ insem: Float (0-30)
                 ├─ ct2: Float (0-70)
                 └─ total: Float (0-130, computed)
```

---

## Proposed MySQL Schema (Normalized)

### 1. Faculties Table
```sql
CREATE TABLE faculties (
    id VARCHAR(36) PRIMARY KEY,                    -- UUID
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,           -- Indexed, used for login
    employee_id VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,               -- Bcrypt hash
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_employee_id (employee_id)
);
```

**MongoDB → MySQL Mapping:**
- `_id` → Dropped (using `id` as PK)
- `id` → `id` (Primary Key)
- `name` → `name`
- `email` → `email` (UNIQUE, INDEXED)
- `employee_id` → `employee_id` (UNIQUE)
- `password` → `password`
- `assignments` → Separate table `faculty_assignments`

---

### 2. Faculty Assignments Table (NEW - Denormalized from Faculties)
```sql
CREATE TABLE faculty_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id VARCHAR(36) NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    
    FOREIGN KEY (faculty_id) REFERENCES faculties(id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (faculty_id, class_name, subject),
    INDEX idx_faculty_id (faculty_id),
    INDEX idx_class_subject (class_name, subject)
);
```

**Note:** This table flattens the MongoDB embedded array `faculties.assignments[]`

---

### 3. Students Table
```sql
CREATE TABLE students (
    id VARCHAR(36) PRIMARY KEY,                    -- UUID
    name VARCHAR(255) NOT NULL,
    student_id VARCHAR(50) NOT NULL UNIQUE,       -- Indexed
    class_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_student_id (student_id),
    INDEX idx_class_name (class_name)
);
```

**MongoDB → MySQL Mapping:**
- `_id` → Dropped (using `id` as PK)
- `id` → `id` (Primary Key)
- `name` → `name`
- `student_id` → `student_id` (UNIQUE, INDEXED)
- `class_name` → `class_name`
- `enrolled_subjects` → Separate table `student_enrollments`

---

### 4. Student Enrollments Table (NEW - Denormalized from Students)
```sql
CREATE TABLE student_enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(36) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, subject),
    INDEX idx_student_id (student_id),
    INDEX idx_subject (subject)
);
```

**Note:** This table flattens the MongoDB embedded array `students.enrolled_subjects[]`

---

### 5. Marks Table
```sql
CREATE TABLE marks (
    id VARCHAR(36) PRIMARY KEY,                    -- UUID
    student_id VARCHAR(36) NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    faculty_email VARCHAR(255) NOT NULL,
    ct1 DECIMAL(5,2),                             -- 0-30 range
    insem DECIMAL(5,2),                           -- 0-30 range
    ct2 DECIMAL(5,2),                             -- 0-70 range
    total DECIMAL(6,2),                           -- 0-130 range (computed)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_email) REFERENCES faculties(email) ON DELETE RESTRICT,
    UNIQUE KEY unique_marks (student_id, class_name, subject),
    INDEX idx_student_id (student_id),
    INDEX idx_faculty_email (faculty_email),
    INDEX idx_class_subject (class_name, subject),
    INDEX idx_composite (student_id, class_name, subject)
);
```

**MongoDB → MySQL Mapping:**
- `_id` → Dropped (using `id` as PK)
- `id` → `id` (Primary Key)
- `student_id` → `student_id` (FK to students)
- `class_name` → `class_name`
- `subject` → `subject`
- `faculty_email` → `faculty_email` (FK to faculties)
- `ct1` → `ct1` (DECIMAL)
- `insem` → `insem` (DECIMAL)
- `ct2` → `ct2` (DECIMAL)
- `total` → `total` (DECIMAL, computed)

---

## Data Relationships Diagram

```
┌──────────────────────────┐
│      faculties           │
├──────────────────────────┤
│ id (PK, UUID)            │◄─────────────┐
│ email (UNIQUE)           │              │
│ name                     │              │
│ employee_id (UNIQUE)     │              │
│ password                 │              │
└──────────────────────────┘              │
         │                                 │
         │ 1:Many                         │
         │                                 │
         ▼                                 │
┌──────────────────────────┐              │
│ faculty_assignments      │              │
├──────────────────────────┤              │
│ id (PK, AUTO_INCREMENT)  │              │
│ faculty_id (FK) ────────►│              │
│ class_name               │              │
│ subject                  │              │
└──────────────────────────┘              │
                                          │
┌──────────────────────────┐              │
│ marks                    │              │
├──────────────────────────┤              │
│ id (PK, UUID)            │              │
│ student_id (FK) ─────┐   │              │
│ class_name           │   │              │
│ subject              │   │              │
│ faculty_email (FK) ──┼───┼──────────────┘
│ ct1, insem, ct2      │   │
│ total                │   │
└──────────────────────┘   │
                           │
┌──────────────────────────┐│
│ students                 ││
├──────────────────────────┤│
│ id (PK, UUID) ◄──────────┘
│ name                     │
│ student_id (UNIQUE)      │
│ class_name               │
└──────────────────────────┘
         │
         │ 1:Many
         │
         ▼
┌──────────────────────────┐
│ student_enrollments      │
├──────────────────────────┤
│ id (PK, AUTO_INCREMENT)  │
│ student_id (FK)          │
│ subject                  │
└──────────────────────────┘
```

---

## Query Mapping: MongoDB → MySQL

### Query 1: Faculty Login (Find Faculty by Email)

**MongoDB:**
```javascript
db.faculties.find_one({ email: "rajesh@university.edu" })
```

**MySQL:**
```sql
SELECT * FROM faculties WHERE email = 'rajesh@university.edu';
```

**Index:** `idx_email` on `faculties.email`

---

### Query 2: Get Faculty with Assignments

**MongoDB:**
```javascript
db.faculties.find_one({ email: "rajesh@university.edu" })
// Then build assignments from embedded array
```

**MySQL:**
```sql
SELECT 
    f.id, f.name, f.email, f.employee_id,
    fa.class_name, fa.subject
FROM faculties f
LEFT JOIN faculty_assignments fa ON f.id = fa.faculty_id
WHERE f.email = 'rajesh@university.edu';
```

**Note:** Application will need to reconstruct the nested structure from multiple rows

---

### Query 3: Get Students for Class-Subject (with Marks)

**MongoDB:**
```javascript
db.students.find({
    class_name: "Class 10A",
    enrolled_subjects: "Mathematics"
})
// Then join with marks collection
```

**MySQL:**
```sql
SELECT 
    s.id, s.name, s.student_id, s.class_name,
    m.id as marks_id, m.ct1, m.insem, m.ct2, m.total
FROM students s
LEFT JOIN student_enrollments se ON s.id = se.student_id AND se.subject = 'Mathematics'
LEFT JOIN marks m ON s.id = m.student_id 
    AND m.class_name = 'Class 10A' 
    AND m.subject = 'Mathematics'
WHERE s.class_name = 'Class 10A'
AND se.subject = 'Mathematics';
```

**Indexes:** 
- `idx_class_name` on students
- `unique_enrollment` on student_enrollments
- `idx_composite` on marks

---

### Query 4: Save/Update Marks (Upsert)

**MongoDB:**
```javascript
db.marks.update_one(
    {
        student_id: "student_uuid",
        class_name: "Class 10A",
        subject: "Mathematics"
    },
    { $set: { ct1: 25, insem: 28, ct2: 65, total: 118 } },
    { upsert: true }
)
```

**MySQL:**
```sql
INSERT INTO marks (
    id, student_id, class_name, subject, 
    faculty_email, ct1, insem, ct2, total
) VALUES (
    UUID(), 'student_uuid', 'Class 10A', 'Mathematics',
    'rajesh@university.edu', 25, 28, 65, 118
)
ON DUPLICATE KEY UPDATE
    ct1 = 25,
    insem = 28,
    ct2 = 65,
    total = 118,
    updated_at = CURRENT_TIMESTAMP;
```

**Unique Constraint:** `unique_marks` on `(student_id, class_name, subject)`

---

## Data Denormalization vs Normalization

### MongoDB (Document-Oriented - Denormalized)
- Embeds related data within documents
- Fewer queries needed
- Duplicates data for performance

```json
{
  "id": "faculty_uuid",
  "email": "rajesh@university.edu",
  "assignments": [
    { "class_name": "Class 10A", "subject": "Math" },
    { "class_name": "Class 10B", "subject": "Math" }
  ]
}
```

### MySQL (Relational - Normalized)
- Separates related data into tables
- Follows ACID principles
- Uses foreign keys and JOINs
- More queries but less redundancy

```sql
-- Faculty
SELECT * FROM faculties WHERE id = 'faculty_uuid';

-- Their Assignments
SELECT * FROM faculty_assignments 
WHERE faculty_id = 'faculty_uuid';
```

---

## Migration Strategy

### Phase 1: Schema Creation
1. Create all MySQL tables with proper indexes
2. Keep MongoDB running in parallel
3. No data migration yet

### Phase 2: Data Migration
1. Export all MongoDB documents
2. Transform and load into MySQL tables
3. Handle embedded arrays → separate tables
4. Verify data integrity

### Phase 3: Code Migration
1. Replace Motor with SQLAlchemy + asyncmy
2. Update all database queries
3. Handle result transformation (joins vs embedded docs)

### Phase 4: Testing
1. Unit tests for all endpoints
2. Integration tests with MySQL
3. Load testing and performance tuning
4. Compare MongoDB vs MySQL behavior

### Phase 5: Cutover
1. Switch application to MySQL
2. Monitor for issues
3. Keep MongoDB as fallback for 30 days
4. Archive MongoDB data

---

## Index Strategy for MySQL

### Critical Indexes (Performance)
```sql
-- For login queries
CREATE INDEX idx_email ON faculties(email);

-- For student queries
CREATE INDEX idx_class_name ON students(class_name);
CREATE UNIQUE INDEX idx_student_id ON students(student_id);

-- For marks queries (most critical)
CREATE UNIQUE INDEX idx_marks_composite ON marks(student_id, class_name, subject);
CREATE INDEX idx_marks_faculty ON marks(faculty_email);

-- For enrollment queries
CREATE UNIQUE INDEX idx_enrollment_unique ON student_enrollments(student_id, subject);
```

### Query Optimization Tips
1. Use composite indexes for multi-column WHERE clauses
2. Index foreign keys on both sides of relationships
3. For marks table, the composite index covers most queries
4. Monitor slow query log during testing

---

## Sample Data Volume

| Table | Current Records | Estimated Growth |
|-------|-----------------|------------------|
| faculties | 3 | Low (adds per semester) |
| faculty_assignments | 5-6 | Low (updates with faculties) |
| students | 9 | Medium (grows per batch) |
| student_enrollments | ~20-25 | Medium (grows per batch) |
| marks | 0 (dynamic) | High (all students × subjects × semesters) |

---

## Breaking Changes for Application

### API Response Format
MongoDB returns nested objects. MySQL requires JOINs and reconstruction:

**MongoDB Response (current):**
```json
{
  "id": "faculty_uuid",
  "name": "Dr. Rajesh",
  "assignments": [
    { "class_name": "Class 10A", "subject": "Math" }
  ]
}
```

**MySQL Response (needs transformation):**
```json
[
  {
    "id": "faculty_uuid",
    "name": "Dr. Rajesh",
    "class_name": "Class 10A",
    "subject": "Math"
  }
]
// Application must reconstruct nested structure
```

**Solution:** Update response serializers to rebuild nested structures from flat JOIN results.

---

## Testing Checklist

- [ ] All faculties can login with correct credentials
- [ ] Faculties see only their assigned classes/subjects
- [ ] Students list correctly filtered by class and subject
- [ ] Marks save correctly (INSERT and UPDATE cases)
- [ ] Marks validation (0-30, 0-70 ranges) works
- [ ] Total calculation is correct
- [ ] Authentication tokens work correctly
- [ ] CORS headers are correct
- [ ] Performance is acceptable (< 200ms for most queries)
- [ ] Concurrent access doesn't cause issues
- [ ] Data consistency is maintained

