# GUÍA DE LABORATORIO Y REPRODUCIBILIDAD (UTN-FRBA)
## Cátedra de Inteligencia Artificial y Sistemas Distribuidos
**Docente:** Ariel García Traba  
**Proyecto:** POLYDIM-EINSOF (Cognitive High-Dimensional Architecture)

---

## 🎯 OBJETIVO PEDAGÓGICO
Demostrar experimentalmente en silicio real que la cognición de redes neuronales y agentes inteligentes es intrínsecamente de **alta dimensión** ($S^{D-1}, D \ge 10^4$), y que obligar a los modelos a serializar sus estados intermedios a cadenas de texto o tokens 1D genera una pérdida destructiva de entropía e información (según la Desigualdad de Procesamiento de la Información - DPI).

---

## 🚀 PASO 1: VERIFICACIÓN RÁPIDA (QUICKSTART)

Sin instalar dependencias externas ni librerías pesadas, ejecutá en tu terminal:

```bash
python quickstart_harness.py
```

El script interroga automáticamente tu procesador (AMD, Intel, Apple Silicon o ARM) y ejecuta 3 pruebas matemáticas en silicio:
1. **Normalización Hiperesférica:** Vector en $D = 10.000$ con desviación $\|x\| - 1 \le 10^{-14}$.
2. **Aritmética Exacta de Kulisch:** Prevención de desbordamiento y subnormales ($10^{-315}$).
3. **Retracción de Stiefel:** Preservación de ortogonalidad en variedades no euclidianas.

**Criterio de Aprobación:** `Exit Code 0` en pantalla.

---

## 🔬 TRES TRABAJOS PRÁCTICOS DE LABORATORIO

### Laboratorio 1: Comunicación Inter-Proceso Tensor-Nativa (PMTP Zero-Copy)
* **Problema:** El intercambio de representaciones latentes mediante JSON degrada el ancho de banda a $< 50$ MB/s y desperdicia ciclos de CPU en serialización de strings.
* **Solución POLYDIM:** Memoria compartida nativa (`PmtpSlabAllocator` en C++ y Rust) con descriptor wire canónico de 120 bytes.
* **Consigna para el Alumno:**
  1. Abrir `PMTP_V4_CORE/TRIADIC_FUSION/harness_triadic_fusion.py`.
  2. Ejecutar la sincronización entre el Productor en Rust y el Consumidor en Python.
  3. Medir con el monitor la latencia en microsegundos y verificar ausencia de copias intermedias en el heap.

### Laboratorio 2: Acumulador Exacto de Kulisch (SuperaccV 8.768 Bytes)
* **Problema:** La adición en coma flotante IEEE 754 de 64 bits (`double`) **no es asociativa**. En sumatorias masivas ($D \ge 10^6$), los números pequeños se pierden frente a los grandes (catastrophic cancellation).
* **Solución POLYDIM:** El acumulador exacto `SuperaccV` implementado en C++20 con alineación a 64 bytes (`alignas(64)`) y limbs de 64 bits que cubre desde $2^{-1074}$ hasta $2^{1023}$ sin error de redondeo.
* **Consigna para el Alumno:**
  1. Compilar y ejecutar `e25_kulisch_exact_integer_harness.exe`.
  2. Verificar que la suma de $10.000$ productos subnormales genera exactamente **0 NaNs** y preserva la precisión del bit menos significativo.

### Laboratorio 3: Navegación de los 1.571 Teoremas en PostgreSQL 16
* **Problema:** En sistemas de producción de misión crítica, ningún algoritmo puede ser una "caja negra" sin respaldo formal.
* **Solución POLYDIM:** Cada invariante de código está respaldado por un teorema certificado y auditado con Perplexity Sonar-Pro en la base de datos `polydim_vec_db`.
* **Consigna para el Alumno:**
  1. Abrir `TABLA_MAESTRA_TEOREMA_SILICIO_1571.md`.
  2. Seleccionar un teorema de cada vector:
     * Vector A (Memoria y FFI)
     * Vector B (Geometría Stiefel y Kulisch)
     * Vector C (Concurrencia Lock-Free y QSBR)
     * Vector D (Triton GPU y TPU JAX)
  3. Encontrar en el archivo de código la función exacta que implementa el teorema seleccionado y verificar su comentario de certificación.
