#!/usr/bin/env python3
"""Compile CUDA on an NVIDIA host and run project-specific silicon tests.

This harness deliberately does not guess the source project's C ABI. A project
adapter must call the real CUDA and Triton entry points and return measured
results. The harness returns exit code 0 only when compilation, dynamic loading,
GPU runtime smoke-test, and all adapter acceptance checks pass.
"""
from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
import platform
import shlex
import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any


class RunLog:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.handle = path.open("w", encoding="utf-8", newline="\n")

    def write(self, message: str = "") -> None:
        line = str(message)
        print(line, flush=True)
        self.handle.write(line + "\n")
        self.handle.flush()

    def close(self) -> None:
        self.handle.close()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_command(command: list[str], *, cwd: Path, log: RunLog,
                env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    log.write("\n$ " + shlex.join(command))
    log.write(f"[cwd] {cwd}")
    try:
        result = subprocess.run(
            command, cwd=str(cwd), env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
    except FileNotFoundError as exc:
        log.write(f"[launch error] {exc}")
        return subprocess.CompletedProcess(command, 127, "", str(exc))
    log.write("----- STDOUT BEGIN -----")
    log.write(result.stdout.rstrip("\n"))
    log.write("----- STDOUT END -----")
    log.write("----- STDERR BEGIN -----")
    log.write(result.stderr.rstrip("\n"))
    log.write("----- STDERR END -----")
    log.write(f"[command exit code] {result.returncode}")
    return result


def import_torch_and_probe(log: RunLog) -> tuple[Any | None, dict[str, Any]]:
    probe: dict[str, Any] = {}
    try:
        import torch  # type: ignore
        probe["torch_version"] = getattr(torch, "__version__", "unknown")
        probe["torch_cuda_build"] = getattr(torch.version, "cuda", None)
        probe["torch_cuda_available"] = bool(torch.cuda.is_available())
        if not torch.cuda.is_available():
            log.write("[GPU PROBE] torch.cuda.is_available() = False")
            return torch, probe
        index = torch.cuda.current_device()
        props = torch.cuda.get_device_properties(index)
        major, minor = torch.cuda.get_device_capability(index)
        probe.update({
            "cuda_device_index": int(index),
            "cuda_device_name": str(props.name),
            "compute_capability": f"{major}.{minor}",
            "compute_arch": f"sm_{major}{minor}",
            "device_total_memory_bytes": int(props.total_memory),
        })
        log.write("[GPU PROBE] " + json.dumps(probe, sort_keys=True))

        # A small actual device operation + synchronization. This checks the
        # CUDA runtime separately from project-specific kernel tests.
        n = 1024
        x = torch.arange(n, dtype=torch.float64, device="cuda")
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        observed = float((x * x).sum().item())
        end.record()
        torch.cuda.synchronize()
        expected = float(n * (n - 1) * (2 * n - 1) // 6)
        if observed != expected:
            raise RuntimeError(f"CUDA runtime smoke test mismatch: observed={observed}, expected={expected}")
        probe["cuda_runtime_smoke_test"] = "PASS"
        probe["cuda_runtime_smoke_ms"] = float(start.elapsed_time(end))
        log.write(f"[GPU RUNTIME SMOKE TEST] PASS; sumsq={observed:.0f}; synchronized=true; elapsed_ms={probe['cuda_runtime_smoke_ms']:.6f}")
        try:
            import triton  # type: ignore
            probe["triton_version"] = getattr(triton, "__version__", "unknown")
            log.write(f"[TRITON PROBE] import OK; version={probe['triton_version']}")
        except Exception as exc:
            probe["triton_import_error"] = repr(exc)
            log.write(f"[TRITON PROBE] import failed: {exc!r}")
        return torch, probe
    except Exception as exc:
        probe["gpu_probe_error"] = repr(exc)
        log.write("[GPU PROBE ERROR] " + repr(exc))
        log.write(traceback.format_exc())
        return None, probe


def load_adapter(adapter_path: Path, log: RunLog):
    module_name = "_cuda_silicon_test_adapter"
    if str(adapter_path.parent.resolve()) not in sys.path:
        sys.path.insert(0, str(adapter_path.parent.resolve()))
    spec = importlib.util.spec_from_file_location(module_name, adapter_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import adapter: {adapter_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    function = getattr(module, "run_silicon_tests", None)
    if not callable(function):
        raise RuntimeError("Adapter must define callable run_silicon_tests(**kwargs)")
    log.write(f"[ADAPTER] loaded {adapter_path} sha256={sha256_file(adapter_path)}")
    return function


def validate_metrics(metrics: Any, tolerance: float, log: RunLog) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not isinstance(metrics, dict):
        return False, ["adapter did not return a dictionary"]
    log.write("[ADAPTER METRICS JSON] " + json.dumps(metrics, sort_keys=True, default=str))

    for key in ("cuda_passed", "triton_passed", "bitwise_deterministic"):
        if metrics.get(key) is not True:
            failures.append(f"{key} must be true; got {metrics.get(key)!r}")

    error = metrics.get("orthogonality_error")
    if isinstance(error, bool) or not isinstance(error, (int, float)) or not math.isfinite(float(error)):
        failures.append("orthogonality_error must be a finite numeric Frobenius/operator norm reported by the adapter")
    elif float(error) < 0 or float(error) >= tolerance:
        failures.append(f"orthogonality_error={error!r} does not satisfy < {tolerance:g}")

    elapsed = metrics.get("gpu_time_ms")
    if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not math.isfinite(float(elapsed)) or float(elapsed) < 0:
        failures.append("gpu_time_ms must be a finite non-negative GPU-event timing measured by the adapter")

    # Require the adapter to acknowledge stream synchronization after its real
    # kernel calls; cudaGetLastError by itself is not sufficient.
    if metrics.get("synchronized_after_kernel") is not True:
        failures.append("synchronized_after_kernel must be true (check CUDA errors after device/stream synchronization)")
    for failure in failures:
        log.write("[ACCEPTANCE FAILURE] " + failure)
    return not failures, failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cuda-source", type=Path, default=Path("kernel_cuda_v26250.cu.txt"),
                        help="Existing CUDA source (the .txt suffix is OK).")
    parser.add_argument("--triton-source", type=Path, default=Path("polydim_triton_kernel_v26250.py"),
                        help="Existing project Triton source.")
    parser.add_argument("--adapter", type=Path, default=None,
                        help="Project-specific adapter implementing run_silicon_tests(**kwargs).")
    parser.add_argument("--arch", default="auto",
                        help="CUDA architecture, e.g. auto, sm_75 (T4), sm_80 (A100). Default: detect physical GPU.")
    parser.add_argument("--orthogonality-tol", type=float, default=1e-12,
                        help="Required strict bound for ||Y^T Y - I|| as reported by adapter (default: 1e-12).")
    parser.add_argument("--work-dir", type=Path, default=Path("."), help="Build/output root.")
    parser.add_argument("--log-dir", type=Path, default=Path("_HISTORICO/silicio_logs"),
                        help="Directory for timestamped raw logs.")
    parser.add_argument("--compile-only", action="store_true",
                        help="Compile/load/smoke-test only. Explicitly NOT a full kernel certification.")
    parser.add_argument("--clean-build", action="store_true", help="Delete build artifacts after a successful run (default: retain for audit/archive).")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = dt.datetime.now(dt.timezone.utc)
    stamp = started.strftime("%Y%m%dT%H%M%SZ")
    args.work_dir = args.work_dir.resolve()
    args.log_dir = (args.work_dir / args.log_dir).resolve() if not args.log_dir.is_absolute() else args.log_dir
    args.log_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.log_dir / f"silicio_cuda_{stamp}.log"
    log = RunLog(log_path)
    code = 1
    build_dir = args.work_dir / f"build_cuda_silicon_{stamp}"
    try:
        log.write("CUDA/TRITON SILICON VALIDATION LOG")
        log.write(f"UTC start: {started.isoformat()}")
        log.write(f"Host: {platform.platform()}")
        log.write(f"Python: {sys.version.replace(os.linesep, ' ')}")
        log.write(f"Working directory: {args.work_dir}")
        log.write(f"Log file: {log_path}")
        log.write("Acceptance policy: exit code 0 only for a full pass; compile-only is marked NOT CERTIFIED.")

        cuda_source = args.cuda_source.resolve()
        triton_source = args.triton_source.resolve()
        if not cuda_source.is_file():
            raise FileNotFoundError(f"CUDA source not found: {cuda_source}")
        if not triton_source.is_file():
            raise FileNotFoundError(f"Triton source not found: {triton_source}")
        log.write(f"CUDA source: {cuda_source}; sha256={sha256_file(cuda_source)}")
        log.write(f"Triton source: {triton_source}; sha256={sha256_file(triton_source)}")

        torch, probe = import_torch_and_probe(log)
        if torch is None or not probe.get("torch_cuda_available") or probe.get("cuda_runtime_smoke_test") != "PASS":
            raise RuntimeError("A working physical NVIDIA CUDA runtime was not verified; refusing to certify this run.")
        if "triton_version" not in probe:
            raise RuntimeError("Triton cannot be imported in this GPU environment; cannot certify both kernels.")

        nvidia_smi = shutil.which("nvidia-smi")
        if nvidia_smi:
            run_command([nvidia_smi, "-L"], cwd=args.work_dir, log=log)
            run_command([nvidia_smi, "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"], cwd=args.work_dir, log=log)
        else:
            log.write("[WARNING] nvidia-smi not found, though PyTorch reported a functioning CUDA runtime.")

        nvcc = shutil.which("nvcc")
        if not nvcc:
            raise FileNotFoundError("nvcc is not on PATH. The GPU runtime alone is not enough for this compilation proof.")
        nvcc_info = run_command([nvcc, "--version"], cwd=args.work_dir, log=log)
        if nvcc_info.returncode != 0:
            raise RuntimeError("nvcc --version failed")

        if args.arch == "auto":
            arch = str(probe["compute_arch"])
        else:
            arch = args.arch
        if not arch.startswith("sm_") or not arch[3:].isdigit():
            raise ValueError(f"Invalid --arch {arch!r}; expected auto or e.g. sm_75")
        log.write(f"[BUILD TARGET] -arch={arch}; detected physical GPU capability={probe['compute_capability']}")
        if arch != probe["compute_arch"]:
            log.write("[WARNING] Build architecture differs from the detected device. Runtime compatibility must be demonstrated by the tests.")

        build_dir.mkdir(parents=True, exist_ok=True)
        normalized_source = build_dir / "kernel_cuda_v26250.cu"
        shutil.copy2(cuda_source, normalized_source)
        library_path = build_dir / "libpolydim_cuda.so"
        command = [
            nvcc, "-O3", "-std=c++20", "-Xcompiler", "-fPIC", "-arch=" + arch,
            "-shared", str(normalized_source), "-I", str(cuda_source.parent),
            "-lcudart", "-lcublas", "-lcusolver", "-o", str(library_path),
        ]
        log.write("[NVCC BUILD] normalized .cu source is a copy; original file remains unchanged")
        compile_result = run_command(command, cwd=args.work_dir, log=log)
        log.write(f"[NVCC EXIT CODE] {compile_result.returncode}")
        if compile_result.returncode != 0:
            raise RuntimeError(f"nvcc compilation failed with exit code {compile_result.returncode}")
        if not library_path.is_file() or library_path.stat().st_size == 0:
            raise RuntimeError("nvcc returned success but the shared library is missing or empty")
        log.write(f"[BINARY] {library_path}; bytes={library_path.stat().st_size}; sha256={sha256_file(library_path)}")

        # Force dynamic-loader resolution before invoking any project symbols.
        ctypes.CDLL(str(library_path), mode=ctypes.RTLD_LOCAL)
        log.write("[CTYPES LOAD] PASS: shared library loaded into this process")
        nm = shutil.which("nm")
        if nm:
            run_command([nm, "-D", "--defined-only", str(library_path)], cwd=args.work_dir, log=log)

        if args.compile_only:
            log.write("[RESULT] COMPILE_ONLY_NOT_CERTIFIED: compilation/load/GPU smoke test passed, but project CUDA/Triton kernels were not validated.")
            code = 0
        else:
            if args.adapter is None:
                raise RuntimeError("A project-specific --adapter is required. Without the actual source/API, the harness will not guess function signatures or claim kernel execution.")
            adapter_path = args.adapter.resolve()
            if not adapter_path.is_file():
                raise FileNotFoundError(f"Adapter not found: {adapter_path}")
            runner = load_adapter(adapter_path, log)
            output_dir = build_dir / "test_outputs"
            output_dir.mkdir(parents=True, exist_ok=True)
            metrics = runner(
                library_path=str(library_path),
                cuda_source=str(cuda_source),
                triton_source=str(triton_source),
                output_dir=str(output_dir),
                orthogonality_tolerance=float(args.orthogonality_tol),
                log=log.write,
            )
            passed, failures = validate_metrics(metrics, float(args.orthogonality_tol), log)
            if not passed:
                raise RuntimeError("One or more project-specific acceptance checks failed: " + "; ".join(failures))
            log.write("[RESULT] FULL_SILICON_VALIDATION_PASS")
            code = 0

        if args.clean_build and code == 0:
            log.write("[CLEANUP] --clean-build requested; removing build directory after recording artifact hashes.")
            shutil.rmtree(build_dir, ignore_errors=True)
        elif build_dir.exists():
            log.write(f"[BUILD ARTIFACTS] retained at {build_dir}")
    except Exception as exc:
        log.write(f"[FATAL] {type(exc).__name__}: {exc}")
        log.write(traceback.format_exc())
        log.write("[RESULT] FAIL_OR_INCOMPLETE")
        code = 1
    finally:
        finished = dt.datetime.now(dt.timezone.utc)
        log.write(f"UTC finish: {finished.isoformat()}")
        log.write(f"Duration seconds: {(finished - started).total_seconds():.3f}")
        log.write(f"HARNESS EXIT CODE: {code}")
        log.close()
    print(f"\nRaw log: {log_path}", flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
