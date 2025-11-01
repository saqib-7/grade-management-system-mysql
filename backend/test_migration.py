"""
Migration Validation Script
Tests database connection, API endpoints, and data integrity
Run: python test_migration.py
"""

import asyncio
import sys
import json
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from httpx import AsyncClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import FastAPI app and models
from server import app
from db_mysql import (
    AsyncSessionLocal,
    Faculty as FacultyModel,
    FacultyAssignment,
    Student as StudentModel,
    StudentEnrollment,
    Marks as MarksModel
)

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Test results
test_results = {
    "database": {},
    "data_integrity": {},
    "api_endpoints": {},
    "summary": {"passed": 0, "failed": 0}
}


def print_header(text):
    """Print a formatted header"""
    print(f"\n{BLUE}{BOLD}{'='*80}{RESET}")
    print(f"{BLUE}{BOLD}{text:^80}{RESET}")
    print(f"{BLUE}{BOLD}{'='*80}{RESET}\n")


def print_test(name, passed, message=""):
    """Print test result"""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"  {status} - {name}")
    if message:
        print(f"       {YELLOW}└─ {message}{RESET}")
    
    if passed:
        test_results["summary"]["passed"] += 1
    else:
        test_results["summary"]["failed"] += 1


async def test_database_connection():
    """Test MySQL database connection"""
    print_header("1. DATABASE CONNECTION TESTS")
    
    try:
        async with AsyncSessionLocal() as session:
            # Test basic connection
            result = await session.execute(select(func.count(FacultyModel.id)))
            count = result.scalar()
            print_test("MySQL Connection", True, f"Successfully connected to database")
            test_results["database"]["connection"] = "PASS"
    except Exception as e:
        print_test("MySQL Connection", False, str(e))
        test_results["database"]["connection"] = f"FAIL: {str(e)}"
        return False
    
    return True


