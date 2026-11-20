---
name: remember
description: Stores verified concepts, code, and insights into local PostgreSQL 16 + pgvector and GraphRAG so the student's AI never suffers amnesia. Triggered with /remember <concept or note>.
---

# Remember Skill (Local Vector & Graph Memory)

**Trigger**: `/remember <concept, formula, or code>`

## Purpose
Enables **Permanent Local Memory** on the student's machine using `PostgreSQL 16` + `pgvector` and `GraphRAG`.

## Workflow
1. Extracts the core concept and its relational links (Graph node & edges).
2. Computes the semantic vector embedding locally.
3. Inserts into the local `polydim_embeddings` table.
4. Confirms storage to the student: `[+] Saved to local vector memory (ID: XXX, Distance: 0.0)`.
5. Tomorrow, when the student asks about it, the AI retrieves it locally in <5 ms with zero token burn.
