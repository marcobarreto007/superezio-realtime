# Este script inicia os servidores do Superezio Realtime em segundo plano

$projectRoot = $PSScriptRoot

Write-Output "🚀 Iniciando servidor backend Python..."
$backendPath = Join-Path -Path $projectRoot -ChildPath "backend"
$pythonExecutable = Join-Path -Path $backendPath -ChildPath ".venv\Scripts\python.exe"
Start-Process -FilePath $pythonExecutable -ArgumentList "api.py" -WorkingDirectory $backendPath

Write-Output "🚀 Iniciando servidor frontend Node.js..."
# O npm precisa ser chamado através do cmd em Start-Process para funcionar corretamente
Start-Process "cmd.exe" -ArgumentList "/c", "npm", "run", "dev" -WorkingDirectory $projectRoot

Write-Output "✅ Servidores iniciados. Aguarde alguns segundos para que estejam prontos."
Write-Output "Acesse a interface em http://localhost:3000 (ou a porta que o Vite indicar)."
Read-Host -Prompt "Pressione Enter para sair"
