# Este script encerra todos os processos relacionados ao Superezio Realtime

Write-Output "🛑 Encerrando servidor backend Python (api.py)..."
# Encontra e para o processo do backend
$pythonProcess = Get-CimInstance Win32_Process -Filter "Name = 'python.exe' AND CommandLine LIKE '%api.py%'"
if ($pythonProcess) {
    Stop-Process -Id $pythonProcess.ProcessId -Force
    Write-Output "✅ Processo Python (ID: $($pythonProcess.ProcessId)) encerrado."
} else {
    Write-Output "✅ Nenhuma instância do backend Python encontrada."
}

Write-Output "🛑 Encerrando servidor frontend Node.js (Vite)..."
# Encontra e para o processo do frontend
$nodeProcess = Get-CimInstance Win32_Process -Filter "Name = 'node.exe' AND CommandLine LIKE '%vite%'"
if ($nodeProcess) {
    # No Windows, `npm run` pode criar uma árvore de processos. É melhor pegar o processo pai.
    $parentProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($nodeProcess.ParentProcessId)"
    if ($parentProcess.Name -eq "cmd.exe" -or $parentProcess.Name -eq "powershell.exe") {
        Stop-Process -Id $parentProcess.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Output "✅ Processo principal do Node.js (ID: $($parentProcess.ProcessId)) encerrado."
    } else {
         Stop-Process -Id $nodeProcess.ProcessId -Force -ErrorAction SilentlyContinue
         Write-Output "✅ Processo Node.js (ID: $($nodeProcess.ProcessId)) encerrado."
    }
} else {
    Write-Output "✅ Nenhuma instância do frontend Node.js encontrada."
}

Write-Output "✅ Limpeza concluída."
# A linha abaixo é comentada para que o script possa ser usado em automação
# Read-Host -Prompt "Pressione Enter para sair"
