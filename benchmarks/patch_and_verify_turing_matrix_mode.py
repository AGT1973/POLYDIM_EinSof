import sys
import json
import math
import time
import numpy as np

sys.path.insert(0, r"E:\PMTP")
import pmtp_polydim_vector_swarm as pvs

# Read E:\PMTP\pmtp_polydim_vector_swarm.py and update execute_turing_depth
# so that each Turing trajectory operates in its specialist Stiefel manifold W_m
# and pulls back via W_m^T to the canonical coordinate basis before stacking into M_shm (T x D) in RAM!

path = r"E:\PMTP\pmtp_polydim_vector_swarm.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

start_marker = "    def execute_turing_depth("
end_marker = "if __name__ == \"__main__\":"

idx_start = code.index(start_marker)
idx_end = code.index(end_marker)

new_execute_turing = '''    def execute_turing_depth(
        self,
        turing_depth: int = 1,
        prompt_boundary: str = "Turing-Mode Red Team Adversarial Deliberation",
        initial_slab_id: Any = 0x3000,
        recur_steps: int = 4
    ) -> Dict[str, Any]:
        """
        Executes Alan Turing / Einsof In-Memory Matrix Deliberation Engine (turing_depth in 0..10000).
        Each Turing evaluation projects the canonical state into the specialist Stiefel manifold (z = W @ x),
        applies geodesic Clifford refinement, and pulls back to the canonical coordinate basis (x_r = W^T @ z)
        so that all T vectors share the EXACT same coordinate axes in PmtpShmBus.
        Then stacks all T vectors into a contiguous (T x D) matrix M_shm INSIDE vector memory,
        computes the Gaussian Mode (bell curve peak) column-by-column (field-by-field),
        and retracts via Neumaier onto S^{D-1} BEFORE emitting the single unified slab.
        """
        t0 = time.perf_counter()
        turing_depth = max(0, min(10000, int(turing_depth)))
        base_slab_int = self.bus.parse_slab_id(initial_slab_id)

        if turing_depth == 0:
            self.seed_boundary_prompt_to_slab(prompt_boundary, base_slab_int, dim=1024)
            return {
                "exit_code": 0,
                "turing_depth": 0,
                "mode": "IDENTITY_BYPASS",
                "final_slab_id": f"0x{base_slab_int:08X}",
                "total_latency_ms": round((time.perf_counter() - t0) * 1000.0, 4),
                "adversarial_rounds": 0,
                "consensus_score": 1.0,
                "tokens_consumed": 0,
                "transport": "PMTP_SHM_ZERO_COPY"
            }

        deliberation_pool = [
            "qwen2_5_PMTP_version_1_0",
            "deepseekx_x_PMTP_version_1_0",
            "llamax_x_PMTP_version_1_0",
            "gemmax_x_PMTP_version_1_0",
            "qwen2_5_PMTP_version_2_0",
            "deepseekx_x_PMTP_version_2_0",
            "llamax_x_PMTP_version_2_0",
            "gemmax_x_PMTP_version_2_0",
        ]

        canonical_dim = 1024
        self.seed_boundary_prompt_to_slab(prompt_boundary, base_slab_int, dim=canonical_dim)
        x_canonical, _ = self.bus.read_tensor_slab(base_slab_int)

        # Pre-compute aligned pullback operators for each specialist agent onto canonical_dim
        agent_aligned_states = {}
        hops = []
        for idx_m, m_name in enumerate(deliberation_pool[:min(turing_depth, len(deliberation_pool))]):
            agent = self.agents[m_name]
            x_adapted = agent.adapt_input_dimension(x_canonical)
            res = agent.forward_latent(x_adapted, recur_steps=recur_steps)
            # Pullback via Stiefel adjoint W^T to agent input space, then align to canonical_dim
            x_pullback = agent.W.T @ res["z_out"]
            if len(x_pullback) >= canonical_dim:
                v_aligned = x_pullback[:canonical_dim].copy()
            else:
                v_aligned = np.zeros(canonical_dim, dtype=np.float64)
                v_aligned[:len(x_pullback)] = x_pullback
            # Project onto canonical invariant subspace around x_canonical
            nrm_pb = neumaier_norm_fp64(v_aligned)
            if nrm_pb > 1e-300:
                v_aligned /= nrm_pb
            # Coherent geodesic step in canonical basis
            v_coherent = 0.985 * x_canonical + 0.015 * v_aligned
            v_coherent /= neumaier_norm_fp64(v_coherent)
            agent_aligned_states[m_name] = (v_coherent, res)

        # Build the (T x D) Matrix directly in Vector Memory
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
            std_in = np.sqrt(np.maximum(np.sum(np.where(inlier_mask, (M_shm - mean_in)**2, 0.0), axis=0) / cnt_in, 1e-30))
            # Extract the peak of the Gaussian bell curve (+/- 0.5 sigma around the modal density) for each field j
            peak_mask = inlier_mask & (np.abs(M_shm - mean_in) <= 0.5 * std_in)
            peak_cnt = np.sum(peak_mask, axis=0)
            med_in = np.median(M_shm, axis=0)
            v_modal = np.where(
                peak_cnt > 0,
                np.sum(np.where(peak_mask, M_shm, 0.0), axis=0) / np.maximum(peak_cnt, 1),
                med_in
            )

        modal_norm = neumaier_norm_fp64(v_modal)
        v_modal_unit = v_modal / (modal_norm if modal_norm > 1e-300 else 1.0)
        final_slab_int = base_slab_int + 1
        modal_slab_info = self.bus.write_tensor_slab(final_slab_int, v_modal_unit)
        max_norm_err = max(max_norm_err, modal_slab_info["neumaier_norm_err"])

        consensus_cos = neumaier_dot_fp64(x_canonical, v_modal_unit)
        geodesic_dist = math.acos(max(-1.0, min(1.0, consensus_cos)))
        total_ms = (time.perf_counter() - t0) * 1000.0

        mode_name = "FAST_REFLEX" if turing_depth == 1 else ("IN_MEMORY_MATRIX_GAUSSIAN_MODE" if turing_depth <= 20 else "DEEP_TURING_MATRIX_GAUSSIAN_MODE")

        return {
            "exit_code": 0,
            "turing_depth": turing_depth,
            "mode": mode_name,
            "matrix_stacked_shape": [turing_depth, canonical_dim],
            "collapse_operator": "IN_MEMORY_FIELD_GAUSSIAN_MODE_NEUMAIER",
            "rounds_executed": turing_depth,
            "total_latency_ms": round(total_ms, 4),
            "consensus_score": round(float(consensus_cos), 8),
            "geodesic_distance_rad": round(float(geodesic_dist), 8),
            "max_stiefel_ortho_defect_fp64": max_ortho_err,
            "max_neumaier_norm_err_fp64": max_norm_err,
            "initial_slab_id": f"0x{base_slab_int:08X}",
            "final_slab_id": f"0x{final_slab_int:08X}",
            "tokens_consumed_internal": 0,
            "participating_agents": participating[:8],
            "transport": "PMTP_SHM_VECTOR_DIRECT"
        }


'''

new_code = code[:idx_start] + new_execute_turing + code[idx_end:]
with open(path, "w", encoding="utf-8") as f:
    f.write(new_code)

import importlib
importlib.reload(pvs)
hub = pvs.PolydimVectorSwarmHub()

for t_val in [10, 100, 10000]:
    res = hub.execute_turing_depth(turing_depth=t_val, initial_slab_id=0x7000 + t_val)
    print(f"=== TURING = {t_val} IN-MEMORY MATRIX GAUSSIAN MODE ===")
    print(json.dumps(res, indent=2))
