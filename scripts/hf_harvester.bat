@echo off
REM HuggingFace Knowledge Harvester - Windows Launcher
REM Autor: Marco Barreto

echo ========================================
echo  HuggingFace Knowledge Harvester
echo  Vampirize HF para RAG System
echo ========================================
echo.

REM Navegar para pasta backend
cd /d "%~dp0..\backend"

REM Ativar venv Python
if exist "..\venv\Scripts\activate.bat" (
    echo Ativando venv...
    call ..\venv\Scripts\activate.bat
) else (
    echo AVISO: venv nao encontrado, usando Python global
)

REM Verificar se .env existe
if not exist ".env" (
    echo.
    echo ERRO: Arquivo .env nao encontrado!
    echo.
    echo Crie o arquivo .env com base no .env.example:
    echo   1. Copie .env.example para .env
    echo   2. Adicione seu token HuggingFace em HF_TOKEN
    echo.
    pause
    exit /b 1
)

REM Verificar dependências
echo.
echo Verificando dependencias...
python -c "import huggingface_hub" 2>nul
if errorlevel 1 (
    echo.
    echo Instalando dependencias necessarias...
    pip install huggingface_hub python-dotenv
)

REM Executar harvester
echo.
echo Iniciando HuggingFace Harvester...
echo.
python hf_harvester.py %*

REM Capturar código de saída
set EXIT_CODE=%errorlevel%

echo.
echo ========================================
if %EXIT_CODE% equ 0 (
    echo  Harvester finalizado com sucesso!
) else (
    echo  Harvester finalizado com erros ^(codigo: %EXIT_CODE%^)
)
echo ========================================
echo.

pause
exit /b %EXIT_CODE%
