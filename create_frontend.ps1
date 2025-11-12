# Script para criar frontend SuperEzio do ZERO
# Todas as funcionalidades: RAG, Agent, WebSearch, Markdown, etc.

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  CRIANDO FRONTEND SUPEREZIO - COMPLETO" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Criar estrutura de pastas
Write-Host "1. Criando estrutura..." -ForegroundColor Yellow
$folders = @(
    "src",
    "src\components",
    "src\services",
    "src\hooks",
    "src\types",
    "src\styles"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
    Write-Host "   ✅ $folder" -ForegroundColor Green
}

Write-Host ""
Write-Host "Frontend pronto para receber arquivos!" -ForegroundColor Green
Write-Host ""
Write-Host "Próximo passo: Criar arquivos TypeScript"
