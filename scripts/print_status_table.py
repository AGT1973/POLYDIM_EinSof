import json
import os

tracker_file = r"E:\SUITE\scripts\hf_fleet_live_status.json"
if not os.path.exists(tracker_file):
    print("Tracker no existe aún.")
    exit(0)

with open(tracker_file, "r", encoding="utf-8") as f:
    tracker = json.load(f)

print("| # | Repositorio Hugging Face | Tipo / Base | Defecto Stiefel | Estado |")
print("| :---: | :--- | :--- | :---: | :---: |")
for item in tracker:
    status_icon = "⏳ Pendiente"
    if item["status"] == "HECHO":
        status_icon = "✅ HECHO"
    elif item["status"] == "EN_PROGRESO":
        status_icon = "🔄 EN PROGRESO"
    elif item["status"] == "ERROR":
        status_icon = f"❌ ERROR"
    
    defect = item["defect"] or "—"
    base = item["base"][:25]
    print(f"| {item['idx']} | `{item['repo_name']}` | {base} | `{defect}` | {status_icon} |")
