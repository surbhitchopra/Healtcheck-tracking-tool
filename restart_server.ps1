# Kill existing Django processes
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.MainModule.FileName -like "*Hc_Final*"} | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Start the server
Set-Location "C:\Users\surchopr\Hc_Final"
Start-Process -NoNewWindow -FilePath "hcvenc\Scripts\python.exe" -ArgumentList "manage.py", "runserver", "3000"

Write-Host "✅ Django server restarted on http://localhost:3000"
Write-Host "🔧 Network-level dates should now display properly!"