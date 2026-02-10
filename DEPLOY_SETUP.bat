@echo off
REM Windows Deployment Script for app.onmedicinainternacional.com
REM This script sets up the production environment on Windows

cd /d "%~dp0"

echo.
echo ============================================
echo PLATAFORMA ON - DEPLOYMENT SETUP
echo ============================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
echo ✅ Python installed

REM Check if pip packages are installed
pip show flask >nul 2>&1
if errorlevel 1 (
    echo ⏳ Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install packages
        pause
        exit /b 1
    )
    echo ✅ Packages installed
) else (
    echo ✅ Flask already installed
)

REM Install Gunicorn for production
pip show gunicorn >nul 2>&1
if errorlevel 1 (
    echo ⏳ Installing Gunicorn (production server)...
    pip install gunicorn
    echo ✅ Gunicorn installed
) else (
    echo ✅ Gunicorn already installed
)

REM Create logs directory
if not exist "logs" (
    mkdir logs
    echo ✅ Created logs directory
)

REM Create uploads directory if not exists
if not exist "uploads" (
    mkdir uploads
    echo ✅ Created uploads directory
)

REM Create backup of current data
set BACKUP_DIR=backups\%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
if not exist "backups" mkdir backups
mkdir "%BACKUP_DIR%"
copy data\*.json "%BACKUP_DIR%\" >nul
echo ✅ Data backed up to: %BACKUP_DIR%

REM Validate database
echo.
echo Validating data files...
python -c "import json; f=open('data/medicamentos.json'); d=json.load(f); print(f'  ✅ Medicamentos: {len(d)} items')"
python -c "import json; f=open('data/leads.json'); d=json.load(f); print(f'  ✅ Leads: {len(d)} items')"
python -c "import json; f=open('data/doctors.json'); d=json.load(f); print(f'  ✅ Doctors: {len(d)} items')"

REM Test Flask application
echo.
echo Testing Flask application...
python -c "from app import app; print('  ✅ Flask application loads successfully')" || (
    echo ❌ Flask application failed to load
    pause
    exit /b 1
)

echo.
echo ============================================
echo DEPLOYMENT PREPARATION COMPLETE
echo ============================================
echo.
echo NEXT STEPS:
echo.
echo 1. For Windows Server (IIS):
echo    - Install IIS with CGI support
echo    - Configure FastCGI
echo    - Create new IIS site pointing to this folder
echo.
echo 2. For Windows Development/Production (Gunicorn):
echo    - Run: gunicorn -c gunicorn_config.py wsgi:app
echo    - Or: python -m gunicorn -c gunicorn_config.py wsgi:app
echo.
echo 3. For Linux Server:
echo    - Follow DEPLOYMENT_GUIDE.md for Nginx + Gunicorn setup
echo.
echo 4. DNS Configuration:
echo    - Update domain registrar DNS records
echo    - Point A record to: [YOUR_SERVER_IP]
echo    - Wait for DNS propagation (15 min - 48 hours)
echo.
echo 5. SSL Certificate:
echo    - Windows: Use IIS Certificate Wizard or Let's Encrypt Certbot
echo    - Linux: Use Let's Encrypt Certbot
echo.
echo For detailed instructions, see: DEPLOYMENT_GUIDE.md
echo.
pause
