@echo off
REM Demo scenario switcher for AI Mobile CI/CD Pipeline

if "%1"=="clean" (
    echo Switching to CLEAN deployment scenario...
    copy ai_decision_clean.json ai_decision.json
    & "C:/Users/sduraisamy/Documents/Projects/AI_DEMO/AI_Demo_ML/ai_mobile_demo_ml/.venv/Scripts/python.exe" "ai/infer_risk.py" "--threshold" "0.5"
    & "C:/Users/sduraisamy/Documents/Projects/AI_DEMO/AI_Demo_ML/ai_mobile_demo_ml/.venv/Scripts/python.exe" "ai/render_report.py"
    echo Clean scenario activated. Check ai_report.html
) else if "%1"=="risky" (
    echo Switching to RISKY deployment scenario...
    echo {  > ai_decision.json
    echo   "signals": { >> ai_decision.json
    echo     "failures": 0, >> ai_decision.json
    echo     "lint_warnings": 8, >> ai_decision.json
    echo     "changed_files": 15, >> ai_decision.json
    echo     "apk_size_mb": 28.5, >> ai_decision.json
    echo     "apk_size_delta_ratio": 0.35, >> ai_decision.json
    echo     "coverage_pct": 65.2, >> ai_decision.json
    echo     "build_duration_s": 200, >> ai_decision.json
    echo     "secrets_found": 0, >> ai_decision.json
    echo     "sensitive_permissions": 3 >> ai_decision.json
    echo   }, >> ai_decision.json
    echo   "review": { >> ai_decision.json
    echo     "failure_pct": 15.0, >> ai_decision.json
    echo     "checks_total": 20, >> ai_decision.json
    echo     "failures": 3 >> ai_decision.json
    echo   } >> ai_decision.json
    echo } >> ai_decision.json
    & "C:/Users/sduraisamy/Documents/Projects/AI_DEMO/AI_Demo_ML/ai_mobile_demo_ml/.venv/Scripts/python.exe" "ai/infer_risk.py" "--threshold" "0.5"
    & "C:/Users/sduraisamy/Documents/Projects/AI_DEMO/AI_Demo_ML/ai_mobile_demo_ml/.venv/Scripts/python.exe" "ai/render_report.py"
    echo Risky scenario activated. Check ai_report.html
) else if "%1"=="train" (
    echo Training ML model...
    & "C:/Users/sduraisamy/Documents/Projects/AI_DEMO/AI_Demo_ML/ai_mobile_demo_ml/.venv/Scripts/python.exe" "ai/train_model.py"
    echo Model training complete!
) else (
    echo AI Mobile Demo - Scenario Switcher
    echo Usage: demo.bat [clean^|risky^|train]
    echo.
    echo   clean  - Low risk deployment (should PROCEED)
    echo   risky  - High risk deployment (should BLOCK)
    echo   train  - Retrain the ML model
    echo.
    echo Current decision files:
    if exist ai_decision.json echo   - ai_decision.json (heuristic signals)
    if exist ai_decision_ml.json echo   - ai_decision_ml.json (ML inference)
    if exist ai_report.html echo   - ai_report.html (risk report)
)