# ============================================
# INICIAR_TUDO.ps1 - ON Medicina Internacional
# ============================================
$ErrorActionPreference = "SilentlyContinue"
$projectDir = "C:\Users\Gabriela Resende\Documents\Plataforma ON"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ON Medicina Internacional - Startup   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- PASSO 1: Limpar processos anteriores ---
Write-Host "[1/4] Limpando processos anteriores..." -ForegroundColor Yellow
Get-Process -Name python*, python3* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
taskkill /F /IM nginx.exe 2>$null | Out-Null
taskkill /F /IM ngrok.exe 2>$null | Out-Null
Start-Sleep -Seconds 3
Write-Host "  OK - Processos limpos" -ForegroundColor Green

# --- PASSO 2: Iniciar Flask (porta 5000) ---
Write-Host "[2/4] Iniciando Flask na porta 5000..." -ForegroundColor Yellow
Set-Location $projectDir
Start-Process python -ArgumentList "app.py" -WorkingDirectory $projectDir -WindowStyle Minimized
Start-Sleep -Seconds 4

try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -UseBasicParsing -TimeoutSec 5
    if ($resp.StatusCode -eq 200) {
        Write-Host "  OK - Flask rodando (porta 5000)" -ForegroundColor Green
    }
} catch {
    Write-Host "  AVISO - Flask pode demorar para iniciar" -ForegroundColor Yellow
}

# --- PASSO 3: Iniciar Nginx (porta 8080) ---
Write-Host "[3/4] Iniciando Nginx na porta 8080..." -ForegroundColor Yellow
Set-Location C:\nginx
Start-Process .\nginx.exe -WorkingDirectory "C:\nginx"
Start-Sleep -Seconds 2

$nginxCheck = netstat -ano | Select-String ":8080.*LISTENING"
if ($nginxCheck) {
    Write-Host "  OK - Nginx rodando (porta 8080)" -ForegroundColor Green
} else {
    Write-Host "  AVISO - Nginx pode nao estar na porta 8080" -ForegroundColor Yellow
}

# --- PASSO 4: Iniciar Ngrok (tunel publico) ---
Write-Host "[4/4] Iniciando Ngrok (tunel publico)..." -ForegroundColor Yellow
if (Test-Path "C:\ngrok-app\ngrok.exe") {
    Start-Process "C:\ngrok-app\ngrok.exe" -ArgumentList "http 8080" -WindowStyle Minimized
    Start-Sleep -Seconds 5
    try {
        $ngrokApi = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 5
        $publicUrl = $ngrokApi.tunnels[0].public_url
        Write-Host "  OK - Ngrok ativo: $publicUrl" -ForegroundColor Green
    } catch {
        Write-Host "  AVISO - Verifique ngrok em http://127.0.0.1:4040" -ForegroundColor Yellow
    }
} else {
    Write-Host "  AVISO - ngrok.exe nao encontrado em C:\ngrok-app\" -ForegroundColor Yellow
}

# --- RESULTADO ---
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SISTEMA INICIADO!                     " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Local:   http://127.0.0.1:5000" -ForegroundColor White
Write-Host "  Nginx:   http://127.0.0.1:8080" -ForegroundColor White
Write-Host "  Publico: http://app.onmedicinainternacional.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para parar tudo:" -ForegroundColor Yellow
Write-Host "  taskkill /F /IM python3.13.exe; taskkill /F /IM nginx.exe; taskkill /F /IM ngrok.exe"
Write-Host ""

Set-Location $projectDir

