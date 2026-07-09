Write-Host "Starting AI Recruitment Platform (Correct Version)..." -ForegroundColor Green

# Kill any existing processes
taskkill /F /IM python.exe 2>$null

Start-Sleep -Seconds 2

# Start Backend (using main.py, NOT main_simple)
Write-Host "Starting Backend with main.py..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend'; Write-Host 'Backend Starting...' -ForegroundColor Green; python -m uvicorn app.main:app --reload --port 8000"

Start-Sleep -Seconds 4

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\frontend'; Write-Host 'Frontend Starting...' -ForegroundColor Green; python -m http.server 3000"

Start-Sleep -Seconds 3

# Open Browser
Write-Host "Opening Browser..." -ForegroundColor Yellow
Start-Process "http://localhost:3000/candidate-dashboard.html"

Write-Host "`n✅ System Started!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan