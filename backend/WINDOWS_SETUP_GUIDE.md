# Grade Management System - Windows Setup Guide

Complete step-by-step guide for running the application on Windows 10/11

---

## Table of Contents

1. [MySQL Installation](#mysql-installation)
2. [Python Setup](#python-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## MySQL Installation

### Step 1: Download MySQL

1. Visit: https://dev.mysql.com/downloads/mysql/
2. Select version **8.0.x** (LTS)
3. Download **MySQL Community Server (64-bit)**
4. Choose installer: `mysql-installer-community-X.X.XX.msi`

### Step 2: Run MySQL Installer

1. Double-click the `.msi` file
2. Click **Next** to start installation wizard
3. Select **Setup Type**: Choose **Developer Default**
4. Click **Next** and **Execute** to download packages
5. Click **Next** through the configuration

### Step 3: Configure MySQL Server

**Configuration Type:**
- Select: **Standalone MySQL Server / Classic MySQL Replication**
- Click **Next**

**Port Configuration:**
- Port: **3306** (default)
- Click **Next**

**MySQL Server - Type and Networking:**
- Config Type: **Development Machine**
- TCP Port: **3306**
- Click **Next**

**Authentication Method:**
- Select: **Use Strong Password Encryption**
- Click **Next**

**Accounts and Roles:**
- Root Password: Enter a **strong password** (remember it!)
  - Suggested: `Admin@123` or `MySQL@Password`
- Click **Add User**
  - Username: `grade_user`
  - Password: `password123`
  - Confirm: `password123`
  - Role: **DB Admin**
- Click **OK** then **Next**

**Windows Service:**
- Check: **Configure MySQL Server as a Windows Service**
- Service Name: `MySQL80` (default)
- Click **Next**

**Apply Configuration:**
- Click **Execute** to apply settings
- Click **Finish**

### Step 4: Verify MySQL Installation

Open **Command Prompt** (Win+R, type `cmd`):

```cmd
mysql --version
```

Expected output: `mysql Ver X.X.XX`

### Step 5: Test MySQL Connection

```cmd
mysql -u root -p
```

When prompted for password, enter your **root password**:

```
Enter password: (your root password)
```

If successful, you'll see:

```
Welcome to the MySQL monitor...
mysql>
```

Type `exit` to quit:

```
mysql> exit
```

---

## Python Setup

### Step 1: Check Python Installation

Open **Command Prompt**:

```cmd
python --version
```

**If Python is installed:** Skip to [Backend Setup](#backend-setup)

**If Python is NOT installed:** Continue below

### Step 2: Download Python

1. Visit: https://www.python.org/downloads/
2. Download **Python 3.10 or 3.11** (64-bit)
3. Run the installer `.exe` file

### Step 3: Install Python

1. **Check both boxes:**
   - ☑ Add Python to PATH (IMPORTANT!)
   - ☑ Install pip
2. Click **Install Now**
3. Wait for installation to complete
4. Click **Close**

### Step 4: Verify Python Installation

Open **Command Prompt** (new window):

```cmd
python --version
pip --version
```

Both commands should show version numbers.

---

## Backend Setup

### Step 1: Navigate to Project Directory

Open **Command Prompt** and navigate to the project:

```cmd
cd /path/to/grade-management-system/backend
```

**Example:**
```cmd
cd C:\Users\YourName\Developer\grade-management-system\backend
```

### Step 2: Create Python Virtual Environment

```cmd
python -m venv venv
```

This creates a `venv` folder.

### Step 3: Activate Virtual Environment

```cmd
venv\Scripts\activate
```

You should see `(venv)` at the start of your command prompt.

### Step 4: Install Dependencies

```cmd
pip install -r requirements_mysql.txt
```

This installs all required packages:
- FastAPI
- SQLAlchemy
- asyncmy
- uvicorn
- etc.

**Wait for installation** (usually 2-5 minutes)

### Step 5: Create Database in MySQL

Open a **new Command Prompt** window:

```cmd
mysql -u root -p
```

Enter your **root password**, then execute:

```sql
CREATE DATABASE grade_management_db;
CREATE USER 'grade_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON grade_management_db.* TO 'grade_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 6: Load Database Schema

Go back to your first Command Prompt (with `(venv)` active):

```cmd
mysql -u grade_user -p grade_management_db < database_setup.sql
```

When prompted: `Enter password: password123`

**Verify the data loaded:**

```cmd
mysql -u grade_user -p
```

Then:
```sql
USE grade_management_db;
SELECT COUNT(*) FROM faculties;
SELECT COUNT(*) FROM students;
EXIT;
```

Should show: `3` faculty and `9` students

### Step 7: Create .env File

In the backend folder, create a new file named `.env`:

**Method 1: Using Notepad**
1. Right-click in the backend folder
2. New → Text Document
3. Name it `.env`
4. Open it and add:

```
DATABASE_URL=mysql+asyncmy://grade_user:password123@localhost/grade_management_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=development
```

5. Save (Ctrl+S)

**Method 2: Using Command Prompt**
```cmd
(echo DATABASE_URL=mysql+asyncmy://grade_user:password123@localhost/grade_management_db & echo SECRET_KEY=your-secret-key-change-in-production) > .env
```

### Step 8: Validate Migration

With `(venv)` still active:

```cmd
python test_migration.py
```

You should see:
```
✓ PASS - MySQL Connection
✓ PASS - Faculty Count
✓ PASS - Student Count
... (all tests should pass)
```

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

Open **Command Prompt** (new window, no need for Python venv):

```cmd
cd C:\path\to\grade-management-system\frontend
```

### Step 2: Check Node.js Installation

```cmd
node --version
npm --version
```

**If NOT installed:**
1. Visit: https://nodejs.org/
2. Download **LTS version**
3. Run installer and follow prompts
4. Restart Command Prompt and verify

### Step 3: Install Dependencies

```cmd
npm install
```

Or if using Yarn:
```cmd
yarn install
```

### Step 4: Create .env File for Frontend

In the `frontend` folder, create `.env`:

```
REACT_APP_BACKEND_URL=http://localhost:8000
```

This tells React where the backend API is running.

---

## Running the Application

### Method 1: Two Separate Command Prompts (Recommended)

**Terminal 1 - Backend:**

```cmd
cd C:\path\to\grade-management-system\backend
venv\Scripts\activate
python -m uvicorn server:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 - Frontend:**

```cmd
cd C:\path\to\grade-management-system\frontend
npm start
```

You should see:
```
Compiled successfully!
Local: http://localhost:3000
```

### Method 2: Using VS Code

1. Open VS Code
2. File → Open Folder → Select `grade-management-system`
3. Terminal → New Terminal
4. Run both commands in split terminals

---

## Testing the Application

### Step 1: Open Browser

Go to: `http://localhost:3000`

You should see the **Grade Management** login page.

### Step 2: Test Login

Enter credentials:
- Email: `rajesh@university.edu`
- Password: `password123`

Click **Sign In**

You should see the dashboard with student marks.

### Step 3: Test Save Marks

1. Select **Class 10A** from dropdown
2. Select **Mathematics** from dropdown
3. Enter marks for a student:
   - CT1: 25
   - Insem: 28
   - CT2: 65
4. Click **Save**

You should see: **"Marks saved successfully!"**

### Step 4: Test Other Credentials

Try logging in with:
- `priya@university.edu` / `password123` (Physics)
- `amit@university.edu` / `password123` (Chemistry)

---

## Troubleshooting

### "MySQL server has gone away"

**Problem:** Backend can't connect to MySQL

**Solution:**
```cmd
# Verify MySQL is running
mysql -u root -p
```

If it doesn't work, MySQL service stopped:

1. Open **Services** (Win+R, type `services.msc`)
2. Find **MySQL80**
3. Right-click → **Start**

Or restart from Command Prompt:
```cmd
net start MySQL80
```

---

### "Access denied for user 'grade_user'"

**Problem:** Wrong password or user doesn't exist

**Solution:**
```cmd
# Log in as root
mysql -u root -p
# Create user again
CREATE USER 'grade_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON grade_management_db.* TO 'grade_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

### "ModuleNotFoundError: No module named 'sqlalchemy'"

**Problem:** Virtual environment not activated

**Solution:**
```cmd
# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements_mysql.txt
```

---

### "Port 8000 already in use"

**Problem:** Another application using port 8000

**Solution 1:** Use different port:
```cmd
python -m uvicorn server:app --reload --port 8001
```

Then update frontend `.env`:
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Solution 2:** Kill the process using port 8000:
```cmd
# Find process
netstat -ano | findstr :8000

# Kill it (replace PID)
taskkill /PID <PID> /F
```

---

### "Port 3000 already in use"

**Problem:** Another React instance running

**Solution:**
```cmd
# Kill the process
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different port
npm start -- --port 3001
```

---

### "npm: command not found"

**Problem:** Node.js not installed or not in PATH

**Solution:**
1. Download Node.js from https://nodejs.org/
2. Run installer
3. Check **Add to PATH**
4. Restart Command Prompt
5. Verify: `npm --version`

---

### "python: command not found"

**Problem:** Python not in PATH

**Solution:**
1. Reinstall Python from https://www.python.org/
2. **Check the box:** "Add Python to PATH"
3. Restart Command Prompt
4. Verify: `python --version`

---

### "401 Invalid authentication credentials"

**Problem:** Login failed

**Possible causes:**
1. Wrong email or password
2. Database not populated with sample data

**Solution:**
```cmd
# Check database
mysql -u grade_user -p
USE grade_management_db;
SELECT email, name FROM faculties;
EXIT;
```

Verify emails match credentials.

---

### "403 You are not assigned to teach this subject"

**Problem:** Faculty not assigned to class-subject

**Solution:**
Check that the faculty-assignment in database:

```cmd
mysql -u grade_user -p
USE grade_management_db;
SELECT * FROM faculty_assignments;
EXIT;
```

Faculty can only see classes/subjects they teach.

---

### "Connection refused" on frontend

**Problem:** Frontend can't reach backend API

**Solution:**
1. Verify backend is running: `http://localhost:8000/api/health`
2. Check frontend `.env` has correct URL:
   ```
   REACT_APP_BACKEND_URL=http://localhost:8000
   ```
3. Restart frontend: `npm start`

---

### "CORS error" in browser console

**Problem:** Cross-origin request blocked

**Solution:**
This should NOT happen as CORS is configured. If it does:

1. Verify backend URL in frontend `.env`
2. Check backend is running
3. Try different browser or incognito mode
4. Clear browser cache

---

### Application runs but frontend is blank

**Problem:** Build not completed

**Solution:**
1. Stop frontend (Ctrl+C)
2. Clear cache:
   ```cmd
   cd frontend
   rm -r node_modules
   npm install
   npm start
   ```
3. Wait for "Compiled successfully!"

---

## Performance Tips

### Speed Up Backend

```cmd
# Run without debug logging
python -m uvicorn server:app
```

### Speed Up Frontend

1. Close unnecessary browser tabs
2. Disable browser extensions
3. Clear browser cache (Ctrl+Shift+Delete)

---

## Stopping the Application

### Stop Backend

In backend terminal: **Ctrl+C**

### Stop Frontend

In frontend terminal: **Ctrl+C**

### Stop MySQL Service

```cmd
net stop MySQL80
```

---

## Restarting Everything

```cmd
# Terminal 1
cd backend
venv\Scripts\activate
python -m uvicorn server:app --reload

# Terminal 2
cd frontend
npm start
```

---

## Production Deployment Notes

⚠️ **DO NOT use these settings in production:**

1. **Change SECRET_KEY** from default value
2. **Use strong database password** (not `password123`)
3. **Set ENVIRONMENT=production** in .env
4. **Run without --reload flag**
5. **Use proper SSL certificates**
6. **Configure proper CORS origins**

---

## Support & Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- SQLAlchemy: https://docs.sqlalchemy.org/
- MySQL Docs: https://dev.mysql.com/doc/

---

**Successfully completed Windows setup!** 🎉

Your Grade Management System is now ready to use on Windows.


