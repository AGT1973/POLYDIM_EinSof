# Auditoría matemática: aplicación exponencial y transporte paralelo en los colectores de Stiefel y Grassmann

**Fecha:** 25 de octubre de 2026  
**Alcance:** Fórmulas matriciales de la aplicación exponencial, el transporte paralelo, el logaritmo y las retracciones asociadas en $\mathrm{St}(n,p)$ y $\mathrm{Gr}(n,p)$; afirmaciones teóricas frecuentes (en textos, apuntes, código y respuestas generadas por modelos de lenguaje); y limitaciones numéricas.  
**Método:** Contraste con las fuentes primarias, deducción formal de cada fórmula y verificación numérica reproducible (script `verificacion.py`, salida en `resultados.txt`, NumPy 2.x / SciPy 1.x, doble precisión IEEE-754).

---

## 1. Resumen ejecutivo

| Id | Hallazgo | Tipo | Gravedad |
|:---|:---|:---|:---|
| **H1** | Omitir el factor $e^{-tA}$ en la exponencial euclídea de Stiefel: la curva sigue en el colector, pero no es una geodésica y su velocidad inicial es $\Delta+YA$. | Error de fórmula | Alta (silencioso) |
| **H2** | Calcular la QR de $\Delta$ en vez de $(I-YY^\top)\Delta$ en la exponencial canónica. | Error de fórmula | Alta |
| **H3** | Escribir la exponencial canónica como $\exp(t(\Delta Y^\top - Y\Delta^\top))Y$: da una geodésica válida, pero con la componente $A$ duplicada. | Error / alucinación frecuente | Alta (silencioso) |
| **H4** | Invertir el signo del bloque $\begin{psmallmatrix}A&-R^\top\\R&0\end{psmallmatrix}$: da una geodésica válida, pero en otra dirección. | Error de fórmula | Alta (silencioso) |
| **H5** | Afirmar que $[Y \; Q]$ siempre es ortonormal en la exponencial canónica (falla si $n<2p$ o si hay rango deficiente); la fórmula sigue siendo correcta. | Imprecisión teórica | Media |
| **H6** | Afirmar que no existe ninguna expresión para el transporte paralelo en Stiefel (afirmación desactualizada), o el error opuesto: que existe una fórmula cerrada de costo $O(np^2)$ del tipo Grassmann. | Alucinación / obsolescencia | Media |
| **H7** | Identificar el transporte por proyección con el transporte paralelo. | Alucinación frecuente | Alta |
| **H8** | Afirmar que el transporte paralelo canónico conserva la norma de Frobenius. | Alucinación | Media |
| **H9** | Mezclar métricas: integrar la EDO del transporte euclídeo a lo largo de una geodésica canónica. | Error de formulación | Alta |
| **H10** | Omitir el $V^\top$ final en la exponencial de Grassmann, o combinar representantes incompatibles con el transporte. | Error de formulación | Alta en código |
| **H11** | Omitir el término $I-UU^\top$ o invertir el signo de $\sin$ en el transporte de Grassmann. | Error de fórmula | Alta |
| **H12** | Afirmar que la geodésica entre dos subespacios siempre es única, o que el radio de inyectividad de Stiefel es $\pi/2$ o $\pi$ para cualquier métrica. | Alucinación teórica | Media |
| **H13** | Afirmar que la retracción QR es de segundo orden. | Alucinación | Media |
| **N1** | Inestabilidad del logaritmo de Grassmann en el lugar de corte (variantes con $M^{-1}$) y pérdida de precisión de $\arcsin$ cerca de $\pi/2$. | Limitación numérica | Media |
| **N2** | Tangentes que no son exactamente horizontales o tangentes: la pérdida de ortogonalidad es proporcional al residuo. | Limitación numérica | Media |
| **N3** | El logaritmo de Stiefel solo converge localmente; más allá del radio de inyectividad devuelve otro vector (más corto). | Limitación teórica y numérica | Media |

---

## 2. Marco de referencia formal

### 2.1 Stiefel
$$\mathrm{St}(n,p)=\{Y\in\mathbb R^{n\times p}: Y^\top Y=I_p\},\qquad \dim \mathrm{St}(n,p)=np-\tfrac{p(p+1)}{2}$$

