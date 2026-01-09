#! /usr/bin/env python3
import json, os, html, datetime

now = datetime.datetime.utcnow().isoformat() + "Z"
ml_path = "ai_decision_ml.json"
h_path = "ai_decision.json"

if os.path.exists(ml_path):
    d = json.load(open(ml_path, "r", encoding="utf-8"))
    source = "ML"
elif os.path.exists(h_path):
    d = json.load(open(h_path, "r", encoding="utf-8"))
    source = "Heuristic"
else:
    d = {"proceed": False, "risk": None, "signals": {}, "prob": None, "threshold": None}
    source = "None"

signals = d.get("signals", {})
review = d.get("review", {}) or {}
failure_pct = float(review.get("failure_pct", 0.0))
checks_total = int(review.get("checks_total", 0))
fails = int(review.get("failures", 0))

# Badge color based on failure rate
if failure_pct >= 50:
    review_class = "block"
elif failure_pct >= 20:
    review_class = "heuristic"
else:
    review_class = "ok"

review_badge = f'<span class="badge {review_class}">Review Failure: {failure_pct:.1f}% ({fails}/{checks_total})</span>'

warnings = []
if signals.get("apk_size_mb", 0) > 150: warnings.append("APK > 150MB: Play Store may reject.")
if signals.get("sensitive_permissions", 0) > 0: warnings.append("Sensitive permissions present: review required.")
if signals.get("lint_warnings", 0) > 100: warnings.append("High lint warning count: fix quality issues.")
if signals.get("coverage_pct", 0) < 60: warnings.append("Low test coverage: increase tests.")
if signals.get("secrets_found", 0) > 0: warnings.append("Potential secrets found in code: remove immediately.")
if not warnings: warnings.append("No warnings")

def row(k):
    v = signals.get(k, "")
    return f"<tr><td>{html.escape(k)}</td><td>{html.escape(str(v))}</td></tr>"

html_body = f"""<!doctype html>
<html lang=\"en\"><head>
<meta charset=\"utf-8\"><title>AI Risk Report</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:16px;}}
.badge{{display:inline-block;padding:4px 8px;border-radius:6px;color:#fff;font-weight:600}}
.ok{{background:#2e7d32}} .block{{background:#c62828}} .ml{{background:#1565c0}} .heuristic{{background:#6a1b9a}}
table{{border-collapse:collapse;margin-top:8px}} td,th{{border:1px solid #ddd;padding:6px 8px}}
</style></head><body>
<h1>AI Risk Report</h1>
<p><span class=\"badge {'ml' if source=='ML' else 'heuristic'}\">{source}</span>
<span class=\"badge {'ok' if d.get('proceed') else 'block'}\">{'PROCEED' if d.get('proceed') else 'BLOCK'}</span>
&nbsp;&nbsp;<small>{now}</small></p>
<p>{review_badge}</p>

<p><b>Probability:</b> {html.escape(str(d.get('prob')))} &nbsp;&nbsp;
<b>Threshold:</b> {html.escape(str(d.get('threshold')))}</p>

<h3>Signals</h3>
<table>
<tr><th>Signal</th><th>Value</th></tr>
{''.join(row(k) for k in ['failures','lint_warnings','changed_files','apk_size_mb',
                           'apk_size_delta_ratio','coverage_pct','build_duration_s',
                           'secrets_found','sensitive_permissions'])}
<tr><td>review_failure_pct</td><td>{failure_pct:.1f}% ({fails}/{checks_total})</td></tr>
</table>

<h3>Potential Rejection/Quality Warnings</h3>
<ul>{''.join(f'<li>{html.escape(w)}</li>' for w in warnings)}</ul>

</body></html>
"""
open("ai_report.html", "w", encoding="utf-8").write(html_body)
print("Wrote ai_report.html")
