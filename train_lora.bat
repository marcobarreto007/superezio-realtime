@echo off
chcp 65001 >nul
title SuperEzio - LoRA Training

cls
echo ================================================================================
echo  SUPEREZIO LORA TRAINING
echo ================================================================================
echo.
echo 🎯 Este script vai treinar um adaptador LoRA customizado
echo    para a personalidade SuperEzio.
echo.
echo ⏱️ Tempo estimado: 10-30 minutos (RTX 3060)
echo 📊 VRAM necessária: ~8-10GB
echo.
echo 📚 Dataset: data/persona_superezio.jsonl
echo 💾 Output: models/lora_superezio/
echo.
echo ================================================================================
echo.
pause

cd backend
call venv\Scripts\activate

echo.
echo 🚀 Iniciando treinamento...
echo.

python ..\scripts\train_lora.py

echo.
echo ================================================================================
echo.

if errorlevel 1 (
    echo ❌ ERRO no treinamento!
    echo Verifique os logs acima.
) else (
    echo ✅ TREINO COMPLETO!
    echo.
    echo 🎉 LoRA adapter SuperEzio criado com sucesso!
    echo 📁 Localização: models\lora_superezio\
    echo.
    echo 🔄 Próximo passo: Reinicie o backend para usar o adapter
    echo    Execute: start_optimized.bat
)

echo.
echo ================================================================================
pause

