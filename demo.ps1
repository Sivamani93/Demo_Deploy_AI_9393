# Demo scenario switcher for AI Mobile CI/CD Pipeline
param(
    [string]$Scenario = ""
)

$pythonExe = "C:/Users/sduraisamy/Documents/Projects/AI_DEMO/AI_Demo_ML/ai_mobile_demo_ml/.venv/Scripts/python.exe"

switch ($Scenario) {
    "clean" {
        Write-Host "Switching to CLEAN deployment scenario..." -ForegroundColor Green
        Copy-Item "ai_decision_clean.json" "ai_decision.json" -Force
        & $pythonExe "ai/infer_risk.py" "--threshold" "0.5"
        & $pythonExe "ai/render_report.py"
        Write-Host "Clean scenario activated. Check ai_report.html" -ForegroundColor Green
    }
    "risky" {
        Write-Host "Switching to RISKY deployment scenario..." -ForegroundColor Red
        $riskyData = @{
            signals = @{
                failures = 0
                lint_warnings = 8
                changed_files = 15
                apk_size_mb = 28.5
                apk_size_delta_ratio = 0.35
                coverage_pct = 65.2
                build_duration_s = 200
                secrets_found = 0
                sensitive_permissions = 3
            }
            review = @{
                failure_pct = 15.0
                checks_total = 20
                failures = 3
            }
        }
        $riskyData | ConvertTo-Json | Out-File "ai_decision.json" -Encoding ASCII -Force
        & $pythonExe "ai/infer_risk.py" "--threshold" "0.5"
        & $pythonExe "ai/render_report.py"
        Write-Host "Risky scenario activated. Check ai_report.html" -ForegroundColor Red
    }
    "train" {
        Write-Host "Training ML model..." -ForegroundColor Yellow
        & $pythonExe "ai/train_model.py"
        Write-Host "Model training complete!" -ForegroundColor Green
    }
    default {
        Write-Host "AI Mobile Demo - Scenario Switcher" -ForegroundColor Cyan
        Write-Host "Usage: .\demo.ps1 [clean|risky|train]" -ForegroundColor White
        Write-Host ""
        Write-Host "  clean  - Low risk deployment (should PROCEED)" -ForegroundColor Green
        Write-Host "  risky  - High risk deployment (should BLOCK)" -ForegroundColor Red  
        Write-Host "  train  - Retrain the ML model" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Current decision files:" -ForegroundColor White
        if (Test-Path "ai_decision.json") { Write-Host "  - ai_decision.json (heuristic signals)" }
        if (Test-Path "ai_decision_ml.json") { Write-Host "  - ai_decision_ml.json (ML inference)" }
        if (Test-Path "ai_report.html") { Write-Host "  - ai_report.html (risk report)" }
    }
}