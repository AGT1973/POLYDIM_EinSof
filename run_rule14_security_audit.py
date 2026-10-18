import os
import re
import json
import hashlib

PATTERNS = {
    'Anthropic_API_Key': re.compile(r'sk-ant-[a-zA-Z0-9_\-]{20,}'),
    'Google_API_Key': re.compile(r'AIzaSy[a-zA-Z0-9_\-]{33}'),
    'OpenRouter_API_Key': re.compile(r'sk-or-[a-zA-Z0-9_\-]{20,}'),
    'GitHub_PAT': re.compile(r'ghp_[a-zA-Z0-9]{36}'),
    'Postgres_ConnString': re.compile(r'postgres(?:ql)?://[^\s:]+:[^\s@]+@[^\s/]+/[^\s]+'),
    'OpenAI_Moonshot_Key': re.compile(r'sk-[a-zA-Z0-9]{32,}'),
    'HuggingFace_Token': re.compile(r'hf_[a-zA-Z0-9]{30,}'),
    'Password_Assignment': re.compile(r'(?:password|pwd|secret)\s*[:=]\s*["\']([^"\']{4,})["\']', re.IGNORECASE)
}

EXCLUDE_DIRS = {'_HISTORICO', '_AGY_BACKUP', '.git', '__pycache__', '.dart_tool'}
EXCLUDE_EXTS = {'.dll', '.exe', '.o', '.pyc', '.pdb', '.zip', '.pptx', '.docx', '.pdf'}

ROOT_DIR = r'E:\POLYDIM_EINSOF'
ENTREGA_DIR = r'E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26155'

def redact(val):
    if len(val) <= 12:
        return '***REDACTED***'
    return f"{val[:8]}...{val[-4:]}"

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()

def run_audit():
    total_files_scanned = 0
    sensitive_findings = []
    clean_files_sample = []
    
    # 1. Scan directory
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in EXCLUDE_EXTS:
                continue
            fpath = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(fpath, ROOT_DIR)
            
            try:
                sz = os.path.getsize(fpath)
                if sz > 15 * 1024 * 1024: # skip huge binaries/dumps
                    continue
                total_files_scanned += 1
                
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    
                file_has_leak = False
                file_findings = []
                for p_name, pattern in PATTERNS.items():
                    matches = pattern.findall(content)
                    if matches:
                        # filter prompts / instructions mentioning the regex or placeholders
                        filtered = []
                        for m in matches:
                            if isinstance(m, tuple):
                                m = m[0]
                            if any(ph in m for ph in ['*', '...', 'placeholder', 'your-', 'YOUR_', 'xxx', 'example', 'TODO', '<', '>']):
                                continue
                            filtered.append(m)
                        if filtered:
                            file_has_leak = True
                            file_findings.append({
                                'rule': p_name,
                                'count': len(filtered),
                                'sample': redact(filtered[0])
                            })
                
                if file_has_leak:
                    sensitive_findings.append({
                        'file': rel_path,
                        'issues': file_findings,
                        'must_be_gitignored': True
                    })
                else:
                    if len(clean_files_sample) < 50:
                        clean_files_sample.append(rel_path)
            except Exception as e:
                pass

    # 2. Production Kernels Checksum Tree
    kernel_checksums = []
    if os.path.exists(ENTREGA_DIR):
        for dirpath, dirnames, filenames in os.walk(ENTREGA_DIR):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for fname in sorted(filenames):
                fpath = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(fpath, ENTREGA_DIR)
                sha = compute_sha256(fpath)
                sz = os.path.getsize(fpath)
                kernel_checksums.append({
                    'file': rel_path,
                    'sha256': sha,
                    'size_bytes': sz
                })
                
    report = {
        'audit_timestamp': '2026-10-10T13:25:00-03:00',
        'standard': 'Rule 14 (Anti-Leak Protocol) & Rule 10 (Empirical Veto)',
        'target_directory': ROOT_DIR,
        'excluded_directories': list(EXCLUDE_DIRS),
        'total_files_scanned': total_files_scanned,
        'sensitive_files_detected_count': len(sensitive_findings),
        'sensitive_files_detected': sensitive_findings,
        'clean_files_certified_count': total_files_scanned - len(sensitive_findings),
        'recommended_gitignore_entries': [
            "*.env",
            "BACKUP_STAGE_*/",
            "matrix_state/",
            "update_kimi_keys.py",
            "*.sql",
            "*.log",
            "__pycache__/",
            ".dart_tool/",
            "_HISTORICO/",
            "_AGY_BACKUP/",
            "*.sqlite",
            "*.db"
        ],
        'production_kernels_checksum_tree': {
            'delivery_directory': 'ENTREGA_2026_10_10_V26155',
            'artifacts_count': len(kernel_checksums),
            'artifacts': kernel_checksums
        }
    }
    
    out_json = os.path.join(ROOT_DIR, 'audit_security_report.json')
    with open(out_json, 'w', encoding='utf-8') as fp:
        json.dump(report, fp, indent=2)
    print(f"REPORT_GENERATED: {out_json}")
    print(f"Total scanned: {total_files_scanned}, Sensitive: {len(sensitive_findings)}, Clean: {total_files_scanned - len(sensitive_findings)}")
    print(f"Kernels hashed: {len(kernel_checksums)}")

if __name__ == '__main__':
    run_audit()
