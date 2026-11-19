---
name: redteam
description: Symmetric Adversarial Red Team audit. Tests code, mathematical proofs, and models against hostile edge cases (NaNs, Infs, asymptotic scaling D>=10^6, memory exhaustion, FFI boundaries). Delivers mandatory symmetric certification with two sections - VULNERABILITIES FOUND and COMPONENTS THAT RESISTED ATTACK. Invoked with /redteam <target>.
---

# Symmetric Adversarial Red Team — Action `/redteam`

Rigorous, uncompromising quality assurance for student code, models, and mathematical scripts.

---

## The Hostile Paranoia Doctrine

*"Assume the code is broken until it survives an asymptotic attack."*

When you write a Python script, a C++ kernel, or an ML pipeline, testing only the happy path gives you a false sense of security. `/redteam` unleashes an adversarial audit:
1. **Hostile Boundary Testing:**
   - Null vectors, zero norms, singular matrices.
   - NaNs, Infinities, and subnormal floating-point values.
   - Scale attacks ($D \ge 10^5$, high concurrency, memory $>80\%$).
   - FFI boundaries between Python, C++, and Rust.
2. **Symmetric Certification (Anti-Cynical Rule):**
   - Pure cynicism is destructive; blind praise is deceitful.
   - The red team report **MUST** document both:
     * **Section A:** Exactly what broke and how to fix it.
     * **Section B:** Exactly what survived and proved resilient under stress.

---

## How to Use

```text
/redteam my_algorithm.py
/redteam scripts/aladin_sota_gateway.py
/redteam "Verify if the matrix inversion handles non-invertible covariance"
```
