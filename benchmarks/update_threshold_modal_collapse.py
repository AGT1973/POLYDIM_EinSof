import sys
import json
import numpy as np

sys.path.insert(0, r"E:\PMTP")
import pmtp_polydim_vector_swarm as pvs

path = r"E:\PMTP\pmtp_polydim_vector_swarm.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

old_fn = '''    @staticmethod
    def freeman_diaconis_column_mode_fp64(M: np.ndarray) -> np.ndarray:
        """
        Calcula la Moda Estadística Exacta por coordenada (columna j = 0..D-1) sobre la matriz M in R^{T x D}
        usando el estimador no-paramétrico de máxima densidad (Half-Sample / Cuantil Modal de Bickel),
        100% libre de hiperparámetros arbitrarios o sesgos artificiales.
        Para cada columna j, ordena las T activaciones y halla la ventana contigua de longitud K = ceil(T/2)
        de ancho mínimo (máxima concentración de medida dP/dx), extrayendo el punto de máxima densidad.
        """
        T, D = M.shape
        if T == 1:
            return M[0].copy()
        if T == 2:
            return 0.5 * (M[0] + M[1])

        # Ordenar cada columna j independientemente en O(T log T) vectorizado en C/SIMD
        S = np.sort(M, axis=0)
        # Ventana de máxima densidad (Shorth / Half-Sample Mode estimator: ventana de 50% de masa con ancho mínimo)
        w = max(1, T // 2)
        widths = S[w:, :] - S[:T - w, :]
        best_start = np.argmin(widths, axis=0)
        # Extraer el centro exacto de la ventana de máxima concentración de probabilidad por cada coordenada j
        cols = np.arange(D)
        idx_mid = best_start + (w // 2)
        v_mode = 0.5 * (S[best_start, cols] + S[best_start + w, cols])
        # Refinar con el valor mediano dentro de la ventana modal de máxima densidad
        v_mode = 0.5 * (v_mode + S[idx_mid, cols])
        return v_mode'''

new_fn = '''    @staticmethod
    def freeman_diaconis_column_mode_fp64(M: np.ndarray) -> np.ndarray:
        """
        Colapso Modal con Umbral de Densidad en Memoria Vectorial sobre M in R^{T x D}:
        1. Descarta las colas de ruido que caen bajo el umbral de densidad estadística (las N-k estados inválidos).
        2. Aísla la rama modal dominante que supera el umbral (ej. 51% o 49%, ambas válidas frente al piso de ruido).
        3. Extrae el pico de la campana de Gauss por campo j dentro de la rama que superó el umbral.
        """
        T, D = M.shape
        if T == 1:
            return M[0].copy()
        if T == 2:
            return 0.5 * (M[0] + M[1])

        # 1. Umbral de coherencia en la variedad: identificar la rama de alta densidad sobre el piso de ruido
        # Calculamos la matriz de proyección rápida contra la componente principal para separar ramas (ej. 51% vs 49% vs ruido)
        c0 = M[0]
        proj = M @ c0
        n_bins = min(64, max(10, int(math.sqrt(T))))
        counts, edges = np.histogram(proj, bins=n_bins)
        # Umbral: todo bin con densidad menor al 10% del pico máximo es ruido inválido (los 99,998 estados espurios)
        peak_bin = int(np.argmax(counts))
        low_e, high_e = edges[peak_bin], edges[peak_bin + 1]
        # Expandir al lóbulo gaussiano contiguo que supera el umbral (threshold >= 0.25 * max_count)
        thresh = 0.25 * counts[peak_bin]
        l_idx = peak_bin
        while l_idx > 0 and counts[l_idx - 1] >= thresh:
            l_idx -= 1
        r_idx = peak_bin
        while r_idx < len(counts) - 1 and counts[r_idx + 1] >= thresh:
            r_idx += 1
        branch_mask = (proj >= edges[l_idx]) & (proj <= edges[r_idx + 1])
        M_valid = M[branch_mask] if np.sum(branch_mask) >= 3 else M

        # 2. Sobre los vectores que superaron el umbral, extraer la cúspide de la campana de Gauss campo por campo
        T_v = M_valid.shape[0]
        S = np.sort(M_valid, axis=0)
        w = max(1, T_v // 2)
        widths = S[w:, :] - S[:T_v - w, :]
        best_start = np.argmin(widths, axis=0)
        cols = np.arange(D)
        idx_mid = best_start + (w // 2)
        v_mode = 0.5 * (0.5 * (S[best_start, cols] + S[best_start + w, cols]) + S[idx_mid, cols])
        return v_mode'''

assert old_fn in code, "old_fn not found"
code = code.replace(old_fn, new_fn)
with open(path, "w", encoding="utf-8") as f:
    f.write(code)
print("Updated freeman_diaconis_column_mode_fp64 with Thresholded Modal Branch Collapse: OK")
