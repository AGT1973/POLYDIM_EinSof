---
name: mathesis_qlora
description: >-
  Internalized Mathesis (.mth) compilation and continuous manifold execution directly within QLoRA adapters.
  Activates zero-prompt math compilation via the <|mathesis|> special trigger token, eliminating the 1,200 token
  system instruction overhead and executing direct native PE64/ELF64 emission without C/C++ or external runtimes.
---

# Skill: `mathesis_qlora` — Internalized Mathesis in QLoRA Adapters

> **POLYDIM-EINSOF Sovereign Architecture | Ariel García Traba**  
> Direct Silicon Compilation & Zero-Prompt-Tax Execution (Rule 2: War Economy & Rule 19: Silicon Proof)

---

## 1. Concept & Architectural Rationale

Traditionally, using LLMs to write or compile non-human mathematical code like **Mathesis** (`.mth`) required injecting a massive textual system prompt (1,000–1,500 tokens) detailing ISA MATHESIS-64, opcodes, stack layouts, and compiler rules.

This skill governs models where **Mathesis is baked directly into the QLoRA adapter weights ($W_{\text{lora\_A}}, W_{\text{lora\_B}}$)**:
* **Zero Prompt Tax:** Eliminates bulky textual instructions. The model's default basal state natively knows `.mth` grammar, Lyapunov attractors, and Stiefel polar retractions.
* **Special Trigger Token `<|mathesis|>:`** A single 1-byte BPE token switches the output distribution to emit pure, verifiable `.mth` bytecode/source code.
* **Vector-First Forwarding:** When receiving a continuous latent tensor $z \in S^{D-1}$ via `PmtpShmBus`, the model bypasses text tokenization completely, operating at 0 prompt tokens.

---

## 2. Invocation & Syntax

### A. Minimal Trigger Mode (1 Token Overhead)
```text
<|mathesis|>
Define a Kerr black hole ergosphere simulation on S^2047 with Lyapunov equilibrium.
```

### B. Output Format (Pure Silicon Mathesis .mth)
The fine-tuned model immediately responds with clean, executable `.mth` code without conversational filler:
```mathesis
ROT_LIE_SO|DEST=0x1000|D=2048|SAGES=EULER
SYMPLECTIC_COVARIANT_UK|DEST=0x2000|A=0x1000|D=2048|THETA=0.125|SAGES=POINCARE
RETRACT_STIEFEL|DEST=0x2000|D=2048
COLLAPSE_1D_MMIO|DEST=0x0000|A=0x2000|D=2048
HALT_EQUILIBRIUM|DEST=0x2000|D=2048
```

---

## 3. Direct Silicon Compilation Pipeline

Once the `.mth` code is produced by the model, compile and execute it locally without toolchain dependencies:

```bash
# Windows Native PE32+ (No CRT, No Visual Studio required)
python mthc.py program.mth -o program.exe

# Linux ELF64 Native
python mthc.py program.mth -t elf64 -o program.elf

# Direct Rust Assembler
mathesis2bin program.mth
```

---

## 4. Training Invariants for QLoRA SFT

When training adapters with `einsof_kaggle_qlora_sft.py`:
1. **Empty System Prompt:** `{"role": "system", "content": ""}`.
2. **User Prefix:** `{"role": "user", "content": "<|mathesis|>\n" + instruction}`.
3. **Target Modules:** Full projection set `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]` with Stiefel polar projection applied at epoch close.
