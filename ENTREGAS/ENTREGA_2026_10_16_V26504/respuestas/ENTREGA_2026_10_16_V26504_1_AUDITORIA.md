# AUDITORÍA DE LA ACTUALIZACIÓN — ENTREGA_2026_10_16_V26504_1

**Archivo auditado:** `ENTREGA_2026_10_16_V26504_1.rar` (43 archivos: 42 de V26502 + setup.py; RAR5, todos con CRC32 correcto).  
**Referencia de comparación:** `ENTREGA_2026_10_16_V26502.rar` y su informe `ENTREGA_2026_10_16_V26502_AUDITORIA.md`.  
**Prefijo de nuevos hallazgos:** `V4-`

---

## 0. Resumen Ejecutivo y Veredicto

La actualización corrige bien una parte del núcleo C++ y lo demás no acompaña. El paquete, tal como se entrega, no es utilizable de extremo a extremo:

1. **Desalineación ABI Crítica:** Solo cambian 6 archivos. Los kernels C++ y Rust pasan a versión de protocolo 26503 y a símbolos `_v26503`. El monolito Python (`PMTP_VERSION = 26501`, símbolos `_v26502`), Dart (26502), el test cruzado y el README no se actualizaron. Ningún consumidor enlaza los kernels nuevos; el monolito cae silenciosamente a Python (13/13 passed falsos) sin tocar silicio.
2. **setup.py genera un paquete inusable:** Falla en `import polydim` (`No module named 'polydim.core'`) al faltar `__init__.py` en los subdirectorios.
3. **C++ claim_writer sube generación en slab nunca publicado:** La recuperación por obsolescencia calcula `rec_gen = (cur >> 2) + 1`, permitiendo que un lector acepte ceros como snapshot válido.
4. **Ruptura de Paridad C++ vs. Rust:** El nuevo `dot` de C++ (con `two_prod`) difiere bit a bit de Rust en el 42.5% de pares gaussianos y en el 100% de vectores casi ortogonales.
5. **Divergencia Semántica Rust vs C++:** En CAM con $q = 0$, C++ devuelve la media uniforme de $V$; Rust devuelve ceros. Rust sigue incrementando generación en `abort` y `force_recover`.
6. **Harness Triton Retroactivo (V4-TST-01):** En V26502 las 22 aserciones eran `if not (cond, "msg"):` (tupla siempre verdadera; nunca podía fallar). Corregido en V26504_1.

---

## 1. Tabla de Nuevos Hallazgos Principales

| ID | Sev. | Ev. | Resumen |
|---|---|---|---|
| **V4-PKG-01** | **Crítica** | **[R]** | Versión de protocolo y nombres de símbolo/archivo incoherentes entre kernels (26503), monolito (26501/_v26502), Dart (26502), test cruzado y README. |
| **V4-PKG-02** | **Alta** | **[R]** | `setup.py` produce un paquete que falla en `import polydim` (`No module named 'polydim.core'`) y no incluye binarios. |
| **V4-CPP-01** | **Alta** | **[R]** | `claim_writer` (recuperación por obsolescencia) sigue subiendo la generación en slab nunca publicado: lector acepta ceros como snapshot válido. |
| **V4-CPP-02** | **Media** | **[R]** | Carrera residual de limpieza post-CAS: 1 TOKEN_MISMATCH en 14.3 M publicaciones con lock retenido. TSan reporta 8 sitios. |
| **V4-CPP-03** | **Alta** | **[R]** | El `dot` nuevo de C++ (con `two_prod`) difiere bit a bit de Rust en 42.5% de pares gaussianos y 500/500 casi ortogonales. |
| **V4-RST-01** | **Alta** | **[E]** | Rust `abort_writer` y `force_recover` siguen sumando 1 a la generación: slab nunca publicado pasa a gen 1. |
| **V4-RST-02** | **Media** | **[E]** | Protocolos de limpieza opuestos: Rust limpia antes del CAS; C++ limpia después. |
| **V4-RST-03** | **Media** | **[E]** | `validate_snapshot` difiere: C++ ignora bit 0; Rust exige `(s & 1) == 0`. |
| **V4-TST-01** | **Alta** | **[R]** | Las 22 aserciones del harness Triton de V26502 eran `if not (cond, "msg"):` (tupla siempre verdadera). V26504_1 lo corrige. |

---

## 2. Parches Quirúrgicos Requeridos

### 2.1 V4-CPP-01 y V4-RST-01 (No subir generación en recuperación de slab no publicado)
```diff
--- kernel_cpp_v26503.cpp
+++ kernel_cpp_v26503.cpp
-                    std::uint64_t rec_gen = (cur >> 2) + 1;
+                    std::uint64_t rec_gen = (cur >> 2);        // recuperación no publica nuevos datos
```
En Rust:
```diff
--- kernel_rust_v26503.rs
+++ kernel_rust_v26503.rs
-                        let next_gen = cur_gen + 1;
+                        let next_gen = cur >> 2;
```

### 2.2 V4-PKG-01: Exposición de Alias de Compatibilidad ABI
En C++ y Rust, registrar alias explícitos `_v26502` para que el monolito y Dart enlacen sin caer en fallback silencioso, mientras se migra el monolito a `PMTP_VERSION = 26503`.

### 2.3 V4-PKG-02: Reparación de setup.py y __init__.py
Agregar `__init__.py` en `polydim/core/`, `polydim/adapters/`, `polydim/transport/` y `polydim/distill/`.
Usar `find_namespace_packages()` en `setup.py` y declarar `install_requires=["numpy"]`.

### 2.4 V4-CPP-03: Paridad bit a bit con Rust
Portar `two_prod` con `f64::mul_add` a Rust, o calibrar la suite de prueba cruzada para admitir acumulación compensada estricta.
