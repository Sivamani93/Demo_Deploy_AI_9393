#! /usr/bin/env python3
import os, sys, json, argparse
from joblib import load

def load_signals():
    base = {'failures':0,'lint_warnings':0,'changed_files':0,'apk_size_mb':0.0,
            'apk_size_delta_ratio':0.0,'coverage_pct':0.0,'build_duration_s':0,
            'secrets_found':0,'sensitive_permissions':0}
    if os.path.exists('ai_decision.json'):
        try:
            d = json.load(open('ai_decision.json','r',encoding='utf-8'))
            s = d.get('signals', {})
            for k in base: base[k] = s.get(k, base[k])
        except Exception as e:
            print(f"[warn] could not read ai_decision.json: {e}")
    return base

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--threshold', type=float, default=None,
                    help='Override model threshold (0..1)')
    ap.add_argument('--fail-on-block', action='store_true',
                    help='Exit 1 if decision is BLOCK')
    args = ap.parse_args()

    signals = load_signals()
    reasons = []

    art = 'ai/model/model.pkl'
    if not os.path.exists(art):
        reasons.append('no_model')
        proceed = (signals['failures']==0 and signals.get('secrets_found',0)==0)
        out = {'prob': None, 'threshold': args.threshold, 'proceed': proceed,
               'signals': signals, 'reasons': reasons}
        print(json.dumps(out, indent=2))
        open('ai_decision_ml.json','w',encoding='utf-8').write(json.dumps(out))
        if args.fail_on_block and not proceed: sys.exit(1)
        return 0

    bundle = load(art)
    scaler, model, features, saved_thr = bundle['scaler'], bundle['model'], bundle['features'], bundle['threshold']
    thr = args.threshold if args.threshold is not None else saved_thr

    x = [[signals.get(f, 0) for f in features]]
    x_s = scaler.transform(x)
    prob = float(model.predict_proba(x_s)[0,1])  # prob of PROCEED

    proceed = (prob >= thr)
    if signals['failures'] > 0:
        proceed = False; reasons.append('test_failures')
    if signals.get('secrets_found',0) > 0:
        proceed = False; reasons.append('secrets_found')

    out = {'prob': round(prob,3), 'threshold': round(thr,3), 'proceed': proceed,
           'signals': signals, 'reasons': reasons}
    print(json.dumps(out, indent=2))
    open('ai_decision_ml.json','w',encoding='utf-8').write(json.dumps(out))

    if args.fail_on_block and not proceed: sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