* Espacio tangente: $T_Y\mathrm{St}=\{\Delta\in\mathbb{R}^{n\times p}: Y^\top\Delta+\Delta^\top Y=0\}$. Todo vector tangente se descompone unívocamente como $\Delta=YA+Y_\perp B$, con $A=Y^\top\Delta \in \mathfrak{so}(p)$ antisimétrica y $Y_\perp \in \mathrm{St}(n, n-p)$ base del complemento ortogonal.
* Métricas Riemannianas estándar ([Edelman, Arias y Smith, 1998](https://arxiv.org/abs/physics/9806030)):
  * **Euclídea** (inducida por la inmersión en $\mathbb{R}^{n\times p}$):
    $$g_e(\Delta_1,\Delta_2)=\operatorname{tr}(\Delta_1^\top\Delta_2)$$
  * **Canónica** (geometría de cociente $O(n)/O(n-p)$):
    $$g_c(\Delta_1,\Delta_2)=\operatorname{tr}\big(\Delta_1^\top(I-\tfrac12YY^\top)\Delta_2\big)$$
  * Ambas forman parte de la familia uniparamétrica de métricas de Hüper et al. (2021) parametrizada por $\beta$: canónica ($\beta=\tfrac12$), euclídea ($\beta=1$).

### 2.2 Grassmann
$$\mathrm{Gr}(n,p)=\mathrm{St}(n,p)/O(p),\qquad \dim=p(n-p)$$
El espacio horizontal en $Y$ es $\{H\in\mathbb{R}^{n\times p}: Y^\top H=0\}$. Sobre vectores horizontales, el término $\tfrac12YY^\top$ de $g_c$ se anula idénticamente ($Y^\top H = 0$), de modo que ambas métricas de Stiefel inducen exactamente la **misma métrica Riemanniana canónica en Grassmann**.

---

## 3. Aplicación exponencial en Stiefel

### 3.1 Métrica euclídea
Fórmula exacta ([Edelman, Arias y Smith, ec. 2.14](https://www.cis.upenn.edu/~cis5150/Stiefel-Grassmann-manifolds-Edelman.pdf)), con $A=Y^\top\Delta$ y $S=\Delta^\top\Delta$:
$$Y(t)=\begin{bmatrix}Y & \Delta\end{bmatrix}\exp\!\left(t\begin{bmatrix}A&-S\\ I_p&A\end{bmatrix}\right)\begin{bmatrix}I_p\\0\end{bmatrix}e^{-tA}$$
Esta curva resuelve de forma exacta la ecuación geodésica euclídea:
$$\ddot Y+Y(\dot Y^\top\dot Y)=0$$

* **H1 (Omisión de $e^{-tA}$):** Al derivar en $t=0$ se obtiene $[Y\;\Delta]\begin{psmallmatrix}A\\I\end{psmallmatrix}=YA+\Delta$. La componente vertical queda duplicada y la curva deja de ser geodésica. El error es silencioso: la ortogonalidad se conserva ($Y(t)^\top Y(t) = I_p$), pero la velocidad inicial es $\Delta + YA \ne \Delta$.

### 3.2 Métrica canónica
Fórmula exacta ([EAS, ec. 2.42](https://www.cis.upenn.edu/~cis5150/Stiefel-Grassmann-manifolds-Edelman.pdf); [Zimmermann, 2017](https://ar5iv.labs.arxiv.org/html/1604.05054)):  
Tomando la descomposición QR compacta $QR=(I-YY^\top)\Delta$:
$$Y(t)=\begin{bmatrix}Y&Q\end{bmatrix}\exp\!\left(t\begin{bmatrix}A&-R^\top\\R&0\end{bmatrix}\right)\begin{bmatrix}I_p\\0\end{bmatrix}$$

* **Forma equivalente $n\times n$ (Proposición 1):** Sea $\Omega=\Delta Y^\top-Y\Delta^\top-YAY^\top$. Entonces $\Omega$ es antisimétrica ($\Omega^\top = -\Omega$), satisface $\Omega Y=\Delta$ y genera la geodésica como:
  $$Y(t)=e^{t\Omega}Y$$
  *Demostración:* $\Omega Y=\Delta - Y\Delta^\top Y - YA = \Delta - Y(A^\top + A) = \Delta$, pues $\Delta^\top Y = A^\top = -A$. En la base $[Y \; Y_\perp]$, $\Omega$ tiene bloque inferior derecho nulo (es horizontal para la fibración $O(n)\to\mathrm{St}$). Por tanto, $e^{t\Omega}Y$ es la proyección de una geodésica de $O(n)$ con métrica biinvariante. $\square$
* **H3 (Forma alucinada $\exp(t(\Delta Y^\top - Y\Delta^\top))Y$):** Sea $W=\Delta Y^\top - Y\Delta^\top$. Entonces $Y^\top WY = 2A$. La geodésica generada es legítima en $\mathrm{St}(n,p)$, pero parte con velocidad $WY = \Delta + YA$, duplicando la velocidad rotacional interna. Solo coincide con la geodésica correcta si $A=0$ (vector horizontal).
* **H4 (Signo invertido):** $\begin{psmallmatrix}A&R^\top\\-R&0\end{psmallmatrix}$ invierte la dirección de avance ortogonal generando velocidad $YA-QR$.
* **H5 y Proposición 2 (Robustez ante rango deficiente y $n<2p$):** Si la fila $i$ de $R$ es nula, la columna $q_i$ no afecta a $Y(t)$, pues queda multiplicada por cero en la exponencial del bloque antisimétrico.

---

## 4. Transporte paralelo en Stiefel

### 4.1 Ecuaciones gobernantes
* **Métrica euclídea ([EAS, ec. 2.16](https://www.cis.upenn.edu/~cis5150/Stiefel-Grassmann-manifolds-Edelman.pdf)):**
  $$\dot\tau=-\tfrac12\,Y(\dot Y^\top\tau+\tau^\top\dot Y)=-Y\,\mathrm{sym}(\dot Y^\top\tau)$$
* **Métrica canónica ([EAS, ecs. 2.48–2.50](https://www.cis.upenn.edu/~cis5150/Stiefel-Grassmann-manifolds-Edelman.pdf)):**
  $$\dot\tau+\Gamma_c(\tau,\dot Y)=0$$
  $$\Gamma_c(\Delta_1,\Delta_2)=\tfrac12(\Delta_1\Delta_2^\top+\Delta_2\Delta_1^\top)Y+\tfrac12Y\big(\Delta_2^\top(I-YY^\top)\Delta_1+\Delta_1^\top(I-YY^\top)\Delta_2\big)$$
* **Caso cerrado de la autovelocidad (Métrica canónica):**
  $$\mathcal{P}_{t\leftarrow 0}\Delta = \Delta M(t) - Y R^\top N(t)$$
  donde $\begin{psmallmatrix}M(t)\\N(t)\end{psmallmatrix} = \exp\left(t\begin{bmatrix}A&-R^\top\\R&0\end{bmatrix}\right)\begin{bmatrix}I_p\\0\end{bmatrix}$.

---

## 5. Exponencial y transporte paralelo en Grassmann

### 5.1 Fórmulas exactas
Dado un vector horizontal $H=U\Sigma V^\top$ (SVD compacta) en el representante $Y$:
$$Y(t)=YV\cos(t\Sigma)V^\top+U\sin(t\Sigma)V^\top$$
$$\tau_X(t)=\Big(\big[-YV\sin(t\Sigma)+U\cos(t\Sigma)\big]U^\top+I-UU^\top\Big)X$$

* **H10 (Factor $V^\top$ final):** Omitir $V^\top$ produce una curva $Y(t)V$ que genera el mismo subespacio en $\mathrm{Gr}(n,p)$, pero parte de $YV \ne Y$, destruyendo el transporte paralelo en el representante Stiefel (discrepancia medida: 7.5).

---

## 6. Logaritmo, lugar de corte y radio de inyectividad

* **Grassmann:** Radio de inyectividad $=\pi/2$. El logaritmo estándar con $\arcsin$ pierde precisión cerca de $\pi/2$ debido a $\frac{d\theta}{ds} = \frac{1}{\sqrt{1-s^2}}$.
  * **Mejora SOTA:** Usar $\theta = \operatorname{atan2}(\hat{s}, c)$ con $c = \operatorname{diag}(R^\top U^\top Y_* R)$, logrando **precisión de máquina ($10^{-15}$)** en todo $[0, \pi/2]$.
* **Stiefel:** 
  * Euclídea: Radio de inyectividad $=\pi$ ([Zimmermann y Stoye, 2025](https://arxiv.org/pdf/2405.02268)).
  * Canónica: Radio acotado por $\approx 0.9133\pi$ ([BIT 2026](https://link.springer.com/article/10.1007/s10543-026-01141-9)).

---

## 7. Retracciones Riemannianas

* **QR ($qf(Y + \Delta)$):** Retracción de **primer orden** (pendiente del error frente a geodésica euclídea: $2.01$).
* **Polar ($\mathcal{P}_{\mathrm{St}}(Y + \Delta)$):** Retracción de **segundo orden** (pendiente del error: $3.00$).
* **Cayley (Wen–Yin):** Retracción de **segundo orden respecto a la geodésica canónica** (pendiente: $3.00$).
