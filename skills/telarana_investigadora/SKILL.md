---
name: telarana_investigadora
description: >-
  Protocolo de Telaraña Investigadora (Investigative Spiderweb): Despliegue jerárquico y capilar de investigación
  distribuida. El Agente Orquestador Raíz (Antigravity/Gandalf) encuadra el objetivo mediante /sabios, /profundo o
  /consulta y comisiona Suborquestadores sectoriales (por zonas geográficas, universidades, áreas temáticas o
  directorios). Cada Suborquestador opera con autonomía, despacha y supervisa Sub-subagentes de terreno, exigiendo
  profundizar, ampliar fuentes o pivotar dentro de su sector, consolidando una síntesis sinérgica de alta fidelidad.
  Invocable con /telaraña, /telarana o /telarana_investigadora.
---

# Protocolo `/telaraña` — Telaraña Investigadora Distribuida (Investigative Spiderweb)

> **Ecosistema Soberano POLYDIM-EINSOF | Ariel García Traba**  
> Directiva de Exploración Capilar Jerárquica, Supervisión Dialéctica y Bucle Activo de Profundización

El protocolo **Telaraña Investigadora** estructura cualquier investigación masiva, multifacética o multipolar en una arquitectura en árbol de tres niveles para erradicar cuellos de botella de contexto, sesgos anglocéntricos (Regla 5) y superficialidad en los resultados.

---

## 1. Activación y Sintaxis

```bash
/telaraña <objetivo o pregunta de investigación compleja>
/telarana <objetivo>
/telarana --sectores "APAC, Europa, Iberoamérica, USA" <tema>
/telarana --profundidad <max_rondas_repregunta> <tema>
```

---

## 2. Arquitectura de 3 Niveles

```mermaid
flowchart TD
    User(["👤 Usuario / Ariel"])::user -->|"Consigna / Objetivo Complejo"| RootOrch["🧙‍♂️ Nivel 0: Orquestador Raíz (Gandalf / Antigravity)"]

    subgraph DeliberacionPreliminar ["1. Encuadre Dialéctico & Ontológico"]
        RootOrch -->|"Encuadre inicial"| SabiosCons["/sabios | /profundo | /consulta"]
        SabiosCons -->|"Criterios, Ejes & Matriz de Partición"| RootOrch
    end

    subgraph Nivel1_Suborquestadores ["2. Nivel 1: Suborquestadores de Sector / Dominio"]
        RootOrch -->|"Brief contextualizado + Mandato de sector"| SubOrch1["🧭 Suborquestador 1\n(Zona Geográfica: APAC / Iberoamérica)"]
        RootOrch -->|"Brief contextualizado + Mandato de sector"| SubOrch2["🧭 Suborquestador 2\n(Universidades / Laboratorios SOTA)"]
        RootOrch -->|"Brief contextualizado + Mandato de sector"| SubOrch3["🧭 Suborquestador 3\n(Industria / Patentes / Repositorios)"]
    end

    subgraph Nivel2_SubSubAgentes ["3. Nivel 2: Sub-subagentes de Terreno / Exploración"]
        SubOrch1 -->|"Misión atómica A"| Leaf1["🔍 Sub-subagente 1.1\n(Universidades China / C9 League)"]
        SubOrch1 -->|"Misión atómica B"| Leaf2["🔍 Sub-subagente 1.2\n(Nodos Iberoamericanos / RIT)"]

        SubOrch2 -->|"Misión atómica C"| Leaf3["🔍 Sub-subagente 2.1\n(Papers ArXiv / S2ORC / OpenAlex)"]
        SubOrch2 -->|"Misión atómica D"| Leaf4["🔍 Sub-subagente 2.2\n(Tesis & Grupos de Investigación)"]

        SubOrch3 -->|"Misión atómica E"| Leaf5["🔍 Sub-subagente 3.1\n(WIPO / Google Patents)"]
        SubOrch3 -->|"Misión atómica F"| Leaf6["🔍 Sub-subagente 3.2\n(GitHub / Benchmarks en Silicio)"]
    end

    subgraph FeedbackLoop ["4. Bucle Activo de Retroalimentación & Profundización"]
        Leaf1 -.->|"Evidencia preliminar"| SubOrch1
        Leaf2 -.->|"Evidencia preliminar"| SubOrch1
        SubOrch1 -.->|"Auditoría de calidad: 'Profundizar en X, buscar autores Y'"| Leaf1
        Leaf3 -.->|"Datos crudos"| SubOrch2
        SubOrch2 -.->|"Re-dirección: 'Descartar 1D, buscar matrices Z'"| Leaf3
    end

    subgraph SintesisFinal ["5. Agregación & Persistencia"]
        SubOrch1 ==>|"Síntesis Sectorial Depurada"| RootOrch
        SubOrch2 ==>|"Síntesis Sectorial Depurada"| RootOrch
        SubOrch3 ==>|"Síntesis Sectorial Depurada"| RootOrch

        RootOrch -->|"Cotejo anti-alucinaciones + Decisión Ejecutiva"| FinalReport["📋 Reporte Maestro Holístico & Dashboard"]
        RootOrch -->|"Ghost / Whisper"| PgVector[("🐘 PostgreSQL 16\npgvector & GraphRAG")]
    end

    classDef user fill:#2d3748,stroke:#cbd5e0,stroke-width:2px,color:#fff;
    classDef default fill:#1a202c,stroke:#4a5568,stroke-width:1px,color:#e2e8f0;
```

