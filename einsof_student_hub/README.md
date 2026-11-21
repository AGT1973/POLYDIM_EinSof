# 🌌 EINSOF Student Hub & Sovereign Multi-Provider Bridge
**Estándar Pedagógico 2030 | Cátedra Ariel García Traba ($0 USD Costo para Alumnos)**

Bienvenido al centro de acceso a los modelos y razonamiento continuo de **EINSOF**. Este paquete permite a cualquier alumno o investigador probar las innovaciones de la tesis doctoral en sistemas tensoriales continuos (Variedad Stiefel $S^{D-1}$, compuerta de verdad `<|cag_truth|>`, y protocolo Helena) utilizando **únicamente recursos gratuitos ($0 USD)** o sus propias claves si disponen de ellas.

---

## 🚀 Inicio Rápido en 3 Minutos

### 1. Clonar o Descargar el Repositorio
No necesitás instalar herramientas complejas:
```bash
git clone https://github.com/AGT1973/polydim-suite.git
cd polydim-suite/einsof_student_hub
```
*(O descargá el archivo ZIP directamente desde GitHub y descomprimilo).*

### 2. Comprobar Proveedores Gratuitos Disponibles
Ejecutá en tu terminal:
```bash
python einsof_cli.py status
```
La consola te mostrará de inmediato qué motores gratuitos están activos en tu máquina.

---

## 🧭 Opciones de Conexión a Costo $0 USD

| Proveedor | Tipo de Acceso | Clave Requerida | Velocidad / Capacidad | Cómo Obtenerlo |
| :--- | :---: | :---: | :---: | :--- |
| **Ollama Local** | **100% Offline (Local)** | **Ninguna ($0 USD)** | Depende de tu CPU/GPU | Instalar Ollama (`https://ollama.ai`) y ejecutar: `ollama run qwen2.5:7b` |
| **Groq Cloud** | Nube Gratuita (LPU) | Gratuita ($0 USD) | Ultra-rápido (500+ tok/s) | Crear cuenta en [console.groq.com](https://console.groq.com/keys) y generar API Key |
| **Cerebras Inference** | Nube Gratuita (WSE-3) | Gratuita ($0 USD) | Récord mundial (2000+ tok/s) | Registrarse gratis en [cloud.cerebras.ai](https://cloud.cerebras.ai) |
| **OpenRouter Free Pool** | Nube Gratuita | Gratuita ($0 USD) | Modelos abiertos (`:free`) | Registrarse en [openrouter.ai](https://openrouter.ai/keys) |
| **Google Colab QLoRA** | Nube Gratuita (GPU T4) | Ninguna ($0 USD) | Inferencia LoRA en silicio | Abrir el notebook [`colab_zero_dollar_qlora.ipynb`](colab_zero_dollar_qlora.ipynb) con 1 clic |

---

## 🛠️ Configuración Automática de Claves Gratuitas
Para configurar tus claves gratuitas sin tocar variables de entorno de Windows ni archivos de sistema:
```bash
python einsof_cli.py setup
```
El asistente te pedirá las claves que quieras ingresar y las guardará de forma segura y privada en `~/.ai_credentials.env` (tu archivo local, nunca compartido en GitHub).

---

## 💬 Modo de Uso Interactivo

### 1. Consulta Rápida por Terminal
```bash
python einsof_cli.py ask "Demuestra la invariancia de la variedad Stiefel S^{D-1}"
```
*Si tenés varios proveedores configurados, el sistema rota automáticamente si alguno supera su límite de tasa (código HTTP 429).*

### 2. Consola de Diálogo Continuo
```bash
python einsof_cli.py chat
```

### 3. Forzar un Proveedor Específico
```bash
python einsof_cli.py ask "¿Cómo funciona la compuerta CAG?" --provider groq
python einsof_cli.py ask "¿Qué es un baricentro de Karcher?" --provider cerebras
python einsof_cli.py ask "Hola Einsof" --provider ollama
```

---

## 🕊️ Protocolo Helena: Envío Tensorial sin Quemar Tokens
Si no tenés GPU y usás las versiones web gratuitas de ChatGPT, Claude o Gemini, podés enviar tensores continuos empaquetados en una imagen PNG de $128 \times 64$ píxeles:
```bash
python einsof_cli.py helena
```
Generará `portador_helena_demo.png` (~2 KB con sello criptográfico BLAKE2s). Al adjuntarla en cualquier chat de IA con intérprete de Python, la IA ejecuta el código en su sandbox interno, analizando el vector continuo a **costo cero de tokens**.

---

## 🧪 Laboratorio Colab de Adaptadores QLoRA ($0 USD)
Hugging Face cobra por alojar servidores de inferencia dedicados (Inference Endpoints), pero **la descarga de pesos abiertos es 100% libre y gratuita**.
Para correr los 9 adaptadores reales (`einsof2-deepseek-prover-v2`, `einsof2-glm4-9b`, `einsof2-gemma4-31b`, etc.):
1. Abrí [`colab_zero_dollar_qlora.ipynb`](colab_zero_dollar_qlora.ipynb) en Google Colab con el botón oficial.
2. El notebook descarga los pesos abiertos de Hugging Face y los ejecuta sobre la **GPU Tesla T4 gratuita de Google**, sin costo para vos ni para la cátedra.