async def test_data_integrity():
    """Test data integrity and sample data"""
    print_header("2. DATA INTEGRITY TESTS")
    
    async with AsyncSessionLocal() as session:
        passed = True
        
        # Test Faculty count
        try:
            result = await session.execute(select(func.count(FacultyModel.id)))
            faculty_count = result.scalar()
            expected_faculty = 3
            if faculty_count == expected_faculty:
                print_test("Faculty Count", True, f"Found {faculty_count} faculty (expected {expected_faculty})")
                test_results["data_integrity"]["faculty_count"] = "PASS"
            else:
                print_test("Faculty Count", False, f"Found {faculty_count}, expected {expected_faculty}")
                test_results["data_integrity"]["faculty_count"] = "FAIL"
                passed = False
        except Exception as e:
            print_test("Faculty Count", False, str(e))
            test_results["data_integrity"]["faculty_count"] = f"FAIL: {str(e)}"
            passed = False
        
        # Test Student count
        try:
            result = await session.execute(select(func.count(StudentModel.id)))
            student_count = result.scalar()
            expected_students = 9
            if student_count == expected_students:
                print_test("Student Count", True, f"Found {student_count} students (expected {expected_students})")
                test_results["data_integrity"]["student_count"] = "PASS"
            else:
                print_test("Student Count", False, f"Found {student_count}, expected {expected_students}")
                test_results["data_integrity"]["student_count"] = "FAIL"
                passed = False
        except Exception as e:
            print_test("Student Count", False, str(e))
            test_results["data_integrity"]["student_count"] = f"FAIL: {str(e)}"
            passed = False
        
        # Test Faculty Assignments
        try:
            result = await session.execute(select(func.count(FacultyAssignment.id)))
            assignment_count = result.scalar()
            expected_assignments = 5
            if assignment_count == expected_assignments:
                print_test("Faculty Assignments", True, f"Found {assignment_count} assignments (expected {expected_assignments})")
                test_results["data_integrity"]["assignments"] = "PASS"
            else:
                print_test("Faculty Assignments", False, f"Found {assignment_count}, expected {expected_assignments}")
                test_results["data_integrity"]["assignments"] = "FAIL"
                passed = False
        except Exception as e:
            print_test("Faculty Assignments", False, str(e))
            test_results["data_integrity"]["assignments"] = f"FAIL: {str(e)}"
            passed = False
        
        # Test Student Enrollments
        try:
            result = await session.execute(select(func.count(StudentEnrollment.id)))
            enrollment_count = result.scalar()
            expected_enrollments = 23
            if enrollment_count == expected_enrollments:
                print_test("Student Enrollments", True, f"Found {enrollment_count} enrollments (expected {expected_enrollments})")
                test_results["data_integrity"]["enrollments"] = "PASS"
            else:
                print_test("Student Enrollments", False, f"Found {enrollment_count}, expected {expected_enrollments}")
                test_results["data_integrity"]["enrollments"] = "FAIL"
                passed = False
        except Exception as e:
            print_test("Student Enrollments", False, str(e))
            test_results["data_integrity"]["enrollments"] = f"FAIL: {str(e)}"
            passed = False
        
        # Test Faculty with valid email
        try:
            result = await session.execute(
                select(FacultyModel).filter(FacultyModel.email == "rajesh@university.edu")
            )
            faculty = result.scalars().first()
            if faculty and faculty.name == "Dr. Rajesh Kumar":
                print_test("Faculty Data Quality", True, f"Found faculty: {faculty.name}")
                test_results["data_integrity"]["faculty_quality"] = "PASS"
            else:
                print_test("Faculty Data Quality", False, "Faculty data mismatch")
                test_results["data_integrity"]["faculty_quality"] = "FAIL"
                passed = False
        except Exception as e:
            print_test("Faculty Data Quality", False, str(e))
            test_results["data_integrity"]["faculty_quality"] = f"FAIL: {str(e)}"
            passed = False
        
        # Test Student with valid data
        try:
            result = await session.execute(
                select(StudentModel).filter(StudentModel.student_id == "10A001")
            )
            student = result.scalars().first()
            if student and student.name == "Aarav Patel":
                print_test("Student Data Quality", True, f"Found student: {student.name}")
                test_results["data_integrity"]["student_quality"] = "PASS"
            else:
                print_test("Student Data Quality", False, "Student data mismatch")
                test_results["data_integrity"]["student_quality"] = "FAIL"
                passed = False
        except Exception as e:
            print_test("Student Data Quality", False, str(e))
            test_results["data_integrity"]["student_quality"] = f"FAIL: {str(e)}"
            passed = False
    
    return passed


