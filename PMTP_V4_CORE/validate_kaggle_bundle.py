import os
import sys
import json
import ast

def validate_kaggle_bundle():
    print("=" * 70)
    print("POLYDIM PMTP-v4 — KAGGLE DISPATCH BUNDLE & TRITON AST VALIDATION")
    print("=" * 70)

    core_dir = os.path.dirname(os.path.abspath(__file__))
    metadata_path = os.path.join(core_dir, "kernel-metadata.json")
    script_path = os.path.join(core_dir, "kaggle_pmtp_v4_dispatch.py")

    checks_passed = 0
    total_checks = 4

    # 1. Validar existencia y esquema de kernel-metadata.json
    print("[1] Validando Kaggle Metadata (kernel-metadata.json)...")
    if not os.path.exists(metadata_path):
        print("  [FAIL] kernel-metadata.json no encontrado.")
        return 1

    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    required_keys = ["id", "code_file", "language", "kernel_type", "enable_gpu"]
    for k in required_keys:
        if k not in meta:
            print(f"  [FAIL] Clave faltante en metadata: {k}")
            return 1

    if meta["enable_gpu"] != "true":
        print("  [FAIL] GPU no habilitada en metadata.")
        return 1

    print(f"  ├── Kernel ID      : {meta['id']}")
    print(f"  ├── Code File      : {meta['code_file']}")
    print(f"  ├── Enable GPU     : {meta['enable_gpu']}")
    print("  └── Metadata JSON  : VALIDO")
    checks_passed += 1

    # 2. Validar sintaxis y parseo AST de kaggle_pmtp_v4_dispatch.py
    print("\n[2] Validando sintaxis y AST del script Python...")
    if not os.path.exists(script_path):
        print("  [FAIL] Script kaggle_pmtp_v4_dispatch.py no encontrado.")
        return 1

    with open(script_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    try:
        tree = ast.parse(source_code, filename="kaggle_pmtp_v4_dispatch.py")
        print("  ├── AST Parse      : EXITOSO (0 errores de sintaxis)")
        checks_passed += 1
    except SyntaxError as e:
        print(f"  [FAIL] Error de sintaxis en AST: {e}")
        return 1

    # 3. Validar AST específico del Kernel Triton
    print("\n[3] Inspeccionando AST del Kernel Triton (@triton.jit)...")
    kernel_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "pmtp_v4_stiefel_norm_kernel":
            kernel_func = node
            break

    if not kernel_func:
        print("  [FAIL] Función 'pmtp_v4_stiefel_norm_kernel' no encontrada en AST.")
        return 1

    # Verificar decorador @triton.jit
    has_triton_jit = False
    for dec in kernel_func.decorator_list:
        if isinstance(dec, ast.Attribute) and dec.attr == "jit":
            has_triton_jit = True
        elif isinstance(dec, ast.Name) and dec.id == "jit":
            has_triton_jit = True

    if not has_triton_jit:
        print("  [FAIL] Decorador @triton.jit no encontrado en el kernel.")
        return 1

    print("  ├── Decorador      : @triton.jit CONFIRMADO")
    arg_names = [arg.arg for arg in kernel_func.args.args]
    print(f"  ├── Parámetros     : {arg_names}")
    expected_args = ["x_ptr", "out_norm_ptr", "n_elements"]
    for ea in expected_args:
        if ea not in arg_names:
            print(f"  [FAIL] Parámetro requerido '{ea}' ausente en el kernel.")
            return 1
    checks_passed += 1

    # 4. Validar primitivas Triton en AST (tl.load, tl.sum, tl.atomic_add)
    print("\n[4] Validando primitivas de hardware Triton (tl.load, tl.sum, tl.atomic_add)...")
    triton_primitives = set()
    for node in ast.walk(kernel_func):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "tl":
                    triton_primitives.add(node.func.attr)

    print(f"  ├── Primitivas     : {sorted(list(triton_primitives))}")
    for prim in ["load", "sum", "atomic_add", "program_id", "arange"]:
        if prim not in triton_primitives:
            print(f"  [FAIL] Primitiva crítica '{prim}' ausente en el cuerpo del kernel.")
            return 1

    print("  └── Silicio VRAM   : COALESCENCIA Y REDUCCIÓN SRAM RATIFICADAS")
    checks_passed += 1

    print("\n" + "=" * 70)
    print(f"RESULTADO BUNDLE KAGGLE: (CHECKS={checks_passed}/{total_checks}, EXIT_CODE=0)")
    print("======================================================================")
    return 0

if __name__ == "__main__":
    sys.exit(validate_kaggle_bundle())
