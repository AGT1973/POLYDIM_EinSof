# CUDA/Triton silicon validation harness

Este paquete **prepara la validación**, pero no contiene ni sustituye los fuentes reales del proyecto y no afirma que ya se haya ejecutado en una GPU remota. En esta conversación no se encontraron `kernel_cuda_v26250.cu.txt` ni `polydim_triton_kernel_v26250.py`; por eso el adapter es una plantilla y debe conectarse a sus APIs reales.

## Qué valida el arnés

- Verifica que PyTorch vea una GPU NVIDIA, ejecuta una operación CUDA real y sincroniza.
- Registra `nvidia-smi`, versión de `nvcc`, versiones de PyTorch/Triton y SHA-256 de fuentes/artefactos.
- Copia el `.cu.txt` a un `.cu` de compilación sin modificar el original.
- Compila con `nvcc -O3 -std=c++20 -arch=<arquitectura-detectada> -shared` y enlaza cuBLAS/cuSOLVER/CUDA Runtime.
- Carga la biblioteca `.so` con `ctypes`.
- Para certificar los kernels reales, exige un adapter que invoque sus APIs conocidas y entregue métricas reales. Solo ese camino puede imprimir `FULL_SILICON_VALIDATION_PASS` y devolver código final 0.

`--compile-only` sirve para aislar el paso de compilación, pero su log queda marcado `COMPILE_ONLY_NOT_CERTIFIED`: **no es prueba de ejecución del kernel del proyecto**.

## Preparar Colab o Kaggle

1. Abrir una sesión Linux con acelerador NVIDIA habilitado y subir/copiar estos archivos junto con los dos fuentes reales del proyecto.
2. Verificar que `nvcc --version`, `nvidia-smi` y `python -c "import torch, triton; print(torch.cuda.is_available())"` funcionan. Si el entorno incluye PyTorch CUDA pero no `nvcc`, escoger una imagen/toolkit que incluya el compilador; no confundir runtime con toolchain.
3. Rellenar `test_adapter_template.py` usando los nombres, firmas y tipos **reales** del `.cu` y la función real del módulo Triton. El adapter debe sincronizar después de cada lanzamiento, verificar errores CUDA, y medir con CUDA Events.
4. Ejecutar, para una NVIDIA T4:

```bash
python harness_cuda_silicon_test.py \
  --cuda-source kernel_cuda_v26250.cu.txt \
  --triton-source polydim_triton_kernel_v26250.py \
  --adapter test_adapter_template.py \
  --arch sm_75 \
  --work-dir .
```

Para una A100, usar `--arch sm_80`. El modo `--arch auto` selecciona la arquitectura que PyTorch detecte para la GPU presente. Compilar con `sm_75` en una A100 no es equivalente a compilar una imagen nativa `sm_80`; use la arquitectura real o pruebe explícitamente la compatibilidad.

5. El log crudo se escribe en `_HISTORICO/silicio_logs/silicio_cuda_<UTC>.log`. Archivar el log, el código exacto, sus SHA-256, el nombre de la GPU, las versiones de toolchain y los artefactos binarios juntos.

## Contrato del adapter

`run_silicon_tests(**kwargs)` debe devolver un diccionario con:

- `cuda_passed: True`
- `triton_passed: True`
- `orthogonality_error: número finito`, estrictamente menor que `1e-12` (configurable)
- `gpu_time_ms: número finito no negativo`, medido por eventos GPU
- `bitwise_deterministic: True`, demostrado comparando las salidas binarias de ejecuciones repetidas en la GPU reportada
- `synchronized_after_kernel: True`, después de comprobar el código de error en sincronización

No se debe marcar bitwise-determinism solamente porque la reducción tenga dos pasadas. Hay que medirlo en las condiciones declaradas. Tampoco debe interpretarse `1e-12` como universal: hay que verificar que el tipo de precisión, definición de norma y contrato numérico justifican ese umbral.

## Importante

Este entorno de ChatGPT no dispone de una GPU NVIDIA accesible ni de `nvcc`, y no se ha conectado a una sesión de Colab/Kaggle. Por tanto, todavía no existe un log de silicio real ni un `Exit Code 0` de esa prueba. Este paquete está diseñado para que el propio entorno de GPU produzca ese registro sin simular resultados.