async def test_api_endpoints():
    """Test all 5 API endpoints"""
    print_header("3. API ENDPOINT TESTS")
    
    passed = True
    token = None
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        # Test 1: Health Check
        try:
            response = await client.get("/api/health")
            if response.status_code == 200:
                print_test("GET /api/health", True, f"Status: {response.status_code}")
                test_results["api_endpoints"]["health"] = "PASS"
            else:
                print_test("GET /api/health", False, f"Status: {response.status_code}")
                test_results["api_endpoints"]["health"] = "FAIL"
                passed = False
        except Exception as e:
            print_test("GET /api/health", False, str(e))
            test_results["api_endpoints"]["health"] = f"FAIL: {str(e)}"
            passed = False
        
        # Test 2: Login
        try:
            response = await client.post(
                "/api/auth/login",
                json={"email": "rajesh@university.edu", "password": "password123"}
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                faculty_name = data.get("faculty", {}).get("name")
                if token and faculty_name == "Dr. Rajesh Kumar":
                    print_test("POST /api/auth/login", True, f"Logged in: {faculty_name}")
                    test_results["api_endpoints"]["login"] = "PASS"
                else:
                    print_test("POST /api/auth/login", False, "Invalid response structure")
                    test_results["api_endpoints"]["login"] = "FAIL"
                    passed = False
            else:
                print_test("POST /api/auth/login", False, f"Status: {response.status_code}")
                test_results["api_endpoints"]["login"] = "FAIL"
                passed = False
        except Exception as e:
            print_test("POST /api/auth/login", False, str(e))
            test_results["api_endpoints"]["login"] = f"FAIL: {str(e)}"
            passed = False
        
        # Test 3: Get Faculty Me
        if token:
            try:
                response = await client.get(
                    "/api/faculty/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    faculty_email = data.get("email")
                    if faculty_email == "rajesh@university.edu":
                        print_test("GET /api/faculty/me", True, f"Retrieved faculty: {faculty_email}")
                        test_results["api_endpoints"]["faculty_me"] = "PASS"
                    else:
                        print_test("GET /api/faculty/me", False, "Email mismatch")
                        test_results["api_endpoints"]["faculty_me"] = "FAIL"
                        passed = False
                else:
                    print_test("GET /api/faculty/me", False, f"Status: {response.status_code}")
                    test_results["api_endpoints"]["faculty_me"] = "FAIL"
                    passed = False
            except Exception as e:
                print_test("GET /api/faculty/me", False, str(e))
                test_results["api_endpoints"]["faculty_me"] = f"FAIL: {str(e)}"
                passed = False
        else:
            print_test("GET /api/faculty/me", False, "No token from login")
            test_results["api_endpoints"]["faculty_me"] = "FAIL"
            passed = False
        
        # Test 4: Get Students
        if token:
            try:
                response = await client.get(
                    "/api/students?class_name=Class%2010A&subject=Mathematics",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        student_count = len(data)
                        print_test("GET /api/students", True, f"Retrieved {student_count} students")
                        test_results["api_endpoints"]["get_students"] = "PASS"
                    else:
                        print_test("GET /api/students", False, "No students returned or invalid format")
                        test_results["api_endpoints"]["get_students"] = "FAIL"
                        passed = False
                else:
                    print_test("GET /api/students", False, f"Status: {response.status_code}")
                    test_results["api_endpoints"]["get_students"] = "FAIL"
                    passed = False
            except Exception as e:
                print_test("GET /api/students", False, str(e))
                test_results["api_endpoints"]["get_students"] = f"FAIL: {str(e)}"
                passed = False
        else:
            print_test("GET /api/students", False, "No token from login")
            test_results["api_endpoints"]["get_students"] = "FAIL"
            passed = False
        
        # Test 5: Save Marks
        if token:
            try:
                response = await client.post(
                    "/api/marks",
                    json={
                        "student_id": "660e8400-e29b-41d4-a716-446655440000",
                        "class_name": "Class 10A",
                        "subject": "Mathematics",
                        "ct1": 25.0,
                        "insem": 28.0,
                        "ct2": 65.0
                    },
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    if "message" in data and "marks" in data:
                        total = data["marks"].get("total")
                        expected_total = 25.0 + 28.0 + 65.0
                        if total == expected_total:
                            print_test("POST /api/marks", True, f"Marks saved, total: {total}")
                            test_results["api_endpoints"]["save_marks"] = "PASS"
                        else:
                            print_test("POST /api/marks", False, f"Total mismatch: {total} != {expected_total}")
                            test_results["api_endpoints"]["save_marks"] = "FAIL"
                            passed = False
                    else:
                        print_test("POST /api/marks", False, "Invalid response structure")
                        test_results["api_endpoints"]["save_marks"] = "FAIL"
                        passed = False
                else:
                    print_test("POST /api/marks", False, f"Status: {response.status_code}")
                    test_results["api_endpoints"]["save_marks"] = "FAIL"
                    passed = False
            except Exception as e:
                print_test("POST /api/marks", False, str(e))
                test_results["api_endpoints"]["save_marks"] = f"FAIL: {str(e)}"
                passed = False
        else:
            print_test("POST /api/marks", False, "No token from login")
            test_results["api_endpoints"]["save_marks"] = "FAIL"
            passed = False
    
    return passed


async def test_authentication_validation():
    """Test authentication edge cases"""
    print_header("4. AUTHENTICATION & VALIDATION TESTS")
    
    passed = True
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        # Test invalid credentials
        try:
            response = await client.post(
                "/api/auth/login",
                json={"email": "rajesh@university.edu", "password": "wrongpassword"}
            )
            if response.status_code == 401:
                print_test("Invalid Credentials", True, "Correctly rejected invalid password")
                test_results["api_endpoints"]["invalid_auth"] = "PASS"
            else:
                print_test("Invalid Credentials", False, f"Status: {response.status_code}")
                test_results["api_endpoints"]["invalid_auth"] = "FAIL"
                passed = False
        except Exception as e:
            print_test("Invalid Credentials", False, str(e))
            test_results["api_endpoints"]["invalid_auth"] = f"FAIL: {str(e)}"
            passed = False
        
        # Test missing token
        try:
            response = await client.get("/api/faculty/me")
            if response.status_code == 403:
                print_test("Missing Authentication Token", True, "Correctly rejected missing token")
                test_results["api_endpoints"]["missing_token"] = "PASS"
            else:
                print_test("Missing Authentication Token", False, f"Status: {response.status_code}")
                test_results["api_endpoints"]["missing_token"] = "FAIL"
                passed = False
        except Exception as e:
            print_test("Missing Authentication Token", False, str(e))
            test_results["api_endpoints"]["missing_token"] = f"FAIL: {str(e)}"
            passed = False
        
        # Test invalid marks range
        response = await client.post(
            "/api/auth/login",
            json={"email": "rajesh@university.edu", "password": "password123"}
        )
        if response.status_code == 200:
            token = response.json().get("token")
            
            try:
                response = await client.post(
                    "/api/marks",
                    json={
                        "student_id": "660e8400-e29b-41d4-a716-446655440000",
                        "class_name": "Class 10A",
                        "subject": "Mathematics",
                        "ct1": 50.0,  # Invalid: > 30
                        "insem": 28.0,
                        "ct2": 65.0
                    },
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 400:
                    print_test("Marks Validation (CT1 > 30)", True, "Correctly rejected invalid marks")
                    test_results["api_endpoints"]["marks_validation"] = "PASS"
                else:
                    print_test("Marks Validation (CT1 > 30)", False, f"Status: {response.status_code}")
                    test_results["api_endpoints"]["marks_validation"] = "FAIL"
                    passed = False
            except Exception as e:
                print_test("Marks Validation (CT1 > 30)", False, str(e))
                test_results["api_endpoints"]["marks_validation"] = f"FAIL: {str(e)}"
                passed = False
    
    return passed


async def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total_tests = test_results["summary"]["passed"] + test_results["summary"]["failed"]
    passed = test_results["summary"]["passed"]
    failed = test_results["summary"]["failed"]
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"{BOLD}Total Tests: {total_tests}{RESET}")
    print(f"{GREEN}{BOLD}Passed: {passed}{RESET}")
    print(f"{RED}{BOLD}Failed: {failed}{RESET}")
    print(f"{YELLOW}{BOLD}Pass Rate: {pass_rate:.1f}%{RESET}\n")
    
    # Print detailed results
    print(f"{BOLD}Detailed Results:{RESET}")
    print(json.dumps(test_results, indent=2))
    
    if failed == 0:
        print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED - MIGRATION SUCCESSFUL!{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{BOLD}✗ SOME TESTS FAILED - REVIEW ABOVE{RESET}\n")
        return 1


async def main():
    """Run all tests"""
    print(f"{BOLD}{BLUE}Grade Management System - Migration Validation{RESET}\n")
    
    # Test database connection first
    if not await test_database_connection():
        print(f"\n{RED}{BOLD}Cannot proceed - database connection failed{RESET}\n")
        return 1
    
    # Run all other tests
    await test_data_integrity()
    await test_api_endpoints()
    await test_authentication_validation()
    
    # Print summary
    return await print_summary()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


