@echo off
REM HuggingFace → RAG Ingestion Pipeline
REM Harvests HF knowledge and ingests into SuperEzio RAG system

echo ========================================
echo  HuggingFace Knowledge Pipeline
echo  SuperEzio RAG Ingestion
echo ========================================
echo.

REM Navigate to backend directory
cd /d "%~dp0..\backend"

REM Activate Python venv
if exist "..\venv\Scripts\activate.bat" (
    echo Ativando venv...
    call ..\venv\Scripts\activate.bat
) else (
    echo AVISO: venv nao encontrado, usando Python global
)

REM Check if .env exists
if not exist ".env" (
    echo.
    echo ERRO: Arquivo .env nao encontrado!
    echo.
    echo Configure o token HuggingFace primeiro:
    echo   1. Copie .env.example para .env
    echo   2. Adicione seu token HF_TOKEN
    echo.
    pause
    exit /b 1
)

REM Step 1: Harvest HF knowledge
echo.
echo ========================================
echo  STEP 1: Harvesting HuggingFace
echo ========================================
echo.
echo Executando batch-harvest...
python hf_harvester.py batch-harvest

if errorlevel 1 (
    echo.
    echo ERRO: Batch harvest falhou
    pause
    exit /b 1
)

REM Step 2: Ingest into RAG
echo.
echo ========================================
echo  STEP 2: Ingesting into RAG
echo ========================================
echo.
echo Verificando se Node server esta rodando...
timeout /t 2 /nobreak >nul

python ingest_hf_to_rag.py

if errorlevel 1 (
    echo.
    echo ERRO: Ingestion falhou
    echo.
    echo Certifique-se de que o Node server esta rodando:
    echo   cd "C:\Users\marco\Superezio Realtime"
    echo   npx tsx server.ts
    pause
    exit /b 1
)

REM Success
echo.
echo ========================================
echo  SUCCESS - Pipeline Complete
echo ========================================
echo.
echo HuggingFace knowledge successfully ingested into RAG!
echo SuperEzio can now answer questions about HF models/datasets.
echo.

pause
