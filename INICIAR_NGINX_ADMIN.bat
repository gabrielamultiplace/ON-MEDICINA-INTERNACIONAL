@echo off
echo.
echo ================================
echo    INICIAR NGINX COM ADMIN
echo ================================
echo.

REM Parar Nginx se estiver rodando
taskkill /F /IM nginx.exe 2>nul

REM Aguardar um pouco
timeout /t 2 /nobreak

REM Verificar se tem algo na porta 80
netstat -ano | find ":80 " | find "LISTENING"
if %ERRORLEVEL% EQU 0 (
    echo.
    echo AVISO: Ja existe algo na porta 80
    echo.
)

REM Ir para pasta do Nginx
cd /d C:\nginx

REM Tentar iniciar
echo Iniciando Nginx...
nginx.exe

echo.
echo Nginx iniciado!
echo.
timeout /t 3 /nobreak

REM Verificar se iniciou
netstat -ano | find ":80 " | find "LISTENING"
if %ERRORLEVEL% EQU 0 (
    echo.
    echo OK: NGINX esta na porta 80!
    echo.
    echo Teste em: http://app.onmedicinainternacional.com
    echo.
) else (
    echo.
    echo ERRO: NGINX nao iniciou na porta 80
    echo.
)

pause
