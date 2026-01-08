
# AI Mobile Demo (Flutter) — ML Integration

This repo demonstrates a **Flutter mobile CI pipeline** with an **AI gate** upgraded to **ML inference** using scikit-learn. It:

- Builds & tests the app (NDJSON machine output)
- Computes signals (failures, lint warnings, changed files, APK size & delta, coverage)
- Runs **ML inference** (logistic regression + calibration) to decide proceed/block
- Generates an **HTML Risk Report** and uploads artifacts
- Logs metrics to `ai/training_data.csv` for future retraining
- Includes a scheduled **model training** workflow

## Quick Start

```bash
flutter pub get
flutter test
flutter run
```

## CI/CD Workflows

- `.github/workflows/mobile-ci.yml` — main pipeline with ML inference & HTML report
- `.github/workflows/model-train.yml` — weekly or manual model training and artifact upload

## Files of Interest

- `ai/train_model.py` — trains logistic regression, saves `ai/model/model.pkl`
- `ai/infer_risk.py` — loads model, performs inference, writes `ai_decision_ml.json`
- `ai/render_report.py` — builds `ai_report.html` from decision JSON
- `ai/training_data.csv` — appended after each run (created by CI)

## Demo Flow

1. Push to GitHub: pipeline runs; see **Actions**.
2. Lint + tests → build APK → signals computed → `ai_decision.json` written.
3. ML inference → `ai_decision_ml.json`; report generated and uploaded.
4. Download APK from **Artifacts** and install on device:
   ```bash
   adb install app-release.apk
   ```
5. Add a failing test to see **BLOCK** decision, then remove it to see **PROCEED**.

## Training the Model

- Accumulate runs to build `ai/training_data.csv`.
- Trigger **Model Training** workflow (Actions → Model Training (weekly)) or run locally:
  ```bash
  pip install pandas scikit-learn joblib
  python ai/train_model.py
  ```
- Commit `ai/model/model.pkl` (or promote via artifact) so inference uses the trained model.

## Notes

- Guardrails: CI **never proceeds** if failures > 0, regardless of model output.
- Threshold can be exposed via repo variable `AI_RISK_THRESHOLD` (for heuristic comparison).
- Extend signals: secrets scan, sensitive permissions, performance timings.

## License

This demo is for educational purposes.
