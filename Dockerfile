# Reproducible 1-Command Auditor Environment for POLYDIM SUITE
# Usage:
#   docker build -t polydim-audit . && docker run --rm --ipc=private polydim-audit
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PMTP_SHM_KEY="POLYDIM_DOCKER_AUDIT_KEY_V1"

RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    rustc \
    cargo \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir numpy pytest

WORKDIR /workspace
COPY . /workspace

RUN sed -i 's/\r$//' scripts/run_full_audit.sh && chmod +x scripts/run_full_audit.sh

CMD ["bash", "scripts/run_full_audit.sh"]
