
import json, os, datetime

now = datetime.datetime.utcnow().isoformat() + 'Z'
ml_path = 'ai_decision_ml.json'
h_path = 'ai_decision.json'

if os.path.exists(ml_path):
    d = json.load(open(ml_path))
    source = 'ML'
elelif os.path.exists(h_path):
    d = json.load(open(h_path))
    source = 'Heuristic'
else:
    d = {'proceed': False, 'risk': None, 'signals': {}, 'prob': None, 'threshold': None}
    source = 'None'

signals = d.get('signals', {})

# Warnings block
warnings = []
if signals.get('apk_size_mb',0) > 150:
    warnings.append('APK > 150MB: Play Store may reject.')
if signals.get('sensitive_permissions',0) > 0:
    warnings.append('Sensitive permissions present: review required.')
if signals.get('lint_warnings',0) > 50:
    warnings.append('High lint warning count: fix quality issues.')
if signals.get('coverage_pct',0) < 50:
    warnings.append('Low test coverage: increase tests.')
if signals.get('secrets_found',0) > 0:
    warnings.append('Potential secrets found in code: remove immediately.')

warn_html = ''.join([f"<li style='color:#d33'>{w}</li>" for w in warnings]) or '<li>No warnings</li>'

html = f"""
<html>
<head>
  <meta charset='utf-8'/>
  <title>AI Risk Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 16px; }}
    .ok {{ color: #0a7; }}
    .bad {{ color: #d33; }}
    .card {{ border: 1px solid #ddd; border-radius: 6px; padding: 12px; margin-bottom: 12px; }}
    code {{ background: #f7f7f7; padding: 2px 6px; border-radius: 4px; }}
    table {{ border-collapse: collapse; }}
    td, th {{ border: 1px solid #eee; padding: 6px 8px; }}
  </style>
</head>
<body>
  <h2>AI Risk Report ({source})</h2>
  <div class='card'>
    <p><strong>Timestamp:</strong> {now}</p>
    <p><strong>Decision:</strong> <span class='{ 'ok' if d.get('proceed') else 'bad' }'>{ 'PROCEED' if d.get('proceed') else 'BLOCK' }</span></p>
    <p><strong>Probability:</strong> <code>{d.get('prob')}</code> (threshold <code>{d.get('threshold')}</code>)</p>
  </div>
  <div class='card'>
    <h3>Signals</h3>
    <table>
      <tr><th>Signal</th><th>Value</th></tr>
      {''.join([f"<tr><td>{k}</td><td><code>{signals.get(k)}</code></td></tr>" for k in ['failures','lint_warnings','changed_files','apk_size_mb','apk_size_delta_ratio','coverage_pct','build_duration_s','secrets_found','sensitive_permissions']])}
    </table>
  </div>
  <div class='card'>
    <h3>Potential Rejection/Quality Warnings</h3>
    <ul>{warn_html}</ul>
  </div>
  <div class='card'><em>Ready to evolve: swap heuristic with trained model and tune threshold via policy.</em></div>
</body>
</html>
"""

open('ai_report.html','w').write(html)
print('Wrote ai_report.html')
