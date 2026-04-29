param([string]$msg = "update")

Write-Host ""
Write-Host "🚀 Deploying SpeedReader..." -ForegroundColor Cyan

# Add all changes
git add .
Write-Host "✅ Files staged" -ForegroundColor Green

# Commit
git commit -m $msg
Write-Host "✅ Committed: $msg" -ForegroundColor Green

# Push
git push origin main
Write-Host ""
Write-Host "🎉 Deployed successfully!" -ForegroundColor Green
Write-Host "🌍 https://web-production-d27f4.up.railway.app" -ForegroundColor Cyan
Write-Host ""