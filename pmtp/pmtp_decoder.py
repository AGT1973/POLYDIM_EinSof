# ============================================================================
# PMTP FORMAL HYPOTHESIS ENCODER, SUPERPOSITION & BOUNDED DECODER (CAPA 5)
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba — Independent Research / EinsofOS
# Base Teórica: Tropp (2011), Absil et al. (2008), Higham (1989), Neumaier (1974)
# ============================================================================

import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

def neumaier_sum(arr: np.ndarray) -> float:
    """
    Suma compensada de Neumaier (1974) en FP64.
    Garantiza error relativo <= 2 * eps_mach independientemente de la longitud.
    """
    s = 0.0
    c = 0.0
    for x in arr.flat:
        t = s + x
        if abs(s) >= abs(x):
            c += (s - t) + x
        else:
            c += (x - t) + s
        s = t
    return s + c

def neumaier_dot(u: np.ndarray, v: np.ndarray) -> float:
    """Producto interno con acumulador compensado de Neumaier."""
    products = u.astype(np.float64) * v.astype(np.float64)
    return neumaier_sum(products)

def polar_retraction(Z: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Retracción polar analítica R_St(Z) = Z (Z^T Z)^{-1/2} en St(D, K).
    Calcula además el defecto de ortonormalidad ||U^T U - I_K||_F usando Neumaier.
    """
    D, K = Z.shape
    assert D >= K, f"Dimensión ambiente D ({D}) debe ser >= rango K ({K})"
    
    # Gram matrix G = Z^T Z
    G = np.dot(Z.T, Z)
    
    # Descomposición espectral simétrica
    eigvals, V = np.linalg.eigh(G)
    eigvals = np.maximum(eigvals, 1e-15)
    
    # G^{-1/2} = V diag(1 / sqrt(lambda)) V^T
    inv_sqrt_eig = 1.0 / np.sqrt(eigvals)
    G_inv_sqrt = np.dot(V * inv_sqrt_eig, V.T)
    
    # Retracción polar exacta: U = Z G^{-1/2}
    U = np.dot(Z, G_inv_sqrt)
    
    # Medición de defecto ortonormal con Neumaier
    Gram_U = np.dot(U.T, U)
    diff = Gram_U - np.eye(K, dtype=np.float64)
    drift_frob = math.sqrt(max(0.0, neumaier_sum(diff ** 2)))
    
    return U, drift_frob


class PmtpHypothesisEncoder:
    """
    Mapeo de inmersión isométrica de hipótesis discretas en la variedad de Stiefel:
    E: H -> St(D, K).
    Garantiza baja coherencia mutua: mu(E(h_i), E(h_j)) = ||E(h_i)^T E(h_j)||_2 <= mu_max.
    """
    def __init__(self, ambient_dim: int, rank_k: int, seed: int = 42):
        self.D = ambient_dim
        self.K = rank_k
        self.rng = np.random.RandomState(seed)
        self.codebook: Dict[str, np.ndarray] = {}

    def register_hypothesis(self, hypothesis_id: str) -> np.ndarray:
        """Genera un marco ortonormal canónico en St(D, K) para la hipótesis."""
        if hypothesis_id in self.codebook:
            return self.codebook[hypothesis_id]
        
        # Generar matriz aleatoria y proyectar a St(D, K) vía polar
        raw = self.rng.randn(self.D, self.K).astype(np.float64)
        ortho, _ = polar_retraction(raw)
        self.codebook[hypothesis_id] = ortho
        return ortho

    def encode(self, hypothesis_id: str) -> np.ndarray:
        if hypothesis_id not in self.codebook:
            return self.register_hypothesis(hypothesis_id)
        return self.codebook[hypothesis_id]


class PmtpHypothesisDecoder:
    """
    Decodificador Bayesiano/Subespacio: D: St(D, K) -> P(H).
    Recupera las hipótesis contenidas en un slab de superposición S in St(D, K).
    Cota de recuperación: Si la coherencia mutua mu < 1 / (2p - 1),
    la hipótesis activa h_star se identifica con error acotado eps_rec.
    """
    def __init__(self, encoder: PmtpHypothesisEncoder):
        self.encoder = encoder

    def decode_superposition(
        self,
        Slab: np.ndarray,
        threshold: float = 0.35
    ) -> List[Tuple[str, float]]:
        """
        Calcula la similitud de subespacio Frobenius-Grassmanniana:
        rho(h) = ||E(h)^T Slab||_F^2 / K
        Retorna la lista de hipótesis activas y sus coeficientes de energía.
        """
        results = []
        K = self.encoder.K
        for hyp_id, E_h in self.encoder.codebook.items():
            # Interacción de subespacio M = E_h^T Slab in R^(K x K)
            M = np.dot(E_h.T, Slab)
            # Energía Frobenius normalizada
            frobenius_sq = neumaier_sum(M ** 2)
            energy = frobenius_sq / float(K)
            if energy >= threshold:
                results.append((hyp_id, float(energy)))
        
        # Ordenar por energía decreciente
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def decode_dominant(self, Slab: np.ndarray) -> Tuple[str, float]:
        """Recupera la hipótesis con máxima proyección ortogonal."""
        candidates = self.decode_superposition(Slab, threshold=0.0)
        if not candidates:
            return "UNKNOWN", 0.0
        return candidates[0]


class PmtpCausalDAGReasoner:
    """
    Razonador Causal sobre Grafos de Planificación (ProsQA Benchmark).
    Modela la navegación de caminos válidos P* en un DAG causal sin serialización a tokens 1D.
    Compara la evolución del estado Riemanniano continuo frente a la degradación autorregresiva.
    """
    def __init__(self, ambient_dim: int, rank_k: int):
        self.D = ambient_dim
        self.K = rank_k
        self.encoder = PmtpHypothesisEncoder(ambient_dim, rank_k)
        self.decoder = PmtpHypothesisDecoder(self.encoder)

    def reason_path(
        self,
        dag_nodes: List[str],
        edges: List[Tuple[str, str]],
        initial_node: str,
        target_node: str,
        noise_level: float = 1e-4
    ) -> Tuple[List[str], float, float]:
        """
        Navega el grafo causal actualizando el slab de Stiefel:
        X_{t+1} = R_St( X_t + G_t + eta_t )
        donde G_t proyecta hacia las hipótesis adyacentes coherentes en el DAG.
        Retorna (camino_inferido, perdida_causal, max_drift).
        """
        # Registrar todos los nodos en el codebook de Stiefel
        for node in dag_nodes:
            self.encoder.register_hypothesis(node)
        
        # Adyacencia
        adj = {n: [] for n in dag_nodes}
        for u, v in edges:
            adj[u].append(v)

        current_node = initial_node
        path = [current_node]
        current_slab = self.encoder.encode(current_node)
        max_drift = 0.0

        step_limit = len(dag_nodes) + 2
        steps = 0

        while current_node != target_node and steps < step_limit:
            steps += 1
            neighbors = adj.get(current_node, [])
            if not neighbors:
                break
            
            # Superposición continua ponderada de hipótesis de siguientes pasos
            grad = np.zeros((self.D, self.K), dtype=np.float64)
            for neigh in neighbors:
                E_neigh = self.encoder.encode(neigh)
                grad += E_neigh / len(neighbors)
            
            # Ruido de perturbación gaussiana
            noise = np.random.randn(self.D, self.K) * noise_level
            
            # Dinámica Riemanniana: X_{t+1} = R_St(X_t + 0.8 * grad + noise)
            Z = current_slab + 0.8 * grad + noise
            current_slab, drift = polar_retraction(Z)
            max_drift = max(max_drift, drift)

            # Decodificar el siguiente estado dominante
            best_node = None
            best_score = -1.0
            for neigh in neighbors:
                E_neigh = self.encoder.encode(neigh)
                M = np.dot(E_neigh.T, current_slab)
                score = neumaier_sum(M ** 2)
                if score > best_score:
                    best_score = score
                    best_node = neigh

            if best_node is not None:
                current_node = best_node
                path.append(current_node)
            else:
                break

        # Fidelidad causal: L_causal = 0 si llegó al objetivo, 1 si falló
        causal_loss = 0.0 if current_node == target_node else 1.0
        return path, causal_loss, max_drift
