# Grade Management System

A modern, full-stack grade management application for educational institutions. Faculty members can securely log in, view their assigned classes, and enter student grades with real-time validation and persistence.

**Recently migrated from MongoDB to MySQL for improved data integrity and relational querying.**

---

## 📋 Table of Contents

- [Technology Stack](#technology-stack)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Default Login Credentials](#default-login-credentials)
- [Frontend Usage](#frontend-usage)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🛠 Technology Stack

### Backend
- **Framework:** FastAPI 0.110.1 (Python)
- **Database:** MySQL 8.0+ (async via SQLAlchemy 2.0.23)
- **Async Driver:** asyncmy 0.2.9
- **Authentication:** JWT (PyJWT) + HTTPBearer
- **Password Hashing:** Bcrypt
- **Web Server:** Uvicorn 0.25.0

### Frontend
- **Framework:** React 19.0.0
- **Build Tool:** Create React App with Craco
- **Styling:** Tailwind CSS 3.4.17
- **UI Components:** Radix UI
- **HTTP Client:** axios 1.8.4
- **Routing:** React Router DOM 7.5.1

### Infrastructure
- **Database:** MySQL Community Server 8.0+
- **Runtime:** Python 3.10+, Node.js 18+ LTS
- **Package Manager:** pip (Python), npm/yarn (Node)

---

## ✨ Features

### Faculty Features
- ✅ **Secure Authentication** - JWT-based login with 24-hour tokens
- ✅ **Role-Based Access** - Faculty can only view assigned classes/subjects
- ✅ **Assignment Management** - View all assigned class-subject combinations
- ✅ **Student Roster** - See enrolled students for assigned classes/subjects
- ✅ **Grade Entry** - Enter three types of marks:
  - CT1 (Class Test 1): 0-30
  - Insem (In-semester): 0-30
  - CT2 (Class Test 2): 0-70
  - **Total:** Auto-calculated (0-130)
- ✅ **Grade Persistence** - Save and update grades
- ✅ **Input Validation** - Real-time range validation
- ✅ **Responsive UI** - Beautiful Tailwind CSS design

### System Features
- ✅ **Multi-User Support** - 3+ faculty accounts with different assignments
- ✅ **Data Integrity** - MySQL with foreign keys and constraints
- ✅ **CORS Support** - Cross-origin requests enabled
- ✅ **Async Architecture** - Non-blocking I/O for performance
- ✅ **Health Check** - Endpoint for monitoring
- ✅ **Sample Data** - Pre-loaded with 3 faculty and 9 students

---

## 📦 Prerequisites

### Required
- **Python 3.10+** (with pip)
- **MySQL 8.0+** (Community Server)
- **Node.js 18+ LTS** (with npm or yarn)
- **Git** (for version control)

### Optional
- **VS Code** - Recommended editor
- **Postman** - For API testing
- **MySQL Workbench** - For database visualization

### System Requirements
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 2GB
- **OS:** Windows 10+, macOS 10.14+, or any Linux distribution

---

## 🚀 Quick Start

### 👥 For Windows Users

**[Complete Step-by-Step Guide →](backend/WINDOWS_SETUP_GUIDE.md)**

Quick summary:
```bash
# 1. Install MySQL (from installer)
# 2. Create database
mysql -u root -p
CREATE DATABASE grade_management_db;
CREATE USER 'grade_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON grade_management_db.* TO 'grade_user'@'localhost';

# 3. Setup backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements_mysql.txt

# 4. Load database
mysql -u grade_user -p grade_management_db < database_setup.sql

# 5. Create .env file
# Add: DATABASE_URL=mysql+asyncmy://grade_user:password123@localhost/grade_management_db

# 6. Run backend
python -m uvicorn server:app --reload

# 7. Run frontend (new terminal)
cd frontend
npm install
npm start

# 8. Open browser → http://localhost:3000
```

---

### 🍎 For macOS & Linux Users

**[Complete Step-by-Step Guide →](backend/MIGRATION_SETUP.md)**

Quick summary:
```bash
# 1. Install MySQL
# macOS: brew install mysql
# Linux: sudo apt-get install mysql-server

# 2. Create database
mysql -u root
CREATE DATABASE grade_management_db;
CREATE USER 'grade_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON grade_management_db.* TO 'grade_user'@'localhost';
EXIT;

# 3. Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_mysql.txt

# 4. Load database
mysql -u grade_user -p grade_management_db < database_setup.sql

# 5. Create .env file
cat > .env << 'EOF'
DATABASE_URL=mysql+asyncmy://grade_user:password123@localhost/grade_management_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=development
EOF

# 6. Validate migration
python test_migration.py

# 7. Run backend
python -m uvicorn server:app --reload

# 8. Run frontend (new terminal)
cd frontend
npm install
npm start

# 9. Open browser → http://localhost:3000
```

---

### ⚡ Validate Migration

After setup, verify everything works:

```bash
cd backend
python test_migration.py
```

Expected output: **✓ ALL TESTS PASSED - MIGRATION SUCCESSFUL!**

---

## 📁 Project Structure

```
grade-management-system/
├── README.md                          ← You are here
├── ANALYSIS.md                        ← Codebase analysis
│
├── backend/
│   ├── db_mysql.py                    ← SQLAlchemy models & database setup
│   ├── database_setup.sql             ← MySQL schema + sample data
│   ├── requirements_mysql.txt         ← Python dependencies
│   ├── server.py                      ← FastAPI application (341 lines)
│   ├── test_migration.py              ← Validation script
│   ├── WINDOWS_SETUP_GUIDE.md         ← Windows 10/11 setup (689 lines)
│   ├── MIGRATION_SETUP.md             ← macOS/Linux setup (235 lines)
│   ├── MIGRATION_COMPLETE.md          ← Detailed migration docs
│   └── .env                           ← Configuration (CREATE THIS)
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js                     ← Main React component
│   │   ├── index.js                   ├─ React entry point
│   │   ├── components/                ├─ UI components (Radix UI)
│   │   ├── hooks/                     └─ Custom React hooks
│   │   └── lib/
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env                           ← REACT_APP_BACKEND_URL

└── (analysis files)
    ├── ANALYSIS_SUMMARY.txt
    ├── ANALYSIS.md
    ├── MONGODB_SCHEMA.md
    ├── MIGRATION_CHECKLIST.md
    ├── README_ANALYSIS.md
    └── INDEX.md
```

---

## 🔌 API Endpoints

### Authentication
- **POST /api/auth/login**
  - Description: Faculty login
  - Request: `{ "email": "string", "password": "string" }`
  - Response: `{ "token": "string", "faculty": {...} }`
  - Status: 401 if invalid credentials

### Faculty
- **GET /api/faculty/me**
  - Description: Get current logged-in faculty info
  - Auth: Required (Bearer token)
  - Response: Faculty object with assignments

### Students
- **GET /api/students**
  - Description: Get students for a specific class-subject
  - Auth: Required (Bearer token)
  - Query Params: `class_name`, `subject`
  - Response: Array of students with marks

### Grades
- **POST /api/marks**
  - Description: Save or update student marks
  - Auth: Required (Bearer token)
  - Request: `{ "student_id": "string", "class_name": "string", "subject": "string", "ct1": number, "insem": number, "ct2": number }`
  - Response: `{ "message": "string", "marks": {...} }`
  - Validation: CT1 (0-30), Insem (0-30), CT2 (0-70)

### System
- **GET /api/health**
  - Description: Application health check
  - Response: `{ "status": "healthy" }`

---

## 🔐 Default Login Credentials

All credentials use password: `password123`

| Email | Password | Teaches | Classes |
|-------|----------|---------|---------|
| `rajesh@university.edu` | password123 | Mathematics | Class 10A, 10B |
| `priya@university.edu` | password123 | Physics | Class 10A |
| `amit@university.edu` | password123 | Chemistry | Class 10A, 10B |

**Sample Students:**
- Class 10A: Aarav Patel, Ananya Singh, Rohan Gupta, Diya Reddy, Arjun Mehta
- Class 10B: Kavya Joshi, Vihaan Desai, Ishaan Kapoor, Saanvi Nair

**Subjects:** Mathematics, Physics, Chemistry

---

## 💻 Frontend Usage

### Login Page
1. Enter faculty email (see credentials above)
2. Enter password: `password123`
3. Click **Sign In**

### Dashboard
1. Select **Class** from dropdown (e.g., "Class 10A")
2. Select **Subject** from dropdown (e.g., "Mathematics")
3. View enrolled students in table
4. Enter marks for each student:
   - **CT1:** 0-30 (Class Test 1)
   - **Insem:** 0-30 (In-semester)
   - **CT2:** 0-70 (Class Test 2)
   - **Total:** Auto-calculated
5. Click **Save** button
6. See confirmation message

### Features
- Real-time mark validation
- Auto-calculated totals
- Responsive design (works on desktop, tablet, mobile)
- Session persistence (reload page, stay logged in)
- Logout button in header

---

## 🔧 Troubleshooting

### MySQL Issues

**"MySQL server has gone away"**
```bash
# Verify MySQL is running
mysql -u root -p

# Or restart service
# Windows: net start MySQL80
# macOS: brew services start mysql
# Linux: sudo systemctl start mysql
```

**"Access denied for user 'grade_user'"**
```bash
# Recreate user with correct permissions
mysql -u root -p
CREATE USER 'grade_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON grade_management_db.* TO 'grade_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

### Python/Dependencies Issues

**"ModuleNotFoundError: No module named 'sqlalchemy'"**
```bash
# Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements_mysql.txt
```

**"Port 8000 already in use"**
```bash
# Use different port
python -m uvicorn server:app --port 8001
```

---

### Frontend Issues

**"npm: command not found"**
- Install Node.js from https://nodejs.org/ (LTS version)
- Check "Add to PATH" during installation

**"Port 3000 already in use"**
```bash
npm start -- --port 3001
```

**"Cannot connect to backend"**
1. Verify backend is running: `http://localhost:8000/api/health`
2. Check frontend `.env` has: `REACT_APP_BACKEND_URL=http://localhost:8000`
3. Restart frontend: `npm start`

---

### Login Issues

**"401 Invalid authentication credentials"**
- Verify email matches exactly (case-sensitive)
- Password is: `password123` for all demo accounts
- Ensure database_setup.sql was executed

**"403 You are not assigned to teach this subject"**
- Faculty can only see classes they're assigned to
- Dr. Rajesh Kumar: Math only
- Dr. Priya Sharma: Physics only
- Prof. Amit Verma: Chemistry only

---

### API Testing

**Test with curl:**
```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"rajesh@university.edu","password":"password123"}'

# Copy the token from response

# Get current faculty
curl -X GET "http://localhost:8000/api/faculty/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get students
curl -X GET "http://localhost:8000/api/students?class_name=Class%2010A&subject=Mathematics" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📊 Migration Information

This project was recently migrated from **MongoDB to MySQL**. 

### Key Changes
- **Database:** MongoDB → MySQL 8.0+
- **Driver:** Motor → asyncmy
- **ORM:** None → SQLAlchemy 2.0
- **Schema:** 3 collections → 5 normalized tables
- **API:** Unchanged (100% backward compatible)

### Migration Validation
Run the comprehensive validation script:
```bash
cd backend
python test_migration.py
```

For detailed migration information, see:
- [Migration Summary](backend/MIGRATION_COMPLETE.md)
- [MySQL Schema Design](MONGODB_SCHEMA.md)
- [Complete Analysis](ANALYSIS.md)

---

## 🧪 Development & Testing

### Run Validation Tests
```bash
cd backend
python test_migration.py
```

### Manual Testing
1. Start backend: `python -m uvicorn server:app --reload`
2. Start frontend: `npm start`
3. Open http://localhost:3000
4. Login with credentials above
5. Test grade entry and save

### Debug Mode
- Backend: `--reload` flag enables auto-restart on changes
- Frontend: Browser DevTools (F12) shows console errors
- Check both terminal outputs for errors

---

## 📚 Documentation

- **[Analysis Summary](ANALYSIS_SUMMARY.txt)** - Quick overview of system
- **[Codebase Analysis](ANALYSIS.md)** - Detailed architecture documentation
- **[MySQL Schema Design](MONGODB_SCHEMA.md)** - Database structure and queries
- **[Migration Checklist](MIGRATION_CHECKLIST.md)** - Step-by-step migration guide
- **[Windows Setup](backend/WINDOWS_SETUP_GUIDE.md)** - Windows-specific instructions
- **[macOS/Linux Setup](backend/MIGRATION_SETUP.md)** - Unix-like setup guide

---

## 🔒 Security Notes

⚠️ **For Development Only**

The current configuration is suitable for development and educational purposes. Before production deployment:

1. **Change SECRET_KEY** in .env to a strong random string
2. **Use strong database password** (not `password123`)
3. **Set ENVIRONMENT=production** in .env
4. **Remove --reload flag** from server startup
5. **Configure proper CORS origins** (not `["*"]`)
6. **Use HTTPS/SSL certificates** for encrypted communication
7. **Hash default passwords** before deployment
8. **Implement rate limiting** for API endpoints
9. **Add database backups** and recovery procedures

---

## 📄 License

Educational Project - MIT License

This project was created for educational purposes and is provided as-is.

---

## 👨‍💼 Credits

### Development
- **Backend:** FastAPI with SQLAlchemy and asyncmy
- **Frontend:** React with Tailwind CSS and Radix UI
- **Database:** MySQL with proper normalization
- **Architecture:** RESTful API with JWT authentication

### Third-Party Libraries
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit and ORM
- [React](https://react.dev/) - JavaScript library for UI
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Radix UI](https://www.radix-ui.com/) - Unstyled accessible components
- [Bcrypt](https://github.com/pyca/bcrypt) - Secure password hashing
- [PyJWT](https://github.com/jpadilla/pyjwt) - JWT implementation

---

## 📞 Support

### For Setup Help
- Windows: See [WINDOWS_SETUP_GUIDE.md](backend/WINDOWS_SETUP_GUIDE.md)
- macOS/Linux: See [MIGRATION_SETUP.md](backend/MIGRATION_SETUP.md)
- General: See Troubleshooting section above

### For Technical Questions
- Review [ANALYSIS.md](ANALYSIS.md) for system architecture
- Check [MIGRATION_COMPLETE.md](backend/MIGRATION_COMPLETE.md) for detailed info
- Run `python test_migration.py` to validate setup

### For Database Issues
- Check MySQL is running: `mysql -u root -p`
- Verify user exists: `mysql -u grade_user -p`
- View schema: `mysql -u grade_user -p grade_management_db -e "SHOW TABLES;"`

---

## ✅ Verification Checklist

Before running the application, verify:

- ✅ Python 3.10+ installed: `python --version`
- ✅ Node.js 18+ installed: `node --version`
- ✅ MySQL 8.0+ installed: `mysql --version`
- ✅ MySQL service running: `mysql -u root -p`
- ✅ Database created: `mysql -u grade_user -p`
- ✅ Virtual environment activated: `(venv)` in prompt
- ✅ Dependencies installed: `pip show sqlalchemy`
- ✅ Database schema loaded: Run validation tests
- ✅ .env file created: In backend directory
- ✅ Frontend .env created: In frontend directory

---

## 🎉 Ready to Get Started?

1. **Choose your OS:** [Windows](backend/WINDOWS_SETUP_GUIDE.md) | [macOS/Linux](backend/MIGRATION_SETUP.md)
2. **Follow the setup guide** for your operating system
3. **Run validation tests** to verify everything works
4. **Start the application** (backend + frontend)
5. **Login with demo credentials** and test features

**Questions?** Check the [Troubleshooting](#troubleshooting) section or review the detailed documentation.

---

**Last Updated:** November 1, 2025  
**Status:** Production Ready ✅  
**API Version:** v1.0  
**Database:** MySQL 8.0+
