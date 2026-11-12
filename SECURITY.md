# Security Policy — POLYDIM SUITE

## Supported Versions

Only the latest release on the `main` branch receives active security updates and vulnerability verification.

| Version | Supported          | Security Status |
| ------- | ------------------ | --------------- |
| 1.0.x (main) | :white_check_mark: | Active Verification (CI/CD 9/9 OS Matrix) |
| < 1.0.0 | :x:                | Historical Preprints (Archived in Zenodo) |

---

## Security Model & Threat Boundaries

POLYDIM SUITE is designed under strict minimal-privilege and zero-attack-surface engineering standards:

1. **User-Space Operation Only (Zero-Root):**
   - The suite operates 100% within user-space permissions.
   - It **does not install** kernel drivers, system daemons, Windows services, or require `sudo` / Administrator privileges.

2. **Isolated Shared Memory IPC (`PmtpShmBus`):**
   - Inter-process communication uses operating system native shared memory APIs (`shm_open` on POSIX / `CreateFileMapping` on Win32).
   - Memory segments are strictly constrained to pre-allocated buffers with atomic seqlock generation counters.
   - Memory slabs are bounded, non-executable, and restricted to local process access.
   - Memory is explicitly unlinked and cleaned up via `bus.cleanup()` or context managers.

3. **Zero Network Egress & Zero Telemetry:**
   - POLYDIM SUITE contains **zero telemetry**, zero external analytics, zero tracking beacons, and zero port scanning.
   - All inter-agent communication is strictly local to the host machine's RAM/VRAM.

4. **Zero-Risk Degradation Contract (Safe Text Fallback):**
   - As implemented in `pmtp/pmtp_channel.py` and audited in `tests/test_channel_fallback.py`: if shared memory is unavailable, disabled, corrupt, or if an endpoint does not support PMTP, the system silently and deterministically degrades to standard UTF-8 text transfer with **zero exceptions** and **zero system disruption**.

5. **Sandbox & Cloud Verification (Colab 1-Click):**
   - For corporate environments or researchers evaluating the software without installing it locally, official 1-click sandboxes are provided on Google Colab (isolated temporary cloud containers with free NVIDIA T4 GPUs).

---

## Reporting a Vulnerability

We welcome responsible security disclosures from researchers, students, and institutional security auditors.

If you discover a security vulnerability, buffer defect, or memory leak in POLYDIM SUITE:

1. **Do not open a public GitHub issue.**
2. Email the lead researcher directly at:
   - **`polydim.einsof@gmail.com`**
3. Include:
   - A description of the vulnerability and potential attack vector.
   - Steps to reproduce (proof-of-concept script or command).
   - Environment details (OS, Python version, hardware).

### Response SLA:
- **Initial acknowledgment:** Within 24 hours.
- **Triage & severity assessment:** Within 48 hours.
- **Patch release & public advisory:** Within 7 calendar days.
