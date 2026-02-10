# ============================================================================
# INICIAR ASAAS - PowerShell Script
# ============================================================================

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    PLATAFORMA ON MEDICINA - ASAAS INTEGRATION v2.0            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

# Verificar Python
Write-Host "📋 Verificando ambiente..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python não encontrado" -ForegroundColor Red
    exit 1
}

# Criar venv se não existir
if (-not (Test-Path "venv")) {
    Write-Host "🔨 Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Ambiente virtual criado" -ForegroundColor Green
}

# Ativar venv
Write-Host "🚀 Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Instalar requirements
Write-Host "📥 Instalando dependências..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt -q
    Write-Host "✅ Dependências instaladas" -ForegroundColor Green
}

# Verificar arquivos
Write-Host "`n📁 Verificando arquivos Asaas..." -ForegroundColor Yellow
$files = @("asaas_integration_v2.py", "asaas_config.py", "app.py", "index.html")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file (FALTANDO)" -ForegroundColor Red
    }
}

# Iniciar servidor
Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                 INICIANDO SERVIDOR FLASK                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

Write-Host "🚀 Servidor iniciando em http://localhost:5000" -ForegroundColor Green
Write-Host "`nEndpoints disponíveis:" -ForegroundColor Cyan
Write-Host "  📱 Frontend: http://localhost:5000" -ForegroundColor Gray
Write-Host "  💳 Pagamento: POST http://localhost:5000/api/asaas/criar-pagamento" -ForegroundColor Gray
Write-Host "  📊 Status: GET http://localhost:5000/api/asaas/status-pagamento/<lead_id>" -ForegroundColor Gray
Write-Host "  🧪 Teste: GET http://localhost:5000/api/asaas/teste" -ForegroundColor Gray
Write-Host "`n🧪 Para testar em outro terminal PowerShell:" -ForegroundColor Yellow
Write-Host "  python test_asaas_integration.py" -ForegroundColor Gray
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow

# Iniciar servidor
python app.py
