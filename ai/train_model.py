
import os, json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, precision_recall_curve, classification_report
from joblib import dump

csv_path = 'ai/training_data.csv'
if not os.path.exists(csv_path):
    print(f"Training data not found at {csv_path}, creating sample data...")
    # Create sample training data
    sample_data = """failures,lint_warnings,changed_files,apk_size_mb,apk_size_delta_ratio,coverage_pct,build_duration_s,secrets_found,sensitive_permissions,proceed
0,1,3,24.5,0.02,85.5,90,0,0,1
2,5,8,26.1,0.15,75.2,150,0,1,0
0,0,2,24.8,0.01,92.1,85,0,0,1
1,3,5,25.2,0.08,82.3,120,0,0,0
0,2,4,24.9,0.03,88.7,95,0,0,1
3,8,12,27.3,0.25,65.4,180,0,2,0
0,1,1,24.6,0.01,94.2,80,0,0,1
0,4,6,25.8,0.12,79.8,110,0,1,0
0,0,3,24.7,0.02,91.5,88,0,0,1
1,6,9,26.5,0.18,73.1,160,0,1,0
0,2,5,25.1,0.05,86.9,100,0,0,1
0,3,7,25.9,0.14,81.2,125,0,0,1
2,9,15,28.1,0.35,62.8,200,1,3,0
0,1,2,24.8,0.01,93.6,82,0,0,1
0,5,8,26.2,0.16,77.9,135,0,1,0
0,2,4,25.0,0.04,89.3,92,0,0,1
1,4,6,25.7,0.13,80.5,115,0,0,0
0,0,1,24.5,0.00,95.1,75,0,0,1
0,6,10,26.8,0.22,74.6,145,0,2,0
0,3,5,25.3,0.07,87.4,105,0,0,1"""
    
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(sample_data)
    print(f"Created sample training data at {csv_path}")

df = pd.read_csv(csv_path)
features = [
    'failures','lint_warnings','changed_files','apk_size_mb','apk_size_delta_ratio',
    'coverage_pct','build_duration_s','secrets_found','sensitive_permissions'
]
for col in features:
    if col not in df.columns:
        df[col] = 0

df = df.fillna(0)
X = df[features].values
y = df['proceed'].astype(int).values

X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y if len(set(y))>1 else None
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_valid_s = scaler.transform(X_valid)

base = LogisticRegression(max_iter=1000, class_weight='balanced')
cal = CalibratedClassifierCV(base, cv=3, method='sigmoid')
cal.fit(X_train_s, y_train)

try:
    probs = cal.predict_proba(X_valid_s)[:,1]
    auc = roc_auc_score(y_valid, probs) if len(set(y_valid))>1 else 0.5
except Exception:
    probs = cal.predict_proba(X_valid_s)[:,1]
    auc = 0.5

prec, rec, thr = precision_recall_curve(y_valid, probs)
f1s = []
for p, r, t in zip(prec[:-1], rec[:-1], thr):
    f1s.append(2*p*r/(p+r+1e-9))
best_idx = max(range(len(f1s)), key=lambda i: f1s[i]) if f1s else 0
best_thr = float(thr[best_idx]) if len(thr)>0 else 0.5

print('ROC-AUC:', round(auc,3))
print('Best threshold (by F1):', round(best_thr,3))
print(classification_report(y_valid, (probs>=best_thr).astype(int)))

os.makedirs('ai/model', exist_ok=True)
dump({'scaler': scaler,'model': cal,'features': features,'threshold': best_thr}, 'ai/model/model.pkl')
with open('ai/model/feature_schema.json','w') as f:
    json.dump({'features': features, 'threshold': best_thr}, f, indent=2)
print('Saved: ai/model/model.pkl and feature_schema.json')
