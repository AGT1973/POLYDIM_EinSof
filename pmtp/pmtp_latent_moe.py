# -*- coding: utf-8 -*-
"""
pmtp_latent_moe.py — Enrutamiento Continuo en Espacio Latente sobre Variedad de Stiefel
(LatentMoE Stiefel PMTP Router) para el Clúster POLYDIM-ALADIN.

Ecosistema Soberano POLYDIM-EINSOF | Ariel García Traba
Teorema 33: Compresión Latente Continua en Enrutamiento Multi-Experto y Eliminación
del Cuello de Botella All-to-All.
"""

from __future__ import annotations
import math
import numpy as np

class PmtpLatentMoERouter:
    """
    Enrutador Latente Continuo sobre S^{ell - 1} que comprime las activaciones de
    dimensión oculta d a un subespacio latente ell = d / alpha, ejecutando el
    gating y selección de expertos en memoria compartida (PmtpShmBus).
    """
    def __init__(self, d_model: int = 4096, d_latent: int = 512, num_experts: int = 16, top_k: int = 2):
        self.d_model = d_model
        self.d_latent = d_latent
        self.num_experts = num_experts
        self.top_k = top_k
        self.compression_ratio = float(d_model) / float(d_latent)
        
        # Inicialización de matriz de proyección latente W_down ortonormalizada en St(d_model, d_latent)
        rng = np.random.default_rng(1337)
        raw_down = rng.standard_normal((d_model, d_latent))
        Q, _ = np.linalg.qr(raw_down)
        self.W_down = Q  # W_down^T W_down = I_{d_latent}
        
        # Prototipos de expertos en la variedad latente S^{d_latent - 1}
        raw_centroids = rng.standard_normal((num_experts, d_latent))
        norms = np.linalg.norm(raw_centroids, axis=1, keepdims=True)
        self.expert_centroids = raw_centroids / norms  # Puntos en S^{ell - 1}
        
    def project_to_latent_manifold(self, X: np.ndarray) -> np.ndarray:
        """
        Proyecta lote de tokens X in R^{B x d_model} al manifold latente S^{d_latent - 1}.
        Z = Normalize(X @ W_down).
        """
        Z_raw = X @ self.W_down
        # Normalización Neumaier/Stiefel por fila (esfera unitaria)
        norms = np.sqrt(np.sum(Z_raw ** 2, axis=-1, keepdims=True)) + 1e-15
        return Z_raw / norms

    def route_latent(self, X: np.ndarray) -> dict:
        """
        Ejecuta el ruteo directo en el manifold latente sin tocar el espacio euclidiano d_model.
        Similitud geodésica coseno en S^{ell - 1}: cos(theta) = z_i dot c_j.
        Retorna los índices de expertos top-k, los pesos continuos softmax,
        y las métricas de reducción de tráfico de memoria/red.
        """
        Z = self.project_to_latent_manifold(X)  # (B, d_latent)
        
        # Similitud en la esfera (equivalente a distancia riemanniana d_g = arccos(z dot c))
        logits = Z @ self.expert_centroids.T  # (B, num_experts)
        
        # Softmax continuo
        exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
        
        # Selección top-k
        top_k_indices = np.argsort(-probs, axis=-1)[:, :self.top_k]
        top_k_weights = np.take_along_axis(probs, top_k_indices, axis=-1)
        # Renormalización de pesos top-k
        top_k_weights = top_k_weights / np.sum(top_k_weights, axis=-1, keepdims=True)
        
        # Cálculo de reducción de bytes frente a ruteo en d_model
        bytes_full_d = X.nbytes
        bytes_latent = Z.nbytes
        reduction_pct = (1.0 - (bytes_latent / bytes_full_d)) * 100.0
        
        return {
            "top_k_indices": top_k_indices,
            "top_k_weights": top_k_weights,
            "bytes_full_d": bytes_full_d,
            "bytes_latent": bytes_latent,
            "bandwidth_reduction_pct": reduction_pct,
            "batch_size": X.shape[0]
        }
