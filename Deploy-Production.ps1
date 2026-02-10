# Windows PowerShell Production Deployment Script
# For Gunicorn-based deployment on Windows

$ProjectRoot = Get-Location
$LogFile = "logs\deployment.log"

function Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

# Create log file
if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" -Force | Out-Null }
Log "=== Deployment Started ===" "INFO"

# Stop any running Python processes
Log "Stopping existing Python processes..." "INFO"
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Validate environment
Log "Validating Python environment..." "INFO"
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Log "Python not found" "ERROR"
    exit 1
}
Log "Python version: $pythonVersion" "INFO"

# Install/update packages
Log "Installing dependencies..." "INFO"
pip install -q -r requirements.txt
pip install -q gunicorn

# Create necessary directories
Log "Creating necessary directories..." "INFO"
@("uploads", "data", "logs", "backups") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

# Validate data files
Log "Validating data files..." "INFO"
try {
    $medCount = python -c "import json; d=json.load(open('data/medicamentos.json')); print(len(d))" 2>&1
    Log "Medicamentos: $medCount items" "INFO"
    
    $leadCount = python -c "import json; d=json.load(open('data/leads.json')); print(len(d))" 2>&1
    Log "Leads: $leadCount items" "INFO"
} catch {
    Log "Data validation failed: $_" "ERROR"
}

# Test Flask application
Log "Testing Flask application..." "INFO"
$testResult = python -c "from app import app; print('OK')" 2>&1
if ($testResult -match "OK") {
    Log "Flask application test PASSED" "INFO"
} else {
    Log "Flask application test FAILED: $testResult" "ERROR"
    exit 1
}

# Display information for next steps
Log "Deployment preparation COMPLETE" "INFO"
Log "============================================" "INFO"
Log "READY FOR PRODUCTION DEPLOYMENT" "INFO"
Log "============================================" "INFO"

Write-Host @"

DEPLOYMENT READY!

Current Configuration:
  - Python Version: $pythonVersion
  - Project Path: $ProjectRoot
  - Medications: $medCount
  - Leads: $leadCount

TO START PRODUCTION SERVER:
  
  Option 1 - Gunicorn (Recommended):
    gunicorn -c gunicorn_config.py wsgi:app

  Option 2 - Flask Development Server:
    python app.py

DATABASE BACKUP LOCATION:
  $ProjectRoot\backups\

LOG FILE:
  $LogFile

DEPLOYMENT GUIDE:
  See DEPLOYMENT_GUIDE.md for DNS, SSL, and nginx configuration

"@

Log "Environment ready for deployment" "INFO"
