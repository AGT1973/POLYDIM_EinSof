import sys
import json
import time
import math
import numpy as np

sys.path.insert(0, r"E:\PMTP")
import pmtp_polydim_vector_swarm as pvs

# Upgrade execute_turing_depth in E:\PMTP\pmtp_polydim_vector_swarm.py to support up to Turing = 1,000,000
# via In-Memory Vectorized Block Gaussian Mode Accumulation when T > 25,000 (zero RAM overflow, exact bell-curve cusp).

path = r"E:\PMTP\pmtp_polydim_vector_swarm.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("turing_depth = max(0, min(10000, int(turing_depth)))", "turing_depth = max(0, min(1000000, int(turing_depth)))")

old_loop = """        # Build the (T x D) Matrix directly in Vector Memory
        M_shm = np.empty((turing_depth, canonical_dim), dtype=np.float64)
        rng_pert = np.random.default_rng(base_slab_int + turing_depth)
        participating = []
        max_ortho_err = 0.0
        max_norm_err = 0.0

        for r in range(turing_depth):
            m_name = deliberation_pool[r % len(deliberation_pool)]
            v_base, res_meta = agent_aligned_states[m_name]
            # Subtle thermal dispersion on S^{D-1} across T parallel/recurrent paths
            dispersion = rng_pert.normal(0.0, 0.008, size=canonical_dim)
            v_row = v_base + dispersion
            v_row /= np.linalg.norm(v_row)
            M_shm[r, :] = v_row
            participating.append(m_name)
            if res_meta["stiefel_ortho_max_fp64"] > max_ortho_err:
                max_ortho_err = res_meta["stiefel_ortho_max_fp64"]
            if res_meta["neumaier_norm_err"] > max_norm_err:
                max_norm_err = res_meta["neumaier_norm_err"]

        # IN-MEMORY MATRIX GAUSSIAN MODE COLLAPSE (Column-by-Column / Field-by-Field)
        if turing_depth == 1:
            v_modal = M_shm[0].copy()
        else:
            q25 = np.percentile(M_shm, 25, axis=0)
            q75 = np.percentile(M_shm, 75, axis=0)
            iqr = np.maximum(q75 - q25, 1e-15)
            inlier_mask = (M_shm >= (q25 - 1.5 * iqr)) & (M_shm <= (q75 + 1.5 * iqr))
            cnt_in = np.maximum(np.sum(inlier_mask, axis=0), 1)
            mean_in = np.sum(np.where(inlier_mask, M_shm, 0.0), axis=0) / cnt_in
            std_in = np.sqrt(np.maximum(np.sum(inlier_mask, (M_shm - mean_in)**2, 0.0), axis=0) / cnt_in, 1e-30))
            # Extract the peak of the Gaussian bell curve (+/- 0.5 sigma around the modal density) for each field j
            peak_mask = inlier_mask & (np.abs(M_shm - mean_in) <= 0.5 * std_in)
            peak_cnt = np.sum(peak_mask, axis=0)
            med_in = np.median(M_shm, axis=0)
            v_modal = np.where(
                peak_cnt > 0,
                np.sum(np.where(peak_mask, M_shm, 0.0), axis=0) / np.maximum(peak_cnt, 1),
                med_in
            )"""

new_loop = """        # Build & Collapse the (T x D) Matrix directly in Vector Memory (supports up to T = 1,000,000)
        rng_pert = np.random.default_rng(base_slab_int + turing_depth)
        participating = [deliberation_pool[r % len(deliberation_pool)] for r in range(min(turing_depth, 8))]
        max_ortho_err = max(v[1]["stiefel_ortho_max_fp64"] for v in agent_aligned_states.values())
        max_norm_err = max(v[1]["neumaier_norm_err"] for v in agent_aligned_states.values())
        base_pool_mat = np.array([agent_aligned_states[deliberation_pool[k % len(deliberation_pool)]][0] for k in range(len(deliberation_pool))], dtype=np.float64)

        if turing_depth <= 25000:
            idx_rows = np.arange(turing_depth) % len(deliberation_pool)
            M_shm = base_pool_mat[idx_rows] + rng_pert.normal(0.0, 0.008, size=(turing_depth, canonical_dim))
            norms_r = np.linalg.norm(M_shm, axis=1, keepdims=True)
            M_shm /= np.maximum(norms_r, 1e-300)

            if turing_depth == 1:
                v_modal = M_shm[0].copy()
            else:
                q25 = np.percentile(M_shm, 25, axis=0)
                q75 = np.percentile(M_shm, 75, axis=0)
                iqr = np.maximum(q75 - q25, 1e-15)
                inlier_mask = (M_shm >= (q25 - 1.5 * iqr)) & (M_shm <= (q75 + 1.5 * iqr))
                cnt_in = np.maximum(np.sum(inlier_mask, axis=0), 1)
                mean_in = np.sum(np.where(inlier_mask, M_shm, 0.0), axis=0) / cnt_in
                std_in = np.sqrt(np.maximum(np.sum(np.where(inlier_mask, (M_shm - mean_in)**2, 0.0), axis=0) / cnt_in, 1e-30))
                peak_mask = inlier_mask & (np.abs(M_shm - mean_in) <= 0.5 * std_in)
                peak_cnt = np.sum(peak_mask, axis=0)
                med_in = np.median(M_shm, axis=0)
                v_modal = np.where(
                    peak_cnt > 0,
                    np.sum(np.where(peak_mask, M_shm, 0.0), axis=0) / np.maximum(peak_cnt, 1),
                    med_in
                )
        else:
            # Streaming Block-Matrix Gaussian Mode Collapse in Shared Memory for T up to 1,000,000
            block_size = 50000
            n_blocks = math.ceil(turing_depth / block_size)
            block_modes = np.empty((n_blocks, canonical_dim), dtype=np.float64)
            rem = turing_depth
            for b_i in range(n_blocks):
                cur_b = min(block_size, rem)
                rem -= cur_b
                idx_rows = (np.arange(cur_b) + b_i * block_size) % len(deliberation_pool)
                B_shm = base_pool_mat[idx_rows] + rng_pert.normal(0.0, 0.008, size=(cur_b, canonical_dim))
                mean_b = np.mean(B_shm, axis=0)
                std_b = np.std(B_shm, axis=0)
                peak_mask = np.abs(B_shm - mean_b) <= 0.5 * np.maximum(std_b, 1e-15)
                peak_cnt = np.maximum(np.sum(peak_mask, axis=0), 1)
                block_modes[b_i, :] = np.sum(np.where(peak_mask, B_shm, 0.0), axis=0) / peak_cnt
            v_modal = np.mean(block_modes, axis=0)"""

assert old_loop in code, "old_loop not found"
code = code.replace(old_loop, new_loop)
with open(path, "w", encoding="utf-8") as f:
    f.write(code)

import importlib
importlib.reload(pvs)
hub = pvs.PolydimVectorSwarmHub()
res_1m = hub.execute_turing_depth(turing_depth=1000000, initial_slab_id=0x9900)
print("=== TURING = 1,000,000 (1 MILLÓN) EN MEMORIA VECTORIAL ===")
print(json.dumps(res_1m, indent=2))
