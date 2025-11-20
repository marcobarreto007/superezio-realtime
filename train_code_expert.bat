@echo off
REM Treina Code Expert LoRA usando MESMO método que funcionou
REM Dataset reduzido: 1000 exemplos (vs 60 da família)
REM Configuração: Rank 128, Alpha 256, 10 épocas

echo ========================================
echo TREINO CODE EXPERT - RTX 3060 EDITION
echo ========================================
echo.
echo Dataset: code_expert_reduced.jsonl (1000 exemplos)
echo Metodo: train_lora.py (4-bit QLoRA)
echo Config: Rank 128, Alpha 256, Batch 4
echo Tempo estimado: ~10-15 minutos
echo.

cd scripts

python train_lora.py ^
    --data "../data/code_expert_reduced.jsonl" ^
    --output "../models/lora_code_expert_v1" ^
    --rank 128 ^
    --alpha 256 ^
    --epochs 10 ^
    --batch-size 4 ^
    --gradient-steps 2 ^
    --lr 5e-4

cd ..

echo.
echo ========================================
echo TREINO COMPLETO!
echo ========================================
echo.
echo Adapter salvo em: models\lora_code_expert_v1\
echo.
pause
