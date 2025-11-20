@echo off
chcp 65001 >nul
title SuperEzio Realtime - OTIMIZADO 10X

cls
echo ================================================================================
echo   ____                       _____     _       
echo  / ___| _   _ _ __   ___ _ _| ____|___(_) ___  
echo  \___ \| | | | '_ \ / _ \ '__|| |_ / __| |/ _ \ 
echo   ___) | |_| | |_) |  __/ |   | _|  __/ | (_) |
echo  |____/ \__,_| .__/ \___|_|   |___|_  |_|\___/ 
echo              |_|                                
echo.
echo  REALTIME - VERSÃO OTIMIZADA 10X
echo ================================================================================
echo.
echo 🚀 MELHORIAS:
echo    ✅ SSE Streaming (tokens em tempo real)
echo    ✅ Quantização 4-bit (3-5x mais rápido)
echo    ✅ CUDA optimizations (20-40%% speedup)
echo    ✅ LoRA SuperEzio (personalidade foda)
echo    ✅ Sem Express (arquitetura direta)
echo.
echo ================================================================================
echo.
pause

REM Limpar processos antigos
echo [1/4] 🧹 Limpando processos...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

REM Model Loader
echo.
echo [2/4] 📦 Iniciando Model Loader...
cd backend
start "SuperEzio - Model Loader" cmd /k "call venv\Scripts\activate && python model_loader.py"
cd ..

echo [2/4] ⏳ Aguardando modelo carregar (60s)...
timeout /t 60 /nobreak >nul

REM FastAPI Backend
echo.
echo [3/4] 🔥 Iniciando FastAPI Backend (porta 8000)...
cd backend
start "SuperEzio - FastAPI Backend" cmd /k "call venv\Scripts\activate && set PYTHONUTF8=1 && set PYTHONIOENCODING=utf-8 && python api.py"
cd ..

timeout /t 5 /nobreak >nul

REM Frontend
echo.
echo [4/4] ⚛️ Iniciando Frontend React (porta 3000)...
start "SuperEzio - Frontend" cmd /k "npm run dev"

echo.
echo ================================================================================
echo ✅ SISTEMA INICIADO!
echo ================================================================================
echo.
echo 🌐 Frontend:  http://localhost:3000
echo 🔥 FastAPI:   http://localhost:8000
echo 📊 Health:    http://localhost:8000/health
echo.
echo 🎯 Performance Esperada:
echo    • Velocidade: 20-40 chars/s (vs 3-7 anterior)
echo    • Latência: 1-5s (vs 5-35s anterior)
echo    • VRAM: ~4-5GB (vs 8.8GB anterior)
echo    • UX: Streaming em tempo real!
echo.
echo 🎭 LoRA Adapter: SuperEzio personality ATIVADO
echo.
echo ================================================================================
echo.
echo Pressione qualquer tecla para abrir browser...
pause >nul
start http://localhost:3000

