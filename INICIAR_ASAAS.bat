@echo off
REM ============================================================================
REM INICIAR SISTEMA COM ASAAS INTEGRADO - WINDOWS
REM ============================================================================

title Plataforma ON Medicina - Asaas Integration v2.0

cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║    PLATAFORMA ON MEDICINA - ASAAS PAYMENT INTEGRATION         ║
echo ║                     Versão 2.0                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Verificar Python
echo 📋 Verificando ambiente...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
    echo ✅ Python: %%i
)

REM Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip não encontrado
    pause
    exit /b 1
)

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo.
    echo 🔨 Criando ambiente virtual...
    python -m venv venv
    echo ✅ Ambiente virtual criado
)

REM Ativar ambiente virtual
echo.
echo 🚀 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar requirements
echo.
echo 📥 Instalando dependências...
if exist "requirements.txt" (
    pip install -r requirements.txt -q
    echo ✅ Dependências instaladas
) else (
    echo ⚠️  requirements.txt não encontrado
    echo 📥 Instalando pacotes essenciais...
    pip install flask requests -q
)

REM Verificar arquivos Asaas
echo.
echo 📁 Verificando arquivos Asaas...

set "FILES_OK=1"
if exist "asaas_integration_v2.py" (
    echo ✅ asaas_integration_v2.py
) else (
    echo ❌ asaas_integration_v2.py (FALTANDO)
    set "FILES_OK=0"
)

if exist "asaas_config.py" (
    echo ✅ asaas_config.py
) else (
    echo ❌ asaas_config.py (FALTANDO)
    set "FILES_OK=0"
)

if exist "app.py" (
    echo ✅ app.py
) else (
    echo ❌ app.py (FALTANDO)
    set "FILES_OK=0"
)

if exist "index.html" (
    echo ✅ index.html
) else (
    echo ❌ index.html (FALTANDO)
    set "FILES_OK=0"
)

if "%FILES_OK%"=="0" (
    echo.
    echo ❌ Alguns arquivos estão faltando!
    pause
    exit /b 1
)

REM Verificar API Key
echo.
echo 🔑 Verificando API Key Asaas...

findstr /M "aact_prod_" asaas_integration_v2.py >nul
if errorlevel 1 (
    echo ⚠️  API Key não encontrada
    echo    Configure via variável de ambiente: ASAAS_API_KEY
) else (
    echo ✅ API Key configurada
)

REM Testar módulo
echo.
echo 🧪 Testando módulo Asaas...

python -c "from asaas_integration_v2 import AsaasIntegration; AsaasIntegration(); print('✅ Módulo carregado com sucesso')" 2>nul
if errorlevel 1 (
    echo ⚠️  Erro ao carregar módulo Asaas
)

REM Iniciar servidor
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                 INICIANDO SERVIDOR FLASK                      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 🚀 Servidor iniciando em http://localhost:5000
echo.
echo Endpoints disponíveis:
echo   📱 Frontend: http://localhost:5000
echo   💳 Pagamento: POST http://localhost:5000/api/asaas/criar-pagamento
echo   📊 Status: GET http://localhost:5000/api/asaas/status-pagamento/^<lead_id^>
echo   🧪 Teste: GET http://localhost:5000/api/asaas/teste
echo.
echo 📚 Documentação:
echo   - ASAAS_INTEGRATION.md - Documentação completa
echo   - ASAAS_RESUMO_FINAL.md - Resumo de implementação
echo.
echo 🧪 Para testar em outro terminal:
echo   python test_asaas_integration.py
echo.
echo Press Ctrl+C para parar o servidor
echo.

REM Iniciar servidor Flask
python app.py

pause
