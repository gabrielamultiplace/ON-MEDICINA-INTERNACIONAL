@echo off
REM Script para iniciar o servidor com auto-reload
REM Reinicia automaticamente quando há mudanças nos arquivos

setlocal enabledelayedexpansion

cd /d "c:\Users\Gabriela Resende\Documents\Plataforma ON"

echo.
echo ===============================================
echo   ON Medicina Internacional
echo   Servidor com Auto-Reload
echo ===============================================
echo.

REM Verificar se pip está instalado
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado!
    echo Baixe Python em: https://python.org
    pause
    exit /b 1
)

REM Verificar se Flask está instalado
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Instalando dependências...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERRO ao instalar dependências!
        pause
        exit /b 1
    )
)

echo.
echo ✓ Tudo pronto!
echo.
echo Iniciando servidor...
echo.
echo URL: http://localhost:5000
echo Login: gabrielamultiplace@gmail.com / @On2025@
echo.
echo Pressione CTRL+C para parar
echo.

REM Iniciar Flask com debug mode (auto-reload)
python app.py

pause
