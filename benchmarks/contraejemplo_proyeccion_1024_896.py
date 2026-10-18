"""
Contraejemplo formal para proyección ortogonal de 1024D a 896D.
Demuestra que U @ U.T = I_896 no es isometría de R^1024 en R^896:
existe un núcleo ker(U) de dimensión 128 donde la información se anula por completo.
"""
import numpy as np

n_in, n_out = 1024, 896
# U con filas ortonormales; no puede tener columnas ortonormales
U = np.zeros((n_out, n_in), dtype=np.float64)
U[np.arange(n_out), np.arange(n_out)] = 1.0

# Vector x en el núcleo de U (componente en la dimensión 1024)
x = np.zeros(n_in)
x[-1] = 1.0

# Proyección y pseudo-reconstrucción
z = U @ x
reconstruction = U.T @ z

assert np.allclose(U @ U.T, np.eye(n_out))
assert np.linalg.norm(x - reconstruction) == 1.0

print('error de ortogonalidad de filas (U @ U.T - I_896):', np.max(np.abs(U @ U.T - np.eye(n_out))))
print('error de reconstruccion de x unitario ||x - U.T @ U @ x||:', np.linalg.norm(x - reconstruction))
print('energia media perdida (entrada isotropica):', (n_in - n_out) / n_in)
print('resultado: contraejemplo formal confirmado (ker(U) = 128D)')
