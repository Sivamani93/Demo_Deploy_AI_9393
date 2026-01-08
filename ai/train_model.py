
import os, json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, precision_recall_curve, classification_report
from joblib import dump

# 1) Load data
csv_path = 'ai/training_data.csv'
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"Training data not found: {csv_path}")

df = pd.read_csv(csv_path)

# 2) Feature selection
features = [
    'failures', 'lint_warnings', 'changed_files',
    'apk_size_mb', 'apk_size_delta_ratio',
    'coverage_pct', 'build_duration_s',
    'secrets_found', 'sensitive_permissions'
]
for col in features:
    if col not in df.columns:
        df[col] = 0

df = df.fillna(0)
X = df[features].values
if 'proceed' not in df.columns:
    raise ValueError("Column 'proceed' missing in training data")
y = df['proceed'].astype(int).values

# 3) Train/valid split
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y if len(set(y))>1 else None
)

# 4) Scale + model
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_valid_s = scaler.transform(X_valid)

base_model = LogisticRegression(max_iter=1000, class_weight='balanced')
cal_model = CalibratedClassifierCV(base_model, cv=3, method='sigmoid')
cal_model.fit(X_train_s, y_train)

# 5) Evaluate
try:
    probs = cal_model.predict_proba(X_valid_s)[:, 1]
    auc = roc_auc_score(y_valid, probs) if len(set(y_valid))>1 else 0.5
except Exception:
    probs = cal_model.predict_proba(X_valid_s)[:, 1]
    auc = 0.5

prec, rec, thr = precision_recall_curve(y_valid, probs)
f1s = []
for p, r, t in zip(prec[:-1], rec[:-1], thr):
    f1s.append(2*p*r/(p+r+1e-9))
best_idx = max(range(len(f1s)), key=lambda i: f1s[i]) if f1s else 0
best_thr = float(thr[best_idx]) if len(thr)>0 else 0.5

print("ROC-AUC:", round(auc, 3))
print("Best threshold (by F1):", round(best_thr, 3))
print(classification_report(y_valid, (probs >= best_thr).astype(int)))

# 6) Save model artifacts
os.makedirs('ai/model', exist_ok=True)
dump({
    'scaler': scaler,
    'model': cal_model,
    'features': features,
    'threshold': best_thr
}, 'ai/model/model.pkl')
with open('ai/model/feature_schema.json', 'w') as f:
    json.dump({'features': features, 'threshold': best_thr}, f, indent=2)

print('Saved: ai/model/model.pkl and feature_schema.json')
