#!/usr/bin/env python3
"""Rule 10 Anti-Leak regression guard for git-tracked files in E:\\SUITE."""

import re
import subprocess
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parent.parent

SECRET_PATTERNS = [
    ("CEREBRAS_KEY", re.compile(r"csk-[A-Za-z0-9]{20,}")),
    ("HF_TOKEN", re.compile(r"hf_[A-Za-z0-9]{20,}")),
    ("GITLAB_PAT", re.compile(r"glpat-[A-Za-z0-9_\-]{15,}")),
    ("GROQ_KEY", re.compile(r"gsk_[A-Za-z0-9]{20,}")),
    ("BAILIAN_KEY", re.compile(r"sk-ws-[A-Za-z0-9._\-]{20,}")),
    ("GOOGLE_API_KEY", re.compile(r"AIzaSy[A-Za-z0-9_\-]{25,}")),
]

TEXT_EXTS = {".py", ".md", ".json", ".ps1", ".sh", ".bat", ".txt", ".yml", ".yaml", ".toml"}


def test_no_leaked_secrets_in_tracked_files():
    import shutil
    git_bin = shutil.which("git")
    candidate_files = []
    if git_bin and (SUITE_ROOT / ".git").exists():
        try:
            res = subprocess.run([git_bin, "-C", str(SUITE_ROOT), "ls-files"], capture_output=True, text=True, check=True)
            for rel in res.stdout.splitlines():
                candidate_files.append(SUITE_ROOT / rel)
        except Exception:
            candidate_files = []

    if not candidate_files:
        for p in SUITE_ROOT.rglob("*"):
            if p.is_file() and not any(part.startswith(".") for part in p.relative_to(SUITE_ROOT).parts):
                candidate_files.append(p)

    leaks = []
    for p in candidate_files:
        if not p.is_file() or p.suffix.lower() not in TEXT_EXTS:
            continue
        rel = p.relative_to(SUITE_ROOT)
        content = p.read_text(encoding="utf-8", errors="ignore")
        for label, rx in SECRET_PATTERNS:
            for m in rx.finditer(content):
                val = m.group(0)
                if any(marker in val for marker in ("TU_TOKEN", "EXAMPLE", "XXXX", "your_")):
                    continue
                leaks.append(f"{rel}: {label} ({val[:10]}...)")
    assert not leaks, f"Rule 10 violation — leaked secrets detected: {leaks}"
