@echo off
chcp 65001 >nul
title SuperEzio - Performance Test

cls
echo ================================================================================
echo  TESTE DE PERFORMANCE - SUPEREZIO OTIMIZADO
echo ================================================================================
echo.

echo [1/3] Verificando servidores...
echo.
curl -s http://localhost:8000/health
echo.
echo.

echo ================================================================================
echo [2/3] Teste de latência simples
echo ================================================================================
echo Request: "Olá, quanto é 2+2?"
echo.
powershell -Command "$start = Get-Date; curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"messages\":[{\"role\":\"user\",\"content\":\"Olá, quanto é 2+2?\"}],\"max_tokens\":50}' -UseBasicParsing | Out-Null; $end = Get-Date; Write-Host \"⏱️ Tempo: $(($end - $start).TotalSeconds) segundos\""
echo.
echo.

echo ================================================================================
echo [3/3] Teste de streaming SSE
echo ================================================================================
echo Request: "Explique Python brevemente"
echo.
curl -N -X POST http://localhost:8000/chat/stream -H "Content-Type: application/json" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Explique Python em uma frase\"}],\"stream\":true,\"max_tokens\":100}"
echo.

echo.
echo ================================================================================
echo ✅ Testes completos!
echo ================================================================================
echo.
echo 💡 Benchmarks esperados:
echo    • Latência simples: 1-3 segundos
echo    • Streaming: começa em ^< 1 segundo
echo    • Throughput: 20-40 chars/segundo
echo.
pause

