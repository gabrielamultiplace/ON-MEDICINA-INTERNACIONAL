@echo off
REM =====================================================
REM Iniciar Servidor - ON Medicina Internacional
REM =====================================================
REM Este script inicia o servidor da plataforma
REM Qualquer mudança nos arquivos recarrega a página
REM =====================================================

title ON Medicina Internacional - Servidor

cd /d "c:\Users\Gabriela Resende\Documents\Plataforma ON"

cls

echo.
echo ╔═════════════════════════════════════════════════════════╗
echo ║                                                         ║
echo ║   🏥 ON Medicina Internacional - Servidor              ║
echo ║                                                         ║
echo ║   Iniciando...                                          ║
echo ║                                                         ║
echo ╚═════════════════════════════════════════════════════════╝
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python não encontrado!
    echo.
    echo Baixe em: https://python.org
    echo Marque: "Add Python to PATH"
    pause
    exit /b 1
)

REM Instalar dependências se necessário
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ✓ Instalando dependências...
    echo.
    pip install -r requirements.txt
    echo.
)

cls

echo.
echo ╔═════════════════════════════════════════════════════════╗
echo ║                                                         ║
echo ║   ✅ Servidor iniciado!                                ║
echo ║                                                         ║
echo ║   🔗 URL: http://localhost:5000                        ║
echo ║                                                         ║
echo ║   📧 Email: gabrielamultiplace@gmail.com              ║
echo ║   🔑 Senha: @On2025@                                   ║
echo ║                                                         ║
echo ║   ⏹ Para parar: Pressione CTRL + C                    ║
echo ║                                                         ║
echo ╚═════════════════════════════════════════════════════════╝
echo.

python app.py

pause
