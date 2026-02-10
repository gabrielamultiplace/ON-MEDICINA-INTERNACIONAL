@echo off
cls
echo.
echo ════════════════════════════════════════════════════════════
echo        INICIANDO NGROK - EXPONDO APP NA INTERNET
echo ════════════════════════════════════════════════════════════
echo.

cd C:\ngrok-app

echo Conectando seu app local ao ngrok...
echo.
echo Estou criando um link publico que aponta para localhost:8080
echo Aguarde alguns segundos...
echo.

C:\ngrok-app\ngrok.exe http 8080

pause
