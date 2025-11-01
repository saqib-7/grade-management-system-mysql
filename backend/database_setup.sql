-- Grade Management Database Setup for MySQL
-- This script creates all tables and populates sample data

-- Create faculties table
CREATE TABLE IF NOT EXISTS faculties (
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

-- Create faculty_assignments table
CREATE TABLE IF NOT EXISTS faculty_assignments (
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

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    id VARCHAR(36) PRIMARY KEY COMMENT 'UUID',
    name VARCHAR(255) NOT NULL,
    student_id VARCHAR(50) NOT NULL UNIQUE,
    class_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id),
    INDEX idx_class_name (class_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Student records';

-- Create student_enrollments table
CREATE TABLE IF NOT EXISTS student_enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(36) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, subject),
    INDEX idx_student_id (student_id),
    INDEX idx_subject (subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Student subject enrollments';

-- Create marks table
CREATE TABLE IF NOT EXISTS marks (
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

-- Sample Data: Faculty
INSERT INTO faculties (id, name, email, employee_id, password) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Dr. Rajesh Kumar', 'rajesh@university.edu', 'FAC001', '$2b$12$iKkBAG7M0aCmD6vQiJGBW.mPvgH3p0j6rEzlJwHngYI5oMGLgnZKq'),
('550e8400-e29b-41d4-a716-446655440001', 'Dr. Priya Sharma', 'priya@university.edu', 'FAC002', '$2b$12$iKkBAG7M0aCmD6vQiJGBW.mPvgH3p0j6rEzlJwHngYI5oMGLgnZKq'),
('550e8400-e29b-41d4-a716-446655440002', 'Prof. Amit Verma', 'amit@university.edu', 'FAC003', '$2b$12$iKkBAG7M0aCmD6vQiJGBW.mPvgH3p0j6rEzlJwHngYI5oMGLgnZKq');

-- Sample Data: Faculty Assignments
INSERT INTO faculty_assignments (faculty_id, class_name, subject) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Class 10A', 'Mathematics'),
('550e8400-e29b-41d4-a716-446655440000', 'Class 10B', 'Mathematics'),
('550e8400-e29b-41d4-a716-446655440001', 'Class 10A', 'Physics'),
('550e8400-e29b-41d4-a716-446655440002', 'Class 10B', 'Chemistry'),
('550e8400-e29b-41d4-a716-446655440002', 'Class 10A', 'Chemistry');

-- Sample Data: Students for Class 10A
INSERT INTO students (id, name, student_id, class_name) VALUES
('660e8400-e29b-41d4-a716-446655440000', 'Aarav Patel', '10A001', 'Class 10A'),
('660e8400-e29b-41d4-a716-446655440001', 'Ananya Singh', '10A002', 'Class 10A'),
('660e8400-e29b-41d4-a716-446655440002', 'Rohan Gupta', '10A003', 'Class 10A'),
('660e8400-e29b-41d4-a716-446655440003', 'Diya Reddy', '10A004', 'Class 10A'),
('660e8400-e29b-41d4-a716-446655440004', 'Arjun Mehta', '10A005', 'Class 10A');

-- Sample Data: Students for Class 10B
INSERT INTO students (id, name, student_id, class_name) VALUES
('660e8400-e29b-41d4-a716-446655440005', 'Kavya Joshi', '10B001', 'Class 10B'),
('660e8400-e29b-41d4-a716-446655440006', 'Vihaan Desai', '10B002', 'Class 10B'),
('660e8400-e29b-41d4-a716-446655440007', 'Ishaan Kapoor', '10B003', 'Class 10B'),
('660e8400-e29b-41d4-a716-446655440008', 'Saanvi Nair', '10B004', 'Class 10B');

-- Sample Data: Student Enrollments (Class 10A)
INSERT INTO student_enrollments (student_id, subject) VALUES
('660e8400-e29b-41d4-a716-446655440000', 'Mathematics'),
('660e8400-e29b-41d4-a716-446655440000', 'Physics'),
('660e8400-e29b-41d4-a716-446655440000', 'Chemistry'),
('660e8400-e29b-41d4-a716-446655440001', 'Mathematics'),
('660e8400-e29b-41d4-a716-446655440001', 'Physics'),
('660e8400-e29b-41d4-a716-446655440001', 'Chemistry'),
('660e8400-e29b-41d4-a716-446655440002', 'Mathematics'),
('660e8400-e29b-41d4-a716-446655440002', 'Physics'),
('660e8400-e29b-41d4-a716-446655440002', 'Chemistry'),
('660e8400-e29b-41d4-a716-446655440003', 'Mathematics'),
('660e8400-e29b-41d4-a716-446655440003', 'Physics'),
('660e8400-e29b-41d4-a716-446655440003', 'Chemistry'),
('660e8400-e29b-41d4-a716-446655440004', 'Mathematics'),
('660e8400-e29b-41d4-a716-446655440004', 'Physics'),
('660e8400-e29b-41d4-a716-446655440004', 'Chemistry');

-- Sample Data: Student Enrollments (Class 10B)
INSERT INTO student_enrollments (student_id, subject) VALUES
('660e8400-e29b-41d4-a716-446655440005', 'Mathematics'),
('660e8400-e29b-41d4-a716-446655440005', 'Chemistry'),
('660e8400-e29b-41d4-a716-446655440006', 'Mathematics'),
('660e8400-e29b-41d4-a716-446655440006', 'Chemistry'),
('660e8400-e29b-41d4-a716-446655440007', 'Mathematics'),
('660e8400-e29b-41d4-a716-446655440007', 'Chemistry'),
('660e8400-e29b-41d4-a716-446655440008', 'Mathematics'),
('660e8400-e29b-41d4-a716-446655440008', 'Chemistry');


