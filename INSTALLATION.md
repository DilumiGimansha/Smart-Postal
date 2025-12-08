# Installation Guide for New Users

## 🎯 Overview

This guide will help you set up the Smart Postal System on a new PC.

## ⏱️ Estimated Time

- **With experience**: 20-30 minutes
- **First time**: 45-60 minutes

## 📋 Prerequisites Installation

### 1. Install Python 3.11+

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ **CHECK "Add Python to PATH"**
4. Click "Install Now"
5. Verify:
```bash
python --version
```

**macOS:**
```bash
brew install python@3.11
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### 2. Install Node.js 18+

Download from https://nodejs.org/ (LTS version)

Verify:
```bash
node --version
npm --version
```

### 3. Install MySQL (via XAMPP)

**Windows/macOS:**
1. Download XAMPP from https://www.apachefriends.org/
2. Install with MySQL component
3. Open XAMPP Control Panel
4. Start MySQL

**Linux:**
```bash
sudo apt install mysql-server
sudo systemctl start mysql
```

### 4. Install Git

Download from https://git-scm.com/

Verify:
```bash
git --version
```

## 🚀 Project Setup

### Step 1: Clone Repository
```bash
# Clone the project
git clone https://github.com/YOUR_USERNAME/smart-postal-system.git

# Navigate into project
cd smart-postal-system
```

### Step 2: Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**If mysqlclient fails on Windows:**
```bash
# Download wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
# Then:
pip install mysqlclient-[version]-win_amd64.whl
```

### Step 3: Database Setup

**Create Database:**

1. Open XAMPP → Start MySQL
2. Click "Admin" (opens phpMyAdmin)
3. Click "New"
4. Database name: `postal_system`
5. Collation: `utf8mb4_unicode_ci`
6. Click "Create"

**Configure Environment:**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

Update these values in `.env`:
```env
DB_NAME=postal_system
DB_USER=root
DB_PASSWORD=  # Leave empty for XAMPP default
DB_HOST=localhost
DB_PORT=3306
GOOGLE_MAPS_API_KEY=your_key_here  # Optional
```

### Step 4: Run Migrations
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: [your choice]
```

### Step 5: Test Backend
```bash
# Start development server
python manage.py runserver
```

Open http://localhost:8000/api/

✅ Should see Django REST Framework API page

**Keep this terminal running!**

### Step 6: Frontend Setup

**Open NEW terminal:**
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open http://localhost:5173/

✅ Should see Smart Postal System interface

## ✅ Verification

Test that everything works:

1. ✅ Backend running: http://localhost:8000/api/
2. ✅ Frontend running: http://localhost:5173
3. ✅ Can access admin: http://localhost:8000/admin/
4. ✅ No console errors (F12 in browser)

## 🎮 First Use

1. **Upload Sample Data**:
   - Use `sample_data.csv` provided
   - Or create your own following CSV format in README

2. **Test Manual Entry**:
   - Add a mail item manually
   - Watch coordinates auto-populate

3. **Optimize Route**:
   - Select multiple items
   - Click "Optimize Route"
   - Wait for Q-Learning training (15-20 sec)
   - View results in Dashboard

4. **Configure Google Maps** (Optional):
   - Click ⚙️ Settings
   - Add API key
   - View routes on map

## 🐛 Common Issues

### Port Already in Use

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID [PID] /F
```

**macOS/Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

### MySQL Connection Error

- Check XAMPP MySQL is running (green)
- Verify database name: `postal_system`
- Check credentials in `.env`

### Module Not Found

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
rm -rf node_modules
npm install
```

### Geocoding Not Working

- Check internet connection
- Verify address format includes city
- Wait 1 second between requests


## ✨ You're Ready!

Start optimizing routes! 🚀