<!-- PROMPT BRECHA 3: FORMAL LEAN 4 PROOFS (CLIFFORD ISOMETRY & PMTP DPI THEOREM) -->
<!-- PROTOCOLO: Regla 15 (Inglés formal), Regla 10 (Empirical Veto: 0 sorry), Regla 16 (Anti-Passive Auditing) -->
<!-- TARGET API: Perplexity Sonar-Pro / OpenAI o3 / Moonshot Kimi k3 -->

# MISSION CONTEXT: COMPLETE LEAN 4 FORMALIZATION WITHOUT SORRY
You are a Principal Formal Verification Mathematician specializing in Lean 4, Differential Geometry, and Information Theory.

## THE PROBLEM
POLYDIM has formalized 4 foundational LeaseGuard shared-memory axioms in `pmtp_v4_axioms.lean`, compiling them to C object code (`pmtp_v4_axioms.o`) with Exit Code 0. However, the two crowning theoretical contributions of the doctoral thesis remain unformalized in Lean 4:
1. **The Clifford Invariance Theorem:** For any spinor rotation $R \in \text{Spin}(p,q)$ acting on a state vector $\psi \in S^{D-1}$, the manifold metric and geometric product are strictly isometric: $\langle R\psi R^\dagger, R\phi R^\dagger \rangle = \langle \psi, \phi \rangle$.
2. **The PMTP Data Processing Inequality (DPI) Conservation Theorem:** Let $X \in \mathbb{R}^D$ be a latent activation tensor. If $X$ is collapsed to a 1D discrete sequence of tokens $T = \text{tokenizer}(X)$, then the mutual information with any downstream reasoning target $Y$ satisfies $I(T; Y) < I(X; Y)$ with an entropy deficit $\Delta H \ge D \log(2\pi e) - \mathcal{O}(L \log |\mathcal{V}|)$. In contrast, PMTP tensor transmission preserves $I(X; Y)$ with zero discrete entropy destruction.

## YOUR MANDATE
Produce the complete, fully valid Lean 4 source file `polydim_formal_core_theorems.lean`:
1. Define the algebraic structures for hyperspherical embeddings $S^{D-1}$, Clifford blades, and Mutual Information bounds.
2. Provide complete proofs for:
   - `theorem clifford_spinor_isometry`: Strict inner-product invariance under rotor conjugation.
   - `theorem pmtp_dpi_entropy_preservation`: Strict information preservation of direct shared-memory tensor transit vs 1D tokenized collapse.
3. Every theorem must be proven rigorously without using the `sorry` tactic.
4. Provide the exact command-line invocation to compile the `.lean` file to `.c` and `.o` using Lean 4.34+.
