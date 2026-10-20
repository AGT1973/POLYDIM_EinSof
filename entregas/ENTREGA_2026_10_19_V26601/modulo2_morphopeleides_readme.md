# ENTREGA V26600 — MÓDULO 2: MORPHO PELEIDES
## Verificación de Propiedades Matemáticas Adversariales

**Estado:** ✅ 7/7 PASS | EXIT CODE 0  
**Evaluadores:** Perplexity Sonar-Pro + Claude 3.5 Sonnet (Red Team Dialéctico)

---

## ¿Qué es MorphoPeleides?

MorphoPeleides es el sistema de **transmisión de estados cognitivos latentes** a través del puente Stiefel-PMTP. Toma las representaciones internas de un modelo de lenguaje (e.g. Qwen2.5-0.5B) y las descompone en coordenadas esféricas $(u, \rho)$ donde:

- $u \in S^{D-1}$: Dirección unitaria (qué información)
- $\rho = \|z\|_2$: Amplitud (cuánta información)

El objetivo es que estas coordenadas puedan transmitirse sin pérdida a través del bus PMTP (Zero-Copy en /dev/shm) entre procesos o nodos del clúster dual.

---

## Los 5 Contraejemplos Adversariales Verificados

### MP-48: Torn-Read sin Leases (Contraejemplo Válido)
**¿Qué muestra?** Sin protección por lease atómico, un lector puede observar una combinación imposible de datos: el primer elemento del snapshot A y el segundo del snapshot B sobrescrito.

```
Payload observado sin protección: (10.0, 40.0)
Payload legítimo A: (10, 10) | Payload B: (30, 30) | Payload C: (40, 40)
→ El valor (10, 40) es espurio e IMPOSIBLE sin el bug de concurrencia.
```

**Con leases atómicos PMTP:** el escritor rechaza sobreescribir el slot retenido. **El torn-read desaparece.**

### MP-49: PolarSafe — Umbral Relativo vs Absoluto
**El problema:** Si usamos un umbral absoluto de valor singular (`svd < 1e-8`) para detectar matrices mal condicionadas, rechazamos matrices bien condicionadas a pequeña escala (e.g. $I \cdot 10^{-9}$ tiene $\kappa = 1.0$ pero $\sigma_{min} = 10^{-9}$) y aceptamos matrices explosivas (e.g. $\text{diag}(10^9, 10^{-7})$ con $\kappa = 10^{16}$).

**Solución correcta:** usar el **número de condición relativo** $\kappa = \sigma_{max}/\sigma_{min}$.

### MP-50: Bypass Esférico Exacto con $\beta = 0$
La operación de inyección tangente `h_new = h + beta * W @ delta_z` debe retornar `h` exactamente cuando $\beta = 0$, independientemente de `delta_z`. La prueba verifica que la implementación con el residuo correcto `delta_z = rho * (u_new - u_old)` produce `h_good = h` con error de punto flotante $< 10^{-15}$.

### MP-51: NaN-Safety y Paridad de Cero con Signo
- `0.0 * NaN = NaN` (IEEE-754 inviolable): el bypass `beta = 0` no puede multiplicar un delta no finito para anularlo.
- `-0.0 + 0.0 = +0.0` (los bits del signo difieren): la preservación de estados que contienen `-0.0` requiere copia directa de bytes, no aritmética.
- Con `beta < 0`: la norma del incremento debe usar `|beta|`, no `beta`.

### MP-52: CAM Softmax con Claves Correlacionadas
La memoria asociativa (CAM) basada en softmax puede recuperar asociaciones correctas en 8/8 casos incluso cuando las claves están altamente correlacionadas ($\cos(\text{key}_i, \text{key}_j) \in [0.891, 0.930]$), siempre que la **temperatura sea lo suficientemente baja** (aquí $T = 0.01$).

---

## Instrucción de Ejecución

```bash
# Sin dependencias adicionales (solo numpy):
python morpho_redteam_v26600.py
```

**Salida esperada:**
```
[PASS] MP-48_ABA_without_leases_produces_torn_read
[PASS] MP-49_kappa_relative_good_matrix
[PASS] MP-49_kappa_relative_bad_matrix
[PASS] MP-50_spherical_bypass_beta0_exact
[PASS] MP-51_beta0_nan_is_nan
[PASS] MP-51_beta_negative_norm_absolute_value
[PASS] MP-52_CAM_softmax_accuracy_8_of_8
MODULO 2 MorphoPeleides: 7/7 PASS | Exit Code: 0
```
