@echo off
echo.
echo ============================================================
echo   TREINAMENTO LORA - FUNCTION CALLING
echo   PRIORIDADE: TREINO NA VEIA!
echo ============================================================
echo.
echo Dataset: 45 exemplos
echo  - 31 personalidade SuperEzio
echo  - 14 function calling (ferramentas)
echo.
echo Tempo: 15-25 minutos
echo VRAM: ~10GB
echo.
echo ⚠️  IMPORTANTE: Parando o backend primeiro!
echo    (Liberar VRAM para o treinamento)
echo.
echo ============================================================
echo.

REM Parar todos os processos Python do Superezio
echo 🛑 Parando backend Python...
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *Superezio*" 2>nul
timeout /t 3 /nobreak >nul
echo ✅ Backend parado!
echo.

pause

cd scripts
..\backend\venv\Scripts\python.exe train_lora.py

echo.
echo ============================================================
echo   TREINAMENTO CONCLUIDO!
echo ============================================================
echo.
echo Proximo passo:
echo   1. Inicie o backend novamente para usar o novo adaptador
echo   2. SuperEzio agora sabe USAR FERRAMENTAS! 🔥
echo.
pause
