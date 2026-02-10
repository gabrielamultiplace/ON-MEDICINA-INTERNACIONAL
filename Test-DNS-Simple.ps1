# PowerShell Script - Teste DNS Simples
# Uso: .\Test-DNS-Simple.ps1

$Domain = "app.onmedicinainternacional.com"
$ExpectedIP = "186.232.133.253"
$Port = 5000

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE DE DNS - Verificaccao" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: DNS Resolution
Write-Host "[1] RESOLUCAO DE DNS..." -ForegroundColor Yellow
try {
    $DnsResult = (Resolve-DnsName -Name $Domain -Type A -ErrorAction Stop).IPAddress | Select-Object -First 1
    if ($DnsResult -eq $ExpectedIP) {
        Write-Host "    OK - DNS RESOLVIDO CORRETAMENTE" -ForegroundColor Green
        Write-Host "       Nome: $Domain" -ForegroundColor Green
        Write-Host "       IP: $DnsResult" -ForegroundColor Green
    } elseif ($DnsResult) {
        Write-Host "    AVISO - IP DIFERENTE" -ForegroundColor Yellow
        Write-Host "       Esperado: $ExpectedIP" -ForegroundColor Yellow
        Write-Host "       Resolvi: $DnsResult" -ForegroundColor Yellow
    } else {
        Write-Host "    ERRO - DNS nao resolvido" -ForegroundColor Red
    }
} catch {
    Write-Host "    ERRO - DNS nao funcionando" -ForegroundColor Red
    Write-Host "       Causa: DNS ainda nao propagou (aguarde 15 min - 48h)" -ForegroundColor Yellow
}
Write-Host ""

# Test 2: Ping
Write-Host "[2] TESTE DE PING..." -ForegroundColor Yellow
try {
    $PingResult = Test-Connection -ComputerName $Domain -Count 1 -ErrorAction Stop
    Write-Host "    OK - Ping respondendo" -ForegroundColor Green
    Write-Host "       IP: $($PingResult.IPV4Address)" -ForegroundColor Green
    Write-Host "       Tempo: $($PingResult.ResponseTime)ms" -ForegroundColor Green
} catch {
    Write-Host "    ERRO - Ping falhou (possivel firewall bloquear ICMP)" -ForegroundColor Red
}
Write-Host ""

# Test 3: HTTP Port
Write-Host "[3] CONECTIVIDADE HTTP (Porta $Port)..." -ForegroundColor Yellow
try {
    $Response = Invoke-WebRequest -Uri "http://$Domain`:$Port/" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    Write-Host "    OK - Servidor respondendo" -ForegroundColor Green
    Write-Host "       URL: http://$Domain`:$Port/" -ForegroundColor Green
    Write-Host "       Status: $($Response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "    ERRO - Nao conseguiu conectar" -ForegroundColor Red
    Write-Host "       Possivel causa: Flask nao esta rodando ou firewall bloqueado" -ForegroundColor Yellow
}
Write-Host ""

# Test 4: Local Server
Write-Host "[4] SERVIDOR LOCAL (localhost:$Port)..." -ForegroundColor Yellow
$LocalServer = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
if ($LocalServer.TcpTestSucceeded) {
    Write-Host "    OK - Servidor local respondendo" -ForegroundColor Green
} else {
    Write-Host "    ERRO - Servidor local nao respondendo" -ForegroundColor Red
    Write-Host "       Execute: python app.py" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: Python Process
Write-Host "[5] PROCESSO PYTHON..." -ForegroundColor Yellow
$PythonRunning = Get-Process python -ErrorAction SilentlyContinue
if ($PythonRunning) {
    Write-Host "    OK - Python rodando" -ForegroundColor Green
} else {
    Write-Host "    ERRO - Python nao esta rodando" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMO: Consulte CONFIGUGACAO_DNS.md para proximas etapas" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
