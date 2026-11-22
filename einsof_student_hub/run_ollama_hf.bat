@echo off
chcp 65001 >nul
echo ======================================================================
echo   EINSOF-II: EJECUCIÓN PÚBLICA DIRECTA EN OLLAMA ($0 USD)
echo   Descarga y corre modelos GGUF oficiales de Hugging Face sin pagar
echo ======================================================================
echo.
echo Seleccione el modelo soberano que desea ejecutar:
echo   [1] GLM-4 9B Stiefel (Razonamiento General y Mathesis)
echo   [2] DeepSeek Prover V2 7B Stiefel (Demostración Formal y Lean 4)
echo   [3] Granite 8B Qiskit Stiefel (Computación Cuántica)
echo   [4] EuroLLM 9B Stiefel (Multilingüe Multipolar)
echo.
set /p opt="Ingrese opción [1-4] (por defecto 1): "
if "%opt%"=="" set opt=1

if "%opt%"=="1" (
    echo [*] Iniciando GLM-4 9B Stiefel desde Hugging Face...
    ollama run hf.co/Polydim-Einsof/einsof2-glm4-9b-stiefel-gguf:Q4_K_M
) else if "%opt%"=="2" (
    echo [*] Iniciando DeepSeek Prover V2 7B Stiefel desde Hugging Face...
    ollama run hf.co/Polydim-Einsof/einsof2-deepseek-prover-v2-stiefel-gguf:Q4_K_M
) else if "%opt%"=="3" (
    echo [*] Iniciando Granite 8B Qiskit Stiefel desde Hugging Face...
    ollama run hf.co/Polydim-Einsof/einsof2-granite-8b-qiskit-stiefel-gguf:Q4_K_M
) else if "%opt%"=="4" (
    echo [*] Iniciando EuroLLM 9B Stiefel desde Hugging Face...
    ollama run hf.co/Polydim-Einsof/einsof2-eurollm-9b-stiefel-gguf:Q4_K_M
) else (
    echo [!] Opción no válida.
)
pause
