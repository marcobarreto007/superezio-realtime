@echo off
cd /d "C:\Users\marco\LLaMA-Factory"
set HF_HOME=C:\Users\marco\.cache\huggingface

echo.
echo ═══════════════════════════════════════
echo 🚀 TREINO CODE-EXPERT V1 OVERNIGHT
echo ═══════════════════════════════════════
echo 📊 QLoRA 4-bit ^| Rank 64 ^| 50k exemplos
echo 🔥 5 épocas ^| ~30k steps  
echo 💾 VRAM: 8-10 GB
echo ⏱️  ETA: 4-8 horas
echo ═══════════════════════════════════════
echo.

.\venv\Scripts\llamafactory-cli.exe train "examples\train_lora\qwen_code_expert_lora.yaml"

echo.
echo ═══════════════════════════════════════
echo ✅ TREINO CONCLUÍDO!
echo ═══════════════════════════════════════
pause
