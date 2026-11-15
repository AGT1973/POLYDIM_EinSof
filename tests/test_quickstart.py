import subprocess
import sys
import os

def test_quickstart_execution():
    script_path = os.path.join(os.path.dirname(__file__), "..", "examples", "quickstart_dual_model_transfer.py")
    res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    assert res.returncode == 0, f"Error en quickstart: {res.stderr}"
    assert ">>> LATENCIA TOTAL TRANSFERENCIA" in res.stdout
    assert "Error Cuadrático Medio: 0.00e+00" in res.stdout
