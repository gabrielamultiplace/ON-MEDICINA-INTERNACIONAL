@echo off
REM Script para iniciar Nginx como Administrador
REM Salve este arquivo e clique duas vezes para executar

REM Verificar se est√° rodando como admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Tentando elevar privilegios...
    powershell -Command "Start-Process cmd -ArgumentList '/c %0' -Verb RunAs"
    exit /b
)

echo ================================
echo   INICIANDO NGINX
echo ================================
echo.

cd /d C:\nginx

REM Parar Nginx anterior
echo Parando Nginx anterior...
taskkill /F /IM nginx.exe >nul 2>&1
timeout /t 1 >nul

REM Iniciar Nginx
echo Iniciando Nginx na porta 80...
start nginx.exe
timeout /t 2 >nul

REM Verificar se iniciou
tasklist /FI "IMAGENAME eq nginx.exe" >nul
if %errorLevel% equ 0 (
    echo.
    echo ================================
    echo   NGINX INICIADO COM SUCESSO!
    echo ================================
    echo.
    echo Seu dominio esta pronto em:
    echo   http://app.onmedicinainternacional.com
    echo.
    echo Digite qualquer coisa para fechar...
    pause >nul
) else (
    echo ERRO: Nginx nao iniciou!
    pause
)
