# Integración de PCs del Equipo (Facundo, Andrea y Joaquín)

Este kit prepara la PC de cada integrante para operar contra **ALADIN (`192.168.100.21`)** sin exponer claves en Git ni en carpetas compartidas.

## 1. Requisitos en la PC cliente (Windows)
- Python 3.10+ con `numpy` (`pip install numpy`)
- Conectividad LAN o VPN/Tailscale hacia `192.168.100.21`

## 2. Instalación inicial
Ejecutar en PowerShell (reemplazar `<miembro>` por `facundo`, `andrea` o `joaquin`):
```powershell
powershell -ExecutionPolicy Bypass -File .\setup_team_pc.ps1 -Miembro <miembro>
```
Esto crea `%USERPROFILE%\.gandalf_vault` con permisos `icacls` exclusivos del usuario local y `SYSTEM`, copia `sabios_dispatcher.py` + `helena_carrier_bridge.py` en `C:\POLYDIM_CLIENT`, y valida acceso a ALADIN (`:11434` y `:9999`).

## 3. Política de Mínimo Costo
- Por defecto (`--dry-run` o consulta directa): usa **ALADIN/Ollama local + Free-Tier ($0 USD)**.
- Solo si el usuario autorizado necesita APIs pagas y cuenta con su `.gandalf_vault` habilitado por Ariel/Gandalf, se usa `--paid`.
