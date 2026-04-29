param([string]$msg = "update")
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "Deploying SpeedReader..." -ForegroundColor Cyan

git add .
Write-Host "OK - Files staged" -ForegroundColor Green

git commit -m $msg
Write-Host "OK - Committed: $msg" -ForegroundColor Green

git push origin main
Write-Host ""
Write-Host "SUCCESS - Deployed!" -ForegroundColor Green
Write-Host "URL: https://web-production-d27f4.up.railway.app" -ForegroundColor Cyan
Write-Host ""