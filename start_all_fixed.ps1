Write-Host "Iniciando servidores..." -ForegroundColor Cyan

Write-Host "1. Backend Python (porta 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\marco\Superezio Realtime\backend'; .\venv\Scripts\python.exe api.py"
Start-Sleep -Seconds 30

Write-Host "2. Express Proxy (porta 8080)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\marco\Superezio Realtime'; npm run serve:watch"
Start-Sleep -Seconds 5

Write-Host "3. Frontend Vite (porta 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\marco\Superezio Realtime'; npm run dev"
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Servidores iniciados!" -ForegroundColor Green
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "Express:  http://localhost:8080" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
