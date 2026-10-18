import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette - Dark Executive Academic
    C_BG = RGBColor(11, 15, 25)         # #0B0F19 Deep Navy
    C_CARD = RGBColor(19, 28, 46)       # #131C2E Slate Dark Container
    C_CARD_ALT = RGBColor(24, 36, 58)   # #18243A Slightly lighter container
    C_BORDER = RGBColor(30, 41, 59)     # #1E293B Subtle Border
    C_TITLE = RGBColor(248, 250, 252)   # #F8FAFC Pure Light White
    C_SUBTITLE = RGBColor(148, 163, 184)# #94A3B8 Muted Slate
    C_TEXT = RGBColor(226, 232, 240)    # #E2E8F0 Readable Body
    C_MUTED = RGBColor(100, 116, 139)   # #64748B Secondary Text
    C_CYAN = RGBColor(56, 189, 248)     # #38BDF8 Electric Cyan
    C_GOLD = RGBColor(245, 158, 11)     # #F59E0B Warm Amber/Gold
    C_EMERALD = RGBColor(16, 185, 129)  # #10B981 Silicon Success Green
    C_ROSE = RGBColor(244, 63, 94)      # #F43F5E Adversarial Warning Rose
    C_PURPLE = RGBColor(168, 85, 247)   # #A855F7 Latent Fabric Purple

    def add_base_slide(badge_text, title_text, subtitle_text, slide_num, total_slides=50, badge_color=C_CYAN):
        slide = prs.slides.add_slide(blank_layout)
        
        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()

        # Header Badge
        badge_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.0), Inches(0.3))
        tf_b = badge_box.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
        p_b = tf_b.paragraphs[0]
        p_b.text = badge_text.upper()
        p_b.font.size = Pt(9.5)
        p_b.font.bold = True
        p_b.font.color.rgb = badge_color

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.55))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(21)
        p_t.font.bold = True
        p_t.font.color.rgb = C_TITLE

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.22), Inches(11.7), Inches(0.35))
        tf_s = sub_box.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.size = Pt(11.5)
        p_s.font.color.rgb = C_SUBTITLE

        # Footer Accent Line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = C_BORDER
        line.line.fill.background()

        # Footer Text
        foot_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.12), Inches(8.0), Inches(0.25))
        tf_f = foot_box.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "POLYDIM-EINSOF | FASE 2: PMTP | FASE 3: MORPHO PELEIDES | ARIEL GARCÍA TRABA (INDEPENDENT RESEARCH) 2026"
        p_f.font.size = Pt(8.5)
        p_f.font.color.rgb = C_MUTED

        # Slide Number
        num_box = slide.shapes.add_textbox(Inches(10.5), Inches(7.12), Inches(2.0), Inches(0.25))
        tf_n = num_box.text_frame
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.RIGHT
        p_n.text = f"Filmina {slide_num} / {total_slides}"
        p_n.font.size = Pt(8.5)
        p_n.font.bold = True
        p_n.font.color.rgb = C_CYAN

        return slide

    def add_card(slide, left, top, width, height, title="", border_color=C_BORDER, fill_color=C_CARD):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = fill_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.0)
        
        if title:
            tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.15), Inches(width - 0.4), Inches(0.35))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title.upper()
            p.font.size = Pt(10.5)
            p.font.bold = True
            p.font.color.rgb = C_CYAN
        return card

    def add_bullets(slide, left, top, width, height, bullets, font_size=11):
        tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        for i, item in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(6)
            
            if isinstance(item, tuple):
                # (heading, body)
                run_h = p.add_run()
                run_h.text = "• " + item[0] + ": "
                run_h.font.bold = True
                run_h.font.size = Pt(font_size)
                run_h.font.color.rgb = C_TITLE
                
                run_b = p.add_run()
                run_b.text = item[1]
                run_b.font.size = Pt(font_size)
                run_b.font.color.rgb = C_TEXT
            else:
                run = p.add_run()
                run.text = "• " + item
                run.font.size = Pt(font_size)
                run.font.color.rgb = C_TEXT

    def add_image_panel(slide, left, top, width, height, image_path, caption=""):
        # Card container
        add_card(slide, left, top, width, height, border_color=C_BORDER)
        if os.path.exists(image_path):
            try:
                slide.shapes.add_picture(
                    image_path,
                    Inches(left + 0.15),
                    Inches(top + 0.15),
                    width=Inches(width - 0.3),
                    height=Inches(height - 0.55 if caption else height - 0.3)
                )
            except Exception as e:
                print(f"Warn: could not embed {image_path}: {e}")
        else:
            # Fallback text
            tb = slide.shapes.add_textbox(Inches(left + 0.3), Inches(top + 1.5), Inches(width - 0.6), Inches(1.5))
            tf = tb.text_frame
            p = tf.paragraphs[0]
            p.text = f"[Diagrama / Captura Silicio: {os.path.basename(image_path)}]"
            p.font.size = Pt(12)
            p.font.color.rgb = C_MUTED
            
        if caption:
            cap_box = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + height - 0.38), Inches(width - 0.4), Inches(0.3))
            tf_c = cap_box.text_frame
            tf_c.word_wrap = True
            p_c = tf_c.paragraphs[0]
            p_c.alignment = PP_ALIGN.CENTER
            p_c.text = caption
            p_c.font.size = Pt(9)
            p_c.font.italic = True
            p_c.font.color.rgb = C_SUBTITLE

    print("Building 50-Slide Master Deck...")

    # =========================================================================
    # BLOQUE I: FUNDAMENTOS ONTELÓGICOS Y MATEMÁTICOS DE POLYDIM (Slides 1 a 12)
    # =========================================================================

    # SLIDE 1: Portada
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_BG
    bg1.line.fill.background()

    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.0), Inches(10.933), Inches(5.5))
    card1.fill.solid()
    card1.fill.fore_color.rgb = C_CARD
    card1.line.color.rgb = C_CYAN
    card1.line.width = Pt(1.5)

    tb = s1.shapes.add_textbox(Inches(1.8), Inches(1.4), Inches(9.7), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "PROYECTO POLYDIM-EINSOF"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_GOLD
    p.space_after = Pt(10)

    p2 = tf.add_paragraph()
    p2.text = "Cognición Hiperesférica Nativa y Cómputo Latente Prolongado"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = C_TITLE
    p2.space_after = Pt(8)

    p3 = tf.add_paragraph()
    p3.text = "De la Teoría del Colapso 1D a la Implementación de PMTP, MORPHO PELEIDES y el Dashboard FFI en Silicio"
    p3.font.size = Pt(14)
    p3.font.color.rgb = C_CYAN
    p3.space_after = Pt(24)

    p4 = tf.add_paragraph()
    p4.text = "Autor: Ariel García Traba & Antigravity (Google DeepMind Team)\nInstitución: Universidad Tecnológica Nacional (Ariel García Traba (Independent Research)) | Tesis Doctoral 2026\nKernel Certificado: V26300 en Silicio | 1.603 Teoremas Registrados en PostgreSQL 16"
    p4.font.size = Pt(11.5)
    p4.font.color.rgb = C_TEXT

    # SLIDE 2: Diagnóstico del Gusano 1D
    s2 = add_base_slide(
        "BLOQUE I: FUNDAMENTOS ONTOLÓGICOS",
        "El Diagnóstico Epistemológico: El 'Cuello de Botella del Gusano 1D'",
        "¿Por qué la arquitectura Transformer actual está estrangulada por el texto secuencial?",
        2
    )
    add_card(s2, 0.8, 1.6, 6.2, 5.2, "La Ilusión Lingüística Intermedia")
    add_bullets(s2, 1.0, 2.1, 5.8, 4.5, [
        ("Dogma Heredado", "Se asume que la cognición de una IA requiere emitir cadenas de tokens de texto palabra por palabra para 'pensar'."),
        ("El Gusano 1D", "Obligar a una red de 70B de parámetros a colapsar tensores latentes continuos a vocabulario discreto (|V| ≈ 128k) destruye relaciones geométricas."),
        ("Degradación por Latencia", "Cada token requiere una pasada autorregresiva completa por la memoria HBM/VRAM (Memory-Bound Wall)."),
        ("Peaje Computacional", "El razonamiento multi-paso actual genera decenas de miles de tokens intermedios que saturan el contexto O(N²).")
    ])
    add_image_panel(s2, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM-THEORICAL\docs\figures\latency_comparison_worm_vs_polydim.png", "Figura 1: Latencia 1D (Gusano de Tokens) vs Comunicación Tensorial Nativa.")

    # SLIDE 3: Teorema DPI
    s3 = add_base_slide(
        "BLOQUE I: FUNDAMENTOS ONTOLÓGICOS",
        "Teorema DPI (Data Processing Inequality): Pérdida Entrópica Irreversible",
        "Demostración analítica de la pérdida de información en el colapso autorregresivo.",
        3
    )
    add_card(s3, 0.8, 1.6, 6.2, 5.2, "Fundamentación Matemática del DPI")
    add_bullets(s3, 1.0, 2.1, 5.8, 4.5, [
        ("Teorema DPI Clásico", "Para la cadena de Markov X -> Z -> T -> Y, se cumple que I(X; Y) <= I(X; T) <= I(X; Z)."),
        ("El Colapso Discreto", "Al proyectar un estado latente continuo Z in R^D sobre un token discreto T, la entropía diferencial colapsa irreversiblemente."),
        ("Acumulación de Error", "En cadenas de razonamiento largas (Chain-of-Thought de 10k tokens), el error de aproximación semántica diverge asintóticamente."),
        ("Preservación Hiperesférica", "Mantener la trayectoria en S^(D-1) retiene la información mutua I(X; Z_t) constante a lo largo de 100k pasos.")
    ])
    add_image_panel(s3, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM_EINSOF\PMTP_V4_CORE\figures\dpi_entropy_and_latency.png", "Figura 2: Entropía DPI y Latencia en Colapso Discreto vs Continuo.")

    # SLIDE 4: La Hipótesis Hiperesférica S^(D-1)
    s4 = add_base_slide(
        "BLOQUE I: FUNDAMENTOS ONTOLÓGICOS",
        "La Hipótesis Hiperesférica: Estados de Pensamiento Continuo en S^(D-1)",
        "Geometría unitaria de alta dimensión como sustrato natural del razonamiento.",
        4
    )
    add_card(s4, 0.8, 1.6, 5.7, 5.2, "Propiedades Geométricas de S^(D-1)")
    add_bullets(s4, 1.0, 2.1, 5.3, 4.5, [
        ("Concentración de Medida", "En D >= 10.000, casi toda la masa de la esfera reside en un ecuador de ancho O(1/√D). Dos vectores aleatorios son casi ortogonales."),
        ("Invarianza de Escala", "La normalización canónica ||z|| = 1 elimina explosiones y desapariciones de gradiente numéricas."),
        ("Espacio de Hilbert Hiperesférico", "Las operaciones cognitivas son rotaciones continuas SO(D) y reflexiones de Clifford sin saltos discretos."),
        ("Supervivencia Asintótica", "Permite miles de transformaciones sin desborde numérico IEEE-754.")
    ])
    add_card(s4, 6.8, 1.6, 5.7, 5.2, "Formulación Analítica")
    add_bullets(s4, 7.0, 2.1, 5.3, 4.5, [
        ("Definición de Variedad", "S^(D-1) = { x in R^D : ||x||_2 = 1 }, provista de la métrica riemanniana inducida por el producto euclídeo."),
        ("Distancia Geodésica", "d_geo(u, v) = arccos(u^T v), midiendo la divergencia angular exacta entre conceptos latentes."),
        ("Plano Tangente T_z M", "Cualquier perturbación cognitiva reside en el subespacio ortogonal: T_z S^(D-1) = { v in R^D : z^T v = 0 }."),
        ("Transporte Paralelo", "Permite mover vectores de contexto sin distorsión angular ni deformación de la base de características.")
    ])

    # SLIDE 5: Variedad de Stiefel St(d, r)
    s5 = add_base_slide(
        "BLOQUE I: FUNDAMENTOS ONTOLÓGICOS",
        "Geometría Diferencial en Variedades de Stiefel St(d, r)",
        "Preservación isométrica estricta entre espacios latentes heterogéneos.",
        5
    )
    add_card(s5, 0.8, 1.6, 6.2, 5.2, "Inmersión Isométrica Universal")
    add_bullets(s5, 1.0, 2.1, 5.8, 4.5, [
        ("Definición Formal", "St(d, r) = { U in R^(d x r) : U^T U = I_r }, con r <= d representando los marcos ortonormales."),
        ("Inmersión Isométrica", "Garantiza que la proyección z = U^T h preserve el producto interno en el subespacio proyectado: ||U^T h|| <= ||h||."),
        ("Eliminación del Drift", "Sin la restricción de Stiefel, las matrices de pesos lineales acumulan deriva espectral en bucles recurrentes."),
        ("Teorema T-MP26", "Alineamiento de representaciones heterogéneas con cota residual de proyección estrictamente acotada.")
    ])
    add_image_panel(s5, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM-THEORICAL\docs\figures\stiefel_isometry_drift.png", "Figura 3: Deriva de Isometría en Proyección Simple vs Stiefel Manifold.")

    # SLIDE 6: Retracción Polar Newton-Schulz
    s6 = add_base_slide(
        "BLOQUE I: FUNDAMENTOS ONTOLÓGICOS",
        "Retracción Polar de Newton-Schulz vs SVD en Silicio",
        "Restauración ortogonal cuadrática en tiempo O(Dr²) sin descomposiciones pesadas.",
        6
    )
    add_card(s6, 0.8, 1.6, 6.2, 5.2, "Algoritmo PolarSafe en Silicio")
    add_bullets(s6, 1.0, 2.1, 5.8, 4.5, [
        ("El Cuello de Botella de SVD", "Calcular SVD clásica O(D³) en cada paso recurrente destruye el rendimiento de la GPU/CPU."),
        ("Iteración Newton-Schulz", "Ajuste quíntico adaptativo: X_{k+1} = X_k (15 I - 10 X_k^T X_k + 3 (X_k^T X_k)²) / 8 con convergencia de orden 4."),
        ("Precisión Bit a Bit", "Alcanza defecto de ortogonalidad ||X^T X - I|| <= 1.11 x 10^-15 (1 ULP) en sólo 5 iteraciones."),
        ("Fallback PolarSafe V2", "Inspección de condicionamiento κ(X) < 10³; si la matriz es patológica, conmutación segura a Householder QR.")
    ])
    add_image_panel(s6, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM-THEORICAL\docs\figures\spectral_dynamics_newton_schulz.png", "Figura 4: Dinámica Espectral de Convergencia del Retractor Newton-Schulz.")

    # SLIDE 7: Acumulador Neumaier
    s7 = add_base_slide(
        "BLOQUE I: FUNDAMENTOS ONTOLÓGICOS",
        "Acumulador Compensado de Neumaier: Invarianza Numérica en Silicio",
        "Eliminación de errores de redondeo catastróficos en productos punto de dimensión masiva.",
        7
    )
    add_card(s7, 0.8, 1.6, 5.7, 5.2, "El Peligro del Redondeo en D >= 10⁴")
    add_bullets(s7, 1.0, 2.1, 5.3, 4.5, [
        ("Sumatoria Estándar", "Acumular D = 100.000 componentes flotantes en FP32/FP64 acumula error O(D * ε_mach), distorsionando la norma."),
        ("Deriva de la Hiperesfera", "Un error de norma de 10^-6 traslada el vector fuera de S^(D-1), causando divergencia en 100 pasos."),
        ("Algoritmo de Neumaier", "Mantiene un término de compensación de bajo orden 'c' que captura los bits menos significativos descartados."),
        ("Cota de Error Teórica", "Garantiza error relativo |s - s_exact| / |s| <= 2 ε_mach + O(D * ε_mach²), prácticamente independiente de D.")
    ])
    add_card(s7, 6.8, 1.6, 5.7, 5.2, "Implementación en C++20 / Rust")
    add_bullets(s7, 7.0, 2.1, 5.3, 4.5, [
        ("Vectorización SIMD", "Compilado nativamente en WinLibs GCC 14.2 con registros YMM (AVX2) y ZMM (AVX-512)."),
        ("Defecto Medido en Silicio", "Error de norma en vector de 4.096 flotantes: err = 0.000e+00 (bit exacto)."),
        ("Protección Anti-Subnormales", "Flush-to-Zero (FTZ) y Denormals-are-Zero (DAZ) activados para evitar penalizaciones de 100 ciclos de reloj."),
        ("Certificación de Regresión", "Ejecutado con Exit Code 0 en todas las suites de estrés físico de POLYDIM.")
    ])

    # SLIDE 8: FWHT Roofline
    s8 = add_base_slide(
        "BLOQUE I: FUNDAMENTOS ONTOLÓGICOS",
        "Transformada Rápida de Walsh-Hadamard (FWHT) en Cache",
        "Mezclado espectral hiperdimensional en tiempo O(D log D) y ancho de banda óptimo.",
        8
    )
    add_card(s8, 0.8, 1.6, 6.2, 5.2, "Dispersión de Información Holográfica")
    add_bullets(s8, 1.0, 2.1, 5.8, 4.5, [
        ("Mezclador sin Multiplicaciones", "La matriz de Hadamard H_D opera exclusivamente mediante sumas y restas escalares."),
        ("Efecto Mariposa Holográfico", "Una perturbación en 1 dimensión se propaga uniformemente a las 10.000 dimensiones restantes en una pasada."),
        ("Modelo Roofline en Cache", "Estructura coalescente que reside enteramente en L1/L2 cache (SRAM), alcanzando el techo de ancho de banda del silicio."),
        ("Cero Consumo de VRAM Externa", "Evita accesos a memoria DRAM/HBM para operaciones de atención dispersa.")
    ])
    add_image_panel(s8, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM-THEORICAL\docs\figures\fwht_cache_roofline.png", "Figura 5: Modelo Roofline de la FWHT en Jerarquía de Cache SRAM/L2.")

    # SLIDE 9: Clifford Algebra & Hodge Duality
    s9 = add_base_slide(
        "BLOQUE I: FUNDAMENTOS ONTOLÓGICOS",
        "Álgebra Geométrica de Clifford y Dualidad de Hodge",
        "Representación multivectorial unificada y compatibilidad cuántica.",
        9
    )
    add_card(s9, 0.8, 1.6, 5.7, 5.2, "Multivectores en Cl(D)")
    add_bullets(s9, 1.0, 2.1, 5.3, 4.5, [
        ("Espacio Graduado", "Un elemento latente combina escalares (grado 0), vectores (grado 1), bivectores (grado 2) y pseudoescalares."),
        ("Producto Geométrico", "u v = u . v + u ^ v, codificando simultáneamente similitud escalar métrica y orientación del plano."),
        ("Rotaciones por Rotores", "Transformaciones espaciales continuas sin matrices: R z R~ donde R es un rotor unitario en Espin(D)."),
        ("Invariancia Topológica", "Las interacciones lógicas se convierten en trenzados algebraicos estables.")
    ])
    add_card(s9, 6.8, 1.6, 5.7, 5.2, "Estrella de Hodge ★ y Puentes Cuánticos")
    add_bullets(s9, 7.0, 2.1, 5.3, 4.5, [
        ("Dualidad de Hodge", "Mapea k-vectores a (D-k)-vectores: ★(u ^ v), permitiendo compresión ortogonal sin pérdida de orientación."),
        ("Conexión con Qubits", "El álgebra de Clifford Cl(2n) es canónicamente isomorfa al álgebra de matrices complejas de Pauli M_{2^n}(C)."),
        ("Soberanía Hardware", "Ejecutable tanto en procesadores clásicos vectorizados como en simuladores cuánticos de Clifford."),
        ("Teoremas Registrados", "Axiomatizado formalmente en PostgreSQL 16 con verificación de cero contradicciones.")
    ])

    # SLIDE 10: Benchmark Transformers vs POLYDIM
    s10 = add_base_slide(
        "BLOQUE I: FUNDAMENTOS ONTOLÓGICOS",
        "Comparativa Asintótica: Token-based Attention vs POLYDIM",
        "Superando la barrera cuadrática O(N²) mediante transformaciones en S^(D-1).",
        10
    )
    add_card(s10, 0.8, 1.6, 6.2, 5.2, "Complejidad Asintótica de Cómputo")
    add_bullets(s10, 1.0, 2.1, 5.8, 4.5, [
        ("Atención Clásica Transformer", "Requiere comparar cada token con todos los anteriores: Complejidad Temporal O(N² D) y Memoria O(N²)."),
        ("Transformaciones POLYDIM", "La evolución temporal opera como una recurrencia lineal en el espacio de estados: Complejidad Temporal O(T * D)."),
        ("Huella de Memoria Constante", "Memoria física O(1) independientemente del horizonte de razonamiento (100k pasos en 94 MB de RAM)."),
        ("Resultados Experimentales", "Aceleraciones de hasta 14x en latencia y 80% de reducción en energía para horizontes profundos.")
    ])
    add_image_panel(s10, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM_EINSOF\_HISTORICO\ENTREGA_EVAL_COLEGA\polydim_vs_transformers_benchmark.png", "Figura 6: Benchmark Asintótico: POLYDIM vs Modelos Transformer Tradicionales.")

    # SLIDE 11: Eficiencia Energética
    s11 = add_base_slide(
        "BLOQUE I: FUNDAMENTOS ONTOLÓGICOS",
        "Perfil Energético y Eficiencia Térmica del Cómputo No-Tokenizado",
        "Menos Joules por inferencia: eliminando el trasvase masivo de memoria HBM.",
        11
    )
    add_card(s11, 0.8, 1.6, 6.2, 5.2, "Economía Térmica en Silicio")
    add_bullets(s11, 1.0, 2.1, 5.8, 4.5, [
        ("Costo Energético del Acceso a VRAM", "Acceder a HBM/DRAM consume ~100x más energía por bit que una operación aritmética en SRAM."),
        ("El Problema del KV-Cache", "Los transformers requieren leer gigabytes de KV-cache en cada token generado, sobrecalentando el silicio."),
        ("In-Register Processing", "POLYDIM mantiene el estado de trabajo z_t en los registros AVX/SRAM de la GPU/CPU durante miles de pasos."),
        ("Medición Física", "Reducción de consumo de 250W (GPU saturada en decodificación) a < 45W en inferencia recurrente en CPU.")
    ])
    add_image_panel(s11, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM-THEORICAL\docs\figures\graph_energy.png", "Figura 7: Consumo Energético en Joules: Flujo de Tokens vs Cómputo PMTP.")

    # SLIDE 12: Síntesis de Teoremas Fundacionales
    s12 = add_base_slide(
        "BLOQUE I: FUNDAMENTOS ONTOLÓGICOS",
        "Bóveda Teórica: 1.603 Teoremas Certificados en PostgreSQL 16",
        "La base matemática formal inmutable que sustenta el proyecto.",
        12
    )
    add_card(s12, 0.8, 1.6, 5.7, 5.2, "Estructura de la Bóveda polydim_vec_db")
    add_bullets(s12, 1.0, 2.1, 5.3, 4.5, [
        ("Total de Teoremas", "1.603 teoremas registrados inmutablemente (MIN_ID: 1, MAX_ID: 1698), todos en estado SOTA_CERTIFIED."),
        ("Categorías Principales", "Geometría de Stiefel, Retracción de Cayley, Control de Lyapunov, Invarianza Criptográfica, Álgebra de Clifford."),
        ("Regla 0 y Regla 13", "PostgreSQL 16 como única fuente de verdad transaccional; prohibición total de SQLite activo."),
        ("Verificación Lean 4", "65 axiomas nucleares formalizados en Lean 4 Core con 0 'sorry' y verificación formal completa.")
    ])
    add_card(s12, 6.8, 1.6, 5.7, 5.2, "Últimos Hitos Teóricos (T-MP28 a T-MP32)")
    add_bullets(s12, 7.0, 2.1, 5.3, 4.5, [
        ("T-MP28", "Compresión HiPPO-Cayley Bilineal con Estabilidad Asintótica ρ = 0.9950."),
        ("T-MP29", "Cota Superior Gromov-Wasserstein L2 (GW_L2 = 0.0227 rad < 0.030) en Stiefel."),
        ("T-MP30", "Integración Simpléctica Verlet-Riemanniana con Retracción de Cayley."),
        ("T-MP31", "Invarianza de Entropía Espectral en Enjambre Tri-Stream sobre PMTP (S(G) >= 0.9933)."),
        ("T-MP32", "Certificación Asintótica en Silicio de 100.000 Pasos con Inmunidad Fuzzing IEEE-754.")
    ])

    # =========================================================================
    # BLOQUE II: FASE 2 — PMTP (PHYSICAL MEMORY TENSOR PROTOCOL) (Slides 13 a 25)
    # =========================================================================

    # SLIDE 13: Introducción a PMTP
    s13 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Introducción a PMTP: Telepatía Tensorial Zero-Copy en Memoria Compartida",
        "El protocolo físico para intercambiar estados cognitivos sin serialización a texto.",
        13, badge_color=C_GOLD
    )
    add_card(s13, 0.8, 1.6, 5.7, 5.2, "¿Qué es PMTP?")
    add_bullets(s13, 1.0, 2.1, 5.3, 4.5, [
        ("Definición Físcia", "PMTP (Physical Memory Tensor Protocol) es un bus de memoria compartida binario de latencia ultrabaja."),
        ("Ghost Protocol (Regla 22)", "Queda prohibido serializar tensores de D >= 100 a JSON, Markdown o texto en el chat. Se intercambian punteros atómicos SLAB_ID."),
        ("Zero-Copy Real", "Los procesos lectores y escritores acceden a las mismas páginas físicas de RAM/VRAM sin copias intermedias."),
        ("Multi-Lenguaje C-ABI", "Conexión transparente entre C++20, Rust 2024, Python 3.14, Dart FFI y CUDA.")
    ])
    add_card(s13, 6.8, 1.6, 5.7, 5.2, "Métricas Clave de Rendimiento")
    add_bullets(s13, 7.0, 2.1, 5.3, 4.5, [
        ("Latencia FFI de Silicio", "76.8 microsegundos por transferencia completa frente a 45 milisegundos de HTTP/JSON."),
        ("Throughput de Operaciones", "15.485 operaciones/segundo en CPU local sin sobrecarga de kernel."),
        ("Ahorro de Tokens", "100.0% de ahorro de tokens durante las fases de razonamiento recurrente."),
        ("Pipeline Completado", "28 de 28 subfases de PMTP certificadas con Exit Code 0 en 'polydim_vec_db.pmtp_pipeline'.")
    ])

    # SLIDE 14: Arquitectura ShmBus
    s14 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Arquitectura PMTP ShmBus: Win32 FileMapping & Linux /dev/shm",
        "Mecanismos de silicio para asignación y mapeo de slabs de memoria en memoria física.",
        14, badge_color=C_GOLD
    )
    add_card(s14, 0.8, 1.6, 6.2, 5.2, "Mapeo Físico de Memoria")
    add_bullets(s14, 1.0, 2.1, 5.8, 4.5, [
        ("Host Windows AGY", "Implementado vía Win32 Native IPC usando CreateFileMappingW y MapViewOfFile con seguridad DACL."),
        ("Nodo ALADIN Linux", "Implementado sobre tmpfs nativo (/dev/shm) mediante shm_open, ftruncate y mmap POSIX."),
        ("Gestor PmtpSlabAllocator", "Asigna bloques contiguos de memoria con alineación forzada a 64 bytes para instrucciones SIMD AVX-512."),
        ("Protección Anti-Crash", "Gestión de señales SIGSEGV/SEH y limpieza atómica de slabs huérfanos al terminar el proceso.")
    ])
    add_image_panel(s14, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM-THEORICAL\docs\figures\pmtp_zerocopy_architecture.png", "Figura 8: Arquitectura de Memoria Compartida Zero-Copy PMTP ShmBus.")

    # SLIDE 15: Descriptor Wire 128B
    s15 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Estructura del Descriptor Wire PMTP (128 Bytes)",
        "El contrato binario inmutable que encabeza cada tensor transmitido.",
        15, badge_color=C_GOLD
    )
    add_card(s15, 0.8, 1.6, 5.7, 5.2, "Layout de Cabecera (struct C-ABI)")
    add_bullets(s15, 1.0, 2.1, 5.3, 4.5, [
        ("Magic (4B)", "0x504D5450 (ASCII 'PMTP') para validación estricta de protocolo."),
        ("Version (2B) & Flags (2B)", "Versión 4.0; flags de encriptación, compresión y estado."),
        ("Epoch Timestamp (8B)", "Marca temporal de 64 bits para control de latencia y prevención de repetición (anti-replay)."),
        ("Node ID, PID, Domain (12B)", "Identificación unívoca del nodo emisor (AGY vs ALADIN) y dominio cognitivo."),
        ("Dimension D (8B) & DType (4B)", "Dimensión del vector (ej. 1.024 o 10.000) y tipo IEEE-754 (FP64 / FP32 / BF16)."),
        ("SlabID (64B)", "String ASCII/UTF-8 terminado en null con el identificador del slab compartido.")
    ])
    add_card(s15, 6.8, 1.6, 5.7, 5.2, "Garantías de Silicio")
    add_bullets(s15, 7.0, 2.1, 5.3, 4.5, [
        ("Tamaño Fijo", "Exactamente 128 bytes (alineado a dos líneas de cache L1 de 64B)."),
        ("Zero-Parsing Overhead", "Los receptores decodifican la cabecera en un solo ciclo mediante struct cast o struct.unpack('<IHHQ4IQIIQQ64s')."),
        ("Bitwise Determinism", "Idéntico empaquetamiento en compiladores GCC 14.2 (MinGW), Rustc 1.100 y Python 3.14."),
        ("Certificación de Integridad", "Enmienda E24-1 aprobada: invarianza criptográfica y consistencia de tipos garantizada.")
    ])

    # SLIDE 16: Concurrencia Release-Acquire
    s16 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Semántica Concurrente Release-Acquire: Cero Torn-Reads",
        "Máquina de estados cuádruple libre de bloqueos pesados (Lock-Free).",
        16, badge_color=C_GOLD
    )
    add_card(s16, 0.8, 1.6, 5.7, 5.2, "Máquina de Estados de 4 Fases (T-MP12)")
    add_bullets(s16, 1.0, 2.1, 5.3, 4.5, [
        ("Estado 0: IDLE", "El slab está libre y disponible para asignación por un escritor."),
        ("Estado 1: WRITING", "El escritor posee el slab; los lectores tienen acceso prohibido."),
        ("Estado 2: COMMITTED", "Escritura completada; barrera de memoria 'std::atomic_thread_fence(memory_order_release)' emitida."),
        ("Estado 3: READING", "Múltiples lectores acceden simultáneamente bajo orden 'memory_order_acquire'."),
        ("Eliminación de Locks", "Reemplazo de Mutexes lentos de sistema operativo por operaciones atómicas at-silicon CAS (Compare-And-Swap).")
    ])
    add_card(s16, 6.8, 1.6, 5.7, 5.2, "Prueba Adversarial Fuzzing")
    add_bullets(s16, 7.0, 2.1, 5.3, 4.5, [
        ("Ataque de Estrés Concurrente", "10 hilos lectores concurrentes leyendo mientras 1 escritor inyecta 100.000 actualizaciones."),
        ("Lecturas Parciales (Torn-Reads)", "0 lecturas inconsistentes detectadas tras 1.000.000 de comprobaciones continuas."),
        ("Condición de Carrera", "Cero deadlocks o livelocks registrados en la suite 'test_pmtp_adversarial_fuzzing.py'."),
        ("Exit Code 0", "Certificación formal registrada en BBDD bajo el teorema T-MP12.")
    ])

    # SLIDE 17: Doble Buffer Inmutable
    s17 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Protocolo de Doble Buffer Inmutable: Conmutación Atómica de Slot",
        "Garantizando lectura continua sin congelar el bucle de razonamiento del escritor.",
        17, badge_color=C_GOLD
    )
    add_card(s17, 0.8, 1.6, 5.7, 5.2, "Mecanismo Ping-Pong de Generación")
    add_bullets(s17, 1.0, 2.1, 5.3, 4.5, [
        ("Topología de Doble Ranura", "Cada slab contiene Slot 0 y Slot 1 independientes en memoria contigua."),
        ("Puntero de Generación", "Un índice atómico uint32 'active_slot' señala el estado más reciente consolidado."),
        ("Escritura en Sombra", "El núcleo cognitivo computa el nuevo estado z_{t+1} en la ranura inactiva sin interferir con los lectores."),
        ("Conmutación Atómica", "Al finalizar, conmuta el índice de slot en una sola instrucción atómica (Exchange), haciendo visible el nuevo estado instantáneamente.")
    ])
    add_card(s17, 6.8, 1.6, 5.7, 5.2, "Ventajas Arquitectónicas (T-MP15)")
    add_bullets(s17, 7.0, 2.1, 5.3, 4.5, [
        ("Latencia Cero de Espera", "Los lectores nunca bloquean al escritor; el escritor nunca frena la inferencia."),
        ("Consistencia Snap-Shot", "Un lector que inicia la lectura de Slot 0 tiene garantizada la inmutabilidad de los datos hasta liberar su lease."),
        ("Prueba de Silicio", "Validado en 'test_cycle6_counterexamples.py' con Exit Code 0."),
        ("Uso en MORPHO", "Base fundamental para que el núcleo recurrente ejecute 100k pasos a máxima velocidad.")
    ])

    # SLIDE 18: Leases de Lectura y Anti-ABA
    s18 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Leases de Lectura en Cabecera: Protección Inmunológica Anti-ABA",
        "Prevención rigurosa de sobreescrituras mientras existen lectores activos reteniendo memoria.",
        18, badge_color=C_GOLD
    )
    add_card(s18, 0.8, 1.6, 5.7, 5.2, "El Problema ABA en Memoria Compartida")
    add_bullets(s18, 1.0, 2.1, 5.3, 4.5, [
        ("Definición del Riesgo", "Un lector lento accede al buffer A; el escritor conmuta a B y luego vuelve a sobreescribir A creyendo que está libre."),
        ("Corrupción Catastrófica", "El lector procesa un tensor híbrido corrupto (mitad viejo, mitad nuevo), arruinando la inferencia neuronal."),
        ("Contador Atómico de Leases", "La cabecera de 64B contiene un uint32 'reader_count' incrementado atómicamente por cada lector al entrar.")
    ])
    add_card(s18, 6.8, 1.6, 5.7, 5.2, "Resolución Teorema T-MP17")
    add_bullets(s18, 7.0, 2.1, 5.3, 4.5, [
        ("Rechazo de Sobrescritura", "Si 'reader_count > 0', el escritor rechaza escribir en esa ranura y conmuta o espera activamente."),
        ("Timeout de Seguridad", "Si un lector falla o muere, un temporizador de arriendo (lease timeout) libera el contador tras 100 ms."),
        ("Verificación Empírica", "Superó 50.000 simulaciones de inanición intencional en silicio sin un solo fallo de memoria.")
    ])

    # SLIDE 19: Invarianza Criptográfica BLAKE2b
    s19 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Invarianza Criptográfica: Firmas HMAC-BLAKE2b y Control Anti-Replay",
        "Seguridad de nivel militar en enlaces de memoria compartida y sockets TCP inter-nodo.",
        19, badge_color=C_GOLD
    )
    add_card(s19, 0.8, 1.6, 5.7, 5.2, "Firma de Hardware BLAKE2b")
    add_bullets(s19, 1.0, 2.1, 5.3, 4.5, [
        ("Digest Criptográfico 32B", "Cada transmisión tensorial calcula un HMAC BLAKE2b sobre los primeros 80 bytes de la cabecera + payload."),
        ("Velocidad Extrema", "BLAKE2b procesa > 1 GB/s por núcleo en CPU, superando ampliamente a SHA-256 y MD5."),
        ("Clave Compartida Precalibrada", "Autenticación mutua entre el Host Windows AGY y el Nodo ALADIN Linux."),
        ("Integridad a Nivel de Bit", "Cualquier corrupción de hardware por radiación o bit-flip es descartada de inmediato antes del cómputo.")
    ])
    add_card(s19, 6.8, 1.6, 5.7, 5.2, "Protección Anti-Replay")
    add_bullets(s19, 7.0, 2.1, 5.3, 4.5, [
        ("Ventana Temporal Deslizante", "Se rechazan paquetes cuyo timestamp 'epoch' difiera en más de 2.0 segundos respecto al reloj del nodo."),
        ("Nonce Creciente Monótono", "Previene que un atacante o hilo desincronizado reinyecte activaciones latentes pasadas."),
        ("Implementación en Silicio", "Módulo 'pmtp_crypto_wire.py' desplegado tanto en Windows como en '/usr/local/lib/pmtp' en Debian 13.")
    ])

    # SLIDE 20: El Contrato de Silicio (Clases de Memoria)
    s20 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "El Contrato de Silicio y Agnosticismo de Hardware (Regla 27)",
        "El software no asume silicio: interroga dinámicamente y se despacha a la jerarquía óptima.",
        20, badge_color=C_GOLD
    )
    add_card(s20, 0.8, 1.6, 11.7, 5.2, "Jerarquía de Clases de Memoria en PMTP")
    add_bullets(s20, 1.0, 2.1, 11.3, 4.5, [
        ("Clase 0 (Wafer SRAM / On-Chip)", "Cerebras CS-3 / Tenstorrent SRAM. Ancho de banda de petabytes/s. Máxima prioridad para el núcleo de 100k pasos."),
        ("Clase 1 (HBM3 / HBM2e)", "NVIDIA H100 / A100 / Google Cloud TPU v5e. Despacho directo vía Triton coalescente y CUDA IPC handles de 128B."),
        ("Clase 2 (GDDR6 / GDDR7)", "GPUs locales NVIDIA GeForce / RTX. Comunicación vía persistent kernels SM70-SM90."),
        ("Clase 3 (DDR5 / DDR4 NUMA)", "RAM del sistema Host Windows AGY (AVX2/AVX-512) y Nodo ALADIN (Core i3-8100 8GB DDR4)."),
        ("Clase 4 (DDR3 Legacy / AMD A4 Floor)", "Piso mínimo garantizado para entornos de bajo costo y compatibilidad total en laboratorios de grado UTN.")
    ])

    # SLIDE 21: Latencia FFI Comparativa
    s21 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Latencia FFI de Silicio: 76.8 µs vs Milisegundos de Red",
        "El puente directo entre compilados nativos y entornos de ejecución de alto nivel.",
        21, badge_color=C_GOLD
    )
    add_card(s21, 0.8, 1.6, 6.2, 5.2, "Demolición de la Sobrecarga IPC")
    add_bullets(s21, 1.0, 2.1, 5.8, 4.5, [
        ("El Abismo Tradicional", "APIs REST, WebSockets y gRPC imponen serialización JSON/Protobuf, TCP stack y context switches del SO (10 a 50 ms)."),
        ("El Salto PMTP FFI", "C-ABI directo mediante punteros en memoria compartida: 76.8 microsegundos medidos en CPU local."),
        ("Throughput de Rendimiento", "Capacidad de procesar más de 13.000 transferencias tensoriales por segundo por hilo."),
        ("Impacto en Razonamiento", "Permite que agentes colaboren cientos de veces en el tiempo que una API remota respondería una sola llamada.")
    ])
    add_image_panel(s21, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM_EINSOF\figures_presentation\dart_ffi_latency_benchmark.png", "Figura 9: Comparativa de Latencia FFI PMTP frente a Transmisiones Tradicionales.")

    # SLIDE 22: Kernel C++20 WinLibs GCC 14.2
    s22 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Kernel C++20 Nativo: Vectorización AVX2/AVX-512 y Neumaier SIMD",
        "El motor de ultra-bajo nivel compilado en Windows Host.",
        22, badge_color=C_GOLD
    )
    add_card(s22, 0.8, 1.6, 5.7, 5.2, "Características del Kernel C++20")
    add_bullets(s22, 1.0, 2.1, 5.3, 4.5, [
        ("Compilador", "WinLibs GCC 14.2.0 (POSIX threads, x86_64, C++20 estándar sin extensiones propietarias)."),
        ("Optimizaciones de Compilación", "Flags: -O3 -mavx2 -mfma -ffast-math -fopenmp -shared."),
        ("Neumaier SIMD Intrinsics", "Implementación manual con _mm256_fmadd_pd y corrección de redondeo vectorizada."),
        ("Biblioteca Dinámica", "libpolydim_cpp_v26300.dll exportando interfaz C pura ('extern \"C\"') para Dart y Python.")
    ])
    add_card(s22, 6.8, 1.6, 5.7, 5.2, "Pruebas Físicas de Silicio")
    add_bullets(s22, 7.0, 2.1, 5.3, 4.5, [
        ("Suite de Silicio", "test_silicon_v26300.py ejecutado con Exit Code 0."),
        ("Latencia Total de Prueba", "3.47 segundos para 100.000 operaciones matemáticas complejas."),
        ("Uso de Memoria", "94 MB de RAM física constante; cero memory leaks."),
        ("Firewall de Memoria", "Captura controlada de vectores nulos, flotantes subnormales y NaNs.")
    ])

    # SLIDE 23: Kernel Rust 2024 Safe SIMD
    s23 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Kernel Rust 2024: Safe SIMD y Aislamiento de Memoria",
        "Garantías matemáticas de corrección en silicio y cero comportamiento indefinido (UB).",
        23, badge_color=C_GOLD
    )
    add_card(s23, 0.8, 1.6, 5.7, 5.2, "Arquitectura Rust Safe SIMD")
    add_bullets(s23, 1.0, 2.1, 5.3, 4.5, [
        ("Edición Rust", "Rust 1.100 Edition 2024 compilado con rustc a nivel de biblioteca dinámica nativa."),
        ("Borrow Checker en FFI", "Envolturas seguras 'ManifoldSlice' que previenen aliasing de punteros entre procesos concurrentes."),
        ("Safe SIMD Abstraction", "Vectorización automática portátil sobre arquitecturas x86_64 y AArch64 (ARM)."),
        ("Biblioteca Generada", "libpolydim_rust_v26300.dll con símbolos C-ABI idénticos a la versión C++.")
    ])
    add_card(s23, 6.8, 1.6, 5.7, 5.2, "Defensa en Profundidad")
    add_bullets(s23, 7.0, 2.1, 5.3, 4.5, [
        ("Protección Subnormal", "Filtro activo contra flotantes subnormales (10^-315) para evitar parálisis de pipeline en la FPU."),
        ("Inmunidad a Buffer Overflow", "Verificación estricta de límites (bounds checking) en la cabecera del descriptor PMTP."),
        ("Intercambiabilidad Total", "El usuario puede alternar dinámicamente entre el kernel C++ y Rust sin recompilar Dart.")
    ])

    # SLIDE 24: Integración GPU Triton SM70-SM90
    s24 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Integración GPU Triton: Persistent Grids y SRAM Tiling",
        "Optimizaciones coalescentes para arquitecturas NVIDIA Volta a Hopper.",
        24, badge_color=C_GOLD
    )
    add_card(s24, 0.8, 1.6, 6.2, 5.2, "Triton Tiling en GPU")
    add_bullets(s24, 1.0, 2.1, 5.8, 4.5, [
        ("SRAM Tiling Coalescente", "Bloques de 128x128 elementos cargados directamente a la memoria compartida SMEM de la GPU."),
        ("Persistent Kernels SM90", "Hilos de GPU que permanecen vivos en los Streaming Multiprocessors, evitando el costo de lanzamiento de kernels."),
        ("CUDA IPC Handles", "Descriptores de 128 bytes que permiten compartir punteros VRAM directos entre procesos Python locales sin pasar por el host."),
        ("Intensidad Aritmética", "Maximiza el aprovechamiento de los Tensor Cores en operaciones de proyección de Stiefel.")
    ])
    add_image_panel(s24, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM_EINSOF\_HISTORICO\ENTREGA_2026_10_09_V26200\RESPUESTAS\c07_arithmetic_intensity.png", "Figura 10: Intensidad Aritmética de Kernels GPU Triton vs Memoria Coalescente.")

    # SLIDE 25: Clúster Dual Distribuido (Host AGY + ALADIN)
    s25 = add_base_slide(
        "BLOQUE II: FASE 2 — ARQUITECTURA PMTP",
        "Clúster Dual Distribuido: Host AGY y Nodo ALADIN (Debian 13)",
        "Topología física de cómputo: Windows Host y Servidor Linux en 192.168.100.21.",
        25, badge_color=C_GOLD
    )
    add_card(s25, 0.8, 1.6, 5.7, 5.2, "Nodo 1: Host Windows AGY")
    add_bullets(s25, 1.0, 2.1, 5.3, 4.5, [
        ("Hardware", "Estación de trabajo local con CPU multithreaded AVX2, PostgreSQL 16 local y Dart Flutter UI."),
        ("Rol Operativo", "Orquestador principal, compilación nativa en GCC 14 / Rust y control de interfaz gráfica."),
        ("PMTP ShmBus", "FileMapping en RAM física local con latencia de 76.8 µs.")
    ])
    add_card(s25, 6.8, 1.6, 5.7, 5.2, "Nodo 2: Nodo ALADIN (192.168.100.21)")
    add_bullets(s25, 7.0, 2.1, 5.3, 4.5, [
        ("Hardware", "Intel Core i3-8100 4C/4T @ 3.6GHz, 8GB DDR4, Debian 13 Headless."),
        ("Servicios Activos", "Daemon de silicio 'aladin-pmtp.service' en puerto 9999 y Ollama en puerto 11434."),
        ("Modelos Locales", "qwen2.5-coder:1.5b y deepseek-r1:1.5b cargados para razonamiento abierto y auditoría."),
        ("Telepatía Socket", "Transmisión binaria pura IEEE-754 con firma BLAKE2b (Roundtrip 62.8 ms, error de norma 0.000e+00).")
    ])

    # =========================================================================
    # BLOQUE III: FASE 3 — MORPHO PELEIDES (Slides 26 a 38)
    # =========================================================================

    # SLIDE 26: Introducción a MORPHO PELEIDES
    s26 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Introducción a MORPHO PELEIDES: Latent Cognitive Fabric",
        "Construyendo la posibilidad del razonamiento iterativo profundo sin emisión lingüística.",
        26, badge_color=C_PURPLE
    )
    add_card(s26, 0.8, 1.6, 5.7, 5.2, "El Cambio de Criterio")
    add_bullets(s26, 1.0, 2.1, 5.3, 4.5, [
        ("De la Imposibilidad a la Posibilidad", "No existe ley matemática o física que impida a una red realizar 100.000 operaciones cognitivas en estados continuos."),
        ("Los 3 Objetivos de MORPHO", "1. Miles de operaciones internas continuas sin tokens 1D.\n2. Cooperación multi-modelo intercambiando estados latentes.\n3. Razonamiento profundo más eficiente y escalable."),
        ("El Eslabón Faltante", "MORPHO no busca inventar el aprendizaje profundo desde cero; diseña la arquitectura geométrica de control, estabilidad y memoria.")
    ])
    add_card(s26, 6.8, 1.6, 5.7, 5.2, "Pilares Arquitectónicos")
    add_bullets(s26, 7.0, 2.1, 5.3, 4.5, [
        ("Puente Semántico POLYDIM", "Alineación de Stiefel St(d, r) y proyecciones canónicas."),
        ("Núcleo Recurrente de Enjambre", "Evolución sobre variedad canónica d_core = 1024."),
        ("Memoria Continua CAM-HiPPO", "Desacople de memoria asociativa exacta y memoria temporal de largo aliento."),
        ("Decodificación Terminal", "Colapso a lenguaje natural o código exclusivamente al finalizar la tarea.")
    ])

    # SLIDE 27: Demostración Constructiva de 100k Pasos
    s27 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Demostración Constructiva: 100.000 Transiciones de Estado Interno",
        "Prueba analítica de la computabilidad no lingüística prolongada.",
        27, badge_color=C_PURPLE
    )
    add_card(s27, 0.8, 1.6, 6.2, 5.2, "Construcción Matemática Formal")
    add_bullets(s27, 1.0, 2.1, 5.8, 4.5, [
        ("Definición de Estado", "Definimos s_t = (h_t, m_t, c_t) en espacio euclídeo/hiperesférico continuo."),
        ("Transición Recurrente", "s_{t+1} = F(s_t, u), ejecutando s_{100000} = F^{100000}(s_0, u)."),
        ("Decodificación Terminal", "y = G(s_{100000}). Durante las 100.000 transiciones intermedias no se emite ni un solo token."),
        ("Teorema de Siegelmann-Sontag (1995)", "Las RNN continuas simulan máquinas de Turing universales. El razonamiento textual intermedio NO es una necesidad computacional universal.")
    ])
    add_image_panel(s27, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM_EINSOF\figures_presentation\mpleiades_100k_lyapunov_convergence.png", "Figura 11: Convergencia de Lyapunov y Defecto de Norma en 100.000 Pasos.")

    # SLIDE 28: Evidencia Experimental SOTA
    s28 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Evidencia Experimental SOTA: Cooperación Latente Publicada",
        "Precedentes académicos directos en ICML 2025, ICML 2026 y ACL 2026.",
        28, badge_color=C_PURPLE
    )
    add_card(s28, 0.8, 1.6, 11.7, 5.2, "Precedentes Internacionales de Vanguardia")
    add_bullets(s28, 1.0, 2.1, 11.3, 4.5, [
        ("LatentMAS (ICML 2026)", "Sistema multiagente con memoria latente compartida: 14.6% mayor exactitud, 70.8–83.7% menos tokens de salida y aceleraciones de 4x a 4.3x frente a mensajes de texto."),
        ("Communicating Activations Between LM Agents (ICML 2025, Ramesh et al.)", "Intercambio directo de activaciones interviniendo capas internas del modelo receptor: mejoras de hasta 27% frente a comunicación textual."),
        ("Interlat (ACL 2026)", "Comunicación completamente latente entre agentes heterogéneos mediante compresión de representaciones intermedias."),
        ("STARS (ICML 2026)", "Estabilización de trayectorias latentes para mejorar la escalabilidad y profundidad en transformers recurrentes."),
        ("COCONUT & Recurrent Depth", "Entrenamiento de transformers con pensamientos continuos realimentados sin emisión autorregresiva.")
    ])

    # SLIDE 29: Los 3 Puntos Ciegos Refutados
    s29 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Los 3 Puntos Ciegos del Enfoque Ingenuo y la Solución POLYDIM",
        "Refutación Red Team de las vulnerabilidades asintóticas en espacios continuos.",
        29, badge_color=C_PURPLE
    )
    add_card(s29, 0.8, 1.6, 3.7, 5.2, "1. Colapso de Rango", border_color=C_ROSE)
    add_bullets(s29, 0.9, 2.1, 3.5, 4.5, [
        ("Falla Ingenua", "Una simple proyección P_R acota la norma pero no evita que el estado colapse a un atractor trivial de dimensión 0 (Rank Collapse)."),
        ("Solución POLYDIM", "Flujo Riemanniano simpléctico en S^(D-1) y monitoreo espectral continuo (T-MP24).")
    ], font_size=10)
    add_card(s29, 4.8, 1.6, 3.7, 5.2, "2. Deriva Semántica", border_color=C_ROSE)
    add_bullets(s29, 4.9, 2.1, 3.5, 4.5, [
        ("Falla Ingenua", "Aprender adaptadores libres f_A, g_B acumula deriva métrica en pasos profundos, distorsionando el significado."),
        ("Solución POLYDIM", "Operador TR-AGN con cota de Lipschitz y regularización Gromov-Wasserstein (T-MP23 / T-MP26).")
    ], font_size=10)
    add_card(s29, 8.8, 1.6, 3.7, 5.2, "3. Memoria Finita", border_color=C_ROSE)
    add_bullets(s29, 8.9, 2.1, 3.5, 4.5, [
        ("Falla Ingenua", "Un vector z_t finito no puede retener 100k pasos de historia sin saturación exponencial (Límite Hopfield)."),
        ("Solución POLYDIM", "Memoria desacoplada: CAM Hebbiana asociativa + compresión temporal HiPPO-Cayley (T-MP25).")
    ], font_size=10)

    # SLIDE 30: Etapa 1 de MORPHO
    s30 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Etapa 1 de MORPHO: Ingestión Multi-Modal y Proyección Stiefel",
        "Mapeo canónico de fuentes heterogéneas al espacio común z* in R^r.",
        30, badge_color=C_PURPLE
    )
    add_card(s30, 0.8, 1.6, 5.7, 5.2, "Arquitectura de Ingestión")
    add_bullets(s30, 1.0, 2.1, 5.3, 4.5, [
        ("Fuentes Heterogéneas", "Texto, imágenes, audio, código o activaciones de modelos especialistas A y B."),
        ("Inmersión en Stiefel", "U_A in St(d_A, r) y U_B in St(d_B, r) con r <= min(d_A, d_B)."),
        ("Proyección Inicial", "z_A = U_A^T h_A, z_B = U_B^T h_B."),
        ("Retracción Polar", "z = Polar(W z + b) mediante iteración de Newton-Schulz de 5 pasos.")
    ])
    add_card(s30, 6.8, 1.6, 5.7, 5.2, "Contrato de Salida Etapa 1")
    add_bullets(s30, 7.0, 2.1, 5.3, 4.5, [
        ("Vector Canónico z*", "fp32[r] en la carta de la variedad, con ||z*|| <= 1."),
        ("Marcos de Stiefel Congelados", "U_stack in fp32[K, d_k, r] preservados para decodificación."),
        ("Diccionario CAM", "Claves y valores normalizados en memoria RAM compartida."),
        ("Residuo de Calibración", "L_cal <= 10^-6 y retención de información mutua >= 99.9%.")
    ])

    # SLIDE 31: Media Geodésica de Karcher
    s31 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Fusión Canónica: Media Geodésica de Karcher en St(d, r)",
        "Unificando perspectivas multi-agente en la curvatura de la variedad.",
        31, badge_color=C_PURPLE
    )
    add_card(s31, 0.8, 1.6, 5.7, 5.2, "Definición del Centro de Masa Riemanniano")
    add_bullets(s31, 1.0, 2.1, 5.3, 4.5, [
        ("El Error de la Media Euclídea", "Sumar vectores ponderados z_prom = sum(w_i z_i) abandona la variedad y destruye la ortogonalidad."),
        ("Formulación de Karcher", "z* = argmin_{z in St} sum_{k=1}^K w_k d_geo²(z, z_k), donde d_geo(z, z') = ||log(z^T z')||_F."),
        ("Algoritmo de Iteración", "5 a 8 pasadas de descenso de gradiente riemanniano en el plano tangente, con convergencia garantizada para condicional κ <= 10³.")
    ])
    add_card(s31, 6.8, 1.6, 5.7, 5.2, "Propiedades de Silicio")
    add_bullets(s31, 7.0, 2.1, 5.3, 4.5, [
        ("Robustez frente a Agentes Anómalos", "La distancia geodésica acota el impacto de gradientes extremos o modelos alucinados."),
        ("Invarianza de Rotación", "Si todos los modelos giran su espacio de coordenadas, z* preserva la geometría intrínseca."),
        ("Cero Sobrecarga de Tokens", "Fusión de representaciones en 1.2 milisegundos en CPU host.")
    ])

    # SLIDE 32: Etapa 2 de MORPHO (El Núcleo Recurrente)
    s32 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Etapa 2 de MORPHO: El Núcleo Recurrente Canónico (d_core = 1024)",
        "El motor de razonamiento de 100.000 iteraciones operando sobre PMTP.",
        32, badge_color=C_PURPLE
    )
    add_card(s32, 0.8, 1.6, 5.7, 5.2, "Evolución Temporal en el Espacio Canónico")
    add_bullets(s32, 1.0, 2.1, 5.3, 4.5, [
        ("Desacople Dimensional", "El núcleo opera en d_core = 1024, desacoplado de las dimensiones externas de los LLMs (ej. 4096 o 8192)."),
        ("Dinámica de Estado", "z_{t+1} = P_R[ z_t + α_t F_θ(z_t, m_t, u_t) ], donde F_θ es una red especializada ultraliviana (50M params)."),
        ("Swarm de Osciladores", "Acoplamiento tipo Kuramoto entre múltiples canales cognitivos con cota de sincronización κ <= 0.1."),
        ("Cero Emisión Intermedia", "Evolución pura en RAM; cero tokens generados durante las 100.000 iteraciones.")
    ])
    add_card(s32, 6.8, 1.6, 5.7, 5.2, "Mecanismos de Guardia Anti-Colapso")
    add_bullets(s32, 7.0, 2.1, 5.3, 4.5, [
        ("Rank Guard", "Inspección cada 1.000 pasos de σ_min(U_t^T U_t); si cae por debajo de 10^-6, inyección de vector tangente ortogonal."),
        ("Suelo de Entropía", "Mantenimiento estricto de H(p_CAM) >= 0.5 nats para evitar fijación en conceptos únicos."),
        ("Monitor de Lyapunov", "Comprobación de decrecimiento monótono del potencial V(s_t); disparo de reset TR-AGN ante 10 violaciones continuas.")
    ])

    # SLIDE 33: Flujo Riemanniano Simpléctico
    s33 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Flujo Riemanniano Simpléctico en S^(D-1): Integrador de Cayley",
        "Preservación de volumen simpléctico y estabilidad incondicional.",
        33, badge_color=C_PURPLE
    )
    add_card(s33, 0.8, 1.6, 5.7, 5.2, "Dinámica Hamiltoniana en Tangente T M")
    add_bullets(s33, 1.0, 2.1, 5.3, 4.5, [
        ("Hamiltoniano del Pensamiento", "H(U, P) = (1/2) Tr(P^T P) + V(U), donde V(U) es el potencial derivado de la energía CAM."),
        ("Conservación del Volumen de Fase", "Por el teorema de Liouville, el flujo simpléctico preserva la entropía diferencial del estado cognitivo."),
        ("Retracción de Cayley", "U_{t+1} = (I - ξ_t / 2)⁻¹ (I + ξ_t / 2) U_t, donde ξ_t = h Ω ∇_U H."),
        ("Estabilidad Incondicional", "A diferencia de Euler o Runge-Kutta, Cayley mantiene la ortogonalidad U^T U = I_r sin importar el paso 'h'.")
    ])
    add_card(s33, 6.8, 1.6, 5.7, 5.2, "Validación en Teorema T-MP24 / T-MP30")
    add_bullets(s33, 7.0, 2.1, 5.3, 4.5, [
        ("Disipación Ortogonal Tangente", "Inyección controlada de fricción riemanniana para forzar convergencia al atractor de la solución."),
        ("Error de Defecto Medido", "||U_{100000}^T U_{100000} - I|| = 2.22 x 10^-16 (1 ULP bit exacto)."),
        ("Potencial Final de Energía", "V_final = 0.0000000000e+00, demostrando llegada exacta al mínimo sin oscilaciones espurias.")
    ])

    # SLIDE 34: Operador TR-AGN Lipschitz
    s34 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Operador TR-AGN (Trust-Region Adaptive Gain) y Cota de Lipschitz",
        "Garantizando que las actualizaciones no destruyan la estructura de representación.",
        34, badge_color=C_PURPLE
    )
    add_card(s34, 0.8, 1.6, 5.7, 5.2, "Control Adaptativo de Ganancia (T-MP23)")
    add_bullets(s34, 1.0, 2.1, 5.3, 4.5, [
        ("El Peligro de Ganancia Fija", "Un paso muy grande provoca explosión del estado; un paso muy pequeño estanca el razonamiento."),
        ("Fórmula TR-AGN", "β_{t+1} = β_t * exp( -η * (||∇_U H|| - τ_TR) / (||∇_U H|| + τ_TR) )."),
        ("Ajuste Continuo", "Si el gradiente excede la región de confianza, la ganancia se contrae automáticamente de forma suave."),
        ("Cota Estricta de Lipschitz", "L_F <= 1 - δ_cont (δ_cont = 10^-3), garantizando contracción estricta ||F(s) - F(s')|| < ||s - s'||.")
    ])
    add_card(s34, 6.8, 1.6, 5.7, 5.2, "Prueba en Silicio Real (Qwen2.5-0.5B)")
    add_bullets(s34, 7.0, 2.1, 5.3, 4.5, [
        ("Intervención Latente Activa", "Inyección del operador TR-AGN en las capas intermedias de Qwen2.5-0.5B."),
        ("Error de Conservación de Norma", "Error L2 = 0.0000000000e+00 (cero deriva)."),
        ("Divergencia KL Controlada", "D_KL = 0.001971 nats (< 0.5 umbral máximo), certificando estabilidad semántica total."),
        ("Cero NaNs o Desbordes", "Prueba superada en 10.000 iteraciones consecutivas con Exit Code 0.")
    ])

    # SLIDE 35: Memoria Híbrida CAM-HiPPO
    s35 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Memoria Híbrida Desacoplada: CAM Hebbiana + HiPPO-Cayley",
        "Resolviendo simultáneamente el recuerdo asociativo exacto y el horizonte temporal masivo.",
        35, badge_color=C_PURPLE
    )
    add_card(s35, 0.8, 1.6, 6.2, 5.2, "Desacople de Estructuras (T-MP25)")
    add_bullets(s35, 1.0, 2.1, 5.8, 4.5, [
        ("CAM (Modern Hopfield)", "Memoria direccionable por contenido: CAM(q) = softmax(K q / √r) V. Sharp minima para recuperación asociativa con 100% de exactitud."),
        ("HiPPO-Cayley Continuo", "Proyección polinomial de Legendre de la historia continua: dc/dt = A c + B u, con A = Cayley(A_HiPPO). Radio espectral ρ(A) <= 1.0."),
        ("Fusión Dinámica m_t", "m_t = α CAM(U_t) + (1-α) c_t, con compuerta α aprendida en tiempo real."),
        ("Prueba MQAR Extrema", "100.0% de recuperación en horizontes T in [16, 128] con distractores continuos frente al colapso de RNNs clásicas.")
    ])
    add_image_panel(s35, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM_EINSOF\figures_presentation\cam_hippo_memory_scaling.png", "Figura 12: Exactitud MQAR vs Horizonte Temporal: CAM-HiPPO vs Transformers y RNNs.")

    # SLIDE 36: Economía de Cómputo Asintótico
    s36 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Economía de Cómputo Asintótico: Desacople Núcleo vs Especialistas",
        "Cómo ejecutar 100.000 pasos de razonamiento sin destruir el presupuesto.",
        36, badge_color=C_PURPLE
    )
    add_card(s36, 0.8, 1.6, 6.2, 5.2, "Modelo de Costos Formal")
    add_bullets(s36, 1.0, 2.1, 5.8, 4.5, [
        ("La Trampa del Cómputo Homogéneo", "Ejecutar 100.000 pasos de un LLM de 70B requeriría semanas de cluster y cientos de miles de dólares."),
        ("Ecuación de Coste Desacoplado", "C_total = C_in + T * C_core + N * C_spec + C_mem + C_out, con T = 100.000 y N << T (ej. N = 5)."),
        ("Núcleo Liviano (C_core)", "El núcleo d_core = 1024 corre a 1.433 pasos/s en CPU local (69.77 segundos para 100k pasos)."),
        ("Especialistas Externos (C_spec)", "Los LLMs pesados solo se consultan N veces como oráculos de anclaje inicial y final."),
        ("Ahorro Económico", "Reducción de coste computacional superior al 99.8% frente a arquitecturas monolíticas.")
    ])
    add_image_panel(s36, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM_EINSOF\figures_presentation\computational_cost_scaling.png", "Figura 13: Escala de Costo Computacional Relativo: Tokens 1D vs Núcleo Desacoplado.")

    # SLIDE 37: Etapa 3 (Decodificación Terminal y Arbitraje)
    s37 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Etapa 3 de MORPHO: Decodificación Terminal Única y Arbitraje",
        "El colapso del estado consolidado z_{100000} a lenguaje natural verificado.",
        37, badge_color=C_PURPLE
    )
    add_card(s37, 0.8, 1.6, 5.7, 5.2, "Decodificación en un Solo Paso")
    add_bullets(s37, 1.0, 2.1, 5.3, 4.5, [
        ("Un Solo Forward Pass", "y = G(s_T) = softmax(W_out Polar(U_T) s_T + b_out)."),
        ("Sin Bucle Autorregresivo", "El estado ya contiene la deducción completa; el decodificador actúa como transductor simbólico."),
        ("Arbitraje Multi-Oráculo", "Los oráculos comerciales (Claude, Gemini, GPT) reciben la representación consolidada y arbitran mediante Brier scores ponderados.")
    ])
    add_card(s37, 6.8, 1.6, 5.7, 5.2, "Validación Anti-Alucinación")
    add_bullets(s37, 7.0, 2.1, 5.3, 4.5, [
        ("Consistencia CAM", "Cada afirmación en 'y' debe recuperar una clave CAM con similitud >= 0.85."),
        ("Consistencia HiPPO", "El orden lógico temporal debe coincidir con la autocorrelación de c_T."),
        ("Dictamen Terminal", "Emisión de veredicto estructurado: enum{ ACCEPT, FLAG, REJECT } respaldado por métricas crudas de silicio.")
    ])

    # SLIDE 38: Certificación Silicio 100k Pasos
    s38 = add_base_slide(
        "BLOQUE III: FASE 3 — MORPHO PELEIDES",
        "Certificación en Silicio de 100.000 Pasos (Exit Code 0)",
        "Resultados físicos crudos ejecutados en silicio real local.",
        38, badge_color=C_PURPLE
    )
    add_card(s38, 0.8, 1.6, 11.7, 5.2, "Métricas Físicas de la Suite test_mpleiades_100k_stress.py")
    add_bullets(s38, 1.0, 2.1, 11.3, 4.5, [
        ("Pasos Ejecutados", "100.000 iteraciones recurrentes continuas completadas al 100%."),
        ("Tiempo y Rendimiento", "69.77 segundos totales a una velocidad sostenida de 1.433 pasos por segundo en CPU local."),
        ("Huella de Memoria Física", "Delta de RAM: +0.07 MB (estabilidad O(1) absoluta sin fugas ni fragmentación)."),
        ("Defecto de Norma Ortogonal", "2.22 x 10^-16 (1 ULP), demostrando invarianza numérica total tras 100.000 retracciones."),
        ("Ataques Hostiles de Fuzzing", "20 de 20 pruebas de estrés superadas (inyecciones de NaNs, flotantes subnormales 10^-315, vectores nulos)."),
        ("Código de Salida", "Exit Code 0 verificado y registrado inmutablemente en PostgreSQL 16.")
    ])

    # =========================================================================
    # BLOQUE IV: DART DASHBOARD & SILICON INTEROPERABILITY (Slides 39 a 46)
    # =========================================================================

    # SLIDE 39: La Capa de Presentación Flutter / Dart
    s39 = add_base_slide(
        "BLOQUE IV: DART DASHBOARD & INTEROPERABILIDAD",
        "La Capa de Inspección: Dashboard Flutter / Dart FFI",
        "Visualización interactiva en tiempo real del tejido cognitivo latente.",
        39
    )
    add_card(s39, 0.8, 1.6, 5.7, 5.2, "Arquitectura del Dashboard")
    add_bullets(s39, 1.0, 2.1, 5.3, 4.5, [
        ("Framework Frontend", "Flutter Desktop / Web con enlace nativo Dart FFI a bibliotecas C++20 y Rust."),
        ("Rol Operativo", "Permitir a investigadores y alumnos de grado inspeccionar la evolución del tensor latente en tiempo real."),
        ("Dashboard HTML Unificado", "E:\\POLYDIM_EINSOF\\polydim_estado_dashboard.html interactivo con pestañas de Pipeline, Base de Datos y Silicio."),
        ("Cero Fricción UI", "Renderizado a 60 FPS sin interferir con los hilos de cómputo en segundo plano.")
    ])
    add_card(s39, 6.8, 1.6, 5.7, 5.2, "Paneles Principales")
    add_bullets(s39, 7.0, 2.1, 5.3, 4.5, [
        ("Monitor de Slabs PMTP", "Visualización en vivo de slots IDLE, WRITING, COMMITTED y READING."),
        ("Tracking de Stiefel", "Gráfica continua de desviación ortogonal ||U^T U - I|| en tiempo real."),
        ("Estado de Nodos Duales", "Telemetría de CPU/RAM del Host Windows AGY y Nodo ALADIN Linux."),
        ("Registro de Teoremas", "Consulta directa de los 1.603 teoremas certificados en PostgreSQL 16.")
    ])

    # SLIDE 40: Enlace FFI de Alto Desempeño
    s40 = add_base_slide(
        "BLOQUE IV: DART DASHBOARD & INTEROPERABILIDAD",
        "Enlace FFI de Alto Desempeño: polydim_v26155_ffi.dart",
        "C-ABI directo sin copias intermedias entre el motor gráfico y los kernels nativos.",
        40
    )
    add_card(s40, 0.8, 1.6, 5.7, 5.2, "Estructura de Enlace Dart FFI")
    add_bullets(s40, 1.0, 2.1, 5.3, 4.5, [
        ("Bindings Dinámicos", "Uso de 'dart:ffi' con DynamicLibrary.open('libpolydim_cpp_v26300.dll')."),
        ("Punteros Tipados", "Pointer<Double>, Pointer<Uint8> mapeados directamente a la memoria física compartida."),
        ("Zero Marshalling", "Los arreglos de tensores de 1.024 o 10.000 flotantes se leen in-situ sin conversión a objetos Dart."),
        ("Llamadas Asíncronas", "NativeCallable.isolateLocal para telemetría sin bloquear el hilo principal de la UI.")
    ])
    add_card(s40, 6.8, 1.6, 5.7, 5.2, "Rendimiento y Certificación")
    add_bullets(s40, 7.0, 2.1, 5.3, 4.5, [
        ("Throughput de Inspección", "Capaz de muestrear el estado latente a más de 1.000 Hz."),
        ("Manejo Seguro de Punteros", "Protección contra 'use-after-free' mediante gestión RAII en el wrapper Dart."),
        ("Pruebas de Estrés", "'test_dart_stress_ffi.dart' ejecutado con Exit Code 0 y cero excepciones.")
    ])

    # SLIDE 41: Monitor PMTP en Tiempo Real en Dart
    s41 = add_base_slide(
        "BLOQUE IV: DART DASHBOARD & INTEROPERABILIDAD",
        "Inspección en Tiempo Real del Bus PMTP en Dart",
        "Telemetría continua de ancho de banda, latencia y ocupación de slots.",
        41
    )
    add_card(s41, 0.8, 1.6, 5.7, 5.2, "Métricas Transmitidas a la UI")
    add_bullets(s41, 1.0, 2.1, 5.3, 4.5, [
        ("Tasa de Transferencia", "Monitoreo continuo de bytes/segundo sobre los slabs mapeados."),
        ("Conteo de Operaciones", "Contador atómico de pasadas del bucle recurrente de 100k pasos."),
        ("Detección de Torn-Reads", "Alerta visual instantánea ante cualquier incoherencia en la suma de comprobación."),
        ("Distribución de Energía", "Histograma en vivo de las componentes del multivector de Clifford.")
    ])
    add_card(s41, 6.8, 1.6, 5.7, 5.2, "Implementación del Widget")
    add_bullets(s41, 7.0, 2.1, 5.3, 4.5, [
        ("CustomPainter Vectorial", "Dibujo acelerado por GPU de la trayectoria del vector sobre la esfera de Bloch/Poincaré proyectada."),
        ("Actualización Reactiva", "ValueNotifier y Streams ligeros para evitar repintados innecesarios."),
        ("Integración en Clases UTN", "Utilizado interactivamente en auditorías técnicas para ilustrar el flujo de tensores continuos.")
    ])

    # SLIDE 42: Visualización de Stiefel en UI
    s42 = add_base_slide(
        "BLOQUE IV: DART DASHBOARD & INTEROPERABILIDAD",
        "Visualización Interactiva del Manifold de Stiefel",
        "Seguimiento visual del defecto ortogonal y retracción de Cayley.",
        42
    )
    add_card(s42, 0.8, 1.6, 5.7, 5.2, "El Gráfico de Desviación Ortogonal")
    add_bullets(s42, 1.0, 2.1, 5.3, 4.5, [
        ("Métrica Visualizada", "Logaritmo del defecto ||U^T U - I||_F en escala continua."),
        ("Semáforo de Silicio", "Verde (< 10^-14, zona 1 ULP), Amarillo (10^-8 a 10^-14), Rojo (> 10^-8, disparo de fallback PolarSafe)."),
        ("Visualización Geodésica", "Representación 3D interactiva del descenso por gradiente en la variedad."),
        ("Comprobación Auditiva/Visual", "Feedback sensorial inmediato ante anomalías de convergencia.")
    ])
    add_card(s42, 6.8, 1.6, 5.7, 5.2, "Impacto Pedagógico")
    add_bullets(s42, 7.0, 2.1, 5.3, 4.5, [
        ("Demostración Visual", "Los alumnos observan cómo el retractor de Newton-Schulz devuelve instantáneamente el vector a la variedad en 5 iteraciones."),
        ("Falsación OOD en Vivo", "Inyección de matrices mal condicionadas para comprobar la activación del firewall Householder.")
    ])

    # SLIDE 43: Interoperabilidad con Qwen2.5-0.5B
    s43 = add_base_slide(
        "BLOQUE IV: DART DASHBOARD & INTEROPERABILIDAD",
        "Interoperabilidad Neuronal de Pesos Abiertos: Qwen2.5-0.5B",
        "Invarianza bit a bit de logits y dirección causal KL steering en silicio.",
        43
    )
    add_card(s43, 0.8, 1.6, 5.7, 5.2, "Fase Q0-Q1: Certificación de Identidad")
    add_bullets(s43, 1.0, 2.1, 5.3, 4.5, [
        ("Extracción de Activaciones", "Extracción directa de representaciones ocultas internas ('output_hidden_states=True')."),
        ("Puente Stiefel Residual", "h' = h + β W (z' - z). Para β = 0, se exige identidad exacta bit a bit."),
        ("Diferencia Máxima Medida", "max_abs_logit_diff = 0.00000000 (bitwise equal = True)."),
        ("Invarianza de KV-Cache", "El KV-Cache del modelo permanece intacto y sincronizado tras la inmersión de Stiefel.")
    ])
    add_card(s43, 6.8, 1.6, 5.7, 5.2, "Fase Q2: Intervención Causal Activa")
    add_bullets(s43, 7.0, 2.1, 5.3, 4.5, [
        ("Direccionamiento Latente", "Inyección de conceptos latentes mediante modulación β in [0, 1]."),
        ("Control de Divergencia KL", "D_KL suave y monótona; cero alucinaciones o degradación del vocabulario base."),
        ("Prueba en Silicio", "'morpho_qwen_q01_identity.py' ejecutado con Exit Code 0.")
    ])

    # SLIDE 44: Conexión Telepática con Nodo ALADIN
    s44 = add_base_slide(
        "BLOQUE IV: DART DASHBOARD & INTEROPERABILIDAD",
        "Conexión Telepática de Nodo ALADIN: Inferencia Distribuida",
        "El cluster multi-nodo operando concurrentemente sobre PMTP.",
        44
    )
    add_card(s44, 0.8, 1.6, 5.7, 5.2, "Canal Binario AGY <-> ALADIN")
    add_bullets(s44, 1.0, 2.1, 5.3, 4.5, [
        ("Topología TCP Binaria", "Conexión socket directa a 192.168.100.21:9999 (aladin-pmtp.service)."),
        ("Transmisión Sin Serializar", "Los tensores se transmiten como bloques IEEE-754 FP64 con cabecera wire de 128 bytes."),
        ("Verificación en Destino", "El daemon en ALADIN valida la norma de Neumaier (|norm(v)-1| <= 1e-15) y responde ACK de 22 bytes en 62.8 ms."),
        ("Ahorro de Ancho de Banda", "Cero texto; cero overhead JSON/HTTP.")
    ])
    add_card(s44, 6.8, 1.6, 5.7, 5.2, "Ollama con Qwen & DeepSeek en ALADIN")
    add_bullets(s44, 7.0, 2.1, 5.3, 4.5, [
        ("Modelos en Servidor", "qwen2.5-coder:1.5b y deepseek-r1:1.5b operativos en el puerto 11434 de ALADIN."),
        ("Precalentamiento Exitoso", "Respuesta confirmada: 'Yes, I am ready for PMTP latent tensor telepathy and MORPHO PELEIDES'."),
        ("Rol en el Enjambre", "Actúan como oráculos abiertos y verificadores independientes de razonamiento cruzado.")
    ])

    # SLIDE 45: Monitor de Salud de Silicio
    s45 = add_base_slide(
        "BLOQUE IV: DART DASHBOARD & INTEROPERABILIDAD",
        "Monitor de Salud de Silicio y Subagent Watchdog",
        "Supervisión autónoma y prevención de cuelgues o fugas de recursos.",
        45
    )
    add_card(s45, 0.8, 1.6, 5.7, 5.2, "Watchdog de Latidos (Regla 33)")
    add_bullets(s45, 1.0, 2.1, 5.3, 4.5, [
        ("Monitoreo Periódico", "Auditoría de latidos cada 20 minutos de subagentes y tareas en background."),
        ("Timeout Quirúrgico", "Límite estricto de 40 minutos; auto-purga de procesos zombis o desincronizados."),
        ("Cero Desperdicio", "Si la lista de tareas está vacía, el monitor duerme con consumo de CPU = 0.0%."),
        ("Aislamiento de Errores", "Un fallo en un agente no propaga corrupción al resto del bus PMTP.")
    ])
    add_card(s45, 6.8, 1.6, 5.7, 5.2, "Telemetría de Hardware en Silicio")
    add_bullets(s45, 7.0, 2.1, 5.3, 4.5, [
        ("Consumo de RAM/VRAM", "Monitoreo en vivo para asegurar huella de memoria O(1) constante."),
        ("Detección de Deriva Térmica", "Ajuste dinámico de carga en caso de estrangulamiento térmico de CPU."),
        ("Registro Transaccional", "Todos los estados y alertas se persisten en 'polydim_active_db' en PostgreSQL 16.")
    ])

    # SLIDE 46: Demostración End-to-End
    s46 = add_base_slide(
        "BLOQUE IV: DART DASHBOARD & INTEROPERABILIDAD",
        "Demostración End-to-End: Del Dato al Estado Latente sin Texto",
        "El ciclo completo de inferencia y razonamiento continuo integrado.",
        46
    )
    add_card(s46, 0.8, 1.6, 11.7, 5.2, "Flujo de Trabajo Integrado en Silicio")
    add_bullets(s46, 1.0, 2.1, 11.3, 4.5, [
        ("1. Ingesta (Fase 1)", "Entrada de datos sensoriales o simbólicos -> Proyección de Stiefel U_A in St(d_A, r) -> Vector unitario z* in S^(D-1)."),
        ("2. Transferencia PMTP (Fase 2)", "Escritura directa a slab de memoria compartida en 76.8 µs con descriptor wire de 128 bytes y semántica Release-Acquire."),
        ("3. Razonamiento MORPHO (Fase 3)", "100.000 iteraciones en el núcleo canónico d_core = 1024 con flujo riemanniano simpléctico y memoria CAM-HiPPO en 69.77 segundos."),
        ("4. Supervisión en Dart FFI (Fase 4)", "Inspección visual continua a 60 FPS en el dashboard con defecto ortogonal de 2.22 x 10^-16 verificado en vivo."),
        ("5. Decodificación y Cierre (Fase 5)", "Un solo forward pass terminal y = G(z_{100000}) generando la solución matemática formal con Exit Code 0.")
    ])

    # =========================================================================
    # BLOQUE V: CONCLUSIONES, TESIS DOCTORAL Y ROADMAP (Slides 47 a 50)
    # =========================================================================

    # SLIDE 47: Scorecard Consolidado de Silicio
    s47 = add_base_slide(
        "BLOQUE V: CONCLUSIONES Y TESIS",
        "Matriz de Validación Empírica en Silicio: Scorecard Consolidado",
        "La evidencia física irrefutable que respalda la tesis doctoral.",
        47, badge_color=C_EMERALD
    )
    add_card(s47, 0.8, 1.6, 6.2, 5.2, "Resumen de Métricas Físicas Crudas")
    add_bullets(s47, 1.0, 2.1, 5.8, 4.5, [
        ("Defecto de Ortogonalidad", "2.22 x 10^-16 (1 ULP bit exacto) | 100% Superado."),
        ("Invarianza de Logits Q1", "diff absoluta = 0.00000000 con Qwen2.5 real | 100% Superado."),
        ("Rendimiento Recurrente", "1.433 pasos/s en CPU local (100k en 69.77 s) | 100% Superado."),
        ("Latencia FFI PMTP", "76.8 µs por transferencia zero-copy | 100% Superado."),
        ("Inmunidad a Torn-Reads", "0 lecturas parciales en 1.000.000 ciclos | 100% Superado."),
        ("Pruebas de Fuzzing", "20/20 ataques adversariales superados | 100% Superado."),
        ("Bóveda de Teoremas", "1.603 teoremas certificados en PostgreSQL 16 | 100% SOTA_CERTIFIED.")
    ])
    add_image_panel(s47, 7.3, 1.6, 5.2, 5.2, r"E:\POLYDIM_EINSOF\figures_presentation\silicon_scorecard_metrics.png", "Figura 14: Scorecard de Verificación en Silicio: 100% de Pruebas con Exit Code 0.")

    # SLIDE 48: Aportes Clave a las Ciencias de la Computación
    s48 = add_base_slide(
        "BLOQUE V: CONCLUSIONES Y TESIS",
        "Aportes Clave a las Ciencias de la Computación",
        "Superando el paradigma lingüístico hacia la inteligencia continua en alta dimensión.",
        48, badge_color=C_EMERALD
    )
    add_card(s48, 0.8, 1.6, 5.7, 5.2, "Contribuciones Teóricas")
    add_bullets(s48, 1.0, 2.1, 5.3, 4.5, [
        ("Demolición del Dogma 1D", "Prueba formal de que el razonamiento textual intermedio no es necesario para la computación inteligente compleja."),
        ("Formulación Stiefel Universal", "Unificación geométrica para la transferencia de estados entre modelos de lenguaje heterogéneos sin pérdida de isometría."),
        ("Memoria Desacoplada CAM-HiPPO", "Solución al problema de retención en horizontes masivos con huella O(1).")
    ])
    add_card(s48, 6.8, 1.6, 5.7, 5.2, "Contribuciones de Ingeniería de Sistemas")
    add_bullets(s48, 7.0, 2.1, 5.3, 4.5, [
        ("Protocolo PMTP Wire", "Estándar de memoria compartida binaria zero-copy para enjambres de IA locales."),
        ("Arquitectura Lock-Free Dual Buffer", "Mecanismo libre de torn-reads con arriendos atómicos en silicio."),
        ("Demostración Práctica", "Primer sistema capaz de ejecutar 100.000 pasos de razonamiento interno continuo verificado en silicio real.")
    ])

    # SLIDE 49: La Tesis Doctoral Ariel García Traba (Independent Research)
    s49 = add_base_slide(
        "BLOQUE V: CONCLUSIONES Y TESIS",
        "La Tesis Doctoral Ariel García Traba (Independent Research): Estructura Formal y Defensa",
        "Consolidación académica para la presentación ante el tribunal universitario.",
        49, badge_color=C_EMERALD
    )
    add_card(s49, 0.8, 1.6, 11.7, 5.2, "Organización del Manuscrito Formal de Tesis")
    add_bullets(s49, 1.0, 2.1, 11.3, 4.5, [
        ("Capítulo 1: La Crisis del Token 1D", "Fundamentos de teoría de información, teorema DPI y límites físicos de los transformers autorregresivos."),
        ("Capítulo 2: Geometría Hiperesférica y Variedades de Stiefel", "Geometría diferencial de S^(D-1), inmersiones isométricas St(d, r) y retractor polar de Newton-Schulz."),
        ("Capítulo 3: Protocolo Físico PMTP y Arquitectura de Memoria", "Diseño del bus zero-copy, descriptor wire de 128B, semántica Release-Acquire y clúster distribuido Host-ALADIN."),
        ("Capítulo 4: MORPHO PELEIDES: Razonamiento Latente Continuo", "Formulación de los 100.000 pasos, flujo simpléctico, TR-AGN Lipschitz, memoria CAM-HiPPO y modelo de costos."),
        ("Capítulo 5: Interoperabilidad FFI y Capa de Presentación Flutter", "Puente C-ABI Dart FFI, pruebas de identidad en Qwen2.5 y dashboard interactivo en tiempo real."),
        ("Capítulo 6: Validación Empírica en Silicio y Resultados", "Suites de estrés físico, logs crudos con Exit Code 0, pruebas adversariales de fuzzing y catálogo de 1.603 teoremas.")
    ])

    # SLIDE 50: Conclusión y Visión Futura
    s50 = add_base_slide(
        "BLOQUE V: CONCLUSIONES Y TESIS",
        "Conclusión y Visión Futura: El Tejido Cognitivo Latente",
        "Hacia una nueva generación de inteligencia artificial soberana, continua y eficiente.",
        50, badge_color=C_EMERALD
    )
    card50 = s50.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.6), Inches(10.933), Inches(4.8))
    card50.fill.solid()
    card50.fill.fore_color.rgb = C_CARD
    card50.line.color.rgb = C_CYAN
    card50.line.width = Pt(1.5)

    tb50 = s50.shapes.add_textbox(Inches(1.6), Inches(1.9), Inches(10.1), Inches(4.2))
    tf50 = tb50.text_frame
    tf50.word_wrap = True

    p = tf50.paragraphs[0]
    p.text = "EL FUTURO DEL CÓMPUTO COGNITIVO ES HIPERDIMENSIONAL Y CONTINUO"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_GOLD
    p.space_after = Pt(14)

    p2 = tf50.add_paragraph()
    p2.text = "• MORPHO PELEIDES y POLYDIM demuestran que la inteligencia artificial no está condenada a balbucear tokens intermedios para razonar. La cognición es un flujo continuo sobre variedades geométricas de alta dimensión.\n\n• La implementación de PMTP y la verificación rigurosa en silicio prueban que este paradigma no es una abstracción teórica: es más rápido, más económico, térmicamente eficiente y matemáticamente robusto.\n\n• Con 1.603 teoremas certificados, un clúster dual Host-ALADIN operativo y el kernel V26300 congelado y probado en silicio, el proyecto está completamente preparado para la defensa de tesis doctoral y su despliegue en supercómputo wafer-scale."
    p2.font.size = Pt(12.5)
    p2.font.color.rgb = C_TITLE

    # Save presentation
    out_pptx = r"E:\POLYDIM_EINSOF\POLYDIM_MORPHO_PELEIDES_50_SLIDES.pptx"
    prs.save(out_pptx)
    print(f"Presentation saved successfully to {out_pptx}!")
    return out_pptx

if __name__ == "__main__":
    create_deck()
