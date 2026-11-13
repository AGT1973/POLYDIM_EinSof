# ============================================================================
# POLYDIM-SUITE Reproducible Verification Container
# Note: Docker mounts a private 64 MiB /dev/shm per container by default.
# Use `--shm-size=256m` only if allocating large slabs inside this container.
# `--ipc=host` is NOT needed for same-container tests and should remain unset
# to preserve IPC namespace isolation.
# ============================================================================
FROM python:3.12.7-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends g++ && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 pmtpuser
WORKDIR /app

COPY pyproject.toml README.md AGENT_BOOTSTRAP.md ./
COPY pmtp/ ./pmtp/
COPY tools/ ./tools/
COPY tests/ ./tests/

RUN pip install --no-cache-dir \
    numpy==2.1.3 \
    pytest==8.3.4 && \
    pip install --no-cache-dir --no-deps -e . && \
    chown -R pmtpuser:pmtpuser /app

USER pmtpuser
CMD ["pytest", "-v", "tests/"]
