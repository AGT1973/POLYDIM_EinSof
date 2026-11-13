# Reproducible 1-Command Auditor Environment for POLYDIM SUITE
# Usage:
#   docker build -t polydim-audit . && docker run --rm --ipc=private polydim-audit
FROM python:3.12.7-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    rustc \
    cargo \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 pmtpuser && \
    pip install --no-cache-dir numpy==2.1.3 pytest==8.3.4

WORKDIR /workspace
COPY . /workspace

RUN sed -i 's/\r$//' scripts/run_full_audit.sh && \
    chmod +x scripts/run_full_audit.sh && \
    chown -R pmtpuser:pmtpuser /workspace

USER pmtpuser
CMD ["bash", "scripts/run_full_audit.sh"]
