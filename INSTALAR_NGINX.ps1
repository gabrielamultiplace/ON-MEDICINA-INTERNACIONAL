# Script para automatizar instalacao e configuracao do Nginx no Windows
# Execute como Administrador: Right-Click > Run with PowerShell > Run as Administrator

Write-Host "================================" -ForegroundColor Cyan
Write-Host " INSTALACAO AUTOMATICA DO NGINX" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se é admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "ERRO: Este script deve ser executado como Administrador!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Clique com botao direito no PowerShell e selecione 'Run as Administrator'"
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "[1/4] Verificando instalacao do Nginx..." -ForegroundColor Yellow
if (Test-Path "C:\nginx\nginx.exe") {
    Write-Host "✓ Nginx já está instalado em C:\nginx" -ForegroundColor Green
} else {
    Write-Host "AVISO: Nginx não encontrado em C:\nginx" -ForegroundColor Red
    Write-Host ""
    Write-Host "INSTRUCOES:"
    Write-Host "  1. Visite: https://nginx.org/en/download.html"
    Write-Host "  2. Baixe: nginx-x.x.x.zip"
    Write-Host "  3. Extraia para: C:\nginx\"
    Write-Host "  4. Execute este script novamente"
    Write-Host ""
    Read-Host "Pressione Enter quando completar a instalacao"
    
    if (-not (Test-Path "C:\nginx\nginx.exe")) {
        Write-Host "ERRO: Nginx ainda nao encontrado!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "[2/4] Configurando ficheiro nginx.conf..." -ForegroundColor Yellow

$confDir = "C:\nginx\conf\sites-available"
New-Item -ItemType Directory -Path $confDir -Force | Out-Null

# Copiar arquivo de configuracao
$nginxConfigOrigin = "$PSScriptRoot\nginx_default.conf"
$nginxConfigDest = "$confDir\default.conf"

if (Test-Path $nginxConfigOrigin) {
    Copy-Item $nginxConfigOrigin -Destination $nginxConfigDest -Force
    Write-Host "✓ Arquivo de configuracao copiado" -ForegroundColor Green
} else {
    Write-Host "ERRO: arquivo nginx_default.conf nao encontrado!" -ForegroundColor Red
    exit 1
}

# Modificar nginx.conf para incluir sites-available
Write-Host "✓ Atualizando nginx.conf..." -ForegroundColor Green
$mainConf = "C:\nginx\conf\nginx.conf"

if (Test-Path $mainConf) {
    $content = Get-Content $mainConf -Raw
    
    if ($content -notmatch "sites-available") {
        # Backup
        Copy-Item $mainConf "$mainConf.bak" -Force
        
        # Adicionar include antes do ultimo }
        $content = $content -replace "(\s+include\s+mime\.types;)", '$1
    include sites-available/*.conf;'
        
        Set-Content $mainConf $content -Encoding UTF8
        Write-Host "✓ nginx.conf atualizado com include sites-available" -ForegroundColor Green
    } else {
        Write-Host "✓ sites-available ja incluido no nginx.conf" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[3/4] Testando configuracao..." -ForegroundColor Yellow

$testOutput = & "C:\nginx\nginx.exe" -t 2>&1
if ($testOutput -match "successful") {
    Write-Host "✓ Configuracao valida!" -ForegroundColor Green
} else {
    Write-Host "ERRO na configuracao:" -ForegroundColor Red
    Write-Host $testOutput
    exit 1
}

Write-Host ""
Write-Host "[4/4] Iniciando Nginx..." -ForegroundColor Yellow

# Parar qualquer nginx em execucao
Get-Process nginx -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

# Iniciar
Push-Location "C:\nginx"
.\nginx.exe
Pop-Location

Start-Sleep -Seconds 2

# Verificar se iniciou
$nginxProcess = Get-Process nginx -ErrorAction SilentlyContinue
if ($nginxProcess) {
    Write-Host "✓ Nginx iniciado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "ERRO: Nginx nao iniciou!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host " CONFIGURACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Seu dominio esta pronto!"
Write-Host ""
Write-Host "Acesse em 1-2 minutos:" -ForegroundColor Cyan
Write-Host "  http://app.onmedicinainternacional.com"
Write-Host ""
Write-Host "Para testes locais:" -ForegroundColor Cyan
Write-Host "  http://localhost"
Write-Host ""
Write-Host "Comandos uteis:" -ForegroundColor Yellow
Write-Host "  Parar Nginx:      taskkill /F /IM nginx.exe"
Write-Host "  Reiniciar:        cd C:\nginx; .\nginx.exe -s reload"
Write-Host "  Ver logs:         Get-Content C:\nginx\logs\error.log -Tail 50"
Write-Host ""

Read-Host "Pressione Enter para fechar"
