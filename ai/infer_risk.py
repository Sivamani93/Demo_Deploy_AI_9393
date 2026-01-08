
import os, json
from joblib import load

art = 'ai/model/model.pkl'
signals = {'failures':0,'lint_warnings':0,'changed_files':0,'apk_size_mb':0.0,'apk_size_delta_ratio':0.0,
           'coverage_pct':0.0,'build_duration_s':0,'secrets_found':0,'sensitive_permissions':0}

# Load heuristic decision if present
if os.path.exists('ai_decision.json'):
    try:
        d = json.load(open('ai_decision.json'))
        s = d.get('signals', {})
        for k in signals:
            signals[k] = s.get(k, signals[k])
    except Exception as e:
        print(f"[warn] could not read ai_decision.json: {e}")

if not os.path.exists(art):
    print('[warn] model.pkl missing, fallback: block on failures, else proceed')
    proceed = signals['failures'] == 0 and signals.get('secrets_found',0)==0
    out = {'prob': None, 'threshold': None, 'proceed': proceed, 'signals': signals, 'reason': 'fallback_no_model'}
    print(json.dumps(out, indent=2))
    open('ai_decision_ml.json','w').write(json.dumps(out))
    raise SystemExit(0)

bundle = load(art)
scaler, model, features, thr = bundle['scaler'], bundle['model'], bundle['features'], bundle['threshold']

x = [[signals.get(f,0) for f in features]]
x_s = scaler.transform(x)
prob = float(model.predict_proba(x_s)[0,1])
proceed = prob >= thr

# Guardrails
if signals['failures'] > 0:
    proceed = False
if signals.get('secrets_found',0) > 0:
    proceed = False

out = {'prob': round(prob,3), 'threshold': round(thr,3), 'proceed': proceed, 'signals': signals}
print(json.dumps(out, indent=2))
open('ai_decision_ml.json','w').write(json.dumps(out))
