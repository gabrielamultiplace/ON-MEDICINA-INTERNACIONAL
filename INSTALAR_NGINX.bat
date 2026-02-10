@echo off
REM Script para instalar e configurar Nginx em Windows
REM Executar como Administrador!

echo.
echo =========================================
echo   INSTALACAO NGINX - PROXY REVERSO
echo =========================================
echo.

REM Verificar se está rodando como admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute este script como Administrador!
    echo.
    echo Clique com botao direito no terminal e selecione "Executar como administrador"
    pause
    exit /b 1
)

echo [1/5] Verificando se Nginx está instalado...
if exist "C:\nginx\nginx.exe" (
    echo ✓ Nginx já está instalado!
    goto :config
)

echo.
echo [2/5] Nginx não encontrado. Baixando...
echo.
echo OPCAO 1: Instalação Manual (Recomendado)
echo   - Visite: https://nginx.org/en/download.html
echo   - Baixe: nginx-x.x.x.zip (mainline version)
echo   - Extraia em: C:\nginx\
echo.
echo OPCAO 2: Usar Chocolatey (se instalado)
echo   choco install nginx
echo.
echo Para continuar, baixe e extraia o Nginx em C:\nginx\
echo Depois execute este script novamente.
echo.
pause
exit /b 0

:config
echo.
echo [3/5] Configurando Nginx como proxy reverso...

REM Backup do arquivo original
if not exist "C:\nginx\conf\nginx.conf.bak" (
    copy "C:\nginx\conf\nginx.conf" "C:\nginx\conf\nginx.conf.bak"
    echo ✓ Backup criado: nginx.conf.bak
)

REM Copiar arquivo de configuração customizado
copy "%~dp0nginx_default.conf" "C:\nginx\conf\sites-available\default.conf" >nul 2>&1
mkdir "C:\nginx\conf\sites-available" >nul 2>&1
copy "%~dp0nginx_default.conf" "C:\nginx\conf\sites-available\default.conf"
echo ✓ Arquivo de configuração copiado

REM Testar configuração
echo.
echo [4/5] Testando configuração do Nginx...
cd /d C:\nginx
nginx.exe -t
if %errorLevel% neq 0 (
    echo.
    echo ERRO: Configuracao invalida!
    pause
    exit /b 1
)
echo ✓ Configuracao valida!

REM Iniciar Nginx
echo.
echo [5/5] Iniciando Nginx...
taskkill /F /IM nginx.exe >nul 2>&1
timeout /t 1 >nul

cd /d C:\nginx
start nginx.exe
timeout /t 2 >nul

tasklist /FI "IMAGENAME eq nginx.exe" >nul
if %errorLevel% equ 0 (
    echo ✓ Nginx iniciado com sucesso!
    echo.
    echo =========================================
    echo   CONFIGURACAO CONCLUIDA
    echo =========================================
    echo.
    echo Acesse: http://app.onmedicinainternacional.com
    echo.
    echo Comandos uteis:
    echo   Parar:    taskkill /F /IM nginx.exe
    echo   Reiniciar: nginx.exe -s reload
    echo   Testar:    nginx.exe -t
    echo.
) else (
    echo ERRO: Nginx nao iniciou!
    pause
    exit /b 1
)

pause