---

## 3. Protocolo Operativo Paso a Paso

### Paso 1: Encuadre en el Orquestador Raíz (Nivel 0)
1. **Recepción:** El Orquestador Raíz (Gandalf) analiza la meta y formula la hipótesis central.
2. **Encuadre con Sabios / Consulta:**
   - Si requiere debate de frontera o consenso complejo: convoca `/sabios` o `/profundo`.
   - Si requiere rápida exploración a costo \$0 USD: convoca `/consulta` (Tier Free SOTA + Einsof local).
3. **Matriz de Partición:** Divide el universo de exploración en $K$ sectores ortogonales (ej. regiones geográficas según Regla 5, directorios universitarios, repositorios de código, literatura indexada).
4. **Despacho:** Instancia a los **Suborquestadores (Nivel 1)** mediante `invoke_subagent` o canales equivalentes, transfiriéndoles el contexto íntegro del sistema (sin silos ciegos, Regla 3.2).

### Paso 2: Operación del Suborquestador Sectorial (Nivel 1)
Cada Suborquestador asume la soberanía táctica de su sector:
1. **Desglose Atómico:** Descompone el sector en tareas de terreno especializadas.
2. **Despacho de Sub-subagentes (Nivel 2):** Despliega investigadores de terreno para ejecutar búsquedas en la web, repositorios, directorios o preprints.
3. **Auditoría Hostil de Hallazgos (Bucle de Repregunta Activa):**
   - El Suborquestador **nunca acepta pasivamente un primer informe genérico**.
   - Evalúa rigor, citas reales, ausencia de alucinaciones y existencia de datos de silicio/código.
   - **Instrucción de Profundización:** *"El autor citado postula X, pero no se presenta la métrica empírica; profundiza en el anexo técnico o en el repositorio GitHub oficial"*.
   - **Instrucción de Búsqueda Alternativa:** *"La fuente A no reporta resultados; redirige la búsqueda hacia el catálogo B del mismo sector"*.
4. **Límite de Control de Tokens (Regla 2):** Máximo **2 rondas de profundización** por sub-subagente para garantizar economía de guerra y evitar derivas no acotadas.

### Paso 3: Síntesis Sectorial y Reporte Ascendente
1. Una vez satisfecho el estándar de suficiencia o alcanzado el límite de rondas, el Suborquestador consolida un **Reporte Sectorial Estructurado**:
   - Hallazgos clave certificados con enlaces y evidencia directa.
   - Puntos ciegos o ausencias documentadas en su sector.
   - Evaluación crítica contra la hipótesis central.
2. Envía el reporte depurado al Orquestador Raíz.

### Paso 4: Fusión Holística, Decisión Ejecutiva y Persistencia
1. **Fusión y Descarte Dialéctico:** El Orquestador Raíz cruza las síntesis sectoriales, elimina redundancias y resuelve discrepancias.
2. **Decisión Ejecutiva (Radical Honesty — Regla 1):** Documenta qué hipótesis fueron ratificadas, qué conjeturas cayeron y qué componentes resistieron.
3. **Persistencia Obligatoria (Regla 0 & Regla 3):**
   - `polydim_vec_db.polydim_embeddings` (representación vectorial semántica).
   - `polydim_vec_db.einsof_graph_nodes` & `einsof_graph_edges` (nodos y aristas de conocimiento en GraphRAG).
   - `polydim_active_db.active_vault` (resumen ejecutivo y metadatos de la corrida).

---

## 4. Invariantes y Reglas Constitucionales Aplicadas

1. **Regla 1 (Radical Honesty):** Cero victorias ficticias. Toda cita, paper o repositorio reportado debe existir con URL y evidencia verificable.
2. **Regla 2 (Token War Economy):** Prioridad a modelos libres y locales (Einsof / ALADIN / SambaNova / Groq) en las etapas de rastreo e intermediación. Límite estricto de 2 iteraciones de profundización por hoja.
3. **Regla 3 & 3.2 (Ghost Protocol & Veto a Silos):** Toda representación tensorial opera en memoria compartida (`PmtpShmBus`). Los suborquestadores reciben el contexto completo del problema, nunca fragmentos aislados sin visión holística.
4. **Regla 5 (Multipolar Anti-Bias):** Obligación de incluir sectores fuera del eje anglocéntrico (Iberoamérica, Asia-Pacífico, Europa continental, África).
