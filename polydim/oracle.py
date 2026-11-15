# polydim/oracle.py
import numpy as np

class StiefelOracle:
    """
    Oráculo de Certificación Geométrica sobre la variedad de Stiefel St(D, K).
    Evalúa ||X^T X - I_K||_F con decisión formal de 3 estados (ACCEPT, REJECT, REFINE)
    conforme al arbitraje de la Etapa 21 de Perplexity Sonar-Pro (P28).
    """
    @staticmethod
    def audit(tensor_data: np.ndarray, tol: float = 1e-10) -> dict:
        if tensor_data.ndim == 1:
            X = tensor_data.reshape(-1, 1)
        else:
            X = tensor_data
            
        D, K = X.shape
        # Matriz Gram G = X^T X (K x K)
        G = np.dot(X.T, X)
        I_K = np.eye(K, dtype=np.float64)
        
        diff = G - I_K
        frob_err = float(np.linalg.norm(diff, ord='fro'))
        max_diag_err = float(np.max(np.abs(np.diag(G) - 1.0)))
        max_off_diag = float(np.max(np.abs(diff - np.diag(np.diag(diff))))) if K > 1 else 0.0
        
        if frob_err <= tol:
            verdict = "ACCEPT"
        elif frob_err > tol * 100.0:
            verdict = "REJECT"
        else:
            verdict = "REFINE"
            
        return {
            "verdict": verdict,
            "frobenius_error": frob_err,
            "max_norm_error": max_diag_err,
            "max_orthogonality_error": max_off_diag,
            "tolerance": tol,
            "d": D,
            "k": K,
            "is_valid": (verdict == "ACCEPT")
        }
