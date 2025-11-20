# Este script reinicia todos os processos do Superezio Realtime

$currentDir = $PSScriptRoot

Write-Output "--- REINICIANDO SUPEREZIO ---"

# Executa o script para matar os processos
Write-Output "[1/2] Encerrando servidores existentes..."
$killScriptPath = Join-Path -Path $currentDir -ChildPath "kill_all.ps1"
powershell -ExecutionPolicy Bypass -File $killScriptPath

# Pausa de 2 segundos para garantir que as portas sejam liberadas
Start-Sleep -Seconds 2

# Executa o script para iniciar os processos
Write-Output "[2/2] Iniciando novos servidores..."
$startScriptPath = Join-Path -Path $currentDir -ChildPath "start_all.ps1"
powershell -ExecutionPolicy Bypass -File $startScriptPath

Write-Output "--- REINICIALIZAÇÃO COMPLETA ---"
Read-Host -Prompt "Pressione Enter para sair"
