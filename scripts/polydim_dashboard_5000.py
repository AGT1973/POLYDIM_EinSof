"""
POLYDIM-EINSOF — Panel de Control de Silicio (Puerto 5000)
===========================================================
Dashboard en tiempo real para monitoreo de:
  1. Auditorías QA Adversarial (Sabueso Autónomo)
  2. Tribunal Plenario de los 17 Sabios
  3. Evaluaciones de informes externos (Rafael, alumnos)
  4. Incidentes, soluciones y mejoras propuestas

Accesible en: http://0.0.0.0:5000 (LAN) / http://192.168.100.X:5000
Lee en tiempo real desde PostgreSQL 16 (polydim_active_db.active_vault).
"""

import os
import json
import time
from datetime import datetime, timezone
from flask import Flask, render_template_string, jsonify
import psycopg2

app = Flask(__name__)

PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PORT = int(os.environ.get("PGPORT", 5432))
PG_USER = os.environ.get("PGUSER", "postgres")
PG_PASSWORD = os.environ.get("PGPASSWORD", "1234")
PG_DB = os.environ.get("PGDATABASE", "polydim_active_db")

def get_db():
    return psycopg2.connect(dbname=PG_DB, host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASSWORD)

def query_vault(category, limit=50):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT key_name, value, notes, updated_at FROM active_vault WHERE category=%s ORDER BY updated_at DESC LIMIT %s",
            (category, limit)
        )
        rows = cur.fetchall()
        conn.close()
        results = []
        for r in rows:
            try:
                val = json.loads(r[1]) if isinstance(r[1], str) else r[1]
            except Exception:
                val = r[1]
            results.append({"key": r[0], "value": val, "notes": r[2], "updated": str(r[3])})
        return results
    except Exception as e:
        return [{"key": "ERROR", "value": str(e), "notes": "", "updated": ""}]

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="20">
<title>POLYDIM — Panel de Silicio (17 Sabios + QA Adversarial)</title>
<style>
  :root {
    --bg: #0a0e17; --card: #111827; --border: #1e293b;
    --green: #22c55e; --yellow: #eab308; --red: #ef4444;
    --cyan: #06b6d4; --white: #f1f5f9; --muted: #94a3b8;
    --accent: #818cf8;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--bg); color:var(--white); font-family:'Segoe UI',system-ui,sans-serif; }
  .header {
    background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
    padding: 20px 30px; border-bottom: 2px solid var(--accent);
    display: flex; justify-content: space-between; align-items: center;
  }
  .header h1 { font-size:1.5rem; letter-spacing:0.05em; }
  .header h1 span { color: var(--accent); }
  .header .meta { color: var(--muted); font-size: 0.85rem; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 20px; }
  .full { grid-column: 1 / -1; }
  .card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px; overflow: hidden;
  }
  .card h2 {
    font-size: 1rem; color: var(--cyan); margin-bottom: 12px;
    padding-bottom: 8px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 8px;
  }
  .card h2 .dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
  .dot-green { background: var(--green); box-shadow: 0 0 6px var(--green); }
  .dot-yellow { background: var(--yellow); box-shadow: 0 0 6px var(--yellow); }
  .dot-red { background: var(--red); box-shadow: 0 0 6px var(--red); }
  table { width:100%; border-collapse:collapse; font-size:0.82rem; }
  th { text-align:left; color:var(--muted); padding:6px 8px; border-bottom:1px solid var(--border); font-weight:500; }
  td { padding:6px 8px; border-bottom:1px solid #1a2332; vertical-align:top; }
  tr:hover { background: #1a2332; }
  .badge {
    display:inline-block; padding:2px 8px; border-radius:4px; font-size:0.72rem; font-weight:600;
  }
  .badge-ok { background:#14532d; color:#4ade80; }
  .badge-warn { background:#713f12; color:#fbbf24; }
  .badge-fail { background:#7f1d1d; color:#fca5a5; }
  .badge-info { background:#1e3a5f; color:#7dd3fc; }
  .sabio-row { display:flex; align-items:center; gap:8px; padding:5px 0; border-bottom:1px solid #1a2332; }
  .sabio-id { background:var(--accent); color:#fff; border-radius:4px; padding:1px 6px; font-size:0.72rem; font-weight:700; min-width:36px; text-align:center; }
  .sabio-name { font-weight:600; min-width:200px; }
  .sabio-canal { color:var(--muted); font-size:0.78rem; flex:1; }
  .sabio-latency { color:var(--cyan); font-size:0.78rem; min-width:70px; text-align:right; }
  .sabio-dict { color:var(--white); font-size:0.78rem; max-width:400px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .incident-block { margin-bottom:10px; padding:10px; background:#0f1729; border-left:3px solid var(--cyan); border-radius:4px; }
  .incident-block.sev-alta { border-left-color: var(--red); }
  .incident-block.sev-critica { border-left-color: var(--red); }
  .incident-block.sev-media { border-left-color: var(--yellow); }
  .incident-title { font-weight:600; font-size:0.85rem; margin-bottom:4px; }
  .incident-detail { color:var(--muted); font-size:0.78rem; }
  .metric-row { display:flex; gap:16px; margin-bottom:10px; }
  .metric-box { flex:1; background:#0f1729; border-radius:8px; padding:12px; text-align:center; }
  .metric-box .num { font-size:1.6rem; font-weight:700; }
  .metric-box .label { font-size:0.72rem; color:var(--muted); margin-top:4px; }
  .num-green { color:var(--green); }
  .num-red { color:var(--red); }
  .num-cyan { color:var(--cyan); }
  .num-yellow { color:var(--yellow); }
  .scroll-box { max-height:400px; overflow-y:auto; }
  .scroll-box::-webkit-scrollbar { width:6px; }
  .scroll-box::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
</style>
</head>
<body>

<div class="header">
  <h1>🔬 <span>POLYDIM</span> — Panel de Control de Silicio</h1>
  <div class="meta">
    Auto-refresh: 20s | ALADIN: 192.168.100.21 | PostgreSQL 16 | Puerto 5000<br>
    Última carga: {{ now }}
  </div>
</div>

<div class="grid">

  <!-- MÉTRICAS RÁPIDAS -->
  <div class="card full">
    <div class="metric-row">
      <div class="metric-box">
        <div class="num num-cyan">{{ sabios_count }}</div>
        <div class="label">Sabios Atendieron</div>
      </div>
      <div class="metric-box">
        <div class="num num-green">{{ qa_passed }}</div>
        <div class="label">QA Tests Passed</div>
      </div>
      <div class="metric-box">
        <div class="num num-red">{{ qa_failed }}</div>
        <div class="label">QA Tests Failed</div>
      </div>
      <div class="metric-box">
        <div class="num num-yellow">{{ total_incidents }}</div>
        <div class="label">Incidentes Registrados</div>
      </div>
      <div class="metric-box">
        <div class="num num-cyan">{{ eval_count }}</div>
        <div class="label">Evaluaciones Externas</div>
      </div>
    </div>
  </div>

  <!-- TRIBUNAL DE LOS 17 SABIOS -->
  <div class="card full">
    <h2><span class="dot dot-green"></span> Tribunal Plenario de los 17 Sabios (Última Sesión)</h2>
    <div class="scroll-box">
      {% for s in sabios %}
      <div class="sabio-row">
        <span class="sabio-id">{{ "%02d"|format(s.id) }}/17</span>
        <span class="sabio-name">{{ s.nombre }}</span>
        <span class="sabio-canal">{{ s.canal }}</span>
        <span class="sabio-latency">{{ s.latencia_ms }}ms</span>
        <span class="sabio-dict" title="{{ s.dictamen }}">{{ s.dictamen[:80] }}</span>
      </div>
      {% endfor %}
      {% if not sabios %}
      <div style="color:var(--muted); padding:10px;">Sin sesiones del Tribunal registradas.</div>
      {% endif %}
    </div>
  </div>

  <!-- QA ADVERSARIAL -->
  <div class="card">
    <h2><span class="dot dot-yellow"></span> Auditoría QA Adversarial (Sabueso Autónomo)</h2>
    <div class="scroll-box">
      {% for q in qa_results %}
      <div class="incident-block {{ 'sev-alta' if q.severity == 'ALTA' else ('sev-critica' if q.severity == 'CRITICA' else ('sev-media' if q.severity == 'MEDIA' else '')) }}">
        <div class="incident-title">
          {{ q.hound }} → {{ q.test }}
          {% if q.passed %}
            <span class="badge badge-ok">PASSED</span>
          {% else %}
            <span class="badge badge-fail">FAILED</span>
          {% endif %}
          <span class="badge badge-info">{{ q.severity }}</span>
        </div>
        <div class="incident-detail">{{ q.timestamp }} | {{ q.details_short }}</div>
      </div>
      {% endfor %}
      {% if not qa_results %}
      <div style="color:var(--muted); padding:10px;">Sin auditorías QA registradas.</div>
      {% endif %}
    </div>
  </div>

  <!-- EVALUACIONES EXTERNAS -->
  <div class="card">
    <h2><span class="dot dot-green"></span> Evaluaciones e Informes Externos</h2>
    <div class="scroll-box">
      {% for ev in evaluaciones %}
      <div class="incident-block">
        <div class="incident-title">{{ ev.key }} <span class="badge badge-info">EXTERNAL</span></div>
        <div class="incident-detail">
          Autor: {{ ev.autor }}<br>
          Fecha: {{ ev.fecha }}<br>
          Conclusión: {{ ev.conclusion[:120] }}...
        </div>
      </div>
      {% endfor %}
      {% if not evaluaciones %}
      <div style="color:var(--muted); padding:10px;">Sin evaluaciones externas registradas.</div>
      {% endif %}
    </div>
  </div>

  <!-- DELIBERACIONES DE SABIOS HISTÓRICAS -->
  <div class="card full">
    <h2><span class="dot dot-green"></span> Historial de Deliberaciones del Tribunal</h2>
    <div class="scroll-box">
      <table>
        <tr><th>ID</th><th>Fecha</th><th>Prompt</th><th>Modelos</th><th>Atendieron</th><th>Tiempo</th></tr>
        {% for d in deliberaciones %}
        <tr>
          <td>{{ d.key }}</td>
          <td>{{ d.timestamp }}</td>
          <td style="max-width:300px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{{ d.prompt[:60] }}</td>
          <td>{{ d.total }}</td>
          <td>
            {% if d.atendieron == d.total %}
              <span class="badge badge-ok">{{ d.atendieron }}/{{ d.total }}</span>
            {% else %}
              <span class="badge badge-warn">{{ d.atendieron }}/{{ d.total }}</span>
            {% endif %}
          </td>
          <td>{{ d.tiempo }}s</td>
        </tr>
        {% endfor %}
      </table>
    </div>
  </div>

</div>

</body>
</html>
"""

@app.route("/")
def dashboard():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Tribunal de los 17 Sabios (última sesión)
    tribunal_data = query_vault("tribunal_plenario_17", 1)
    sabios = []
    sabios_count = 0
    if tribunal_data and isinstance(tribunal_data[0]["value"], dict):
        t = tribunal_data[0]["value"]
        sabios_count = t.get("atendieron", 0)
        for s in t.get("sabios", []):
            sabios.append({
                "id": s.get("id", 0),
                "nombre": s.get("nombre", "?"),
                "canal": s.get("canal", "?"),
                "latencia_ms": s.get("latencia_ms", 0),
                "dictamen": s.get("dictamen", "Sin dictamen")
            })

    # 2. QA Adversarial Hound
    qa_data = query_vault("qa_adversarial_hound", 30)
    qa_results = []
    qa_passed = 0
    qa_failed = 0
    for q in qa_data:
        v = q["value"]
        if isinstance(v, dict):
            passed = v.get("passed", False)
            if passed:
                qa_passed += 1
            else:
                qa_failed += 1
            details = v.get("details", {})
            details_short = ""
            if isinstance(details, dict):
                if "latency" in details:
                    details_short += f"Latencia: {details['latency']}s "
                if "sample" in details:
                    details_short += f"| Muestra: {str(details['sample'])[:50]}"
                if "error" in details:
                    details_short += f"| Error: {str(details['error'])[:60]}"
                if "defect" in details:
                    details_short += f"| Defecto: {details['defect']}"
            qa_results.append({
                "hound": v.get("hound", "?"),
                "test": v.get("test", "?"),
                "severity": v.get("severity", "INFO"),
                "passed": passed,
                "timestamp": v.get("timestamp", "?"),
                "details_short": details_short or str(details)[:80]
            })

    # 3. Evaluaciones externas
    eval_data = query_vault("EVALUACION_KAGGLE_RAFAEL", 10)
    evaluaciones = []
    for e in eval_data:
        v = e["value"]
        if isinstance(v, dict):
            evaluaciones.append({
                "key": e["key"],
                "autor": v.get("autor_informe", "?"),
                "fecha": v.get("informe_fecha", "?"),
                "conclusion": v.get("conclusion_clave", "Sin conclusión")
            })

    # 4. Historial deliberaciones
    delib_data = query_vault("tribunal_plenario_17", 20)
    deliberaciones = []
    for d in delib_data:
        v = d["value"]
        if isinstance(v, dict):
            deliberaciones.append({
                "key": d["key"],
                "timestamp": v.get("timestamp", "?"),
                "prompt": v.get("prompt", "?"),
                "total": v.get("total_sabios", 0),
                "atendieron": v.get("atendieron", 0),
                "tiempo": v.get("tiempo_total_s", 0)
            })
    # Also add sabios_deliberations from the old dispatcher
    delib_old = query_vault("sabios_deliberations", 20)
    for d in delib_old:
        v = d["value"]
        if isinstance(v, dict):
            deliberaciones.append({
                "key": d["key"],
                "timestamp": v.get("timestamp", "?"),
                "prompt": v.get("prompt", "?"),
                "total": v.get("total_consultadas", 0),
                "atendieron": v.get("participating_models", 0),
                "tiempo": "?"
            })

    total_incidents = len(qa_data)

    return render_template_string(
        DASHBOARD_HTML,
        now=now,
        sabios=sabios,
        sabios_count=sabios_count,
        qa_results=qa_results,
        qa_passed=qa_passed,
        qa_failed=qa_failed,
        total_incidents=total_incidents,
        evaluaciones=evaluaciones,
        eval_count=len(evaluaciones),
        deliberaciones=deliberaciones
    )

@app.route("/api/sabios")
def api_sabios():
    return jsonify(query_vault("tribunal_plenario_17", 5))

@app.route("/api/qa")
def api_qa():
    return jsonify(query_vault("qa_adversarial_hound", 30))

@app.route("/api/eval")
def api_eval():
    return jsonify(query_vault("EVALUACION_KAGGLE_RAFAEL", 10))

if __name__ == "__main__":
    print("=" * 70)
    print("  POLYDIM — Panel de Control de Silicio")
    print("  Accesible en: http://0.0.0.0:5000")
    print("  Desde ALADIN: http://<IP_NODE1>:5000")
    print("=" * 70)
    app.run(host="0.0.0.0", port=5000, debug=False)
