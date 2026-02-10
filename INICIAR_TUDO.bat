@echo off
cls
echo.
echo ================================
echo     SISTEMA DE INICIALIZACAO
echo ================================
echo.

REM Verificar se eh admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Este terminal NAO eh Administrador!
    echo.
    echo Por favor:
    echo 1. Feche este terminal
    echo 2. Abra PowerShell com botao DIREITO
    echo 3. Selecione "Run as Administrator"
    echo 4. Execute este arquivo novamente
    echo.
    pause
    exit /b 1
)

echo OK: Executando como ADMINISTRADOR
echo.

REM 1. Verificar Flask
echo [1/3] Verificando Flask...
tasklist | find /i "python" >nul
if %errorlevel% equ 0 (
    echo OK: Flask ja rodando
) else (
    echo Iniciando Flask...
    cd /d "C:\Users\Gabriela Resende\Documents\Plataforma ON"
    start python app.py
    timeout /t 3 /nobreak
    echo OK: Flask iniciado
)

REM 2. Parar Nginx anterior
echo.
echo [2/3] Preparando Nginx...
taskkill /F /IM nginx.exe 2>nul
timeout /t 1 /nobreak
echo OK: Nginx limpo

REM 3. Iniciar Nginx
echo.
echo [3/3] Iniciando Nginx...
cd /d C:\nginx
start nginx.exe
timeout /t 2 /nobreak

REM Verificação final
echo.
echo ================================
echo     STATUS FINAL
echo ================================
echo.

tasklist | find /i "nginx" >nul
if %errorlevel% equ 0 (
    echo OK: NGINX rodando
) else (
    echo ERRO: NGINX nao iniciou
)

tasklist | find /i "python" >nul
if %errorlevel% equ 0 (
    echo OK: FLASK rodando
) else (
    echo ERRO: FLASK nao iniciou
)

echo.
echo Acesse: http://app.onmedicinainternacional.com:8080
echo.
pause
