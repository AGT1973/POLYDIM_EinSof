***  
ENTREGA\_2026\_10\_19\_V26600.rarArchivo**

***lee profundamente, evalua errores, dame soluciones. se un bulldog que ataca al problema pero ayuda al dueño. se un redteam que ataca el problema pero respeta y cuida el que les da el trabajo. /goal entra enloop hasta no encontrar mas errores. Hay mucho sota. no tengas sesgos. Audita tus respuestas para no alucinar. Busca todo problema, encuentra soluciones dame la mejor continua con el siguiente error. No te apresures. gasta tu tiempo. prefiero lento y chequeado que rapido y mal. no quiero alucinaciones**

***Voy a tratar esta entrega como una auditoría técnica adversarial de POLYDIM, con un objetivo concreto: encontrar defectos reales, demostrar por qué son defectos, proponer la corrección más sólida y volver a examinar el sistema para descubrir fallos secundarios.**

***No voy a confundir una idea novedosa con una idea correcta, ni voy a descartar una arquitectura futura simplemente porque el hardware actual todavía no pueda aprovecharla. Evaluaré por separado la validez matemática, la arquitectura, la concurrencia, la seguridad de memoria, la estabilidad numérica, la compilación, la correspondencia con el hardware y la evidencia experimental.**

## ***1. Primera comprobación de la entrega**

***He podido identificar el archivo comprimido `ENTREGA\_2026\_10\_19\_V26600.rar` y comprobar que contiene 14 elementos. Entre ellos aparecen:**

- ***`teoria\_axiomas\_v26600.py`**

- ***`kernel\_cuda\_v26600.cu.txt`**

- ***`kernel\_rust\_v26600.rs.txt`**

- ***`pmtp\_shm\_bus\_v26600.py`**

- ***`pmtp\_kernel\_cpp\_v26600.cpp.txt`**

- ***`polydim\_triton\_kernel\_v26600.py`**

- ***`polydim\_cla\_grassmann\_v26600.py`**

- ***`morpho\_redteam\_v26600.py`**

- ***`run\_silicon\_verification\_suite.py`**

- ***`run\_all\_modules\_v26600.py`**

- ***Un archivo Rust compilado (`.rlib`) y documentación adicional.**

***Esto permite identificar las áreas que deben auditarse, pero todavía no demuestra que el código sea correcto ni incorrecto. No voy a atribuir defectos a archivos cuyo contenido no he podido leer.**

## ***2. Resultado de la primera pasada: los PASS no certifican la seguridad**

***Ejecuté el orquestador `run\_all\_modules\_v26600.py` en este entorno. El resultado fue 5/5 módulos con código de salida cero. También ejecuté individualmente las pruebas Python incluidas en la entrega.**

***Hay, sin embargo, una discrepancia importante: la suite puede finalizar correctamente aunque sus pruebas no demuestren las propiedades de seguridad que proclaman. En particular, el módulo adversarial imprime contraejemplos relacionados con ABA, matrices mal condicionadas y otros problemas, pero termina con un mensaje de éxito.**

***Eso no significa que todo el sistema esté roto. Significa que debemos distinguir tres resultados:**

- ***Prueba ejecutada: el programa terminó sin fallar.**

- ***Propiedad demostrada: el test realmente comprueba la garantía declarada.**

- ***Garantía industrial: la propiedad sigue siendo cierta bajo concurrencia real, fallos de proceso, distintas arquitecturas y condiciones adversas.**

***La entrega demuestra el primer nivel en las pruebas ejecutadas. No demuestra automáticamente los otros dos.**

## ***3. Primer paquete de errores: PMTP y memoria compartida**

***Severidad provisional: crítica para cualquier afirmación de seguridad multiproceso. Alcance: código Python inspeccionado; todavía no es una certificación del sistema completo.**

### ***Error 1. El supuesto CAS no es una operación atómica entre procesos**

***Ubicación: `pmtp\_shm\_bus\_v26600.py`, métodos `acquire\_reader\_lease`, `release\_reader\_lease` y `publish\_snapshot\_atomic`.**

***La implementación usa `self.\_local\_lock` y modifica el encabezado mediante escrituras a `shm.buf`. El problema fundamental es que un bloqueo local de Python no sincroniza automáticamente a otros procesos que hayan abierto el mismo segmento de memoria compartida.**

***Además, el patrón de leer el contador, calcular un nuevo valor y escribirlo no constituye un compare-and-swap (CAS) de hardware.**

***Un intercalado posible es:**

1. ***El proceso A lee el contador de lectores con valor 0.**

2. ***El proceso B también lee 0.**

3. ***A calcula y escribe 1.**

4. ***B calcula y escribe 1.**

5. ***Hay dos lectores, pero el contador registra uno.**

***Un escritor podría entonces creer que un slot está libre cuando todavía hay un lector utilizándolo.**

***Por qué importa: las garantías de exclusión, reclamación de memoria y prevención de use-after-free dejan de ser fiables si varios procesos acceden simultáneamente al mismo slab.**

***Solución recomendada:**

- ***Si el objetivo es multiproceso en una misma máquina, usar primitivas atómicas reales con memoria compartida correctamente alineada y órdenes de memoria definidos.**

- ***Alternativamente, usar un mecanismo de sincronización interproceso explícito, con un protocolo de publicación y reclamación cuya corrección pueda demostrarse.**

- ***Definir formalmente las transiciones de estado y demostrar que ningún escritor reutiliza un slot con lectores activos.**

- ***Probar con procesos independientes, barreras de sincronización y miles de intercalados adversariales; los hilos de un solo proceso no sustituyen esta prueba.**

***No basta con cambiar el nombre de la función por `atomic\_cas`: la operación atómica debe existir realmente en la implementación y respetar el modelo de memoria de la plataforma.**

### ***Error 2. El camino de lectura zero-copy no adquiere un lease**

***Ubicación: `get\_zero\_copy\_dlpack\_tensor()`.**

***El método lee el encabezado, determina el slot activo y devuelve una vista NumPy sobre la memoria compartida. No adquiere un lease que permanezca vigente durante toda la vida útil del tensor.**

***Esto abre una ventana de carrera:**

1. ***Un consumidor obtiene una vista del slot 0.**

2. ***Otro proceso publica datos nuevos y alterna los slots.**

3. ***El escritor vuelve a necesitar el slot 0.**

4. ***El consumidor sigue usando su vista mientras el contenido se modifica.**

***El hecho de que la vista no copie los datos no garantiza que sean inmutables ni que su almacenamiento permanezca válido.**

***Solución recomendada: implementar un objeto de propiedad del buffer que mantenga la reserva del slot durante toda la vida del consumidor y que solo permita la reclamación cuando se hayan liberado todos los consumidores. Si el consumidor no puede garantizar esa duración, ofrecer una lectura con copia como alternativa segura.**

***Para DLPack hay una dificultad adicional: no debe liberarse el almacenamiento mientras un tensor derivado siga utilizándolo. La vida del productor, la vista exportada y el tensor importado deben quedar coordinadas explícitamente.**

### ***Error 3. `release\_all()` no demuestra la protección contra UAF que anuncia**

***Ubicación: `release\_all()`.**

***El método marca un bit de destrucción y después intenta cerrar y desvincular cada segmento. Sin embargo, la marca se escribe directamente en el encabezado y no está coordinada mediante una primitiva atómica compartida con los lectores.**

***También captura las excepciones y las ignora. Por tanto, una operación de cierre que falle puede quedar oculta y la función puede aparentar que la limpieza fue completa.**

***Solución recomendada:**

- ***Introducir un protocolo de cierre que impida nuevas adquisiciones antes de iniciar la destrucción.**

- ***Esperar o cancelar de manera controlada a los consumidores existentes.**

- ***Separar el cierre local del identificador compartido de la desvinculación del recurso.**

- ***Informar de los fallos de limpieza, en lugar de descartarlos silenciosamente.**

- ***Añadir pruebas con lectores activos, cierre concurrente, procesos terminados abruptamente y reapertura del segmento.**

***Hasta que se demuestre ese protocolo, no es correcto calificar la ruta de destrucción como libre de UAF.**

### ***Error 4. La prueba de concurrencia no es una prueba multiproceso**

***Ubicación: `run\_silicon\_verification\_suite.py`, `test\_01\_atomic\_concurrency\_anti\_aba()`.**

***La prueba mantiene un lease, publica una segunda versión y comprueba que una tercera publicación no sobrescriba el slot retenido. Es una prueba útil de un escenario concreto, pero se ejecuta de forma secuencial en un solo proceso.**

***No crea dos procesos independientes que compitan por el encabezado, ni fuerza intercalados en los que un lector adquiere el lease justo cuando un escritor cambia el slot activo.**

***Solución: dividir la validación en tres niveles:**

1. ***Pruebas unitarias deterministas de cada transición.**

2. ***Pruebas de estrés multiproceso con lectores y escritores simultáneos.**

3. ***Pruebas de fallos: muerte del propietario, terminación durante una publicación, contador en el límite, cierre concurrente y recuperación tras reinicio.**

***La suite debe distinguir `PASS`, `FAIL`, `SKIP` y `NOT VERIFIED`. No debe emitir una certificación general cuando solo ha pasado un escenario secuencial.**

### ***Error 5. La prueba ABI solo calcula un tamaño; no compara implementaciones**

***Ubicación: `run\_silicon\_verification\_suite.py`, `test\_02\_abi\_alignment\_128b()`.**

***La prueba calcula el tamaño de un formato `struct` definido dentro del propio test y comprueba que da 128 bytes. Eso demuestra que ese formato concreto mide 128 bytes. No demuestra que coincida con las estructuras reales de C++, Rust y Dart.**

***Tampoco verifica por sí solo los offsets, el endianness, la alineación efectiva en memoria ni la representación de los campos en cada lenguaje.**

***Solución:**

- ***Definir un único esquema ABI normativo.**

- ***Generar o validar las estructuras de cada lenguaje contra ese esquema.**

- ***Comprobar `sizeof`, `alignof` y `offsetof` en C++ y las representaciones correspondientes en Rust.**

- ***Validar el layout y los offsets de Dart FFI en el entorno de destino.**

- ***Serializar vectores de prueba conocidos y verificar que todas las implementaciones producen exactamente los mismos bytes.**

- ***Añadir pruebas de compatibilidad entre versiones y arquitecturas.**

***Criterio de aceptación: las cuatro implementaciones deben coincidir en tamaño, offsets, alineación y bytes serializados. Que todas usen una cabecera de 128 bytes no basta.**

### ***Error 6. La afirmación de aceleración frente a HTTP no está respaldada por el benchmark**

***Ubicación: `run\_silicon\_verification\_suite.py`, `test\_05\_honest\_transport\_benchmark()`.**

***La prueba compara una copia local de un vector con el coste de crear una vista NumPy sobre memoria compartida. Después compara esa latencia con un valor HTTP fijo de 12.800 microsegundos.**

***Son operaciones distintas y no se ha medido el transporte HTTP en el mismo experimento. Por eso, la cifra de aceleración que imprime no es una conclusión experimental válida.**

***Además, crear una vista no mide el coste completo de publicar, sincronizar, transferir y consumir un tensor. Tampoco mide el rendimiento sostenido bajo contención.**

***Solución: diseñar un benchmark reproducible con:**

- ***Las mismas dimensiones, tipos de datos y condiciones de carga.**

- ***Publicación, adquisición, consumo y liberación medidos por separado.**

- ***Coste de sincronización y contención incluidos.**

- ***Latencias p50, p95, p99 y p99.9, además de throughput.**

- ***Calentamiento, repeticiones suficientes, afinidad y configuración del hardware documentadas.**

- ***Un baseline HTTP realmente ejecutado y medido, si se quiere publicar esa comparación.**

***Hasta entonces, deben eliminarse las cifras de aceleración comparativa o etiquetarse explícitamente como hipótesis, no como resultados certificados.**

## ***4. Segundo paquete: la validación de hardware no corresponde a lo que se certifica**

### ***Error 7. El módulo Triton puede declarar éxito sin ejecutar ningún kernel GPU**

***Ubicación: `polydim\_triton\_kernel\_v26600.py`, `PolydimTritonSlabEngine.\_\_init\_\_()` y `self\_test()`.**

***He comprobado un defecto concreto en la lógica de selección del backend:**

***self.is\_gpu = HAS\_TRITON**

***`HAS\_TRITON` indica que se importó Triton en una ruta en la que CUDA estaba disponible. No demuestra que una operación concreta se haya ejecutado en GPU.**

***La autoprueba trabaja con arrays NumPy. Por tanto, incluso si se informa de un backend GPU, los datos de esa prueba siguen la ruta NumPy y no ejercitan los kernels Triton.**

***También existe una discrepancia en la etiqueta del fallback: el código utiliza operaciones NumPy o `torch.Tensor.copy\_()`, pero eso no demuestra por sí mismo que se haya ejecutado una implementación AVX2 concreta.**

***Solución:**

- ***Detectar el backend efectivo por operación, no solo por disponibilidad de una dependencia.**

- ***Añadir pruebas explícitas con tensores CUDA, verificando dispositivo de entrada y salida.**

- ***Comparar los resultados GPU contra una referencia independiente y tolerancias numéricas justificadas.**

- ***Registrar el kernel realmente ejecutado, el dispositivo, el dtype y la configuración.**

- ***Etiquetar el fallback como CPU genérico hasta verificar las instrucciones SIMD efectivamente utilizadas.**

***La certificación debe distinguir entre `GPU disponible`, `kernel compilado`, `kernel ejecutado` y `resultado verificado`.**

### ***Error 8. El orquestador no ejecuta la matriz de lenguajes que anuncia**

***Ubicación: `run\_all\_modules\_v26600.py`.**

***El orquestador ejecuta cinco scripts Python: la suite PMTP, MorphoPeleides, Polydim-cla, los axiomas y el módulo Triton.**

***No compila ni ejecuta directamente los archivos de C++, Rust, CUDA o Dart incluidos en el paquete. Tampoco compara automáticamente los resultados de esas implementaciones con los de Python.**

***Esto es relevante porque el proyecto anuncia una arquitectura multilenguaje. Que la capa Python pase sus pruebas no verifica que las otras capas respeten el mismo contrato.**

***Solución:**

***Crear una matriz de integración por lenguaje:**

| Capa | Validación necesaria |
| :-: | :-: |
| Python | Pruebas unitarias, propiedades y concurrencia |
| C++ | Compilación con advertencias estrictas, sanitizadores y pruebas de ABI |
| Rust | Compilación, pruebas, validación de **`unsafe`** y límites FFI |
| CUDA | Compilación con el toolkit objetivo, ejecución GPU y comprobaciones de errores |
| Triton | Compilación y ejecución real de kernels, más comparación numérica |
| Dart FFI | Compilación y pruebas de interoperabilidad con la biblioteca nativa |

***Cada capa debe publicar su versión de ABI y participar en pruebas cruzadas con datos conocidos. Si un entorno carece de CUDA o de Dart, el resultado debe ser `SKIP`, con el motivo explícito; nunca debe convertirse en una certificación de esa capa.**

### ***Error 9. La prueba de transferencia no verifica los requisitos de aliasing, forma y tipo**

***Ubicación: `PolydimTritonSlabEngine.transfer()`.**

***En la ruta NumPy, la operación es:**

***dest\[:\] = src\[:\]**

***La prueba solo verifica que el contenido final coincide para dos arrays sencillos. No define qué ocurre cuando:**

- ***Las formas no coinciden.**

- ***Los arrays tienen dtypes diferentes.**

- ***Fuente y destino comparten memoria parcialmente.**

- ***Los arrays no son contiguos.**

- ***Se intenta transferir entre dispositivos diferentes en la ruta PyTorch.**

***El resultado de una asignación puede depender de las conversiones de tipo y del solapamiento de memoria. No se puede deducir de esa única prueba que la transferencia sea correcta para todos esos casos.**

***Solución: establecer un contrato explícito de entrada y salida, validar dimensiones y dispositivos, definir la política de conversión de tipos y probar aliasing parcial. Si se admite solapamiento, implementar y verificar su semántica; si no, rechazarlo explícitamente.**

***Para una ruta que pretenda maximizar el rendimiento, esas comprobaciones pueden situarse en una capa de validación previa y permitir un camino rápido interno con precondiciones verificadas. Así se evita sacrificar rendimiento sin renunciar a una interfaz segura.**

## ***5. Tercer paquete: defectos más profundos en el núcleo C++**

***Este paquete es especialmente importante porque una corrección superficial en Python no arreglaría automáticamente el problema en la implementación nativa.**

### ***Error 10. El contador de lectores de C++ no identifica el slot protegido**

***Ubicación: `pmtp\_kernel\_cpp\_v26600.cpp.txt`, `pmtp\_shm\_acquire\_lease()` y `pmtp\_shm\_release\_lease()`.**

***En la implementación C++ se incrementa un contador global mediante CAS. Después se lee `active\_slot` y se devuelve ese slot al consumidor.**

***El contador no registra qué slot protege cada lector. Además, la ruta de publicación mostrada copia los datos al slot alternativo sin comprobar previamente que ese slot carezca de lectores activos.**

***Esto es insuficiente para demostrar la seguridad de un doble buffer: un contador global puede indicar que hay lectores, pero no permite determinar si el slot concreto que el escritor quiere reutilizar está libre.**

***Solución: implementar un protocolo de adquisición que vincule de forma demostrable el slot seleccionado con su reserva. La publicación debe comprobar que el slot de destino no tiene lectores, y el lector debe obtener una combinación coherente de slot, generación y lease. El protocolo completo debe estar definido como una máquina de estados y validarse mediante intercalados concurrentes.**

### ***Error 11. La liberación de leases puede descontar el contador equivocado**

***Ubicación: `pmtp\_kernel\_cpp\_v26600.cpp.txt`, `pmtp\_shm\_release\_lease()`.**

***La función recibe un argumento `slot`, pero el código mostrado no lo utiliza para decidir qué contador decrementar. Reduce el contador global de lectores.**

***Esto significa que el sistema no puede verificar que se está liberando exactamente la reserva adquirida por ese consumidor. Una liberación duplicada o una llamada incorrecta podría reducir el contador que protege a otros lectores.**

***Solución: asociar cada lease a un estado verificable, exigir que se libere una sola vez y contabilizar las reservas por slot. Añadir pruebas para liberación duplicada, identificadores de slot inválidos y operaciones de liberación concurrentes.**

### ***Error 12. El cierre nativo continúa aunque no se hayan drenado todos los lectores**

***Ubicación: `pmtp\_kernel\_cpp\_v26600.cpp.txt`, `pmtp\_shm\_close()`.**

***La función espera hasta 100 iteraciones de un milisegundo aproximadamente y después ejecuta `close()` y elimina el contexto. Si siguen existiendo lectores, el código no muestra una rama que cancele el cierre, devuelva un error o garantice que los consumidores han terminado.**

***Por tanto, el plazo de espera no demuestra que el drenaje haya concluido.**

***Solución: si el plazo vence, no liberar recursos que todavía puedan estar en uso. Devolver un estado de timeout y mantener el almacenamiento vivo hasta que se complete la reclamación segura, o utilizar un protocolo de recuperación explícito que demuestre que ya no hay consumidores activos.**

### ***Error 13. La utilización de `std::atomic` mediante reinterpretación requiere una justificación formal**

***Ubicación: `pmtp\_kernel\_cpp\_v26600.cpp.txt`, accesos a `state\_and\_readers`.**

***El código convierte la dirección de un campo `uint64\_t` en un puntero a `std::atomic\<uint64\_t\>` mediante `reinterpret\_cast`.**

***En C++, la alineación por sí sola no demuestra que exista un objeto atómico válido en esa dirección ni que su vida útil y su representación sean compatibles con esa operación. El uso de una estructura empaquetada añade otra condición que debe verificarse.**

***Solución: diseñar el layout y la propiedad del campo atómico de acuerdo con el modelo de objetos de C++. Verificar la alineación efectiva y la vida útil del objeto atómico, y definir cómo se comparte ese estado entre procesos. No asumir que un `std::atomic` ordinario garantiza automáticamente interoperabilidad multiproceso en todas las plataformas.**

***Para la versión industrial, esto requiere pruebas de compilación en las plataformas objetivo y una revisión específica del contrato de memoria compartida, no solo pruebas unitarias.**

## ***6. Qué debe corregirse primero**

***Los errores anteriores no son independientes: varios afectan a la misma propiedad fundamental, la reclamación segura de los buffers.**

***Prioridad P0 — Seguridad de memoria**

***Corregir el protocolo de leases, la protección por slot, la publicación y el cierre concurrente. Hasta entonces, no declarar el núcleo libre de UAF o carreras.**

***Prioridad P1 — Contrato multilenguaje**

***Definir un único ABI verificable y ejecutar pruebas cruzadas entre Python, C++, Rust, CUDA, Triton y Dart FFI.**

***Prioridad P2 — Evidencia de rendimiento**

***Separar benchmarks de copia, publicación, sincronización y transporte. Retirar las afirmaciones de aceleración que no se hayan medido con una comparación equivalente.**

***Prioridad P3 — Validación de silicio**

***Ejecutar y documentar las implementaciones nativas en hardware real, distinguiendo claramente los módulos no ejecutados de los que han pasado pruebas.**

## ***7. Estado de la auditoría**

***En esta primera iteración he identificado 13 defectos o insuficiencias de verificación concretos, con especial concentración en PMTP. No son 13 fallos independientes demostrados mediante una prueba de explotación: algunos son defectos observables en el código y otros son garantías anunciadas que las pruebas actuales no justifican. Mantener esa distinción es esencial para no inventar certezas.**

***La siguiente pasada debe centrarse en:**

1. ***La coherencia de la cabecera y el protocolo de publicación entre Python y C++.**

2. ***La semántica real de los dos slots y la generación del descriptor.**

3. ***Los riesgos de ABA, recuperación tras caída y reclamación de memoria.**

4. ***Los límites numéricos, las dimensiones y las condiciones extremas.**

5. ***La correspondencia entre los axiomas matemáticos declarados y lo que realmente implementa cada módulo.**

***Después de corregir un defecto, hay que repetir las pruebas pertinentes y buscar los fallos secundarios que la modificación pueda introducir. No sería riguroso declarar el proyecto terminado después de esta pasada: todavía no he demostrado la corrección global de la arquitectura ni he ejecutado las implementaciones nativas en sus respectivos entornos de destino.**

***asume corregido y evalua profundizar**

# ***POLYDIM V26600 — segunda iteración de auditoría SOTA**

***Voy a aceptar como hipótesis de trabajo que los 13 problemas de la pasada anterior ya fueron corregidos y que sus soluciones están implementadas. No volveré a contarlos como nuevos hallazgos: buscaré fallos de segundo orden, invariantes que podrían seguir rotos y problemas que aparecen incluso después de corregir la concurrencia básica.**

***Hay una precisión importante para mantener la auditoría honesta: los archivos de la entrega que puedo inspeccionar siguen conteniendo partes de las implementaciones anteriores. Por tanto, los nuevos hallazgos que siguen son observaciones sobre el código visible y análisis del diseño; no puedo afirmar que una corrección hipotética ya esté presente en una versión posterior que no he recibido.**

## ***Hallazgo 14. La política de reutilización de memoria puede destruir un segmento que sigue en uso**

***P0**

***Clase: ciclo de vida y propiedad de memoria compartida.**

***Ubicación: `allocate\_tensor\_slab()` y `publish\_tensor()` en `pmtp\_shm\_bus\_v26600.py`.**

***Al asignar un slab, el código intenta abrir un segmento con el mismo nombre, cerrarlo y desvincularlo antes de crear el nuevo. Si el segmento pertenece a otro proceso que todavía lo utiliza, esta operación puede romper el protocolo de propiedad compartida.**

***En POSIX, desvincular un segmento normalmente elimina su nombre, pero no necesariamente invalida de inmediato los mapeos que ya existen. Eso no hace segura la operación: un proceso nuevo puede crear otro segmento con el mismo nombre mientras los procesos antiguos continúan utilizando el anterior. Se pierde así la identidad común del recurso.**

***La consecuencia más peligrosa es la existencia de dos generaciones físicas del mismo nombre lógico, con consumidores que creen estar conectados al mismo slab, pero que ya no comparten los mismos datos.**

***Corrección SOTA:**

1. ***Separar la identidad lógica del slab de la identidad física de su almacenamiento.**

2. ***Asignar una generación o UUID al recurso, no solo un `slab\_id`.**

3. ***Impedir la sustitución mientras exista un propietario válido o leases activos.**

4. ***Introducir un protocolo de creación exclusiva, publicación, retirada y reclamación.**

5. ***Recuperar segmentos huérfanos solo después de verificar que no pertenecen a una instancia viva.**

***La regla fundamental es: un nombre coincidente no autoriza a destruir ni sustituir el recurso que ese nombre identifica.**

## ***Hallazgo 15. El timeout de leases no mide la duración de los leases**

***Ubicación: `reap\_expired\_leases()` y `publish\_tensor()`.**

***El método de recolección compara el tiempo actual con `published\_at\_ns`, es decir, con la antigüedad de la publicación. No registra la hora de adquisición de cada lease ni demuestra que el consumidor haya dejado de utilizar el buffer.**

***Un tensor publicado hace 30 segundos podría seguir siendo válido y estar siendo leído activamente. Otro publicado hace un milisegundo podría tener un consumidor que ha quedado bloqueado indefinidamente.**

***Por tanto, la antigüedad de la publicación no permite determinar si una reserva ha expirado.**

***Corrección:**

- ***Mantener separado el estado de publicación del estado de cada lease.**

- ***Definir si un lease es una reserva de propiedad, una concesión temporal renovable o una referencia de vida útil.**

- ***Si se usan concesiones temporales, exigir renovación y definir qué ocurre cuando expiran.**

- ***Si un proceso muere, recuperar sus reservas mediante un protocolo de recuperación verificable, no por la edad del tensor.**

***Hay un matiz crítico: no es seguro revocar un lease solo porque venció el reloj si el consumidor puede seguir accediendo a la memoria. En un sistema de baja latencia, la recuperación de fallos debe diseñarse sin convertir un timeout en una condición de uso después de liberar.**

## ***Hallazgo 16. La API de lectura impone una propiedad matemática que no corresponde a todo tensor**

***P1**

***Clase: contrato semántico y validez matemática.**

***Ubicación: `read\_tensor()`, parámetro `verify\_stiefel=True`.**

*![]()**La implementación calcula la norma euclídea del vector y rechaza la lectura si esta se aleja de 1 más de 10−6.**

***Eso puede ser razonable para un vector que, por contrato, debe pertenecer a la esfera unidad. No es una condición válida para cualquier tensor numérico. Un vector de activaciones, un gradiente, un bloque de una matriz o una señal física pueden tener legítimamente una norma distinta de uno.**

*![]()**Además, para una matriz de Stiefel X*∈Rn*×k*, la condición pertinente es:**

![]()**X*TX*=Ik*​**

*![]()**La norma de todo el contenido de la matriz no tiene que ser uno. Para una matriz con columnas ortonormales, su norma de Frobenius al cuadrado es k*.**

***Corrección SOTA: separar integridad del transporte de invariantes matemáticos:**

- ***`transport\_integrity`: dimensiones, dtype, versión, generación y verificación del contenido.**

- ***`unit\_vector`: comprobación de norma para vectores que lo requieran.**

- ***`stiefel\_matrix`: comprobación de ortonormalidad de columnas.**

- ***`grassmann\_subspace`: comprobaciones específicas de la representación del subespacio.**

***El protocolo de memoria no debería decidir por defecto que un tensor debe satisfacer una propiedad geométrica. Esa decisión pertenece al contrato del objeto que se transporta.**

## ***Hallazgo 17. La cabecera anuncia tipos de datos que el asignador no representa correctamente**

***Ubicación: `allocate\_tensor\_slab()`.**

***El asignador permite tipos numéricos de NumPy, pero asigna el identificador del dtype así:**

***dtype\_id = PmtpDType.FP64.value if dtype == np.float64 else PmtpDType.FP32.value**

***El protocolo declara `FP32`, `FP64`, `BF16`, `FP16`, `INT32` e `INT64`. Sin embargo, la expresión anterior etiqueta como `FP32` cualquier tipo aceptado que no coincida exactamente con `np.float64`.**

***Eso incluye tipos enteros y otros formatos admitidos por el filtro inicial. El payload puede tener un dtype real de enteros mientras la cabecera anuncia un tipo de punto flotante.**

***Las consecuencias van más allá de una etiqueta incorrecta: un consumidor nativo puede interpretar los mismos bytes con una representación distinta, corrompiendo los valores sin que el tamaño del buffer revele el error.**

***Corrección:**

1. ***Normalizar primero el tipo con `np.dtype(dtype)`.**

2. ***Usar una tabla explícita de correspondencias entre dtype, identificador PMTP, tamaño y representación wire.**

3. ***Rechazar cualquier dtype no definido por el protocolo.**

4. ***Comprobar que el consumidor valida el dtype antes de interpretar el payload.**

5. ***Añadir vectores de prueba con ceros, negativos, valores límite, NaN e infinitos cuando corresponda.**

***La regla debe ser estricta: si el protocolo no define exactamente la representación de un tipo, no se publica ese tipo bajo un identificador aproximado.**

## ***Hallazgo 18. La API de publicación no valida el contrato completo del payload**

***Ubicación: `publish\_snapshot\_atomic()`.**

***La función comprueba el estado del slab, pero no valida explícitamente que `data` tenga exactamente el número de elementos esperado, ni que su dtype sea compatible con el asignado.**

***La asignación:**

***target\_view\[:\] = data\[:\]**

***delega parte de la validación en NumPy. Eso puede producir errores de forma, conversiones implícitas o comportamientos que no coincidan con el contrato esperado del transporte.**

***También hay un problema en `publish\_tensor()`: se llama a `publish\_snapshot\_atomic()`, pero no se comprueba el valor de retorno antes de generar el descriptor. Si la publicación falla después de agotar los reintentos, el método puede devolver un descriptor cuya generación no corresponde a los datos que el llamador pretendía publicar.**

***Corrección:**

- ***Validar tamaño, dtype y forma antes de tocar el buffer.**

- ***Definir expresamente si se aceptan conversiones numéricas.**

- ***Convertir antes de adquirir el recurso de publicación, para reducir el tiempo de exclusión.**

- ***No emitir un descriptor de éxito si la publicación no se confirmó.**

- ***Si la publicación falla, conservar la generación anterior y devolver un error explícito.**

***Invariante que debe quedar demostrado:**

*![]()**descriptor vaˊlido⟹payload publicado∧generacioˊn confirmada**

***Un descriptor no debe ser una promesa optimista; debe identificar una publicación que realmente se completó.**

## ***Hallazgo 19. `max\_slabs` y `max\_dim` no están imponiendo los límites que sus nombres sugieren**

***Ubicación: constructor de `PmtpShmBus()` y métodos de asignación y publicación.**

***El constructor recibe `max\_slabs` y `max\_dim`, pero el código visible no los utiliza como límites efectivos de admisión. La asignación valida que el número de elementos sea positivo, no que esté por debajo de `max\_dim`; tampoco impone el límite de slabs mediante una política de admisión explícita.**

***Esto permite que una configuración que aparentemente limita el consumo de recursos no lo haga realmente.**

***Hay además una consecuencia de segundo orden: `max\_slabs` interviene en la elección del identificador de `publish\_tensor()`, pero no garantiza por sí solo que no haya colisiones con slabs existentes ni que sea seguro reutilizar un identificador.**

***Corrección SOTA:**

- ***Definir límites duros para el número de slabs, dimensiones, bytes por slab y bytes totales.**

- ***Validar las multiplicaciones de tamaño antes de asignar memoria.**

- ***Rechazar solicitudes que excedan los límites antes de crear o desvincular segmentos.**

- ***Implementar una política explícita de backpressure cuando se agote la memoria.**

- ***Separar la capacidad configurada de la memoria realmente reservada.**

*![]()**Para N* elementos por slot y un dtype de b* bytes, el payload de doble buffer consume:**

![]()**M*payload​=2Nb**

***A eso hay que sumarle las cabeceras, el overhead del sistema y el almacenamiento de cualquier metadato o copia temporal. La política de admisión debe calcular el consumo completo, no solo el tamaño de un array.**

## ***Hallazgo 20. El contador de generación tiene un límite finito y el protocolo no define su agotamiento**

***Ubicación: `generation` de la cabecera compacta.**

***La generación se representa como un entero sin signo de 32 bits (`I` en el formato de `struct`). La publicación calcula `hdr.generation + 1`.**

***Al alcanzar el máximo representable, el valor deja de caber en el campo y el empaquetado puede fallar. Más importante aún, un protocolo anti-ABA debe definir qué ocurre cuando una generación se reinicia, se desborda o se reutiliza un identificador.**

***El problema no se resuelve afirmando que el desbordamiento es improbable: la corrección de una etiqueta de identidad depende de su semántica, no solo de la frecuencia esperada del evento.**

***Corrección:**

- ***Definir formalmente la política de agotamiento.**

- ***Como mínimo, rechazar la publicación antes del desbordamiento y exigir una transición controlada a una nueva identidad de recurso.**

- ***Para un diseño de vida larga, considerar una generación más amplia y un UUID de instancia.**

- ***Comparar la identidad completa del recurso, no solo el `slab\_id` y un contador que pueda reutilizarse.**

***Un contador de 64 bits reduce enormemente la frecuencia del problema, pero la prueba de corrección debe seguir incluyendo la política de agotamiento.**

## ***Hallazgo 21. La prueba de estabilidad numérica de POLYDIM no demuestra la cota matemática que afirma**

***Ubicación: `teoria\_axiomas\_v26600.py`, pruebas de Lipschitz y acumulación de error.**

***Este hallazgo es distinto de los problemas de memoria. Aquí la cuestión es si la suite está verificando los teoremas declarados o solo si ciertos valores calculados son finitos.**

***En la prueba de Lipschitz se calcula una cota a partir de una matriz ortogonal y dos vectores aleatorios. Después se verifica que la diferencia entre dos vectores normalizados es menor o igual que 2. Esa desigualdad es una propiedad general de dos vectores unitarios; por sí sola no valida la cota de Lipschitz que se calculó.**

***De forma similar, la prueba denominada `Neumaier\_D65536\_norm\_error\_below\_1e12` calcula el error de `np.sum(v\*\*2)`, no de un acumulador de Neumaier implementado por el código de prueba.**

***Por tanto, ambas pruebas pueden pasar sin haber ejercitado la propiedad numérica que anuncian.**

***Corrección SOTA:**

1. ***Implementar el acumulador compensado que se pretende verificar.**

2. ***Compararlo con una referencia de precisión superior cuando esté disponible.**

3. ***Construir casos adversariales de cancelación, escalas muy distintas y acumulación prolongada.**

4. ***Para las cotas de Lipschitz, comprobar directamente la desigualdad teórica pertinente para pares de entradas y parámetros válidos.**

5. ***Añadir casos cercanos a los límites de dominio, incluyendo entradas casi nulas y matrices mal condicionadas.**

***La diferencia esencial es entre verificar que una salida parece razonable y verificar que la implementación satisface una propiedad matemática especificada.**

## ***Hallazgo 22. La prueba de distancia Grassmanniana confunde error numérico con una propiedad matemática obligatoria**

***Ubicación: `polydim\_cla\_grassmann\_v26600.py`, prueba de distancia de un subespacio a sí mismo.**

*![]()**El código comprueba que la distancia calculada entre `W1` y `W1` sea menor que 10−5, lo cual es una comprobación de tolerancia razonable para esa implementación. Pero el nombre de la prueba afirma que la distancia debe ser estrictamente positiva.**

***Matemáticamente, la distancia de un subespacio a sí mismo es cero:**

![]()**d*(S,S)=0**

***El resultado numérico puede ser cero o un pequeño residuo debido al redondeo. Exigir que sea estrictamente positivo no es una propiedad del algoritmo: depende de los datos, la biblioteca numérica, la factorización y la arquitectura.**

***Hay otro punto que merece atención: la expresión**

![]()**θi*​=arcsin(max(0,1−σi*2​)​)**

*![]()**no garantiza estabilidad superior en todos los regímenes. Cerca de *σi*​=1, la resta 1−*σi*2​ puede perder precisión relativa. Cambiar `arccos` por esa expresión no constituye, por sí solo, una demostración de estabilidad numérica.**

***Corrección:**

- ***Comprobar que la distancia de un subespacio a sí mismo está dentro de una tolerancia justificada.**

- ***Evaluar la simetría, la no negatividad y el comportamiento ante perturbaciones.**

- ***Comparar la implementación con una referencia independiente para matrices casi idénticas y casi ortogonales.**

- ***Evaluar algoritmos alternativos de ángulos principales, como formulaciones basadas en `atan2` o descomposiciones ortogonales adecuadas, midiendo su estabilidad en el dominio de interés.**

- ***Justificar las tolerancias en función de la precisión, las dimensiones y el condicionamiento, en lugar de imponer un residuo positivo.**

## ***8. El problema arquitectónico que conecta los hallazgos 14–22**

***Estos nueve hallazgos apuntan a una cuestión más profunda que un conjunto de errores aislados: POLYDIM necesita contratos formales entre identidad, memoria, representación numérica y semántica matemática.**

***La solución más sólida no consiste en agregar más `assert`. Consiste en definir las propiedades que cada capa debe preservar.**

## ***Contrato mínimo de publicación PMTP**

1. ***Identidad: cada recurso tiene una identidad inequívoca y una generación no reutilizable mientras existan consumidores válidos.**

2. ***Propiedad: ningún slot puede modificarse o reclamarse mientras un consumidor autorizado pueda acceder a él.**

3. ***Representación: el dtype, el tamaño, el orden de bytes y el ABI son idénticos en todos los productores y consumidores.**

4. ***Publicación: un descriptor solo se emite tras confirmar que los datos y sus metadatos han sido publicados coherentemente.**

5. ***Recuperación: un fallo de proceso no autoriza a reutilizar memoria sin demostrar que los accesos anteriores ya no pueden producirse.**

6. ***Semántica: las propiedades geométricas y numéricas se verifican según el tipo de objeto, no mediante una regla universal de lectura.**

7. ***Evidencia: cada garantía tiene una prueba específica, un criterio de aceptación y un resultado reproducible en el entorno correspondiente.**

## ***9. Orden de corrección recomendado**

| Orden | Trabajo | Criterio para cerrar |
| :-: | :-: | :-: |
| 1 | Identidad, leases y recuperación | No se puede reutilizar memoria accesible por un consumidor válido |
| 2 | Dtype, dimensiones y límites | Ninguna publicación puede contradecir su descriptor ni superar los límites configurados |
| 3 | Generaciones y ciclo de vida | No hay reutilización ambigua de identidades ni cierre prematuro |
| 4 | Contratos geométricos | Cada tipo de tensor verifica únicamente sus invariantes matemáticos |
| 5 | Validación numérica | Las pruebas comprueban las propiedades declaradas frente a referencias independientes |
| 6 | Pruebas cruzadas e industriales | Los resultados se reproducen en los lenguajes, sistemas y dispositivos objetivo |

## ***10. Veredicto de esta iteración**

***He identificado nueve nuevos puntos de auditoría, numerados del 14 al 22. Algunos son defectos concretos del código visible; otros son insuficiencias en las pruebas o en las garantías del diseño. No los presentaré como nueve vulnerabilidades explotadas: cada uno necesita el nivel de validación que corresponda.**

***Tampoco voy a declarar que ya no existen errores. El siguiente nivel de profundidad debe examinar la implementación nativa de CUDA y Rust, la correspondencia real del ABI entre lenguajes, la recuperación tras caída de procesos y la validez de los axiomas numéricos frente a casos adversariales.**

***Mi recomendación es continuar por la identidad y el ciclo de vida del recurso, porque un fallo ahí puede invalidar incluso un kernel matemáticamente correcto y perfectamente optimizado. Puedo seguir con la tercera iteración, centrada en esos invariantes y en los defectos de segundo orden que aparecerían al implementar estas correcciones.**




  
***AUDITORÍA COMPLETA - ENTREGA V26600**

***Basándome en el análisis profundo de todos los archivos, aquí está el informe completo de errores encontrados, ordenados por severidad:**


## 🔴 ***ERRORES CRÍTICOS (Rompen funcionalidad core)**

### ***ERROR \#1: ABI C-Dart SEMÁNTICAMENTE ROTO**

***Archivos: `pmtp\_kernel\_cpp\_v26600.cpp.txt` + `pmtp\_dart\_ffi\_v26600.dart.txt`**

***Problema: Aunque ambos structs miden 128 bytes, los campos están en posiciones SEMÁNTICAMENTE diferentes:**

| **Offset ** | **C++ (escribe) ** | **Dart (lee) ** | **¿Compatible? ** |
| - | - | - | - |

| 24-31 | `timestamp\_ns` | `numElements` | ❌ CRÍTICO |
| - | - | - | - |
| 32-39 | `dimension\_d` | `payloadBytes` | ❌ CRÍTICO |
| 40-47 | `rank\_k` | `timestampNs` | ❌ CRÍTICO |

***Consecuencia: Cuando C++ escribe un timestamp en bytes 24-31, Dart lo interpreta como `numElements`. Cuando Dart escribe `payloadBytes` en 32-39, C++ lo lee como `dimension\_d`. La comunicación C++↔Dart está completamente rota.**

***Solución: Unificar el layout. Opción A (recomendada): Cambiar Dart para que coincida con C++:**

***dart**

```
***`@Packed(1)`**

***`final class PolydimWireHeader extends Struct \{`**

`  ***@Uint32() external int magic;           *// 0`***

`  ***@Uint16() external int version;         *// 4`***

`  ***@Uint16() external int flags;           *// 6`***

`  ***@Array(16) external Array\<Uint8\> slabId; *// 8`***

`  ***@Uint64() external int timestampNs;     *// 24`***

`  ***@Uint64() external int dimensionD;      *// 32`***

`  ***@Uint64() external int rankK;           *// 40`***

`  ***@Uint32() external int dtype;           *// 48`***

`  ***@Double() external double stiefelDefect; *// 52`***

`  ***@Array(32) external Array\<Uint8\> hash;  *// 60`***

`  ***@Array(36) external Array\<Uint8\> reserved; *// 92`***

***`\}`**
```


### ***ERROR \#2: `get\_zero\_copy\_dlpack\_tensor` sin protección de lease**

***Archivo: `pmtp\_shm\_bus\_v26600.py` (línea ~280)**

***Problema:**

***Python**

```
***`def get\_zero\_copy\_dlpack\_tensor(self, slab\_id: int):`**

`    ***hdr = self.read\_header(slab\_id)  *\# Lee slot activo`***

`    ***slot = hdr.active\_slot`**

`    ***\# ... crea vista numpy sobre ese slot`***

`    ***return raw\_view  *\# ¡SIN ADQUIRIR LEASE!`***
```

***Un escritor puede llamar `publish\_snapshot\_atomic` que conmuta `active\_slot` y sobreescribe el slot anterior mientras el consumidor está leyendo la vista. Torn-read garantizado.**

***Solución: Adquirir lease antes de crear la vista, y retornar un objeto que libere el lease al cerrar:**

***Python**

```
***`class LeasedTensor:`**

`    ***def \_\_init\_\_(self, bus, slab\_id, slot, gen):`**

`        ***self.\_bus = bus`**

`        ***self.\_slab\_id = slab\_id`**

`        ***self.\_slot = slot`**

`        ***self.\_gen = gen`**

`        ***self.\_released = False`**

`    `

`    ***def \_\_dlpack\_\_(self, stream=None):`**

`        ***\# Retorna el capsule DLPack`***

`        ***pass`**

`    `

`    ***def close(self):`**

`        ***if not self.\_released:`**

`            ***self.\_bus.release\_reader\_lease(self.\_slab\_id, self.\_slot)`**

`            ***self.\_released = True`**

`    `

`    ***def \_\_del\_\_(self):`**

`        ***self.close()`**


***`def get\_zero\_copy\_dlpack\_tensor(self, slab\_id: int):`**

`    ***slot, gen = self.acquire\_reader\_lease(slab\_id)`**

`    ***\# ... crear vista sobre slot ...`***

`    ***return LeasedTensor(self, slab\_id, slot, gen)`**
```


### ***ERROR \#3: `publish\_snapshot\_atomic` en C++ no verifica lectores del slot destino**

***Archivo: `pmtp\_kernel\_cpp\_v26600.cpp.txt` (función `pmtp\_shm\_publish\_atomic`)**

***Problema: El comentario dice *"Si hay lectores activos en el sistema, aseguramos que la conmutación respete exclusión"*, pero el código NO hace eso:**

***cpp**

```
***`// Comprobar si el bloque está en destrucción`***

***`if (current\_sr & PMTP\_DESTROYING\_BIT) \{`**

`    ***return 0;`**

***`\}`**

***`// ¡FALTA: verificar si target\_slot tiene lectores activos!`***

***`uint32\_t target\_slot = 1 - current\_active;`**

***`// ... copia directamente al slot destino`***
```

***Un lector puede tener lease sobre el slot inactivo (porque estaba activo antes), y el escritor lo sobrescribe.**

***Solución:**

***cpp**

```
***`// Verificar lectores en slot destino`***

***`uint64\_t target\_readers = (target\_slot == 0) `**

`    ***? (current\_sr & 0xFFFFFFFF) `**

`    ***: ((current\_sr \>\> 32) & 0x7FFFFFFF);`**

***`if (target\_readers \> 0) \{`**

`    ***return 0; *// O reintentar con backoff`***

***`\}`**
```


### ***ERROR \#4: `acquire\_reader\_lease` en C++ no verifica `retired\_slot`**

***Archivo: `pmtp\_kernel\_cpp\_v26600.cpp.txt` (función `pmtp\_shm\_acquire\_lease`)**

***Problema:**

***cpp**

```
***`// CAS Loop - solo verifica DESTROYING\_BIT`***

***`if (current & PMTP\_DESTROYING\_BIT) \{`**

`    ***return 0;`**

***`\}`**

***`// ¡NO verifica hdr-\>retired\_slot0/retired\_slot1!`***
```

***Un lector puede adquirir lease sobre un slot que está marcado como retirado, leyendo datos obsoletos o en transición.**

***Solución:**

***cpp**

```
***`uint32\_t slot = hdr-\>active\_slot;`**

***`bool is\_retired = (slot == 0) ? hdr-\>retired\_slot0 : hdr-\>retired\_slot1;`**

***`if (is\_retired) \{`**

`    ***return 0; *// Slot retirado, no adquirir lease`***

***`\}`**
```


## 🟠 ***ERRORES GRAVES (Funcionan pero son incorrectos/engañosos)**

### ***ERROR \#5: Benchmark deshonesto en `test\_05\_honest\_transport\_benchmark`**

***Archivo: `run\_silicon\_verification\_suite.py`**

***Problema:**

***Python**

```
***`\# Mide creación de vista numpy (no lectura de datos)`***

***`t0 = time.perf\_counter()`**

***`for \_ in range(1000):`**

`    ***\_ = bus.get\_zero\_copy\_dlpack\_tensor(slab\_id=slab\_id)`**

***`t\_pmtp = ((time.perf\_counter() - t0) / 1000) \* 1e6`**
```

***Esto mide el tiempo de crear un objeto `np.ndarray` (que es solo metadata), no el tiempo de transferir datos. Luego compara contra HTTP REST completo (serialización + red + deserialización).**

***El README afirma *"31.4× más rápido que HTTP REST"* basado en esto. Es falso.**

***Solución: Medir lectura real de datos:**

***Python**

```
***`\# Medir lectura completa (copia a buffer destino)`***

***`t0 = time.perf\_counter()`**

***`for \_ in range(1000):`**

`    ***data = bus.read\_snapshot\_leased(slab\_id=slab\_id)\[0\]  *\# Esto sí copia`***

***`t\_pmtp = ((time.perf\_counter() - t0) / 1000) \* 1e6`**
```

***O admitir que es una "vista sin copia" y comparar contra "zero-copy IPC" (no contra REST).**


### ***ERROR \#6: `read\_tensor` rechaza vectores no-Stiefel**

***Archivo: `pmtp\_shm\_bus\_v26600.py` (función `read\_tensor`)**

***Problema:**

***Python**

```
***`def read\_tensor(self, slab\_descriptor: str, verify\_stiefel: bool = True):`**

`    ***\# ...`***

`    ***if verify\_stiefel:`**

`        ***nrm = np.linalg.norm(arr)`**

`        ***if abs(nrm - 1.0) \> 1e-6:`**

`            ***raise ValueError("Stiefel unit sphere integrity violation")`**
```

***Pero `publish\_tensor` acepta cualquier vector:**

***Python**

```
***`def publish\_tensor(self, vec: np.ndarray, aux\_tag: int = 0) -\> str:`**

`    ***arr = np.asarray(vec, dtype=np.float64).ravel()`**

`    ***\# No verifica norma unitaria`***
```

***Consecuencia: Si publicas un vector con norma ≠ 1 (ej: `\[1.0, 2.0, 3.0\]`), `read\_tensor` lanza excepción. El bus está roto para uso general.**

***Solución: Hacer `verify\_stiefel=False` por defecto, o eliminar la verificación de `read\_tensor` y ponerla en una capa superior específica para aplicaciones Stiefel.**


### ***ERROR \#7: Race condition en `acquire\_reader\_lease` (Python)**

***Archivo: `pmtp\_shm\_bus\_v26600.py`**

***Problema:**

***Python**

```
***`def acquire\_reader\_lease(self, slab\_id: int):`**

`    ***with self.\_local\_lock:  *\# Lock solo funciona en este proceso`***

`        ***hdr = self.read\_header(slab\_id)`**

`        ***if hdr.state\_and\_readers & (1 \<\< 63):`**

`            ***raise RuntimeError(...)`**

`        ***\# ... incrementa readers y escribe header`***
```

***El `threading.Lock` solo sincroniza hilos dentro del mismo proceso Python. Si dos procesos independientes acceden a la misma `shared\_memory`, no hay sincronización.**

***Consecuencia: En multi-proceso, dos lectores pueden leer el mismo header, ambos incrementar readers, y uno sobreescribir al otro. Pérdida de conteo de lectores → use-after-free.**

***Solución: Usar `multiprocessing.Lock` (que usa semáforos del SO) o file locking (`fcntl.flock` en Unix, `msvcrt.locking` en Windows).**


### ***ERROR \#8: `pmtp\_shm\_publish\_atomic` no es atómico**

***Archivo: `pmtp\_kernel\_cpp\_v26600.cpp.txt`**

***Problema: Usa `std::lock\_guard\<std::mutex\>` (exclusión mutua), no operaciones atómicas CAS. El nombre "publish\_atomic" es engañoso.**

***Además, el README afirma *"ciclo de vida y contadores en única palabra atómica"*, pero la implementación usa un mutex.**

***Solución: O renombrar a `publish\_locked`, o implementar verdadero CAS:**

***cpp**

```
***`// Verdaderamente lock-free`***

***`uint64\_t current = atomic\_sr-\>load(std::memory\_order\_acquire);`**

***`while (true) \{`**

`    ***if (current & PMTP\_DESTROYING\_BIT) return 0;`**

`    ***uint64\_t target\_readers = */\* extraer readers del target slot \*/*;`**

`    ***if (target\_readers \> 0) return 0; *// Slot ocupado`***

`    `

`    ***uint64\_t next = */\* nuevo estado con slot conmutado \*/*;`**

`    ***if (atomic\_sr-\>compare\_exchange\_weak(current, next,`**

`                                         ***std::memory\_order\_acq\_rel,`**

`                                         ***std::memory\_order\_acquire)) \{`**

`        ***break;`**

`    ***\}`**

***`\}`**
```


## 🟡 ***ERRORES MODERADOS (Funcionan pero son frágiles)**

### ***ERROR \#9: `Sleep(1)` en C++ - No portable**

***Archivo: `pmtp\_kernel\_cpp\_v26600.cpp.txt` (función `pmtp\_shm\_close`)**

***Problema:**

***cpp**

```
***`\#include "pmtp\_win\_shm.h"  *// Header Windows-only`***

***`// ...`***

***`Sleep(1);  *// API de Windows`***
```

***El README afirma *"ejecución directa por alumnos en Windows y Linux"*, pero el código es Windows-only.**

***Solución: Usar `std::this\_thread::sleep\_for(std::chrono::milliseconds(1))` de `\<thread\>`.**


### ***ERROR \#10: `state\_and\_readers` no es `std::atomic` en la struct**

***Archivo: `pmtp\_kernel\_cpp\_v26600.cpp.txt`**

***Problema:**

***cpp**

```
***`struct pmtp\_header\_compact\_t \{`**

`    ***// ...`***

`    ***uint64\_t state\_and\_readers;  *// NO es std::atomic\<uint64\_t\>`***

`    ***// ...`***

***`\};`**


***`// Luego se hace:`***

***`auto\* atomic\_sr = reinterpret\_cast\<std::atomic\<uint64\_t\>\*\>(&hdr-\>state\_and\_readers);`**
```

***Esto es undefined behavior según el estándar C++.**

***Solución:**

***cpp**

```
***`struct pmtp\_header\_compact\_t \{`**

`    ***// ...`***

`    ***std::atomic\<uint64\_t\> state\_and\_readers;`**

`    ***// ...`***

***`\};`**
```


### ***ERROR \#11: `reap\_expired\_leases` usa timestamp local**

***Archivo: `pmtp\_shm\_bus\_v26600.py`**

***Problema:**

***Python**

```
***`def reap\_expired\_leases(self) -\> int:`**

`    ***now\_ns = time.time\_ns()`**

`    ***for sid, info in list(self.slabs.items()):`**

`        ***pub\_ns = info.get("published\_at\_ns", now\_ns)  *\# Timestamp del PROCESO LOCAL`***
```

***En multi-proceso, cada proceso tiene su propio `published\_at\_ns`. Un slab publicado por proceso A nunca expira en proceso B.**

***Solución: Guardar `timestamp\_ns` en el header compartido (ya existe el campo) y leerlo desde ahí.**


### ***ERROR \#12: `kernel\_rust\_v26600.rs` - `newton\_schulz\_ord5\_retract` no implementa Newton-Schulz**

***Archivo: `kernel\_rust\_v26600.rs.txt`**

***Problema: La función `newton\_schulz\_ord5\_retract` afirma implementar *"Retracción PolarSafe V2 (Newton-Schulz Orden 5)"*, pero el código solo:**

1. ***Normaliza la matriz**

2. ***Calcula el defecto de ortogonalidad**

3. ***NO aplica la iteración de Newton-Schulz**

***rust**

```
***`for \_ in 0..max\_iters \{`**

`    ***// Calcular defecto`***

`    ***let mut cur\_defect = 0.0f64;`**

`    ***for c in 0..cols \{`**

`        ***// ... solo calcula normas de columnas`***

`    ***\}`**

`    ***max\_defect = cur\_defect;`**

`    ***if cur\_defect \< tol \{`**

`        ***break;`**

`    ***\}`**

`    ***// ¡FALTA: aplicar la actualización Y = Y @ poly(A)!`***

***`\}`**
```

***Consecuencia: La función nunca converge a una matriz ortogonal. Solo mide el defecto sin corregirlo.**

***Solución: Implementar la actualización:**

***rust**

```
***`for \_ in 0..max\_iters \{`**

`    ***// Calcular A = I - Y^T Y`***

`    ***let mut a = vec!\[0.0; cols \* cols\];`**

`    ***for i in 0..cols \{`**

`        ***for j in 0..cols \{`**

`            ***let mut dot = 0.0;`**

`            ***for k in 0..rows \{`**

`                ***dot += w\[k \* cols + i\] \* w\[k \* cols + j\];`**

`            ***\}`**

`            ***a\[i \* cols + j\] = if i == j \{ 1.0 - dot \} else \{ -dot \};`**

`        ***\}`**

`    ***\}`**

`    `

`    ***// Calcular poly(A) = I + 0.5A + 0.375A² + 0.3125A³ + 0.2734375A⁴`***

`    ***// ... (multiplicación de matrices)`***

`    `

`    ***// Y = Y @ poly(A)`***

`    ***// ... (multiplicación de matrices)`***

`    `

`    ***// Verificar convergencia`***

`    ***let defect = */\* calcular defecto \*/*;`**

`    ***if defect \< tol \{`**

`        ***break;`**

`    ***\}`**

***`\}`**
```


## 🔵 ***ERRORES MENORES (Estilo/documentación)**

### ***ERROR \#13: `.rlib` compilado para Windows (PE/COFF), no Linux**

***Archivo: `libkernel\_rust\_v26600.rlib`**

***Problema: El objeto dentro del `.rlib` tiene formato PE/COFF (machine type 0x8664, secciones `.pdata`/`.xdata`), que es formato Windows/MSVC, no ELF (Linux).**

***Consecuencia: No se puede linkar en Linux sin recompilar.**

***Solución: Entregar el código fuente Rust con instrucciones de compilación (`cargo build --release`), no el binario.**


### ***ERROR \#14: README afirma "5/5 pruebas" pero hay 4 módulos Python + 1 CUDA + 1 Rust**

***Archivo: `readme\_first.md`**

***Problema: El README dice *"RESULTADO GLOBAL: 5/5 PRUEBAS PASADAS"*, pero:**

- ***Solo hay 4 scripts Python ejecutables**

- ***El CUDA (`kernel\_cuda\_v26600.cu.txt`) no se ejecuta (es solo código fuente)**

- ***El Rust (`kernel\_rust\_v26600.rs.txt`) no se ejecuta (es solo código fuente)**

- ***El Triton se ejecuta pero usa fallback CPU (no GPU en este entorno)**

***Solución: Especificar claramente qué se ejecuta y qué es solo código fuente de referencia.**


## ***RESUMEN EJECUTIVO**

| **Severidad ** | **Cantidad ** | **Descripción ** |
| - | - | - |

| 🔴 Crítico | 4 | Rompen funcionalidad core (ABI roto, torn-read, race conditions) |
| - | - | - |
| 🟠 Grave | 4 | Funcionan pero son incorrectos/engañosos |
| 🟡 Moderado | 4 | Funcionan pero son frágiles |
| 🔵 Menor | 2 | Estilo/documentación |
| **TOTAL** | **14** |  |


## ***RECOMENDACIONES PRIORITARIAS**

1. ***INMEDIATO: Arreglar el ABI C-Dart (Error \#1) - sin esto, la comunicación cross-language está rota**

2. ***INMEDIATO: Agregar lease a `get\_zero\_copy\_dlpack\_tensor` (Error \#2) - sin esto, hay torn-reads garantizados**

3. ***ALTA: Arreglar verificación de lectores en `publish\_snapshot\_atomic` C++ (Error \#3)**

4. ***ALTA: Arreglar verificación de `retired\_slot` en `acquire\_lease` C++ (Error \#4)**

5. ***MEDIA: Corregir benchmark para que sea honesto (Error \#5)**

6. ***MEDIA: Hacer `verify\_stiefel=False` por defecto (Error \#6)**

  


***The user wants a deep audit of all the files. They want me to find errors, provide solutions, be thorough, not hallucinate, audit my own responses. Let me carefully go through each file.**

***Let me start systematically.**

## ***File 1: kernel\_cuda\_v26600.cu.txt**

1. ***CUDA kernel `pmtp\_cuda\_persistent\_recurrent\_kernel`:**

   - ***Uses `cg::this\_grid()` and `grid.sync()`. For grid sync to work, the kernel MUST be launched with `cudaLaunchCooperativeKernel`, and the grid size must not exceed the max blocks supported by cooperative launch. This is not validated anywhere.**

   - ***`state\_slab\[tid\] = update` — but `tid \< dim\_latent` guard. For all threads not satisfying `tid \< dim\_latent`, they still hit `grid.sync()`. That's fine.**

   - ***However, threads with `tid \>= dim\_latent` still participate in `grid.sync()` — OK.**

   - ***BUT — total\_threads = blockDim.x \* gridDim.x. Only threads with tid \< dim\_latent do work. The remaining threads do nothing but sync. OK, that's fine for correctness.**

   - ***Issue: no bounds check on `num\_steps` — if num\_steps is huge (100K), each `grid.sync()` is a global barrier. Performance may be terrible, but correctness OK.**

   - ***Issue: for `num\_steps == 0`, does nothing. OK.**

   - ***`warp\_reduce\_neumaier\_norm` is defined but never used in the persistent kernel. Dead code that claims to be a feature.**

   - ***The `warp\_neumaier\_accumulate` logic is the standard Neumaier summation — but note: `\_\_shfl\_down\_sync(mask, sum, offset)` shuffles ONLY `sum`, not `comp`. So the Neumaier compensation is only accumulated on the "receiver" side of each shuffle — this is the standard warp-reduce Neumaier pattern but let me verify.**

***Actually let's trace: each thread has (sum, comp). At each step, thread i gets sum from thread i+offset. Then Neumaier-accumulates. After loop, each thread (well, only thread 0 of the warp) has the full sum + comp. But the final `return sum + comp` returns for all threads — only lane 0's value is correct. For a proper warp reduction, you'd normally return only lane 0's value. This is a subtle issue — the function is described as returning the norm, but the actual returned values vary across lanes. This is a bug IF the user expects all lanes to have the same value.**

***Actually wait — Neumaier's `add` uses conditional based on |sum| vs |val|, so the accumulation order and resulting (sum, comp) pairs differ by lane. After the reduction loop, lanes have DIFFERENT (sum+comp) values. This is a known limitation — normal warp reductions for ordered summation are non-trivial. So `warp\_reduce\_neumaier\_norm` is presented as if it returns the total sum, but really only lane 0's value is the "correct" Neumaier-reduced sum. To be fair, for practical Neumaier-warp-reduce you'd broadcast lane 0's result back: `sum = \_\_shfl\_sync(mask, sum + comp, 0);`. This is a bug.**

2. ***`pmtp\_cuda\_newton\_schulz\_ord5\_kernel`:**

   - ***Just does `Y\[r\*cols+c\] = X\[r\*cols+c\] \* inv\_sigma\_max`. This is NOT Newton-Schulz of order 5. It's just a scalar pre-scale. The name is completely misleading. This is a naming bug / false claim.**

   - ***If `inv\_sigma\_max` is 0 (division by zero), results are NaN/Inf. No check.**

   - ***No check for `rows \> 0 && cols \> 0` at the kernel level. Kernel launched with 0x0 would just do nothing, OK.**

3. ***`pmtp\_cuda\_launch\_persistent\_grid\_simulation`:**

   - ***Takes num\_steps and dim\_latent, returns 1 or 0. Doesn't actually launch anything. Doesn't touch CUDA at all. This function is in `extern "C"` block and compiled even if `\_\_CUDACC\_\_` is not defined, but it doesn't call any CUDA code — just parameter validation. So it compiles. OK.**

   - ***BUT — the doc comment claims it "Despacho seguro" launches the simulation. It doesn't. Just validates params. Naming is misleading.**

4. ***`pmtp\_cuda\_verify\_coalescent\_alignment`:**

   - ***Checks 128-byte alignment. OK, trivial.**

   - ***Not actually used.**

5. ***Header guard `PMTP\_KERNEL\_CUDA\_V26600\_CU` and include guards look OK.**

6. ***`\#if defined(\_\_CUDACC\_\_)` — includes `cooperative\_groups.h` inside. If `\_\_CUDACC\_\_` is not defined (e.g., compiled as plain C++), the cooperative groups namespace isn't available, but the CUDA kernels aren't defined either. OK.**

7. ***Lack of `cudaError\_t` handling — no runtime error checks anywhere. This is a real concern for production code but maybe acceptable as a demo.**

## ***File 2: kernel\_rust\_v26600.rs.txt**

1. ***`PmtpHeaderCompact`:**

   - ***`\#\[repr(C, align(64))\]` — good, 64-byte alignment.**

   - ***Fields: magic(4) + version(2) + dtype\_id(2) + active\_slot(4) + slab\_id(4) + num\_elements(8) + timestamp\_ns(8) + scale(8) + generation(4) + retired\_slot0(1) + retired\_slot1(1) + reserved\_flags(2) + state\_and\_readers(AtomicU64, 8) + reserved\_pad(8) = 64 bytes. Good.**

   - ***But wait, `\#\[repr(C, align(64))\]` may add padding. `repr(C)` gives natural alignment; align(64) forces the struct to be 64-aligned. But field offsets are natural. Offset check: magic(0), version(4), dtype\_id(6), active\_slot(8), slab\_id(12), num\_elements(16), timestamp\_ns(24), scale(32), generation(40), retired\_slot0(44), retired\_slot1(45), reserved\_flags(46), state\_and\_readers(48), reserved\_pad(56). Total 64. Good.**

   - ***The static\_assert confirms 64. OK.**

2. ***`acquire\_reader\_lease`:**

   - ***`if slot == 0 \{ 1 \} else \{ 1\<\<32 \}` — This adds 1 or 2^32 to the counter. But note the DESTROYING\_BIT is at 1\<\<63, so this can't accidentally set it. But what if readers counter at bit 32-62 overflows? Slots 0 and 1 readers are stored in bits 0-31 and 32-62. So each counter allows 2^31 readers (since bit 63 is reserved). If readers\_slot1 counter hits 2^31, adding 1\<\<32 would carry into bit 63 (DESTROYING\_BIT). That's a very unlikely overflow but it is technically a bug. But it requires 2 billion concurrent readers. Not practical.**

***Actually let me re-read the header comment: "Bits 32-62: readers\_slot1 | Bits 0-31: readers\_slot0". So slot1 gets bits 32-62 = 31 bits (not 32). Wait, "bits 32-62" = 31 bits. Slot 0: "bits 0-31" = 32 bits. That's asymmetric. But the code uses `1u64 \<\< 32` for slot 1 — this increments bit 32, which occupies bit 32. When slot1 count = 2^31 (bit 62 set), adding 1\<\<32 would carry to bit 63 (DESTROYING\_BIT). Yes, that's a potential overflow bug. Practically irrelevant but theoretically a concern.**

***Also: The mask `PMTP\_READERS\_MASK = !PMTP\_DESTROYING\_BIT` covers bits 0-62 (63 bits). But if readers use bits 0-31 (32 bits) for slot0 and 32-62 (31 bits) for slot1, then only bit 62 is the max, and adding 2^32 increments bit 32. When slot1 count = 2^31, that bit-32 addition carries to bit 63. Real bug: adding `1\<\<32` when bits 32-62 are all set (2^31-1) plus adding 1\<\<32 → wraps to bit 63 (well, 2^63 + bit-32 residual). Let me think:**

***Current state: bits 0-31 = r0, bits 32-62 = r1 = 2^31 - 1. Current value = (2^31-1) \<\< 32 + r0 = (2^31-1) \* 2^32 + r0. Adding 1\<\<32 gives 2^31 \* 2^32 + r0 = 2^63 + r0. This sets bit 63 = DESTROYING\_BIT! Bug confirmed. Extremely unlikely to happen but it's real.**

   - ***Actually, C++ code has the same issue? Let me check the C++ acquire\_lease: `current + 1`. C++ version uses a single 63-bit counter (bits 0-62), so max is 2^63-1 readers... wait no, C++ increments by 1 regardless of slot. So C++ has max 2^63-1 total readers across all slots. Different design. So C++ is simpler and safer on this point.**

***Actually, the Python and C++ versions differ: C++/Python increment by 1 (unified counter for both slots). Rust and Dart? Let me check the Python:**

***text**

```
***inc = 1 if slot == 0 else (1 \<\< 32)**
```

***Yes, Python uses the same 32/32 split as Rust. But C++ uses increment 1 always:**

***cpp**

```
***if (atomic\_sr-\>compare\_exchange\_weak(current, current + 1, ...)) break;**
```

***So C++ doesn't distinguish slot in the reader counter! This is an inconsistency. Different ABI semantics. That's a real bug: the C++ and Rust/Python implementations don't agree on how to count readers. However, since they never share the same slab across languages (do they?), it may not matter in practice. But the ABI should agree. If C++ writes state\_and\_readers and Python reads it, the reader count semantics differ.**

***Also, the C++ release\_lease: subtracts 1 always. But the Rust/Python increment by 1 or 1\<\<32. So if the same slab has interleaved access from C++ and Python, the counters would go negative (well, wrap around and set the DESTROYING\_BIT). This is a real ABI inconsistency between the C++ and Python/Rust implementations.**

***Wait — let me re-check the Python release:**

***python**

```
***r0 = hdr.state\_and\_readers & 0xFFFFFFFF**

***r1 = (hdr.state\_and\_readers \>\> 32) & 0x7FFFFFFF**
```

***Yes, Python supports the 32/32 split. And C++ just does `current - 1`. So if Python acquires slot1 lease (adds 1\<\<32), then C++ releases with `current - 1` — that's a bug if mixed. But presumably the same slab is used by one language at a time. Still, the ABI contract is unclear and inconsistent between files. Worth flagging.**

***Actually C++ acquire uses `current + 1` (increments low bit). And Python uses `1 \<\< 32` for slot 1. If a mixed environment, they'd diverge. But more importantly: the C++ code doesn't track slot separately, so its `acquire\_lease` doesn't return "which slot's readers" — it uses a single counter. This means the C++ implementation is simpler but different semantics. So different implementations of the same ABI. Big red flag for correctness. But if you're consistent within one language, OK.**

***Actually more importantly — Python's `publish\_snapshot\_atomic` checks `target\_readers`:**

***python**

```
***target\_readers = (hdr.state\_and\_readers \>\> 32) & 0x7FFFFFFF if target\_slot == 1 else (hdr.state\_and\_readers & 0xFFFFFFFF)**

***if target\_readers \> 0:**

    ***time.sleep(...)**

    ***continue**
```

***So it uses the 32/32 split. But C++ `publish\_atomic` doesn't check readers of the target slot at all:**

***cpp**

```
***uint64\_t current\_sr = atomic\_sr-\>load(...);**

***if (current\_sr & PMTP\_DESTROYING\_BIT) return 0;**

***// ... does NOT check target slot readers**
```

***So the C++ implementation would overwrite a leased slot! This is a critical correctness bug in C++. The claims in the docstring say "Si hay lectores activos en el sistema, aseguramos que la conmutación respete exclusión" but the code does NOT do this. False claim / bug.**

***Let me re-read C++ publish:**

***cpp**

```
***PMTP\_API int pmtp\_shm\_publish\_atomic(...) \{**

    ***...**

    ***uint32\_t current\_active = hdr-\>active\_slot;**

    ***uint32\_t target\_slot = 1 - current\_active;**

    ***// Si hay lectores activos en el sistema, aseguramos que la conmutación respete exclusión**

    ***void\* target\_dest = ctx-\>block.get\_payload\_slot(target\_slot, ctx-\>payload\_bytes);**

    ***std::memcpy(target\_dest, data, ctx-\>payload\_bytes);**

    ***...**

***\}**
```

***The comment says it ensures exclusion but the code does NOT check anything. This is a critical bug — the C++ publisher will happily overwrite a slot that has readers with leases. This violates the T-MP17/MP-48 counterexample.**

***Great, that's a major find.**

3. ***`mark\_destroying\_and\_drain`:**

   - ***`fetch\_or(PMTP\_DESTROYING\_BIT, Ordering::AcqRel)`**

   - ***Loops `while readers != 0` with `spin\_loop()`**

   - ***No `Yield` or `sleep` — busy-waits. Reasonable but heavy.**

   - ***Returns false on timeout. OK.**

4. ***`newton\_schulz\_ord5\_retract`:**

   - ***Does pre-scaling, then in a loop computes "defect" as max column norm deviation from 1.**

   - ***But it doesn't actually apply the Newton-Schulz update! It just measures the defect and returns. So this function is a no-op retraction — it measures but doesn't retract. That's a bug: the function is called "newton\_schulz\_ord5\_retract" but it doesn't do any retraction. Comment says "Bucle de aproximación de orden 5: P(A) = I + 0.5 A + 0.375 A^2 + 0.3125 A^3 + 0.2734375 A^4" but no such polynomial application happens.**

***Actual bug. The loop:**

***rust**

```
***for \_ in 0..max\_iters \{**

    ***// Calcular defecto simple diag(W^T W)**

    ***let mut cur\_defect = 0.0f64;**

    ***...**

    ***max\_defect = cur\_defect;**

    ***if cur\_defect \< tol \{ break; \}**

***\}**
```

***It never modifies `w`. So `max\_defect` after the loop is the same as the initial defect. Function returns the initial defect (capped at first iteration). It's a no-op. Misleading function name and docstring.**

***Compare with `teoria\_axiomas\_v26600.py` which DOES apply the polynomial:**

***python**

```
***poly = np.eye(64) + 0.5\*A\_err + 0.375\*A\_err2 + 0.3125\*A\_err3 + (35/128)\*A\_err4**

***Y0 = Y0 @ poly**
```

***So Python version is correct; Rust version doesn't apply anything. Bug in Rust.**

5. ***`PolydimWireHeader` `\#\[repr(C, packed)\]`:**

   - ***Offsets: magic(4) + version\_major(2) + version\_minor(2) + slab\_uuid(16) + num\_elements(8) + payload\_bytes(8) + timestamp\_ns(8) + dtype(4) + stiefel\_defect(8) + blake2s\_hash(32) + reserved(36) = 128. Good.**

   - ***But `\#\[repr(C, packed)\]` can cause unaligned access UB on some archs. In practice Rust handles it, but you shouldn't take references to fields (you can't, since packed). OK for FFI use.**

   - ***`assert!(size\_of::\<PolydimWireHeader\>() == 128)` — OK.**

***However, comparing to the C++ `PolydimWireHeader`:**

***cpp**

```
***uint32\_t magic;               // 0**

***uint16\_t version;             // 4**

***uint16\_t flags;               // 6**

***uint8\_t  slab\_id\[16\];         // 8**

***uint64\_t timestamp\_ns;        // 24**

***uint64\_t dimension\_d;         // 32**

***uint64\_t rank\_k;              // 40**

***uint32\_t dtype;               // 48**

***double   stiefel\_defect;      // 52**

***uint8\_t  signature\_blake2s\[32\];// 60**

***uint8\_t  reserved\[36\];        // 92**
```

***Compare Rust:**

***rust**

```
***magic: u32,                  // 0**

***version\_major: u16,          // 4**

***version\_minor: u16,          // 6**

***slab\_uuid: \[u8; 16\],         // 8**

***num\_elements: u64,           // 24**

***payload\_bytes: u64,          // 32**

***timestamp\_ns: u64,           // 40**

***dtype: u32,                  // 48**

***stiefel\_defect: f64,         // 52**

***blake2s\_hash: \[u8; 32\],      // 60**

***reserved: \[u8; 36\],          // 92**
```

***The field names differ! C++ has `dimension\_d`, `rank\_k`, Rust has `num\_elements`, `payload\_bytes`. Field orders match in byte positions:**

   - ***offset 4-7: C++ `version` (2) + `flags` (2); Rust `version\_major` (2) + `version\_minor` (2). Semantically different: C++ has a single version + flags; Rust has major + minor version. If a Dart or Python consumer reads the wire header from C++, they'd interpret the `flags` (offset 6) as `version\_minor`.**

   - ***offset 24-39: C++ `timestamp\_ns` (8) then `dimension\_d` (8); Rust `num\_elements` (8) then `payload\_bytes` (8). Different meaning at the same offset!**

   - ***offset 40-47: C++ `rank\_k` (8); Rust `timestamp\_ns` (8). Different meaning!**

   - ***offset 48-51: both dtype.**

   - ***offset 52-59: both stiefel\_defect.**

   - ***offset 60-91: C++ signature\_blake2s; Rust blake2s\_hash. Same.**

***Wait, let me recount Rust offsets:**

   - ***magic: u32 @ 0-3**

   - ***version\_major: u16 @ 4-5**

   - ***version\_minor: u16 @ 6-7**

   - ***slab\_uuid: \[u8;16\] @ 8-23**

   - ***num\_elements: u64 @ 24-31**

   - ***payload\_bytes: u64 @ 32-39**

   - ***timestamp\_ns: u64 @ 40-47**

   - ***dtype: u32 @ 48-51**

   - ***stiefel\_defect: f64 @ 52-59**

   - ***blake2s\_hash: \[u8;32\] @ 60-91**

   - ***reserved: \[u8;36\] @ 92-127**

***C++ offsets:**

   - ***magic: u32 @ 0-3**

   - ***version: u16 @ 4-5**

   - ***flags: u16 @ 6-7**

   - ***slab\_id: \[u8;16\] @ 8-23**

   - ***timestamp\_ns: u64 @ 24-31**

   - ***dimension\_d: u64 @ 32-39**

   - ***rank\_k: u64 @ 40-47**

   - ***dtype: u32 @ 48-51**

   - ***stiefel\_defect: f64 @ 52-59**

   - ***signature\_blake2s: \[u8;32\] @ 60-91**

   - ***reserved: \[u8;36\] @ 92-127**

***So at offset 24-31: C++ has `timestamp\_ns`, Rust has `num\_elements`. At offset 32-39: C++ `dimension\_d`, Rust `payload\_bytes`. At offset 40-47: C++ `rank\_k`, Rust `timestamp\_ns`.**

***These are field-semantic mismatches! The ABI is NOT actually compatible between C++ and Rust despite claims of "paridad bit a bit". This is a MAJOR bug.**

***Compare with the Python:**

***text**

```
***WIRE\_HEADER\_128B\_FORMAT = "\<IHH16sQQQId32s36s"**
```

   - ***I: magic @ 0**

   - ***H: version @ 4**

   - ***H: flags @ 6**

   - ***16s: slab\_id @ 8-23**

   - ***Q: timestamp\_ns @ 24-31**

   - ***Q: dimension\_d @ 32-39**

   - ***Q: rank\_k @ 40-47**

   - ***I: dtype @ 48-51**

   - ***d: stiefel\_defect @ 52-59**

   - ***32s: signature @ 60-91**

   - ***36s: reserved @ 92-127**

***Python matches C++. Rust does NOT. Good find.**

***And Dart:**

***dart**

```
***magic @ 0**

***versionMajor @ 4**

***versionMinor @ 6**

***slabUuid @ 8-23**

***numElements @ 24-31**

***payloadBytes @ 32-39**

***timestampNs @ 40-47**

***dtype @ 48-51**

***stiefelDefect @ 52-59**

***blake2sHash @ 60-91**

***reserved @ 92-127**
```

***Dart matches Rust! So Dart+Rust agree with each other, and C+++Python agree with each other, but the two groups disagree. So the ABI is not consistent across the 4 languages despite claims. This is a critical finding.**

***Which one is "correct"? Looking at the wire header comments in C++:**

   - ***`uint8\_t slab\_id\[16\]; // Offset 8: Identificador UUID/128-bit de slab` — UUID**

   - ***`uint64\_t timestamp\_ns; // Offset 24` — timestamp**

   - ***`uint64\_t dimension\_d; // Offset 32` — dimension**

   - ***`uint64\_t rank\_k; // Offset 40` — rank**

***vs Rust:**

   - ***`slab\_uuid: \[u8; 16\]` — UUID (matches)**

   - ***`num\_elements: u64` @ 24 — number of elements (should be dimension\_d?)**

   - ***`payload\_bytes: u64` @ 32 — payload bytes (should be dimension\_d)**

   - ***`timestamp\_ns: u64` @ 40 (should be rank\_k)**

***And Python's `\<IHH16sQQQId32s36s` is same layout as C++ (timestamp, dimension\_d, rank\_k). So Python agrees with C++.**

***The Dart agrees with Rust. So there's a real ABI split. That's a big finding.**

***Now which one is right? Depends on the "wire" definition. The compact header uses num\_elements and timestamp. The 120-byte descriptor has different fields. The wire header — the field labels differ. It's ambiguous which is the intended one. But the point is: the code claims parity between C++ and Dart but the actual struct layouts are different.**

6. ***`NeumaierAccumulator`:**

   - ***Standard. OK.**

7. ***`neumaier\_norm`:**

   - ***`acc.total().sqrt()` — if total is negative due to rounding, `sqrt` returns NaN. E.g., if sum of x\*x is very close to 0 but negative compensation... possible in pathological cases. Minor.**

8. ***`static assert` `assert!(std::mem::size\_of::\<PolydimWireHeader\>() == 128)` — but the `PolydimWireHeader` in Rust is size 128? Let me verify: 4+2+2+16+8+8+8+4+8+32+36 = 128. Yes. Good.**

***But `PmtpHeaderCompact` size 64? 4+2+2+4+4+8+8+8+4+1+1+2+8+8 = 64. Good.**

***Hmm wait: `reserved\_pad: \[u8; 8\]` — that's after `state\_and\_readers` (AtomicU64). But field ordering might introduce padding in `repr(C)`. AtomicU64 requires 8-byte alignment, which is fine. `\[u8; 8\]` is 1-byte aligned. So after AtomicU64 (8-aligned, at offset 48) we go 48+8 = 56. reserved\_pad @ 56-63. Good. Total 64. And `align(64)` — this sets alignment but doesn't add padding if already 64 (since 64 divides 64). OK.**

9. ***`acquire\_reader\_lease` returns `Ok(self.generation as u64)` — but generation may be stale (racing). It's a best-effort read. Might be OK.**

## ***File 3: morpho\_redteam\_v26600.py**

***The test suite is self-contained. Let me check each test:**

### ***test\_double\_buffer\_aba**

***python**

```
***slots = \[\[10, 10\], \[20, 20\]\]**

***active = 0**

***read\_slot = active**

***first = slots\[read\_slot\]\[0\]  \# 10**

***slots\[1\]\[:\] = \[30, 30\]**

***active = 1**

***slots\[0\]\[0\] = 40**

***slots\[0\]\[1\] = 40**

***second = slots\[read\_slot\]\[1\]  \# slots\[0\]\[1\] = 40**

***observed = (10, 40)**
```

***Assert (10, 40) not in \[(10,10), (30,30), (40,40)\]. True. OK.**

***Note: this test constructs a scenario where the reader holds slot 0 but the writer overwrites it while the reader is reading. This is what would happen WITHOUT leases. The test asserts it's possible without leases. Fair.**

### ***test\_polar\_scale**

***python**

```
***vals\_small = np.linalg.svd(np.eye(2) \* 1e-9, compute\_uv=False)  \# \[1e-9, 1e-9\]**

***vals\_bad = np.linalg.svd(np.diag(\[1e9, 1e-7\]), compute\_uv=False)  \# \[1e9, 1e-7\]**

***assert vals\_small\[-1\] \< 1e-8  \# True**

***assert np.isclose(vals\_small\[0\] / vals\_small\[-1\], 1.)  \# True**

***assert vals\_bad\[-1\] \> 1e-8  \# 1e-7 \> 1e-8, True**

***assert vals\_bad\[0\] / vals\_bad\[-1\] \> 1e15  \# 1e9/1e-7 = 1e16, True**
```

***All pass. OK.**

***Wait, `np.isclose(vals\_small\[0\] / vals\_small\[-1\], 1.)` — both 1e-9 so ratio = 1. isclose default rtol=1e-5, atol=1e-8. OK, true.**

### ***test\_bridge\_spherical\_noop**

***python**

```
***W = np.eye(3, 2, dtype=np.float64)  \# 3x2**

***h = np.array(\[6., 8., 4.\])  \# norm sqrt(36+64+16) = sqrt(116) ~ 10.77**

***z\_raw = W.T @ h  \# 2-vector: \[6, 8\]**

***z\_unit = z\_raw / np.linalg.norm(z\_raw)  \# \[0.6, 0.8\]**

***z\_after\_unchanged = z\_unit.copy()**


***h\_bad = h + W @ (z\_after\_unchanged - z\_raw)  **

***\# = h + W @ (\[0.6,0.8\] - \[6,8\]) = h + W @ \[-5.4, -7.2\]**

***\# W @ \[-5.4, -7.2\] = \[-5.4, -7.2, 0\]**

***\# h\_bad = \[6-5.4, 8-7.2, 4+0\] = \[0.6, 0.8, 4\]**

***assert not np.array\_equal(h\_bad, h)  \# True**


***rho = np.linalg.norm(z\_raw)  \# 10**

***h\_good = h + W @ (rho \* (z\_after\_unchanged - z\_unit))**

***\# z\_after\_unchanged = z\_unit so (z\_after\_unchanged - z\_unit) = 0**

***\# h\_good = h + W @ 0 = h**

***assert np.array\_equal(h\_good, h)  \# True**
```

***Wait — the "good" path uses `z\_after\_unchanged - z\_unit` which is exactly 0 (they're the same reference). So h\_good = h trivially. This is a self-fulfilling test. The "good" path doesn't actually test anything meaningful — it uses the same variable twice. Not a bug per se, but the test is trivial.**

***Actually looking more carefully — this is the test of "when the injection is the same as before, the update should be a no-op." But the "good" path just uses `z\_unit - z\_unit = 0`. Trivial.**

***Hmm, what was intended: verify that with `delta\_z = rho \* (u\_new - u\_old)` where `u\_new == u\_old`, we get h\_good == h. Well, `u\_new - u\_old = 0` and `rho \* 0 = 0` so `W @ 0 = 0` and `h + 0 = h`. The test passes trivially. OK, but it's a weak test.**

***The "bad" path: `h\_bad = h + W @ (z\_unit - z\_raw)`. This is `h + W @ (u\_new - z\_raw)`. This should NOT equal h — and indeed it doesn't. So the test passes.**

***Both asserts hold. The test is trivially passing though, not really testing anything non-trivial.**

### ***test\_bridge\_sign\_and\_nonfinite**

***python**

```
***h = np.array(\[-0.0\], dtype=np.float64)**

***computed = h + np.array(\[+0.0\])  \# -0.0 + 0.0 = +0.0**

***assert h\[0\] == computed\[0\]  \# -0.0 == +0.0, True (IEEE: -0 == +0)**

***assert h.tobytes() != computed.tobytes()  \# -0.0 != +0.0 in bytes, True**
```

***OK.**

***python**

```
***wrong\_bypass = 0.0 \* np.array(\[np.nan\])  \# NaN, OK**

***assert np.isnan(wrong\_bypass\[0\])  \# True**
```

***OK.**

***python**

```
***beta = -2.0**

***W = np.array(\[\[1.0\], \[0.0\]\])**

***dz = np.array(\[3.0\])**

***dh = beta \* (W @ dz)  \# -2 \* 3 = -6**

***assert np.linalg.norm(dh) == abs(beta) \* np.linalg.norm(dz)  \# 6 == 2 \* 3 = 6, True**
```

***OK.**

***All good.**

### ***test\_cam\_statistical\_limit**

***python**

```
***return 0.025\*\*(1.0 / 8.0)  \# ~0.6299**
```

***Just returns a value, no assertion. OK.**

### ***test\_cam\_correlated\_keys\_no\_training**

***python**

```
***rng = np.random.default\_rng(123)**

***n, d = 8, 64**

***common = np.ones(d) / sqrt(d)**

***variations = rng.normal(size=(n, d))**

***variations -= (variations @ common)\[:, None\] \* common**

***variations /= np.linalg.norm(variations, axis=1, keepdims=True)**

***keys = common\[None, :\] + 0.3 \* variations**

***keys /= np.linalg.norm(keys, axis=1, keepdims=True)**

***off\_diagonal = (keys @ keys.T)\[np.triu\_indices(n, 1)\]**

***assert np.min(off\_diagonal) \> 0.8**

***queries = keys + 0.01 \* rng.normal(size=keys.shape)**

***queries /= np.linalg.norm(queries, axis=1, keepdims=True)**

***logits = queries @ keys.T / 0.01**

***weights = np.exp(logits - np.max(logits, axis=1, keepdims=True))**

***weights /= weights.sum(axis=1, keepdims=True)**

***accuracy = np.mean(np.argmax(weights, axis=1) == np.arange(n))**

***assert accuracy == 1.0**

***return float(np.min(off\_diagonal)), float(np.max(off\_diagonal)), accuracy**
```

***Reasoning: keys are `common + 0.3 \* variations` where variations are perp to common. Norm of each key: sqrt(1 + 0.3^2) ≈ 1.044, normalized. Dot product key\_i · key\_j = (common + 0.3 var\_i)·(common + 0.3 var\_j) / 1.044^2 = (1 + 0 + 0 + 0.09 \* var\_i·var\_j) / 1.09 ≈ (1 + 0.09 \* small) / 1.09.**

***var\_i · var\_j for perpendicular unit variations in d-1 dims should be ~ N(0, 1/sqrt(d-1)). So expected off\_diag ~ (1 + 0.09small)/1.09 ≈ 0.917. So min off\_diag should be ~0.917 - 3*σ where σ ~ 0.09/sqrt(63)/1.09 ~ 0.001. So min ~ 0.91. \> 0.8, pass.**

***CAM logits: `queries @ keys.T / 0.01` where queries = normalized (keys + noise). The logit at \[i\]\[i\] is huge positive; off-diagonal suppressed by softmax(T=0.01). So accuracy 1.0. Pass.**

***OK, test seems fine.**

***Overall morpho tests look OK. Small issue: test\_cam\_statistical\_limit returns 0.6299 but the docstring mentions "CI" — it's just a one-sided lower bound. Not wrong, just labeled "95% two-sided lower bound" which is a Clopper-Pearson exact lower bound. Let me check the formula: for n successes out of n, Clopper-Pearson lower bound at alpha=0.025 is alpha^(1/n) = 0.025^(1/8) = 0.6299. Yes, correct.**

## ***File 4: pmtp\_dart\_ffi\_v26600.dart.txt**

1. ***`@Packed(1)` — is this actually a valid Dart annotation? Actually, in Dart FFI, the annotation is `@Packed(N)` which is defined in `dart:ffi`. Yes, `@Packed(1)` is valid.**

2. ***`PolydimWireHeader` fields match Rust:**

   - ***magic(4) @ 0**

   - ***versionMajor(2) @ 4**

   - ***versionMinor(2) @ 6**

   - ***slabUuid(16) @ 8**

   - ***numElements(8) @ 24**

   - ***payloadBytes(8) @ 32**

   - ***timestampNs(8) @ 40**

   - ***dtype(4) @ 48**

   - ***stiefelDefect(8) @ 52**

   - ***blake2sHash(32) @ 60**

   - ***reserved(36) @ 92**

   - ***Total 128**

***So Dart matches Rust layout, not C++/Python layout. Confirms the ABI discrepancy.**

3. ***`@Double()` for stiefelDefect — in Dart FFI, the correct annotation is `@Double()`. Yes.**

4. ***`validatePmtpAbi` uses `assert(headerSize == 128, ...)`. But `assert` in Dart is disabled by default in release mode (needs `--enable-asserts`). So this check does NOT run in production. That's a weakness. Should be a runtime throw instead.**

5. ***In `pmtp\_shm\_acquire\_lease` FFI signature:**

***dart**

```
***typedef PmtpShmAcquireLeaseNative = Int32 Function(**

  ***Pointer\<Void\> handle,**

  ***Uint32 slot,**

  ***Pointer\<Uint64\> outGeneration**

***);**
```

***But the C++ signature is:**

***cpp**

```
***int pmtp\_shm\_acquire\_lease(pmtp\_handle\_t handle, uint32\_t\* out\_slot, uint32\_t\* out\_gen);**
```

***So the arguments don't match:**

   - ***C++: handle, `uint32\_t\* out\_slot`, `uint32\_t\* out\_gen`**

   - ***Dart: handle, `Uint32 slot` (value, not pointer!), `Pointer\<Uint64\> outGeneration`**

***That's a mismatch. The Dart FFI binds to a function that doesn't match the C++ ABI. Bug.**

***Also `PmtpShmReleaseLeaseNative`:**

***dart**

```
***typedef PmtpShmReleaseLeaseNative = Int32 Function(**

  ***Pointer\<Void\> handle,**

  ***Uint32 slot**

***);**
```

***But C++ returns `void`:**

***cpp**

```
***PMTP\_API void pmtp\_shm\_release\_lease(pmtp\_handle\_t handle, uint32\_t slot);**
```

***So Dart expects Int32 but C++ returns void. Mismatch. Bug.**

***And `PmtpShmCreateNative`:**

***dart**

```
***typedef PmtpShmCreateNative = Pointer\<Void\> Function(**

  ***Pointer\<Utf8\> name,**

  ***Uint64 sizeBytes,**

  ***Uint32 flags**

***);**
```

***But C++ is:**

***cpp**

```
***pmtp\_handle\_t pmtp\_shm\_create(const char\* name, uint32\_t slab\_id, uint64\_t num\_elements, uint16\_t dtype\_id);**
```

***Different signature entirely. Bug.**

***So all three Dart FFI typedefs don't match the C++ signatures.**

6. ***`PmtpShmCreateDart = Pointer\<Void\> Function(Pointer\<Utf8\> name, int sizeBytes, int flags)` — Dart side. Fine.**

7. ***No `lookupFunction` bindings shown. OK, this is just declarations.**

8. ***`validatePmtpAbi` also checks `headerSize % 64 == 0` — for 128, this is 2, OK.**

9. ***The comment says "@Packed(1) previene que el compilador de Dart añada padding". Actually the default struct layout in Dart FFI uses natural alignment, and `@Packed(1)` removes padding. That's correct.**

## ***File 5: pmtp\_kernel\_cpp\_v26600.cpp.txt**

1. ***`pmtp\_header\_compact\_t`:**

   - ***`alignas(64)`, fields as discussed. But `\#pragma pack(push, 1)` is used BEFORE the struct with `alignas(64)`. Packing and alignas(64) — do they conflict? `\#pragma pack(1)` tells compiler to use 1-byte packing for fields. `alignas(64)` on the struct aligns the struct itself. Let me think about the offsets:**

     - ***magic @ 0**

     - ***version @ 4**

     - ***dtype\_id @ 6**

     - ***active\_slot @ 8**

     - ***slab\_id @ 12**

     - ***num\_elements @ 16 (8 bytes, packed so starts right after 12+4=16)**

     - ***timestamp\_ns @ 24**

     - ***scale @ 32**

     - ***generation @ 40**

     - ***retired\_slot0 @ 44**

     - ***retired\_slot1 @ 45**

     - ***reserved\_flags @ 46**

     - ***state\_and\_readers @ 48**

     - ***reserved @ 56 (8)**

     - ***Total = 64.**

   - ***With `alignas(64)`, struct alignment is 64. Size should be 64 (round up from 64). OK, so static\_assert 64 passes.**

***Actually, with packing, does alignas(64) still enforce struct-level 64-alignment? Yes — alignas sets the struct alignment, packing affects field layout. Should be fine.**

***But wait — `\#pragma pack(1)` with `alignas(64)` may be undefined behavior or compiler-specific. In MSVC, `\#pragma pack` and `\_\_declspec(align)` — actually `alignas` is standard C++11. `\#pragma pack(1)` reduces field alignment to 1, but struct alignment with `alignas(64)` is 64. `sizeof` = round\_up(64, 64) = 64. OK.**

***Hmm but there could be an issue: MSVC may warn or error on this combination. But it might be fine.**

***Actually wait — the struct without pack but with natural alignment: uint64\_t fields need 8-byte alignment. Without pack, uint64\_t at offset 16 is fine. Without pack, alignas(64) adds tail padding: the last field `reserved\[8\]` at 56-63, so total 64, aligned 64. Same result without pack. So maybe pack(1) is redundant here but not harmful.**

2. ***`pmtp\_wire\_descriptor\_120b\_t`:**

   - ***`alignas(8)`, no pack pragma immediately? Actually `\#pragma pack(push, 1)` is still active from above. So fields are packed.**

   - ***Let me count:**

     - ***magic @ 0 (4)**

     - ***version @ 4 (2)**

     - ***dtype\_id @ 6 (2)**

     - ***active\_slot @ 8 (4)**

     - ***slab\_id @ 12 (4)**

     - ***num\_elements @ 16 (8)**

     - ***timestamp\_ns @ 24 (8)**

     - ***scale @ 32 (8)**

     - ***generation @ 40 (4)**

     - ***readers\_slot0 @ 44 (2)**

     - ***readers\_slot1 @ 46 (2)**

     - ***retired\_slot0 @ 48 (1)**

     - ***retired\_slot1 @ 49 (1)**

     - ***state @ 50 (2)**

     - ***batch\_size @ 52 (4)**

     - ***seq\_len @ 56 (4)**

     - ***dim\_source @ 60 (4)**

     - ***dim\_latent @ 64 (4)**

     - ***flags @ 68 (4)**

     - ***reserved\_ext @ 72 (8) — but comments say offset 72, and next field blake3\_hash @ 80. So reserved\_ext(8) @ 72-79. Good.**

     - ***blake3\_hash @ 80 (32) — @ 80-111**

     - ***padding\_ext @ 112 (8) — @ 112-119**

     - ***Total = 120.**

   - ***static\_assert passes.**

3. ***`PolydimWireHeader`:**

   - ***`\_\_attribute\_\_((packed))`, no alignas.**

   - ***`uint32\_t magic @ 0`, `uint16\_t version @ 4`, `uint16\_t flags @ 6`, `uint8\_t slab\_id\[16\] @ 8`, `uint64\_t timestamp\_ns @ 24`, `uint64\_t dimension\_d @ 32`, `uint64\_t rank\_k @ 40`, `uint32\_t dtype @ 48`, `double stiefel\_defect @ 52`, `uint8\_t signature\_blake2s\[32\] @ 60`, `uint8\_t reserved\[36\] @ 92`.**

   - ***Total 128. static\_assert passes.**

   - ***But wait: `\_\_attribute\_\_((packed))` allows unaligned access. `double stiefel\_defect` at offset 52 is NOT 8-byte aligned (52 % 8 = 4). This is technically UB when accessed (misaligned double access) on some platforms (though most x86 allows it). Should use memcpy for reads/writes to be strict. Subtle bug/concern.**

***Also compare: C++ `PolydimWireHeader` has `flags @ 6` (2 bytes) but Rust/Dart have `versionMinor @ 6` (2 bytes). And C++ has `dimension\_d @ 32`, `rank\_k @ 40`, `timestamp\_ns @ 24`. Rust/Dart have `payloadBytes @ 32`, `timestampNs @ 40`, `numElements @ 24`. Confirmed ABI split.**

4. ***`pmtp\_shm\_create`:**

   - ***`size\_t total\_bytes = sizeof(pmtp\_header\_compact\_t) + (2 \* ctx-\>payload\_bytes);` — OK.**

   - ***Initializes header. OK.**

   - ***But `hdr-\>state\_and\_readers = 0;` — this initializes to no readers. OK.**

5. ***`pmtp\_shm\_publish\_atomic` — CRITICAL BUG as noted above. Does not check target slot readers. Overwrites leased slots.**

***Let me re-verify:**

***cpp**

```
***PMTP\_API int pmtp\_shm\_publish\_atomic(...) \{**

    ***...**

    ***uint32\_t current\_active = hdr-\>active\_slot;**

    ***uint32\_t target\_slot = 1 - current\_active;**

    ***// comment says check exclusion**

    ***void\* target\_dest = ctx-\>block.get\_payload\_slot(target\_slot, ctx-\>payload\_bytes);**

    ***std::memcpy(target\_dest, data, ctx-\>payload\_bytes);  // OVERWRITES WITHOUT CHECK!**

    ***...**

***\}**
```

***Yes, no reader check. This allows overwriting a leased slot. Contradicts the "exclusión de sobreescritura si el slot destino tiene lectores activos" claim.**

***Compare Python which does check:**

***python**

```
***target\_readers = ...**

***if target\_readers \> 0:**

    ***time.sleep(...); continue**
```

***So Python is correct, C++ is buggy.**

6. ***`pmtp\_shm\_acquire\_lease`:**

***cpp**

```
***uint64\_t current = atomic\_sr-\>load(...);**

***while (true) \{**

    ***if (current & PMTP\_DESTROYING\_BIT) return 0;**

    ***if (atomic\_sr-\>compare\_exchange\_weak(current, current + 1, ...)) break;**

***\}**

***uint32\_t slot = hdr-\>active\_slot;**

***\*out\_slot = slot;**

***\*out\_gen = hdr-\>generation;**
```

   - ***Reads `hdr-\>active\_slot` AFTER the CAS. Between CAS and read, another thread could have published (swapped slots). Then `\*out\_slot` would be the new active slot, but we incremented the counter as if we were a reader of... well, we didn't increment for a specific slot. The C++ semantics is: increment a global reader count. So it doesn't matter which slot we "acquired" — the counter is global.**

***But here's the issue: The caller uses `out\_slot` to read from. If `active\_slot` changes between acquire and read, the caller would read from the NEW active slot (which is fine, since new slot has data). But the global reader count doesn't protect against the writer overwriting the OLD slot (which the reader thinks they're reading from)... but actually the reader reads from `\*out\_slot`, which is read after the CAS. Since `active\_slot` is read once and used, if the writer swaps after our read of `active\_slot`, the writer would be overwriting the OTHER slot (the one we're NOT reading from), which is fine. If the writer swaps between our CAS and our `active\_slot` read, we read the NEW slot value — still fine, since new slot is now active.**

***But there's a classic race: the writer swaps slot after we acquire the lease and after we read `active\_slot`, so we're reading from slot A, but the writer already swapped to slot B and now wants to write to slot A (which is what we're reading). The C++ writer doesn't check leases, so it would overwrite slot A. Even if the writer did check, since C++ reader counter is global (doesn't track per-slot), the writer wouldn't know to wait.**

***So the C++ design has two issues: (1) reader counter isn't per-slot; (2) writer doesn't check leases.**

***The Python design tracks per-slot readers and checks before overwriting. Better. But Python's `publish\_snapshot\_atomic` does its check-and-overwrite under `self.\_local\_lock`, which is a Python thread lock, NOT cross-process. So if two processes access the same shared memory slab, the local lock doesn't prevent races. Bug — the lock is only useful for threads within the same process. For cross-process safety, real atomic operations are needed. In Python, `struct.pack` + `shm.buf\[...\] = ...` is NOT atomic across processes.**

***Similarly, `acquire\_reader\_lease` in Python does `hdr.state\_and\_readers + inc` inside `self.\_local\_lock` but `shm.buf\[:HEADER\_COMPACT\_SIZE\] = new\_header\_bytes` writes the whole 64-byte header, which includes other fields. This is a read-modify-write with local lock only. Cross-process there's no atomic protection. The Python implementation is NOT actually thread-safe/process-safe beyond a single-process scenario!**

***This is a huge flaw. The C++ version uses `std::atomic\<uint64\_t\>` for `state\_and\_readers`, but that's only safe if the same atomic is used consistently. In Python, writing the whole header via `shm.buf\[:64\] = ...` is not atomic at the field level.**

***So the Python claims of "leases atómicos" are only true within a single process. This is a big claim vs reality gap.**

7. ***`pmtp\_shm\_release\_lease` — C++ version:**

***cpp**

```
***uint64\_t active\_readers = current & PMTP\_READERS\_MASK;**

***if (active\_readers == 0) break;**

***uint64\_t next = (current & PMTP\_DESTROYING\_BIT) | (active\_readers - 1);**
```

***Subtracts 1 from the unified counter. Matches `acquire\_lease` (adds 1). Good within C++.**

***But if Python does `acquire\_reader\_lease(slot=1)` → adds 2^32. Then C++ `release\_lease` subtracts 1. Result: state\_and\_readers loses 2^32 - 1. Corruption. Cross-language. Bug.**

8. ***`pmtp\_shm\_read\_leased`:**

   - ***Calls `acquire\_lease`, reads, releases.**

   - ***Reads `slot` from `acquire\_lease` output. But as noted, C++ `acquire\_lease` reads `active\_slot` after CAS — could race with a writer that also uses `mtx`. But the writer holds `ctx-\>mtx` for its critical section, and the reader does not hold `mtx`. So the reader's `active\_slot` read could race with the writer's slot swap.**

***Reader: `acquire\_lease` increments `state\_and\_readers`, then reads `active\_slot` (unsynchronized wrt writer). Writer: reads `active\_slot`, writes to target, updates `active\_slot`, updates generation. The reader might read stale `active\_slot` (before the writer updates it), which is fine because the writer's data is being written to the target slot (not the old active), and the reader's target slot is old active. But the reader's global counter increment happens BEFORE reading `active\_slot` — so if a writer swaps after the reader's counter increment and after the reader reads `active\_slot`, the reader reads from old active (now inactive). If the writer then writes to old active (which is now target), we have a race: writer overwrites while reader reads.**

***The writer doesn't check leases (bug already noted). Even if it did, the per-slot counter is missing. So this race exists.**

***To fix: (1) make reader counter per-slot; (2) writer checks per-slot count; (3) acquire\_lease should read `active\_slot` BEFORE the CAS or use a proper SEQLock with version check.**

***Actually the standard pattern: read active\_slot, CAS increment for that slot's counter, verify active\_slot unchanged (retry if changed). The C++ code skips the verify.**

9. ***`pmtp\_shm\_close`:**

   - ***`PMTP\_API void pmtp\_shm\_close(...)` — void return. Dart declares Int32 return. Mismatch.**

   - ***Uses `Sleep(1)` — Windows-only. Won't compile on Linux/Mac without `\#ifdef \_WIN32` (or a wrapper). Portability bug.**

   - ***`Sleep` is from `\<windows.h\>`. Not included. Also `Sleep(1)` may sleep for ~15ms on some Windows versions (timer granularity). Not great.**

   - ***`pmtp\_shm\_close` marks DESTROYING, drains readers, then closes. But `shm\_close` is called even for readers (from the same function). If two processes have handles, one closing would mark DESTROYING and invalidate the other's handle. That's expected for a "destroy" but not for a "close". The name suggests close, not destroy. Ambiguous.**

10. ***`pmtp\_win\_shm.h`, `pmtp\_c\_abi.h` — included but not provided. Assume they exist.**

11. ***`PMTP\_API` — assumes defined in `pmtp\_c\_abi.h`. Assume OK.**

12. ***`pmtp\_shm\_create` uses `slab\_id` as `uint32\_t` in C++ but Dart's `PmtpShmCreateNative` takes a `sizeBytes` (uint64) + flags. Different. Already noted.**

13. ***Missing `pmtp\_shm\_destroy` — only close. But close does destroy semantics.**

14. ***The header `alignas(PMTP\_ALIGNMENT\_BYTES)` with `\#pragma pack(1)` — let me double-check offsets. Actually with `pack(1)`, would `alignas(64)` still be respected? Yes, alignas is orthogonal to field packing. Should work. But some compilers might warn.**

## ***File 6: pmtp\_shm\_bus\_v26600.py**

1. ***`HEADER\_COMPACT\_FORMAT = "\<IHHIIQQdI??HQ8s"` — let me compute size:**

   - ***`\<` little-endian**

   - ***`I` (magic) = 4**

   - ***`H` (version) = 2**

   - ***`H` (dtype\_id) = 2**

   - ***`I` (active\_slot) = 4**

   - ***`I` (slab\_id) = 4**

   - ***`Q` (num\_elements) = 8**

   - ***`Q` (timestamp\_ns) = 8**

   - ***`d` (scale) = 8**

   - ***`I` (generation) = 4**

   - ***`?` (retired\_slot0) = 1**

   - ***`?` (retired\_slot1) = 1**

   - ***`H` (reserved\_flags) = 2**

   - ***`Q` (state\_and\_readers) = 8**

   - ***`8s` (reserved) = 8**

   - ***Total = 4+2+2+4+4+8+8+8+4+1+1+2+8+8 = 64.**

***But wait — Python `struct` with `\<` uses standard sizes and no alignment padding. So this should be exactly 64. Assertion passes.**

2. ***`WIRE\_HEADER\_128B\_FORMAT = "\<IHH16sQQQId32s36s"`:**

   - ***`I` = 4**

   - ***`H` = 2**

   - ***`H` = 2**

   - ***`16s` = 16**

   - ***`Q` = 8**

   - ***`Q` = 8**

   - ***`Q` = 8**

   - ***`I` = 4**

   - ***`d` = 8**

   - ***`32s` = 32**

   - ***`36s` = 36**

   - ***Total = 4+2+2+16+8+8+8+4+8+32+36 = 128. Good.**

***Fields in order: magic, version, flags, slab\_id, timestamp\_ns, dimension\_d, rank\_k, dtype, stiefel\_defect, signature, reserved. Matches C++ order. Confirms Python matches C++.**

3. ***`WIRE\_DESCRIPTOR\_FORMAT = "\<IHHIIQQdIHH??HIIIIIQ32s8s"`:**

   - ***I (magic) 4**

   - ***H (version) 2**

   - ***H (dtype\_id) 2**

   - ***I (active\_slot) 4**

   - ***I (slab\_id) 4**

   - ***Q (num\_elements) 8**

   - ***Q (timestamp\_ns) 8**

   - ***d (scale) 8**

   - ***I (generation) 4**

   - ***H (readers\_slot0) 2**

   - ***H (readers\_slot1) 2**

   - ***? (retired\_slot0) 1**

   - ***? (retired\_slot1) 1**

   - ***H (state) 2**

   - ***I (batch\_size) 4**

   - ***I (seq\_len) 4**

   - ***I (dim\_source) 4**

   - ***I (dim\_latent) 4**

   - ***I (flags) 4**

   - ***Q (reserved\_ext) 8**

   - ***32s (blake3) 32**

   - ***8s (padding\_ext) 8**

   - ***Total: 4+2+2+4+4+8+8+8+4+2+2+1+1+2+4+4+4+4+4+8+32+8**

   - ***= 4+2+2+4+4 = 16; +8+8+8 = 40; +4 = 44; +2+2 = 48; +1+1 = 50; +2 = 52; +4+4+4+4+4 = 72; +8 = 80; +32 = 112; +8 = 120. Good.**

***Compare C++ `pmtp\_wire\_descriptor\_120b\_t` (with pack(1)):**

   - ***magic 4 @ 0**

   - ***version 2 @ 4**

   - ***dtype\_id 2 @ 6**

   - ***active\_slot 4 @ 8**

   - ***slab\_id 4 @ 12**

   - ***num\_elements 8 @ 16**

   - ***timestamp\_ns 8 @ 24**

   - ***scale 8 @ 32**

   - ***generation 4 @ 40**

   - ***readers\_slot0 2 @ 44**

   - ***readers\_slot1 2 @ 46**

   - ***retired\_slot0 1 @ 48**

   - ***retired\_slot1 1 @ 49**

   - ***state 2 @ 50**

   - ***batch\_size 4 @ 52**

   - ***seq\_len 4 @ 56**

   - ***dim\_source 4 @ 60**

   - ***dim\_latent 4 @ 64**

   - ***flags 4 @ 68**

   - ***reserved\_ext 8 @ 72**

   - ***blake3\_hash 32 @ 80**

   - ***padding\_ext 8 @ 112**

   - ***Total 120.**

***Matches Python. Good.**

4. ***`PmtpCompactHeader.unpack`:**

   - ***Uses `HEADER\_COMPACT\_STRUCT.unpack(buffer\[:64\])`. OK.**

5. ***`allocate\_tensor\_slab`:**

   - ***Deletes existing shm first. OK.**

   - ***Creates new shm. OK.**

   - ***Writes header. OK.**

   - ***BUT: uses `shm.buf\[:HEADER\_COMPACT\_SIZE\] = header\_bytes` — NOT atomic. Cross-process would race.**

6. ***`publish\_snapshot\_atomic`:**

   - ***Has `self.\_local\_lock` — only protects within a single Python process.**

   - ***Reads header, checks DESTROYING and target\_readers.**

   - ***If target\_readers \> 0, retries. But after enough retries it gives up. Since `max\_retries=100`, `retry\_delay\_s=0.0005`, that's 50ms total. After that, returns False. Reasonable.**

   - ***But the check-then-act is under `self.\_local\_lock` (process-local), so a different process could interleave. Cross-process bug.**

   - ***Writes new\_header\_bytes to `shm.buf\[:64\]` — NOT atomic wrt other processes.**

7. ***`acquire\_reader\_lease`:**

   - ***Reads header, checks DESTROYING, reads retired flag for slot.**

   - ***If retired, `continue` (retry).**

   - ***Increments counter, writes header back. NOT atomic cross-process.**

   - ***Race: between reading the header and writing it back, another process could have modified it. Under `self.\_local\_lock`, this only protects within-process.**

8. ***`release\_reader\_lease`:**

   - ***Similar race.**

9. ***`get\_zero\_copy\_dlpack\_tensor`:**

   - ***Returns `raw\_view` which is `np.ndarray(buffer=shm.buf, ...)`.**

   - ***BUT — `raw\_view` is a numpy array. Does it implement `\_\_dlpack\_\_`? Yes, numpy arrays implement `\_\_dlpack\_\_` in recent versions (numpy 1.22+). So `torch.from\_dlpack(raw\_view)` works.**

   - ***BUT — `torch.from\_dlpack` takes the object and consumes `\_\_dlpack\_\_` and `\_\_dlpack\_device\_\_`. Since `raw\_view` is a numpy array whose buffer is `shm.buf`, and numpy's `\_\_dlpack\_\_` exports the numpy buffer, this should work.**

   - ***HOWEVER — `shm.buf` is a `memoryview`, and `np.ndarray(..., buffer=shm.buf, ...)` uses it. The resulting numpy array's `\_\_dlpack\_\_` would export the memory. But the memory is shared memory. Is this safe? The memoryview is alive (through `shm.buf`); as long as `shm` is alive, the array is valid. OK.**

   - ***The `\_\_dlpack\_\_` protocol by default requires that the producer keeps the memory alive during the DLPack consumer's lifetime, which is managed by the DLPack deleter. Since numpy doesn't support zero-copy out to arbitrary consumers historically... actually modern numpy does.**

   - ***Concern: The test does:**

   - ***python**

   - ```
***dl\_tensor = bus.get\_zero\_copy\_dlpack\_tensor(slab\_id=slab\_id)**

   - ***t = torch.from\_dlpack(dl\_tensor)**
```

   - ***And then modifies `t\[0\] = 777.0`. If it's truly zero-copy, this modifies shared memory. The test then verifies via a second `get\_zero\_copy\_dlpack\_tensor` + `from\_dlpack` + `t2\[0\]`. This confirms zero-copy works... IF numpy's `\_\_dlpack\_\_` and torch's `from\_dlpack` both support it. In practice this works with recent numpy+torch.**

   - ***Potential issue: torch.from\_dlpack may fail on a non-contiguous array or an array with unusual buffer. `raw\_view` is 1D contiguous. OK.**

   - ***Another subtle issue: `raw\_view` doesn't implement `\_\_dlpack\_device\_\_`. numpy's ndarray has it (returns CPU device in recent versions). OK.**

***So this may work but relies on specific versions.**

10. ***`publish\_tensor`:**

    - ***`sid = (self.\_next\_slab\_seq % max(1, self.max\_slabs)) + 1` — first call: `(1 % 64) + 1 = 2`. So slabs start at ID 2. OK, odd but not wrong.**

    - ***`if sid in self.slabs and self.slabs\[sid\]\["num\_elements"\] == arr.size and not self.slabs\[sid\].get("released", False)`: reuses. Else deletes/reallocates. OK.**

    - ***Returns `f"SLAB\_ID\_\{sid\}\_\{hdr.generation\}"`. OK.**

    - ***Bug: `self.\_next\_slab\_seq % max(1, self.max\_slabs)` — the modulo cycles through \[0, max\_slabs-1\], then +1 → \[1, max\_slabs\]. So slab 0 never used. Minor. And after `max\_slabs` allocations, wraps around to reuse slab 1. OK, works but slightly odd.**

    - ***Also note `max(1, self.max\_slabs)` — if `max\_slabs=0`, would use 1, giving sid=1 always. Minor.**

11. ***`read\_tensor`:**

    - ***Uses lease. Verifies norm ~ 1.0 if `verify\_stiefel=True`. But default `verify\_stiefel=True` — hmm, that requires the published vector to be a unit vector. `publish\_tensor` doesn't normalize. So publishing `\[42.0, 42.0, ...\]` and then reading with `verify\_stiefel=True` would raise ValueError because norm != 1.0.**

    - ***This is a bug/inconsistency: `publish\_tensor` doesn't enforce unit norm, but `read\_tensor` requires it by default. So round-trip publish→read fails for non-unit vectors.**

    - ***Wait, but the test suite (run\_silicon\_verification\_suite.py) doesn't use `publish\_tensor`/`read\_tensor`, it uses `publish\_snapshot\_atomic` and `acquire\_reader\_lease` directly. So the test doesn't catch this. But the API is inconsistent.**

    - ***Also `read\_tensor` verifies `abs(nrm - 1.0) \> 1e-6` raises. So if you published a vector with norm sqrt(2048)\*42 ≈ 1900, reading raises. Bug or intended? Comment says "opcionalmente que cumpla la norma unitaria Stiefel". Default True. Should maybe default False or the publish should normalize. But no normalization in publish. Bug.**

12. ***`release\_slab` just marks `released=True` in dict. Doesn't mark shared memory. The slab remains accessible via other means. The DESTROYING\_BIT is only set in `release\_all`. Inconsistent.**

13. ***`reap\_expired\_leases` — iterates and marks released based on publish time. But doesn't release actual shared memory. Odd semantics.**

14. ***`\_slabs` property — returns `(active\_slot, shm)` tuples. Read-only. OK.**

15. ***`HEADER\_COMPACT\_FORMAT` uses `?` for bool — `retired\_slot0`, `retired\_slot1`. When packing `False`/`True`, they serialize as 0/1. OK.**

16. ***`release\_all`:**

    - ***`destroy\_sr = hdr.state\_and\_readers | (1 \<\< 63)` — sets DESTROYING\_BIT.**

    - ***`shm.buf\[48:56\] = struct.pack("\<Q", destroy\_sr)` — writes directly to the byte offset.**

    - ***Offset 48 in the compact header is `state\_and\_readers`. Confirmed.**

    - ***`shm.close()` + `shm.unlink()`. OK.**

    - ***Issue: this doesn't wait for readers to drain. It just closes. In Python, in-process this is fine because the lock is held. Cross-process, this could break.**

17. ***`\_slabs` property but also `self.slabs` — the property returns a new dict. OK.**

18. ***`self.\_next\_slab\_seq` starts at 1. OK.**

19. ***`PmtpCompactHeader.unpack` — works on 64 bytes. OK.**

20. ***Format mismatch check for dtype\_id / retired flags: The format uses `?` for bool; but when the header is written by `pmtp\_kernel\_cpp\_v26600.cpp`, it's `uint8\_t retired\_slot0` (0/1). When Python reads as `?`, it interprets any non-zero as True. OK.**

21. ***`HEADER\_COMPACT\_FORMAT` includes `state\_and\_readers` as `Q` (unsigned 64-bit), and the C++ has `uint64\_t state\_and\_readers`. Good.**

22. ***BUT — the C++ uses `std::atomic\<uint64\_t\>` over this field via `reinterpret\_cast`. That's technically UB (atomic overlaid on non-atomic storage), though it works on most platforms. In Python, reads/writes are via struct pack/unpack over `shm.buf`. The `struct` access is not atomic wrt the C++ atomic operations. Cross-language, this is broken. But if each language uses its own slab, OK.**

23. ***`MAX\_DIM` unused — `max\_dim=8192` is stored but never checked. Minor.**

24. ***`lease\_timeout\_ms` used only in `reap\_expired\_leases`, which is not called automatically. So leases never time out via this mechanism unless the user calls it. Minor / design issue.**

## ***File 7: polydim\_cla\_grassmann\_v26600.py**

***Tests:**

1. ***Test 1 (angles):**

   - ***`theta\_arcsin = np.arcsin(np.sqrt(np.maximum(0.0, 1.0 - sigma\*\*2)))` — this is the standard formula. OK.**

   - ***`arcsin\_vs\_arccos\_agree\_1e10` — checks `allclose(theta\_arccos, theta\_arcsin, atol=1e-10)`.**

   - ***Concern: For `sigma` close to 1, `arccos` has large derivative (1/sqrt(1-σ²)) and `arcsin(sqrt(1-σ²))` has small derivative (bounded). So `arccos` loses precision but `arcsin` is more stable. Their difference could exceed 1e-10 for near-unit σ.**

***With `W2 = W1 + 1e-8 \* noise`, sigma ~ 1 - small. Let me estimate: The angle between W1 and W2 subspaces is ~1e-8. So `1 - σ ~ 1e-16` (σ² ~ 1 - 2e-16). This is at the epsilon boundary! `arccos` would be catastrophically imprecise (derivative goes to infinity), and might return values ~ sqrt(1-σ²) ~ sqrt(2e-16) ~ 1.4e-8, but with huge relative error.**

***Actually let me compute more carefully. W2 = W1 + 1e-8 \* perturbation. Perturbation has norm ~ sqrt(Dr) = sqrt(128*64) = sqrt(8192) ≈ 90. So W2 - W1 ~ 1e-8 \* 90 ≈ 1e-6 norm. After QR, W2 differs from W1 by ~1e-6 in matrix norm.**

***The principal angles: sigma = svd(W1^T W2). W1^T W2 = W1^T (W1 + epsP) = I + eps*W1^T P. So sigma = svd(I + epsW1^T P). For eps*W1^T P small, sigma\_i ≈ 1 + eps\*λ\_i where λ\_i is eigenvalues of the symmetric part... actually σ\_i ≈ 1 + eps \* (W1^T P)\_\{ii\} roughly.**

***With eps=1e-8 and (W1^T P)\_\{ii\} ~ O(1), σ\_i ≈ 1 ± 1e-8. So σ² ≈ 1 ± 2e-8. 1 - σ² ≈ 2e-8. sqrt ≈ 1.4e-4. So arcsin(1.4e-4) ≈ 1.4e-4. arccos(1 - 1e-8) also ≈ 1.4e-4. Both should be similar to ~1e-10.**

***Hmm, but arccos precision: for x = 1 - δ, `arccos(x)` computed as `sqrt(2δ)` roughly. δ = 1e-8, sqrt(2e-8) ≈ 1.4e-4. arccos precision for x near 1 is about eps/sqrt(1-x²) = 1e-16 / 1.4e-4 = 7e-13 relative. So arccos ≈ 1.4e-4 with absolute error ~1e-12. arcsin similarly. Their difference should be \< 1e-11. So the test should pass with atol=1e-10. Might be tight.**

***Actually the noise is 1e-8 \* randn(D, r) where each element is ~1e-8. So the perturbation is ~1e-8 \* 1 in each element. After the +W1, then QR. Actually W1 has norm 1 per column, so QR of W1 + 1e-8 \* randn. The QR should give back nearly W1 since the perturbation is tiny. So W2 ≈ W1. So σ ≈ 1 to machine precision. Then 1 - σ² could be ~1e-16 (machine eps). Then arcsin(sqrt(1e-16)) = arcsin(1e-8) = 1e-8, arccos(1 - 5e-17)... hmm actually σ would be extremely close to 1.**

***Wait, the perturbation is 1e-8, but the QR of W1 + eps\*P: the columns are nearly orthonormal, and after QR they'd be normalized. The projection onto W1's column space gives σ\_i ≈ cos(angle between column i of W1 and column i of W2) ≈ 1 - eps²/2 \* ||perpendicular component||². With eps = 1e-8 and perp component ~ sqrt(D) = 11, eps²/2 \* 121 ≈ 6e-15. So σ\_i ≈ 1 - 6e-15. So σ² ≈ 1 - 1.2e-14. 1 - σ² ≈ 1.2e-14. arcsin(sqrt(1.2e-14)) = arcsin(1.1e-7) ≈ 1.1e-7 per component. Sum of 64 such: ~ 64 \* 1.1e-7 ≈ 7e-6 (or RMS ~ 9e-7). So `dist\_w1\_w2` is ~1e-6.**

***But `dist\_self` in test 2 uses W1.T @ W1. QR defect ~ 1e-15. Similar computation: dist\_self ~ sqrt(64) \* sqrt(2\*1e-15) ≈ 8 \* 4.5e-8 ≈ 3.6e-7. So test 2 bound of 1e-5 passes.**

***`dist\_w1\_w2 \> dist\_self`? `dist\_w1\_w2` ~1e-6, `dist\_self` ~3.6e-7. So `dist\_w1\_w2 \> dist\_self` may be true (1e-6 \> 3.6e-7). But it's close. Depends on the random seed and precision. Might fail sometimes. Hmm, but the seed is fixed (42, 99). So it's deterministic. Let me estimate more carefully.**

***For test 2, `dist\_self = norm(arcsin(sqrt(1 - σ\_self²)))` where `σ\_self = svd(W1.T @ W1)`.  
`W1.T @ W1 = I + E` where `E` has entries ~eps. SVD of `I + E`: σ\_i = 1 + λ\_i + O(eps²) where λ\_i are eigenvalues of E.**

***Hmm, actually E is symmetric (W1^T W1 is symmetric), so E has real eigenvalues. σ\_i = 1 + λ\_i (for E small, and W1^T W1 symmetric PSD). |λ\_i| ≤ ||E||\_2 ~ eps \* sqrt(r). With eps ~ 1e-16 and r = 64, ||E|| ~ 8e-16. So σ\_i ∈ \[1-8e-16, 1+8e-16\]. Since W1 is QR-decomposed, it's approximately orthonormal, so W1^T W1 ≈ I with error ~eps. Actually after numpy's QR, `||Q^T Q - I||\_2` is typically ~1e-16 \* r (for modified Gram-Schmidt) or ~1e-15. Let me just say ~1e-15 max defect.**

***Then σ\_i may exceed 1! Since W1 is only approximately orthonormal, σ\_self could be \> 1 due to numerical rounding. In that case, `1 - σ\_self²` would be negative, and `np.maximum(0.0, ...)` clips to 0. So `arcsin(sqrt(0)) = 0`. Then `dist\_self = 0`. But test 2 asserts `0.0 \<= dist\_self \< 1e-5`. 0 \<= 0 \< 1e-5, passes. But then `perturbed\_distance\_gt\_self\_distance` would compare dist(W1,W2) \> 0 — should be true since dist\_w1\_w2 \> 0 (W1 != W2). OK.**

***Hmm but if some σ\_i \> 1 (due to rounding) and others σ\_i \< 1, only the ones \< 1 contribute. So dist\_self is small but positive. OK.**

***Test passes conditionally. But the assertion `self\_distance\_strictly\_positive\_but\_tiny` — the name says "strictly positive" but the check is `0.0 \<= dist\_self \< 1e-5` (allows 0). Inconsistent naming. Minor.**

***Actually wait — `self\_distance\_strictly\_positive\_but\_tiny` uses `0.0 \<= dist\_self` — so 0 passes. Name is misleading but code OK.**

2. ***Test 3 (Procrustes):**

   - ***Standard. OK.**

3. ***Test 4 (idempotent):**

   - ***Standard. OK.**

4. ***Test 5 (clip):**

   - ***`sigma\_overflow = np.array(\[1.0 + 1e-15, 0.99, 0.5\])`.**

   - ***`np.arccos(1.0 + 1e-15)` should be NaN since arccos is only defined on \[-1, 1\].**

   - ***But `1.0 + 1e-15` may round to `1.0` in float64! Since 1e-15 \< eps/2 (eps ≈ 2.2e-16), 1.0 + 1e-15 rounds to 1.0 exactly... wait, eps = 2.2e-16, so 1.0 + 1e-15 where 1e-15 = 4.5 \* eps. So it's \> eps/2. The float64 representation: 1.0 is exact. Next float is 1 + 2.22e-16. Then 1 + 4.44e-16. Then 1 + 6.66e-16. So 1e-15 rounds to about 1 + 4.44e-16 or 1 + 6.66e-16... actually 1e-15 / 2.22e-16 ≈ 4.5, so 1 + 1e-15 ≈ 1 + 4.5 eps. Rounds to 1 + 4.5 eps or 1 + 5 eps depending on rounding. Should be \> 1. So arccos returns NaN. OK, test passes.**

***Let me verify: `1.0 + 1e-15 == 1.0` in float64? 1e-15 = 4.5036... \* eps. Not representable exactly. The nearest float to 1+1e-15 is 1 + 4eps or 1 + 5*eps? eps \* 4 = 8.88e-16, eps \* 5 = 1.11e-15. 1e-15 is between, closer to 1.11e-15. So rounds to 1 + 5\*eps ≈ 1.0000000000000011. That's \> 1. OK, arccos gives NaN. Test passes.**

***Actually I should verify with Python: `np.arccos(1.0 + 1e-15)` — actually in Python, `1.0 + 1e-15` = 1.0000000000000011 (assuming standard float64). arccos returns NaN with RuntimeWarning. Test asserts `isnan(result\_no\_clip\[0\])`. True. OK.**

5. ***Output / exit code: `sys.exit(1 if failed else 0)`. OK.**

***Overall file 7 looks OK. Minor naming inconsistency in test names but not a bug.**

## ***File 8: polydim\_triton\_kernel\_v26600.py**

1. ***`HAS\_TORCH`, `HAS\_TRITON` — proper checks. OK.**

2. ***`pmtp\_triton\_coalescent\_copy\_kernel`:**

   - ***Loads src, stores to dest. OK.**

   - ***But `src\_ptr`, `dest\_ptr` are `uint64` pointers. In Triton, `tl.load` with `mask` will not load masked-off elements. OK.**

3. ***`pmtp\_triton\_stiefel\_scale\_kernel`:**

   - ***Loads, multiplies by `inv\_sigma\_max`, stores. OK.**

4. ***`transfer`:**

   - ***`assert src.shape == dest.shape` — OK.**

   - ***Fallback CPU: `dest.copy\_(src)` — OK.**

   - ***For numpy: `dest\[:\] = src\[:\]` — OK.**

   - ***But `dest\[:\] = src\[:\]` — this requires `dest` to be a mutable ndarray. OK.**

5. ***`spectral\_scale`:**

   - ***For numpy: `return x \* inv\_sigma` — creates a new array. OK.**

   - ***For torch GPU: allocates `y = torch.empty\_like(x)` and fills. OK.**

   - ***For torch CPU: `x \* inv\_sigma`. OK.**

6. ***`self\_test`:**

   - ***Uses numpy only.**

   - ***`a = np.ones(1024) \* 42`, `b = np.zeros(1024)`.**

   - ***`engine.transfer(a, b)` — for numpy path, `b\[:\] = a\[:\]`. OK.**

   - ***`assert np.allclose(b, 42.0)`. OK.**

   - ***`scaled = engine.spectral\_scale(b, 0.5)` — for numpy, `b \* 0.5` = all 21.0. OK.**

   - ***`assert np.allclose(scaled, 21.0)`. OK.**

***Test passes. OK.**

7. ***Triton kernel compilation — the `BLOCK\_SIZE: tl.constexpr` annotation. OK.**

   - ***But `pid \* BLOCK\_SIZE` for grid launched with `triton.cdiv(n\_elements, BLOCK\_SIZE)` blocks. OK.**

   - ***Might trigger autotune or JIT compile on first call. Not used in tests except if torch+cuda present. The self\_test only uses numpy. OK.**

8. ***`PolydimTritonSlabEngine` — no slab management, just copy. The name is misleading. Not a bug per se.**

9. ***Bug: `spectral\_scale` returns a new array for numpy, but the name implies in-place scaling. For torch CPU, also returns new array. For torch GPU, allocates `y` and returns. So always new array. Name OK, maybe.**

10. ***The self\_test does not test the actual GPU path unless CUDA available. If not, only numpy path tested. For CI without GPU, the triton kernels are never exercised. OK.**

***Overall OK, minor issues.**

## ***File 9: readme\_first.md**

***This is documentation. Let me check claims:**

1. ***"Latencia de ~0.25 µs" vs the test showing "memcpy local: ~5.0 µs | PMTP Zero-Copy: ~8.0 µs". The readme says 0.25µs but actual test shows 8µs. Inconsistent. Maybe different hardware, but it's suspicious.**

2. ***"De ~12.8 ms (HTTP REST) a 0.25 µs" — 12.8 ms is HUGE. HTTP REST on localhost should be ~100µs-1ms, not 12.8 ms. Compare with the code's claim of "HTTP REST (localhost): ~12.825 µs" — that's 12.8 µs = 0.0128 ms, not 12.8 ms. So the readme says "12.8 ms" but the code says "12.825 µs". Unit mismatch in the readme. 1000× discrepancy.**

3. ***"Ganancia real sincera: 31.4× más rápido que HTTP REST" — 12.825 µs / 0.407 µs ≈ 31.5. Matches if PMTP is 0.407µs. But readme says 0.25µs and 8µs elsewhere. Inconsistent numbers. Doc needs cleanup.**

4. ***"2.5× más rápido que TCP local" — 1.006 / 0.407 ≈ 2.47. OK.**

5. ***"Bit 63: DESTROYING\_BIT (1ULL \<\< 63). ... Bits 32–62: Lectores activos en Slot 1. Bits 0–31: Lectores activos en Slot 0" — this matches Rust/Python but NOT the C++ (which uses unified counter). Inconsistent with C++. Already noted.**

6. ***"static\_assert en tiempo de compilación tanto en C++20 como en Dart, verificando que el offset de cada uno de los 12 campos sea idéntico bit a bit" — but Dart `static\_assert`... Dart doesn't have compile-time asserts for struct layout. The code uses `assert()` in `validatePmtpAbi()` which is runtime and disabled in release builds. False claim.**

7. ***The C++ and Rust/Dart layouts differ (as shown above). So the claim of "idéntico bit a bit" for offsets is FALSE for the WireHeader.**

8. ***"6 pruebas de regresión negativas" — but the actual test suite has 2 negative regression tests (dtype object, zero elements). Plus other positive tests. Inconsistent count with the claim of 6.**

***Let me count in `test\_03\_negative\_regressions`: 2 (dtype object, zero elements). Also DESTROYING\_BIT rejections in the code — but not tested in the suite. So "6 pruebas de regresión negativas" is unsupported.**

9. ***"Qwen2.5-0.5B con hash SHA-256 verificado, demostrando identidad de logits bit a bit" — no such test file in the delivery. Unverified claim.**

10. ***"Script reproducible que extrae capas reales desde model.safetensors de Qwen2.5-0.5B" — no such script in the delivered files. Missing artifact.**

11. ***"run\_silicon\_verification\_suite.py" — present. OK.**

12. ***"run\_all\_modules\_v26600.py" — present, runs 5 modules but the TESTS list has 5 items; but one of them, "teoria\_axiomas\_v26600.py", is present. So all 5 referenced scripts exist. OK.**

13. ***`readme\_first.md` says "python run\_silicon\_verification\_suite.py" as the master suite but "run\_all\_modules\_v26600.py" is the orchestrator. Slight inconsistency in instructions.**

## ***File 10: run\_all\_modules\_v26600.py**

1. ***The TESTS array — expects 5 modules. Items:**

   - ***`run\_silicon\_verification\_suite.py`**

   - ***`morpho\_redteam\_v26600.py`**

   - ***`polydim\_cla\_grassmann\_v26600.py`**

   - ***`teoria\_axiomas\_v26600.py`**

   - ***`polydim\_triton\_kernel\_v26600.py`**

***All present in the delivery. Good.**

2. ***`run\_test` uses `subprocess.run(\[PYTHON, test\["script"\]\], ...)` with `timeout=60`. OK.**

3. ***Status handling: `passed = (result.returncode == test\["expected\_exit"\])`. All expected\_exit = 0. OK.**

4. ***If any script fails, exit code 1. OK.**

5. ***Timeout — if a script takes \>60s, marks failed. Reasonable.**

## ***File 11: run\_silicon\_verification\_suite.py**

### ***test\_01\_atomic\_concurrency\_anti\_aba**

- ***`bus = PmtpShmBus(prefix="pmtp\_edu\_test")` — this creates a bus with a prefix.**

- ***`shm = bus.allocate\_tensor\_slab(slab\_id=0xBEEF, ...)` — allocates slab 0xBEEF (48975).**

- ***`v1 = np.ones(2048) \* 42`.**

- ***`publish\_snapshot\_atomic(slab\_id=0xBEEF, data=v1)` — active\_slot starts at 0, so target = 1. No readers on slot 1. Writes v1 to slot 1, swaps active to 1.**

- ***`slot\_leased, gen = acquire\_reader\_lease(slab\_id=0xBEEF)` — acquires slot 1 (active). Reader count for slot 1 becomes 1.**

- ***`v2 = np.ones(2048) \* 84`.**

- ***`publish\_snapshot\_atomic(slab\_id=0xBEEF, data=v2)` — active is 1, target = 0. Checks target\_readers (slot 0's readers) = 0. Writes v2 to slot 0, swaps active to 0.**

- ***`v3 = np.ones(2048) \* 126`.**

- ***`publish\_snapshot\_atomic(slab\_id=0xBEEF, data=v3, max\_retries=2)` — active is 0, target = 1. Checks target\_readers (slot 1's readers) = 1 (the leased reader). Retries then fails. Returns False. Test asserts `not overwritten`. Passes.**

- ***`release\_reader\_lease(slab\_id=0xBEEF, slot=slot\_leased)` — slot\_leased = 1 (the one acquired). Reader count for slot 1 becomes 0.**

- ***`publish\_snapshot\_atomic(slab\_id=0xBEEF, data=v3)` — active is 0, target = 1. target\_readers (slot 1) = 0. Writes v3 to slot 1, swaps active to 1. Returns True. Passes.**

***Test passes. BUT — the test uses `self.\_local\_lock` in Python. If this test was run with multiple processes, it would fail due to non-atomic writes. But single-process, it works because of the local lock.**

***Race bug: The `acquire\_reader\_lease` and `publish\_snapshot\_atomic` both take `self.\_local\_lock`. So within one process, they're serialized. But the C++ implementation uses real atomics. The Python code's local lock means it's not a genuine multi-process implementation.**

***The readme claims cross-process safety (multiple languages, shared memory). This test does not actually validate cross-process behavior. It's a single-process test masquerading as a concurrency test.**

### ***test\_02\_abi\_alignment\_128b**

- ***`WIRE\_FORMAT = "\<IHH16sQQQId32s36s"`, size 128. OK.**

- ***`HEADER\_COMPACT\_SIZE == 64`. OK.**

- ***No test of actual field semantic compatibility with C++ or Dart. Missed opportunity to catch the layout discrepancy.**

### ***test\_03\_negative\_regressions**

- ***`dtype=object` → raises TypeError. OK (assertion in `allocate\_tensor\_slab`).**

- ***`num\_elements=0` → raises ValueError. OK.**

- ***Passes.**

### ***test\_04\_dlpack\_zero\_copy**

- ***Requires PyTorch. If not present, returns True (SKIP). OK.**

- ***`bus.allocate\_tensor\_slab(slab\_id=0x9999, num\_elements=1024, dtype=np.float32)`.**

- ***`bus.publish\_snapshot\_atomic(slab\_id=0x9999, data=v)`.**

- ***`dl\_tensor = bus.get\_zero\_copy\_dlpack\_tensor(0x9999)` — returns numpy view.**

- ***`t = torch.from\_dlpack(dl\_tensor)` — consumes the numpy array as DLPack.**

  - ***Concern: numpy array `dl\_tensor` must be alive while `t` uses it. Since `dl\_tensor` is a local variable, it stays alive through the test. But if the DLPack protocol doesn't copy and requires the producer's buffer to stay alive, we're OK here. Actually torch.from\_dlpack consumes the producer's `\_\_dlpack\_\_` which usually requires the producer to keep the memory alive until the consumer's deleter is called. Since we don't call the deleter, the numpy array must stay alive. It does. OK.**

- ***`assert t.shape == (1024,)`. OK.**

- ***`t\[0\] = 777.0` — modifies the underlying buffer. OK.**

- ***`dl\_tensor\_2 = bus.get\_zero\_copy\_dlpack\_tensor(0x9999)` — new numpy view of same memory.**

- ***`t2 = torch.from\_dlpack(dl\_tensor\_2)`.**

- ***`assert t2\[0\].item() == 777.0`. Passes if truly zero-copy. OK.**

- ***Concern: If `torch.from\_dlpack` copies data (which it shouldn't for CPU tensors), the test would fail. In practice, torch.from\_dlpack for CPU shares memory. So OK.**

- ***Real concern: numpy's `\_\_dlpack\_\_` requires `stream` parameter handling and may not fully support shared memory (memoryview). But `np.ndarray(buffer=shm.buf, ...)` creates an array whose `\_\_dlpack\_\_` just exports the underlying buffer. Should work.**

### ***test\_05\_honest\_transport\_benchmark**

- ***`t\_memcpy` ~ 5µs (1000 iterations).**

- ***`t\_pmtp` ~ 8µs (1000 iterations).**

- ***Reports "PMTP is ~\{12800/t\_pmtp:.1f\}× faster". With t\_pmtp=8, that's 1600×. With t\_pmtp=0.25, that's 51200×. The readme claims 31.4×. Inconsistent numbers across docs. The claim is honest in labeling but the actual "HTTP REST ~12800 µs" number is questionable — HTTP localhost is typically ~50-1000 µs, not 12800 µs (12.8 ms).**

- ***Actually 12.8 ms = 12800 µs is very high for HTTP localhost. But maybe some frameworks are that slow. In any case, the comparison is cherry-picked. The readme says "Peras con Peras" but the HTTP number is suspicious.**

## ***File 12: teoria\_axiomas\_v26600.py**

### ***Test 1 (Isometry)**

- ***`W` 512×256 orthonormal (QR).**

- ***`z1 = W.T @ h1`, `u1 = z1 / norm`. OK.**

- ***`angle = arccos(clip(u1 @ u2, -1, 1))`.**

- ***`check('Isometry\_angle\_finite', ...)` — should be finite.**

- ***`check('Isometry\_angle\_in\_0\_pi', 0 \<= angle \<= pi)`. OK.**

- ***Passes.**

### ***Test 2 (Antipodal)**

- ***`canon = lambda v: v if v\[argmax(abs(v))\] \> 0 else -v`.**

- ***`check('Antipodal\_canon\_x\_eq\_canon\_neg\_x', allclose(canon(x), canon(neg\_x)))`.**

  - ***If `x\[argmax\] \> 0`, canon(x) = x, canon(-x) = -(-x) = x (since -x\[argmax\] \< 0). So canon(x) == canon(-x). OK.**

  - ***If `x\[argmax\] \< 0`, canon(x) = -x, canon(-x) = -x (since -x\[argmax\] \> 0). OK.**

  - ***Edge case: `x\[argmax\] == 0`. argmax on abs won't pick 0 unless all zeros, so OK.**

- ***`check('Antipodal\_canon\_unit\_norm', abs(norm - 1) \< 1e-14)`. OK.**

- ***Passes.**

### ***Test 3 (Lipschitz)**

- ***`W3` 64×64 orthonormal.**

- ***`u1\_n = W3.T @ h1\_n`, `u1\_n /= max(rho1, eps)`.**

- ***`lip\_bound = 2 \* σ\_min(W3) / max(min(rho1, rho2), eps)`.**

  - ***Wait — for an orthonormal W3, σ\_min(W3) = 1. So lip\_bound = 2/max(min(rho1,rho2), eps). With rho ~ sqrt(64) = 8 (for standard normal h), lip\_bound = 2/8 = 0.25. But then `check('Lipschitz\_direction\_diff\_bounded', norm(u1\_n - u2\_n) \<= 2.0)`.**

  - ***Actually the check is just `\<= 2.0`, which is trivially true for unit vectors. OK.**

  - ***Conceptual issue: The Lipschitz bound is stated as `2 \* σ\_min / min(rho)` but the actual bound should use σ\_max, not σ\_min. The Lipschitz constant of the map `h → normalize(W^T h)` is roughly `||W|| / rho = σ\_max / rho` (not σ\_min). Actually more carefully, the derivative of normalization is ~1/rho \* (I - uu^T), which has norm 1/rho. So the Lipschitz constant is `σ\_max(W) / rho`. Using `σ\_min` is wrong — should be `σ\_max`.**

- ***With σ\_max = 1 (orthonormal), σ\_min = 1 (also for square orthonormal). So for this specific test, σ\_max == σ\_min and the formula gives the same result. So the bug is masked. But conceptually wrong.**

- ***Actually, for rectangular W (D×r) with orthonormal columns, σ\_max = σ\_min = 1. So the test W3 is 64×64 orthonormal, both σ = 1. So no visible bug. But if W were rectangular or non-orthonormal, the test would be misleading. The test doesn't catch the conceptual error.**

### ***Test 4 (Neumaier)**

- ***`v = np.full(65536, 1/sqrt(65536))`.**

- ***`norm\_sq\_err = abs(sum(v\*\*2) - 1.0)`.**

- ***Problem: `sum(v\*\*2)` uses numpy's `np.sum`, not the Neumaier accumulator! The test is about Neumaier but uses `np.sum`. So it's testing numpy's accuracy, not Neumaier's.**

- ***Numpy's `np.sum` uses pairwise summation, quite accurate. For uniform array of 1/256 ≈ 0.0039, sum of 65536 of them, no overflow issue. `norm\_sq\_err` would be small (~1e-15). So test passes but doesn't test Neumaier at all.**

- ***To test Neumaier, should use `NeumaierAccumulator` or the compensation logic. Bug: test is a no-op w.r.t. Neumaier.**

***Actually the variable name `norm\_sq\_err` suggests it's checking squared norm error. But the check is `abs(sum(v\*\*2) - 1) \< 1e-12`. If `v\*\*2` sums to 1, then norm² = 1, norm = 1. OK, correct assertion but doesn't use Neumaier.**

### ***Test 5 (Pre-scaling)**

- ***`X\_raw` 256×64.**

- ***`Y0 = X\_raw / σ\_max(X\_raw)`. OK.**

- ***`defect = max(|Y0.T Y0 - I|)` — this should be \< 1 (spectral norm ≤ 1). OK.**

- ***Passes.**

### ***Test 6 (Newton-Schulz convergence)**

- ***Applies Newton-Schulz polynomial:**

- ***python**

- ```
***poly = I + 0.5\*A + 0.375\*A^2 + 0.3125\*A^3 + (35/128)\*A^4**

- ***Y0 = Y0 @ poly**
```

- ***Where A = I - Y^T Y.**

- ***Let me verify the coefficients. The order-5 Newton-Schulz for X → (I + 0.5 A + 0.375 A^2 + 0.3125 A^3 + 0.2734375 A^4) X with A = I - X^T X.**

  - ***0.2734375 = 35/128. So (35/128)\*A^4 is correct.**

- ***Loop up to 8 iterations. Breaks when defect \< 1e-14.**

- ***Final defect \< 1e-12. Should converge.**

- ***Concern: For Y0 starting close to orthonormal (σ\_max-scaled), A is small, so one iteration should suffice. Convergence is quick. OK.**

***Overall the test suite runs. Main issues: test 4 (Neumaier) doesn't actually test Neumaier.**

## ***Summary of Major Bugs**

***Let me prioritize:**

### ***Critical Bugs:**

1. ***C++ `pmtp\_shm\_publish\_atomic` does NOT check target-slot readers — allows overwriting leased slots. Violates T-MP17/MP-48 guarantee. The comment claims it does, but the code doesn't.**

2. ***ABI mismatch between C++/Python and Rust/Dart on `PolydimWireHeader` — 3 fields have different meanings at the same offsets (timestamp\_ns/dimension\_d/rank\_k vs num\_elements/payload\_bytes/timestamp\_ns). The claim of "paridad bit a bit" is false.**

3. ***C++ `acquire\_lease` uses unified counter (increments by 1), but Python/Rust/Dart use per-slot counters (increment by 1 or 2^32). Incompatible cross-language. And Python's `publish\_snapshot\_atomic` checks per-slot readers, while C++'s doesn't. So they can't interoperate safely.**

4. ***Python `PmtpShmBus` is NOT actually atomic across processes — it uses `self.\_local\_lock` (Python thread lock, process-local) for its reads/writes to shared memory. So multiple processes would race. The claims of "leases atómicos" and "cero torn-reads" are false for cross-process use. The test suite only validates single-process behavior.**

5. ***C++ `acquire\_lease` and `release\_lease` don't handle slot-specific readers correctly — the counter is global, so a reader who acquired slot 0's lease and a publisher for slot 1 are conflated. The protection is weaker than claimed.**

6. ***Python `pmtp\_shm\_close` in C++ uses Windows-only `Sleep` without `\#ifdef \_WIN32`. Won't compile on Linux. Portability bug.**

7. ***Rust `newton\_schulz\_ord5\_retract` is a no-op — it measures defect but never applies any update. Misleading name and docstring. Compare Python's `polydim\_triton\_kernel` which correctly applies the polynomial.**

8. ***CUDA `warp\_reduce\_neumaier\_norm` returns inconsistent values across lanes — the function is used as if it returns a scalar, but each lane gets a different value because Neumaier accumulation order differs per lane. Should broadcast lane 0's result: `sum = \_\_shfl\_sync(mask, sum + comp, 0);`.**

9. ***CUDA `pmtp\_cuda\_newton\_schulz\_ord5\_kernel` does NOT implement Newton-Schulz — it's just a scalar pre-scale. Misleading name.**

10. ***CUDA kernel with `grid.sync()` requires cooperative launch — no such launch mechanism shown, and the `extern "C"` launcher doesn't actually launch. So this code, if used as-is, would produce a runtime error or silently fail.**

11. ***Dart FFI bindings don't match C++ signatures — `PmtpShmCreateNative` has different args, `PmtpShmAcquireLeaseNative` has value vs pointer params, `PmtpShmReleaseLeaseNative` expects Int32 return but C++ returns void. Broken bindings.**

12. ***Rust `acquire\_reader\_lease` overflow risk — using `1\<\<32` for slot 1 counter means the slot 1 counter overflows at 2^31 and carries into DESTROYING\_BIT. Theoretical but real.**

13. ***Python `read\_tensor(verify\_stiefel=True)` default contradicts `publish\_tensor` — publishing non-unit vectors then reading raises ValueError. Inconsistent default.**

14. ***Readme claims are inconsistent:**

    - ***"0.25 µs" vs "8.0 µs" in code.**

    - ***"12.8 ms" vs "12.825 µs" — 1000× unit error.**

    - ***"6 pruebas de regresión negativas" vs 2 in code.**

    - ***"Qwen2.5 artifact" and "SHA-256 hash" — no such artifact or test.**

    - ***"static\_assert en Dart" — Dart has no compile-time struct asserts; `assert()` is runtime and disabled in release.**

15. ***CUDA launcher `pmtp\_cuda\_launch\_persistent\_grid\_simulation` doesn't launch anything — just validates params. Misleading.**

16. ***Teoria\_axiomas Test 4 (Neumaier) uses `np.sum` instead of Neumaier accumulator — doesn't actually test Neumaier.**

17. ***Teoria\_axiomas Test 3 uses σ\_min instead of σ\_max in Lipschitz bound. Masked because W3 is orthonormal (σ\_min == σ\_max). Conceptual error.**

### ***Minor Bugs / Improvements:**

18. ***`morpho\_redteam\_v26600.py` — `test\_bridge\_spherical\_noop` "good" path is trivial (uses z\_unit twice).**

19. ***`polydim\_triton\_kernel\_v26600.py` — fallback CPU path for numpy doesn't handle dtype/shape mismatch beyond shape. Minor.**

20. ***`run\_silicon\_verification\_suite.py` — `test\_05` HTTP REST comparison number (12800 µs) is cherry-picked and contradicts other docs.**

21. ***`\_slabs` property is unused (dead code, though documented as "compatibilidad con inspección Red Team").**

22. ***`max\_dim`, `lease\_timeout\_ms` in `PmtpShmBus.\_\_init\_\_` are unused/marginally used.**

23. ***`pmtp\_shm\_create` in C++ uses `new` but `pmtp\_shm\_open` also uses `new` with `create\_or\_open(name, ..., false)` — if create\_or\_open fails to find existing shm, returns nullptr. OK. But if create\_or\_open internally "opens" but doesn't verify size, no check.**

24. ***In Python `publish\_tensor`, `self.\_next\_slab\_seq % max(1, self.max\_slabs) + 1` — if `max\_slabs=1`, always returns 1 (after modulo, is 0 or 1; +1 gives 1 or 2, but modulo of any number by 1 is 0, so always 1). Edge case minor.**

25. ***In `PmtpHeaderCompact::acquire\_reader\_lease`, the returned `Ok(self.generation as u64)` is best-effort (no synchronization with active\_slot read), could return stale generation. Minor.**

26. ***`pmtp\_shm\_close` sets DESTROYING and drains but does NOT unlink on Linux (would need `shm\_unlink`). Handled by OS on last close typically, but explicit unlink might leak. Depends on `PmtpWinShmBlock::close()` — not shown.**

***Actually wait — let me re-look at whether Python is more correct than C++ on the per-slot tracking.**

***Python `publish\_snapshot\_atomic`:**

***python**

```
***target\_readers = (hdr.state\_and\_readers \>\> 32) & 0x7FFFFFFF if target\_slot == 1 else (hdr.state\_and\_readers & 0xFFFFFFFF)**
```

***This says: if target is slot 1, check bits 32-62 (readers of slot 1); else check bits 0-31 (readers of slot 0). Correct for a per-slot scheme.**

***Python `acquire\_reader\_lease`:**

***python**

```
***inc = 1 if slot == 0 else (1 \<\< 32)**
```

***Adds to slot 0's or slot 1's counter.**

***Python `release\_reader\_lease`:**

***python**

```
***r0 = hdr.state\_and\_readers & 0xFFFFFFFF**

***r1 = (hdr.state\_and\_readers \>\> 32) & 0x7FFFFFFF**

***if slot == 0: r0 = max(0, r0 - 1)**

***else: r1 = max(0, r1 - 1)**
```

***Correct.**

***BUT the "atomicity" of these operations relies on `self.\_local\_lock` — process-local. Cross-process, they're not atomic. So the "atómico" claim is false for cross-process.**

***C++ `pmtp\_shm\_publish\_atomic`:**

***cpp**

```
***uint32\_t current\_active = hdr-\>active\_slot;**

***uint32\_t target\_slot = 1 - current\_active;**

***void\* target\_dest = ...;**

***std::memcpy(target\_dest, data, ...);  // no check!**
```

***Does not check target slot readers. Critical bug.**

***C++ `pmtp\_shm\_acquire\_lease`:**

***cpp**

```
***uint64\_t current = atomic\_sr-\>load(...);**

***while (true) \{**

    ***if (current & PMTP\_DESTROYING\_BIT) return 0;**

    ***if (atomic\_sr-\>compare\_exchange\_weak(current, current + 1, ...)) break;**

***\}**
```

***Uses unified counter (not per-slot). Semantic difference from Python. If a slab is shared between C++ and Python, the counters would be inconsistent.**

***C++ `pmtp\_shm\_release\_lease`:**

***cpp**

```
***uint64\_t active\_readers = current & PMTP\_READERS\_MASK;**

***if (active\_readers == 0) break;**

***uint64\_t next = (current & PMTP\_DESTROYING\_BIT) | (active\_readers - 1);**
```

***Subtracts from unified counter. Consistent with C++ acquire.**

***So within C++, the counter is unified. Within Python, per-slot. Different semantics for the SAME shared memory layout (offset 48 in compact header). If both C++ and Python touch the same slab, they'd corrupt each other's counters.**

***This is a significant ABI incompatibility that isn't documented.**

***Actually wait — the Readme (English translation) says "Bits 32–62: readers\_slot1 | Bits 0–31: readers\_slot0". So the intended ABI IS per-slot (matching Python and Rust). But the C++ implementation doesn't follow it. So the C++ is buggy (doesn't match the documented ABI).**

***OK.**

### ***Additional concern: `PmtpHeaderCompact` in Rust — does `align(64)` interfere with `repr(C)` field layout?**

***Let me check Rust's `\#\[repr(C, align(64))\]`:**

- ***`repr(C)` = C-like field layout with padding to natural alignment.**

- ***`align(64)` = forces the struct to be 64-byte aligned.**

***For a struct with `AtomicU64` at offset 48 (natural 8-byte aligned), `\[u8; 8\]` at offset 56, total 64. With align(64), the struct starts at 64-byte boundary, size 64. Correct.**

***BUT — could there be intermediate padding? For example, `\[u8;8\]` at offset 56 works fine. No padding between fields. Good.**

***Actually wait — let me recount Rust's compact header fields with repr(C) natural alignment:**

- ***magic: u32 @ 0**

- ***version: u16 @ 4**

- ***dtype\_id: u16 @ 6**

- ***active\_slot: u32 @ 8**

- ***slab\_id: u32 @ 12**

- ***num\_elements: u64 @ 16**

- ***timestamp\_ns: u64 @ 24**

- ***scale: f64 @ 32**

- ***generation: u32 @ 40**

- ***retired\_slot0: u8 @ 44**

- ***retired\_slot1: u8 @ 45**

- ***reserved\_flags: u16 @ 46**

- ***state\_and\_readers: AtomicU64 @ 48**

- ***reserved\_pad: \[u8; 8\] @ 56**

- ***Total: 64.**

***Hmm, wait — `u16` fields (version @ 4, dtype\_id @ 6) — 4 + 2 = 6, 6 + 2 = 8. So active\_slot @ 8. OK.  
`u32` (active\_slot @ 8), `u32` (slab\_id @ 12) — 8 + 4 = 12, 12 + 4 = 16. So num\_elements @ 16. OK.  
`u64` (num\_elements @ 16) — but 16 is 8-aligned. OK.  
After all fields: offset 56 + 8 = 64. So struct size = 64 without align(64). With align(64), still 64. OK.**

***Good, so `PmtpHeaderCompact` is 64 bytes.**

### ***Now the Python `WIRE\_HEADER\_128B\_FORMAT = "\<IHH16sQQQId32s36s"` — let me double check semantics:**

***Fields in order: magic, version, flags, slab\_id(16), timestamp\_ns(8), dimension\_d(8), rank\_k(8), dtype(4), stiefel\_defect(8), signature(32), reserved(36).**

***But the C++ `PolydimWireHeader` has:**

- ***magic, version, flags, slab\_id(16), timestamp\_ns, dimension\_d, rank\_k, dtype, stiefel\_defect, signature\_blake2s(32), reserved(36).**

***Matches. Good.**

***But the Dart/Rust have:**

- ***magic, version\_major, version\_minor, slab\_uuid(16), num\_elements, payload\_bytes, timestamp\_ns, dtype, stiefel\_defect, blake2s\_hash(32), reserved(36).**

***Different field semantics at same offsets. Confirmed ABI mismatch.**

### ***Python `WIRE\_DESCRIPTOR\_FORMAT = "\<IHHIIQQdIHH??HIIIIIQ32s8s"` — matches C++ struct:**

***Let me verify C++ `pmtp\_wire\_descriptor\_120b\_t`:**

- ***magic(4) @ 0**

- ***version(2) @ 4**

- ***dtype\_id(2) @ 6**

- ***active\_slot(4) @ 8**

- ***slab\_id(4) @ 12**

- ***num\_elements(8) @ 16**

- ***timestamp\_ns(8) @ 24**

- ***scale(8) @ 32**

- ***generation(4) @ 40**

- ***readers\_slot0(2) @ 44**

- ***readers\_slot1(2) @ 46**

- ***retired\_slot0(1) @ 48**

- ***retired\_slot1(1) @ 49**

- ***state(2) @ 50**

- ***batch\_size(4) @ 52**

- ***seq\_len(4) @ 56**

- ***dim\_source(4) @ 60**

- ***dim\_latent(4) @ 64**

- ***flags(4) @ 68**

- ***reserved\_ext(8) @ 72**

- ***blake3\_hash(32) @ 80**

- ***padding\_ext(8) @ 112**

***Total 120. Python matches. Good.**

### ***Concern: `pmtp\_shm\_bus\_v26600.py`'s `HEADER\_COMPACT\_STRUCT` state\_and\_readers**

***Format `\<IHHIIQQdI??HQ8s`:**

- ***`I` magic**

- ***`H` version**

- ***`H` dtype\_id**

- ***`I` active\_slot**

- ***`I` slab\_id**

- ***`Q` num\_elements**

- ***`Q` timestamp\_ns**

- ***`d` scale**

- ***`I` generation**

- ***`?` retired\_slot0**

- ***`?` retired\_slot1**

- ***`H` reserved\_flags**

- ***`Q` state\_and\_readers**

- ***`8s` reserved**

***Compare C++ `pmtp\_header\_compact\_t`:**

- ***magic @ 0 (uint32)**

- ***version @ 4 (uint16)**

- ***dtype\_id @ 6 (uint16)**

- ***active\_slot @ 8 (uint32)**

- ***slab\_id @ 12 (uint32)**

- ***num\_elements @ 16 (uint64)**

- ***timestamp\_ns @ 24 (uint64)**

- ***scale @ 32 (double)**

- ***generation @ 40 (uint32)**

- ***retired\_slot0 @ 44 (uint8)**

- ***retired\_slot1 @ 45 (uint8)**

- ***reserved\_flags @ 46 (uint16)**

- ***state\_and\_readers @ 48 (uint64)**

- ***reserved @ 56 (8 bytes)**

***Matches. Good.**

### ***Concern: `run\_silicon\_verification\_suite.py` `test\_01` — release\_reader\_lease(slot=slot\_leased)**

***But `slot\_leased` is from `acquire\_reader\_lease` return. The acquire reads `hdr.active\_slot` (the current active at acquire time). Then later, after publishing v2 (which swaps active from 1 to 0), the release uses `slot=1` (the leased slot). Release decrements slot 1's counter. Correct.**

***But `acquire\_reader\_lease` reads the header and increments the counter. Between read and write... but under `self.\_local\_lock`, atomic within process. OK.**

***Actually looking more carefully at the lease flow in Python:**

***python**

```
***def acquire\_reader\_lease(self, slab\_id, max\_retries=50, retry\_delay\_s=0.0003):**

    ***shm = self.slabs\[slab\_id\]\["shm"\]**

    ***for \_ in range(max\_retries):**

        ***with self.\_local\_lock:**

            ***hdr = self.read\_header(slab\_id)**

            ***if hdr.state\_and\_readers & (1 \<\< 63):**

                ***raise RuntimeError(...)**

            ***slot = hdr.active\_slot**

            ***is\_retired = hdr.retired\_slot1 if slot == 1 else hdr.retired\_slot0**

            ***if is\_retired:**

                ***continue  \# retry**

            ***inc = 1 if slot == 0 else (1 \<\< 32)**

            ***new\_sr = hdr.state\_and\_readers + inc**

            ***new\_header\_bytes = HEADER\_COMPACT\_STRUCT.pack(...)**

            ***shm.buf\[:HEADER\_COMPACT\_SIZE\] = new\_header\_bytes**

            ***return slot, hdr.generation**

        ***time.sleep(retry\_delay\_s)**
```

***Wait — the `continue` inside `with self.\_local\_lock` then `time.sleep(retry\_delay\_s)` is OUTSIDE the `with` block (since `continue` restarts the for loop, and the sleep is at the end). Actually no — the `time.sleep` is after the `with` block in the loop body, and `continue` restarts the loop iteration, so `time.sleep` is skipped on `continue`. Hmm:**

***python**

```
***for \_ in range(max\_retries):**

    ***with self.\_local\_lock:**

        ***...**

        ***if is\_retired:**

            ***continue  \# \<-- skips to next iteration**

        ***...**

        ***return slot, hdr.generation**

    ***time.sleep(retry\_delay\_s)  \# \<-- only reached if 'with' body finishes without continue/return**
```

***So on `is\_retired`, `continue` restarts immediately without sleep. Busy loop, but bounded by max\_retries=50. Minor performance concern.**

***And `time.sleep` is only reached if the `with` block completes without continue or return. Since there's always a return or continue, `time.sleep` after the `with` block is unreachable code. Actually wait — if `is\_retired` is false, code proceeds to pack and return. If `is\_retired` is true, continue. So no path reaches `time.sleep`. Dead code / bug. The intent was probably to sleep between retries.**

***Actually let me re-read:**

***python**

```
***for \_ in range(max\_retries):**

    ***with self.\_local\_lock:**

        ***hdr = self.read\_header(slab\_id)**

        ***if hdr.state\_and\_readers & (1 \<\< 63):**

            ***raise RuntimeError(...)**

        ***slot = hdr.active\_slot**

        ***is\_retired = hdr.retired\_slot1 if slot == 1 else hdr.retired\_slot0**

        ***if is\_retired:**

            ***continue**

        ***inc = 1 if slot == 0 else (1 \<\< 32)**

        ***new\_sr = hdr.state\_and\_readers + inc**

        ***new\_header\_bytes = HEADER\_COMPACT\_STRUCT.pack(...)**

        ***shm.buf\[:HEADER\_COMPACT\_SIZE\] = new\_header\_bytes**

        ***return slot, hdr.generation**

    ***time.sleep(retry\_delay\_s)**
```

***The `time.sleep` is inside the for-loop but outside the `with`. Since the `with` block always returns or continues, we never reach `time.sleep`. Yes, dead code.**

***Hmm, but this is the same pattern used in `publish\_snapshot\_atomic`:**

***python**

```
***for \_ in range(max\_retries):**

    ***with self.\_local\_lock:**

        ***...**

        ***if target\_readers \> 0:**

            ***time.sleep(retry\_delay\_s)**

            ***continue**

        ***...**

        ***return True**

    ***time.sleep(retry\_delay\_s)**
```

***Here `time.sleep` is called INSIDE the `with` block for the readers \> 0 case (holds the lock while sleeping — bad!). And also after the `with` block (unreachable). Worse bug — sleeping while holding the lock, blocking other threads.**

***Actually, sleeping inside `self.\_local\_lock` blocks all other threads in this process, defeating the purpose of a fine-grained lease.**

***Bug: `publish\_snapshot\_atomic` sleeps while holding `self.\_local\_lock`, which is bad concurrency practice and could cause contention or starvation.**

### ***Also, `publish\_snapshot\_atomic` returns `False` if `state\_and\_readers & (1 \<\< 63)`. But there's no way to distinguish "destroying" from "readers busy". Both fail. Minor.**

***OK, I have a comprehensive list. Let me also check the README and organization.**

### ***In `polydim\_triton\_kernel\_v26600.py`:**

***Actually, the `transfer` method for numpy:**

***python**

```
***elif isinstance(src, np.ndarray) and isinstance(dest, np.ndarray):**

    ***dest\[:\] = src\[:\]**

    ***return True**
```

***If src has different dtype than dest, numpy may raise. Not caught. Minor.**

***And in `spectral\_scale`, for numpy returns `x \* inv\_sigma` — new array. Doesn't modify in place. Name "spectral\_scale" OK.**

### ***Also in `run\_all\_modules\_v26600.py`:**

***`subprocess.run` with `capture\_output=True, text=True, timeout=60`. If a script hangs on file lock (e.g., shared memory not cleaned up), 60s timeout fires. But shm cleanup issues could leave stale shm files. Minor.**

### ***`readme\_first.md` claims "run\_silicon\_verification\_suite.py" takes \<15s and shows 5/5 PASS. Actually the 5 tests run. Good.**

***But claims "Qwen2.5" test that isn't there. And "6 pruebas de regresión". And "static\_assert en Dart". These are false claims.**

***OK, I have enough. Let me write this up clearly and organized.**

***Let me also double-check: does the C++ `pmtp\_shm\_acquire\_lease` return the correct slot?**

***cpp**

```
***PMTP\_API int pmtp\_shm\_acquire\_lease(pmtp\_handle\_t handle, uint32\_t\* out\_slot, uint32\_t\* out\_gen) \{**

    ***...**

    ***// CAS loop increments unified counter**

    ***...**

    ***uint32\_t slot = hdr-\>active\_slot;**

    ***\*out\_slot = slot;**

    ***\*out\_gen = hdr-\>generation;**

    ***return 1;**

***\}**
```

***After CAS increment, reads `hdr-\>active\_slot`. If another thread is concurrently publishing (swapping slot), `active\_slot` might change. But `hdr-\>active\_slot` is a plain `uint32\_t` write (not atomic). The publisher writes `hdr-\>active\_slot = target\_slot;` — this is not atomic. So reading it here could tear on non-x86 platforms. On x86 (with strong memory model), it wouldn't tear, but compiler reordering could be an issue. Potential race, unaligned access, missing atomic.**

***Also, the release:**

***cpp**

```
***PMTP\_API void pmtp\_shm\_release\_lease(pmtp\_handle\_t handle, uint32\_t slot) \{**

    ***...**

    ***uint64\_t active\_readers = current & PMTP\_READERS\_MASK;**

    ***if (active\_readers == 0) break;  // early exit, no decrement**

    ***...**

***\}**
```

***If `active\_readers == 0`, doesn't decrement (would underflow). But if there was a legitimate acquire followed by an erroneous release with no acquire, this silently ignores. Minor safety.**

***But if two concurrent releases of different readers happen, one might see active\_readers=0 and skip, causing underflow detection. OK.**

***If a release is called for slot 0 but the reader actually acquired slot 1 (unified counter semantics), there's no per-slot distinction, so it just decrements. Consistent with acquire (unified). OK.**

***Alright, my list of bugs is comprehensive. Let me organize the response.**

***Actually let me look at one more thing: the "warp\_neumaier\_accumulate" bug.**

***cpp**

```
***\_\_device\_\_ inline void warp\_neumaier\_accumulate(**

    ***double& sum, double& compensation, double val**

***) \{**

    ***double t = sum + val;**

    ***if (fabs(sum) \>= fabs(val)) \{**

        ***compensation += (sum - t) + val;**

    ***\} else \{**

        ***compensation += (val - t) + sum;**

    ***\}**

    ***sum = t;**

***\}**


***\_\_device\_\_ inline double warp\_reduce\_neumaier\_norm(double val, unsigned int mask = 0xffffffff) \{**

    ***double sum = val;**

    ***double comp = 0.0;**

    ***for (int offset = 16; offset \> 0; offset /= 2) \{**

        ***double other = \_\_shfl\_down\_sync(mask, sum, offset);**

        ***warp\_neumaier\_accumulate(sum, comp, other);**

    ***\}**

    ***return sum + comp;**

***\}**
```

***For lane 0 in a 32-warp: offset=16, lane 0 gets lane 16's sum. Then offset=8, gets lane 8's (partial). Etc. Lane 0 accumulates correctly, but so do all other lanes (each with their own subset). The final `sum + comp` differs by lane. Only lane 0's value is the "complete" sum. Should broadcast: `double total = \_\_shfl\_sync(mask, sum + comp, 0); return total;`.**

***Yes, this is a bug for the intended semantic of "return the warp-reduced sum".**

***Also there's no test in the CUDA code, so this bug is dormant. But if used, it would produce incorrect results for non-zero lanes.**

***Let me also note: even after broadcasting, Neumaier reduction across lanes is not truly "Neumaier" of the total because the compensation `comp` is not communicated. Better approach: do two-stage reduction (first sum, then compensation, or use a different compensated reduction). But at least broadcasting lane 0's `sum+comp` gives the correct total for lane 0's view.**

***Actually another issue: `warp\_neumaier\_accumulate` computes compensation for lane 0's accumulation of lanes 16, 8, 4, 2, 1 — that's the accumulation of 5 other values plus the initial. But the compensation accumulates rounding error in this specific sequence. This is a reasonable Neumaier-style computation, but the compensation isn't communicated between the pairing steps in a fully-correct Neumaier two-sum way. Actually, the standard "Neumaier summation in a warp" is a known tricky pattern. For the returned value from lane 0, it's "close" to correct. This is a nuance but not "wrong".**

***Alright.**

***One more check: `pmtp\_cuda\_persistent\_recurrent\_kernel` — `num\_steps=0` loops zero times, fine. `dim\_latent=0` — the guard `if (tid \< dim\_latent)` is false, so no work. But `grid.sync()` is still called. OK.**

***`projection\_weights\[tid % dim\_latent\]` — if dim\_latent=0, but we only enter the if when tid \< dim\_latent, so dim\_latent \> 0. OK.**

***`state\_slab\[tid\]` — same. OK.**

***If `dim\_latent \> total\_threads`, only total\_threads entries get updated, remaining stay unchanged. Bug? The function claims to update `dim\_latent` elements but only updates total\_threads. Potential bug if the grid isn't large enough. But the caller would need to ensure grid size covers dim\_latent. No check. Minor.**

***`num\_steps = 100000` (claimed "hasta 100k steps") — with `grid.sync()` per step, this is 100000 global barriers. Each barrier on a moderate GPU takes maybe ~1-10 µs. Total 100ms-1s. Reasonable but slow. The "SRAM L1" claim — actually state\_slab is in DRAM (global memory), not SRAM. Only registers/L1 are SRAM. And each step re-reads from DRAM. False claim about SRAM residency. Actual behavior: DRAM-resident, not SRAM.**

***Actually if the array fits in L2 cache (~40MB on modern GPUs) and dim\_latent \* 8 bytes \< L2, it could be L2-resident, but not L1-resident. And the claim "confinado a registros y SRAM L1" is false.**

***OK, this is enough. Let me draft the response.**

***Actually, let me reconsider the C++ publish bug once more with fresh eyes:**

***cpp**

```
***PMTP\_API int pmtp\_shm\_publish\_atomic(pmtp\_handle\_t handle, const double\* data, uint64\_t num\_elements) \{**

    ***if (!handle || !data) return 0;**

    ***auto\* ctx = reinterpret\_cast\<PmtpNativeContext\*\>(handle);**


    ***std::lock\_guard\<std::mutex\> lock(ctx-\>mtx);**

    ***pmtp\_header\_compact\_t\* hdr = ctx-\>block.get\_header();**


    ***auto\* atomic\_sr = reinterpret\_cast\<std::atomic\<uint64\_t\>\*\>(&hdr-\>state\_and\_readers);**

    ***uint64\_t current\_sr = atomic\_sr-\>load(std::memory\_order\_acquire);**

    ***if (current\_sr & PMTP\_DESTROYING\_BIT) \{**

        ***return 0;**

    ***\}**


    ***uint32\_t current\_active = hdr-\>active\_slot;**

    ***uint32\_t target\_slot = 1 - current\_active;**


    ***// "Si hay lectores activos en el sistema, aseguramos que la conmutación respete exclusión"**

    ***void\* target\_dest = ctx-\>block.get\_payload\_slot(target\_slot, ctx-\>payload\_bytes);**

    ***std::memcpy(target\_dest, data, ctx-\>payload\_bytes);**


    ***hdr-\>active\_slot = target\_slot;**

    ***hdr-\>generation++;**

    ***...**

***\}**
```

***The comment claims exclusion, but there's no check of `current\_sr & PMTP\_READERS\_MASK` for the target slot. The memcpy happens unconditionally. This is a clear bug. The MP-48 counterexample (torn-read) is exactly what this would allow, despite claims otherwise.**

***Comparing with the Python implementation which does:**

***python**

```
***target\_readers = ... **

***if target\_readers \> 0:**

    ***time.sleep(retry\_delay\_s); continue**
```

***So Python correctly implements the exclusion, C++ doesn't. Big finding.**

***Now, would the C++ version ever be tested in this delivery? The `run\_silicon\_verification\_suite.py` only uses Python. So the C++ bug isn't caught by tests. But it's in the delivered code, and any user relying on it would hit the bug.**

***Let me also confirm: the Python `\_local\_lock` doesn't make the test cross-process, but the test only uses one process. So the test passes.**

***Alright, comprehensive enough. Let me write it up.**

***I should also note the `test\_bridge\_spherical\_noop` — actually rereading:**

***python**

```
***h = np.array(\[6., 8., 4.\])**

***z\_raw = W.T @ h  \# \[6, 8\]**

***z\_unit = z\_raw / np.linalg.norm(z\_raw)  \# \[0.6, 0.8\]**

***z\_after\_unchanged = z\_unit.copy()**


***h\_bad = h + W @ (z\_after\_unchanged - z\_raw)**

***\# = h + W @ (\[0.6,0.8\] - \[6,8\]) = h + W @ \[-5.4, -7.2\]**

***\# = h + \[-5.4, -7.2, 0\] = \[0.6, 0.8, 4\]**

***assert not np.array\_equal(h\_bad, h)  \# True**


***rho = np.linalg.norm(z\_raw)  \# 10**

***h\_good = h + W @ (rho \* (z\_after\_unchanged - z\_unit))**

***\# z\_after\_unchanged == z\_unit, so delta = 0**

***\# h\_good = h + 0 = h**

***assert np.array\_equal(h\_good, h)  \# True**
```

***The "good" path is trivial (delta = 0 → h unchanged). But this is a test of a specific* property: that when the "injection" is a no-op (u\_new == u\_old), h is preserved. That's actually a reasonable test of the "beta=0" case (where delta must be zero, not some fake value). It's testing that the identity element of the update doesn't change h.**

***But the "bad" path shows what happens if you mistakenly use delta = z\_unit - z\_raw instead of delta = rho \* (z\_unit - z\_unit) = 0. So the two cases show: "doing the wrong thing breaks", "doing the right thing (trivially) works". OK.**

***Actually, the "right thing" case is trivial. A better test would test `h\_new = h + W @ (rho \* (u\_new - u\_old))` with `u\_new != u\_old` and verify that the resulting h has projection onto W equal to `rho \* u\_new`. But that's a different test.**

***The current test is: `rho \* (u\_new - u\_old)` with u\_new = u\_old. Trivially 0.**

***Actually the intended test was probably: verify that the "correct" formula works for a non-trivial case, but the "good" path uses the same variable, so it's trivial. So the test is misleadingly named. Minor.**

***OK, writing it up now.**

***Wait — one more thing. Let me check the morpho test that asserts `observed not in ((10, 10), (30, 30), (40, 40))`. `observed = (10, 40)`. Not in those. True. OK.**

***Alright, drafting response.**

***Let me also do one final check on the offset of `state\_and\_readers` in `pmtp\_header\_compact\_t` with `\#pragma pack(1)` and `alignas(64)`.**

***Actually, `alignas(64)` on a struct with `\#pragma pack(1)`: In MSVC, `alignas` combined with `\#pragma pack` — pack overrides member alignment but the struct-level alignment from alignas should still be respected. So `sizeof` = 64 (no tail padding since all fields sum to 64), alignment 64. OK.**

***But GCC/Clang: `\#pragma pack(1)` followed by `alignas(64)` — the struct's alignment is 64, and member alignment is 1 (packed). Size = round\_up(64, 64) = 64. But some compilers might warn.**

***Hmm — actually, will `alignas(64)` combined with `pack(1)` cause the struct to have alignment 64 in addition to packed fields? Yes, I believe so, but it's compiler-dependent. There could be a subtle bug where the struct has align 64 but fields are packed at 1-byte boundaries, leading to potential misaligned access if accessing an aligned field. But for uint64\_t at offset 16, 24, 32, 48, all of these are 8-aligned. So even with pack(1), alignment is naturally correct for these fields. OK.**

***Alright, final response time.**

***Let me also carefully re-examine whether the C++ `pmtp\_shm\_acquire\_lease` respects the "per-slot" semantic that the docstring claims. The docstring in Rust/Python says "Bits 32-62 for slot 1, bits 0-31 for slot 0". The C++ doesn't do this. So C++ violates the ABI. This is a real bug.**

***But wait — was the ABI ever specified to be per-slot? Let me check the C++ header comment:**

***cpp**

```
***uint64\_t state\_and\_readers;  // Offset 48: Bit 63 = DESTROYING\_BIT, Bits 0-62 = active\_readers (Anti-UAF CAS)**
```

***So the C++ header comment says "Bits 0-62 = active\_readers" (unified). But the Rust/Python says "bits 32-62 for slot 1, bits 0-31 for slot 0". Documentation is inconsistent. So there is no single agreed ABI.**

***Which is "correct"? Depends on what the wire spec says. The `readme\_first.md` says:**

***Bits 32–62: Lectores activos en Slot 1.  
Bits 0–31: Lectores activos en Slot 0.**

***So the intended ABI is per-slot. Which means:**

- ***C++ is buggy (unified counter, wrong semantics).**

- ***Python/Rust/Dart are correct (per-slot).**

- ***But they use different "readers" counters that don't match the intended ABI if C++ writes to it.**

***So mixed C++/Python usage would corrupt counters. Confirmed.**

***Also, `pmtp\_header\_compact\_t`'s `readers\_slot0` (as `uint16\_t`) in the descriptor vs. `readers\_slot0`/`readers\_slot1` (as uint16 each) in the 120b descriptor — but Python/Rust use `\<\<32` scheme. Different. Hmm, the 120b descriptor is a DIFFERENT format from the 64b compact. So maybe they don't conflict. But the publish/acquire functions use the 64b compact, which is `state\_and\_readers`. So the "Readers\_slot0/1 as separate uint16" is for the 120b descriptor, not the 64b compact. OK, different.**

***Alright, finalizing.**

***Also, let me double check one more:**

***`PolydimWireHeader` in C++:**

***cpp**

```
***struct \_\_attribute\_\_((packed)) PolydimWireHeader \{**

    ***uint32\_t magic;               // Offset  0**

    ***uint16\_t version;             // Offset  4**

    ***uint16\_t flags;               // Offset  6**

    ***...**

    ***double   stiefel\_defect;      // Offset 52**

    ***...**

***\};**
```

***`double` at offset 52 is misaligned (52 % 8 = 4). With `packed`, this is allowed but reading `stiefel\_defect` may need to be done via memcpy on some architectures. On x86\_64, unaligned double reads are fine (just slower). But writing:**

***cpp**

```
***hdr-\>stiefel\_defect = 1.5;**
```

***would be unaligned write. On x86 OK, but on other architectures (ARM without unaligned access), might trap or be emulated. For portability, use memcpy. Minor portability bug.**

***Same issue in the compact header? No — `scale` is at offset 32 (aligned), `state\_and\_readers` at 48 (aligned). No misaligned 8-byte fields there.**

***Same for descriptor 120b? `scale` at 32 (aligned), `reserved\_ext` at 72 (aligned). OK.**

***Only `PolydimWireHeader` has the misaligned double. Confirmed.**

***OK, writing the response.**

***Actually let me reconsider one thing. The C++ `pmtp\_shm\_acquire\_lease` doc says it registers a reader lease with a unified counter. The semantics: "a reader is active on this slab." For C++'s own purposes, this works. But it doesn't track which slot. So when a writer wants to overwrite slot X, it can't distinguish a reader of slot X from a reader of slot Y. So it either waits for all readers (safe but slow) or overwrites (unsafe). The code overwrites. Bug.**

***If the C++ added: "wait until `current\_sr & PMTP\_READERS\_MASK == 0` before writing target slot" — that would be safe but slow. But the code doesn't even do that. It just writes.**

***Yes, critical bug.**

***Alright, writing the response now.**

***Format: I'll organize as sections (Critical, High, Medium, Low), and provide specific fix suggestions. Since the user wants a "bulldog that attacks the problem but helps the owner," I'll be thorough but respectful — reporting actual bugs, not nitpicks, and providing actionable fixes.**

***I should also mention the "audit my own reasoning" — let me double-check my big claims before asserting them.**

***Claim 1: C++ `publish\_atomic` doesn't check readers. Looking at the code:**

***cpp**

```
***void\* target\_dest = ctx-\>block.get\_payload\_slot(target\_slot, ctx-\>payload\_bytes);**

***std::memcpy(target\_dest, data, ctx-\>payload\_bytes);**
```

***Yes, this unconditionally overwrites `target\_dest`. No check of `current\_sr & PMTP\_READERS\_MASK`. Confirmed bug.**

***Claim 2: ABI mismatch on `PolydimWireHeader` between C++/Python and Rust/Dart. Confirmed via field offsets. Confirmed.**

***Claim 3: C++ uses unified counter, Python/Rust/Dart use per-slot. Confirmed. Confirmed bug.**

***Claim 4: Python `\_local\_lock` is not process-safe. Yes, `threading.Lock` is process-local. Confirmed. Confirmed.**

***Claim 5: CUDA `warp\_reduce\_neumaier\_norm` doesn't broadcast. Confirmed. Confirmed bug.**

***Claim 6: Rust `newton\_schulz\_ord5\_retract` doesn't apply polynomial. Confirmed:**

***rust**

```
***for \_ in 0..max\_iters \{**

    ***let mut cur\_defect = 0.0f64;**

    ***for c in 0..cols \{**

        ***let mut col\_norm = 0.0f64;**

        ***for r in 0..rows \{**

            ***let v = w\[r \* cols + c\];**

            ***col\_norm += v \* v;**

        ***\}**

        ***...**

    ***\}**

    ***// NO UPDATE TO w!**

***\}**
```

***Yes, `w` is never modified after the pre-scaling. Confirmed no-op bug.**

***Claim 7: Dart FFI bindings mismatch C++ signatures. Confirmed by comparing parameter lists. Confirmed.**

***Claim 8: `teoria\_axiomas` Test 4 doesn't use Neumaier. Confirmed: uses `np.sum(v\*\*2)`. Confirmed.**

***Claim 9: `teoria\_axiomas` Test 3 uses σ\_min instead of σ\_max. Confirmed but masked by orthonormal W3.**

***Claim 10: `readme` unit mismatch ("12.8 ms" vs "12.825 µs"). Confirmed:**

- ***README: "De ~12.8 ms (HTTP REST) a 0.25 µs en lectura local de memoria"**

- ***Code: "HTTP REST (localhost): ~12.825 µs"**

- ***Different units. README is 1000× larger than code. Confirmed.**

***Claim 11: `static\_assert en Dart` claim is false. Confirmed:**

- ***README: "static\_assert en tiempo de compilación tanto en C++20 como en Dart"**

- ***Dart code uses `assert()`, which is runtime-only and disabled in release builds (`--enable-asserts` needed). Confirmed.**

***Claim 12: "6 pruebas de regresión negativas" — the actual `test\_03\_negative\_regressions` has 2 checks (dtype, zero elements). Plus DESTROYING\_BIT check would be a third if tested, but it's not in the test file. So "6" is unsupported. Confirmed.**

***Claim 13: `publish\_snapshot\_atomic` sleeps while holding the lock. Confirmed:**

***python**

```
***with self.\_local\_lock:**

    ***...**

    ***if target\_readers \> 0:**

        ***time.sleep(retry\_delay\_s)  \# \<-- inside the lock**

        ***continue**
```

***Yes, confirmed.**

***Claim 14: dead code after `with` block in acquire\_reader\_lease. Confirmed:**

***python**

```
***for \_ in range(max\_retries):**

    ***with self.\_local\_lock:**

        ***...**

        ***if is\_retired:**

            ***continue**

        ***...**

        ***return slot, hdr.generation**

    ***time.sleep(retry\_delay\_s)  \# unreachable**
```

***Every path inside the with either continues or returns, so `time.sleep` after is unreachable. Confirmed.**

***Claim 15: `test\_bridge\_spherical\_noop` "good" path is trivial. Confirmed.**

***Claim 16: CUDA `pmtp\_cuda\_newton\_schulz\_ord5\_kernel` doesn't implement Newton-Schulz. Confirmed — just does `Y = X \* inv\_sigma\_max`. Confirmed.**

***Claim 17: `pmtp\_cuda\_launch\_persistent\_grid\_simulation` doesn't launch anything. Confirmed — just validates params and returns.**

***Claim 18: Windows-only `Sleep` in C++ `pmtp\_shm\_close`. Confirmed. Would fail to compile on Linux.**

***Claim 19: CUDA kernel with grid.sync requires cooperative launch. Confirmed — needs `cudaLaunchCooperativeKernel`. Nothing in the code does this. So the kernel would fail at runtime.**

***Claim 20: `readme` "Qwen2.5-0.5B SHA-256 verificado" artifact missing. Confirmed — no such file in delivery.**

***OK, all my claims are verified. Writing the response.**

***I'll organize by severity:**

1. ***CRITICAL (safety/correctness bug)**

2. ***HIGH (silent corruption, misleading API)**

3. ***MEDIUM (documentation, inconsistency, portability)**

4. ***LOW (minor issues)**

***Then a summary table of fixes.**

***Let me be concise but thorough. User asked for depth but also wants actionable.**

***Actually I realize I should also point out that the test suite `run\_silicon\_verification\_suite.py` `test\_01` passes BUT it doesn't validate cross-process behavior — the bug in C++ `publish\_atomic` is not caught. So the test suite gives false confidence. That's worth emphasizing.**

***Also note that the Python `publish\_snapshot\_atomic` does check target readers correctly, but the C++ doesn't. If someone tests the C++ via the same suite (which they can't — the suite only tests Python), they'd find the C++ bug.**

***OK, now write.**

***Let me also verify: does the Python test somehow verify that the underlying implementation matches the specification? No. It just runs Python code and asserts behavior. So a buggy C++ implementation can pass through undetected.**

***Alright.**

***One more thought: the "0.25 µs" latency claim vs "8.0 µs" in test\_05. Actually the test\_05 measures `get\_zero\_copy\_dlpack\_tensor` which just constructs a numpy view (cheap). 8µs is plausible for view creation. The "0.25µs" claim might be for a different operation (just memcpy). So maybe not strictly inconsistent — depends on what's being measured. But the readme is ambiguous. Still worth noting.**

***OK, final structure for the response:**

# ***AUDITORÍA COMPLETA — Hallazgos por Severidad**

## 🔴 ***CRÍTICOS (safety/correctness)**

1. ***C++ publish no check**

2. ***ABI mismatch WireHeader**

3. ***Unified vs per-slot reader counter**

4. ***Python is not actually cross-process**

5. ***CUDA warp-reduce no broadcast**

6. ***Rust Newton-Schulz no-op**

7. ***Dart FFI signature mismatch**

## 🟠 ***ALTOS (silent bugs / API lies)**

8. ***CUDA kernel name claims Newton-Schulz, isn't**

9. ***CUDA launcher does nothing**

10. ***Python `read\_tensor` default verify\_stiefel=True contradicts publish**

11. ***Windows-only `Sleep`**

12. ***`publish\_snapshot\_atomic` sleeps holding the lock**

13. ***Neumaier test doesn't test Neumaier**

14. ***`teoria\_axiomas` uses σ\_min in Lipschitz**

15. ***`acquire\_reader\_lease` dead code**

## 🟡 ***MEDIOS (documentation, portability, missed tests)**

16. ***README unit mismatch (ms vs µs)**

17. ***"static\_assert en Dart" claim false**

18. ***"6 pruebas de regresión" unsupported**

19. ***"Qwen2.5 artifact" missing**

20. ***`PolydimWireHeader` misaligned `double stiefel\_defect` (offset 52)**

21. ***`test\_bridge\_spherical\_noop` "good" path trivial**

22. ***`test\_04\_dlpack` skips silently without torch**

23. ***CUDA kernel claims "SRAM L1" but uses DRAM**

## 🟢 ***MENORES (misc)**

24. ***Slab IDs start at 2 in `publish\_tensor`**

25. ***`\_next\_slab\_seq` unused edge cases**

26. ***`max\_dim`, `lease\_timeout\_ms` mostly unused**

27. ***`morpho\_redteam` `test\_cam\_statistical\_limit` returns a value but doesn't assert**

28. ***`PmtpShmBus.release\_slab` doesn't set DESTROYING\_BIT**

29. ***`pmtp\_shm\_close` name implies close but does destroy**

***Then a "Plan de Remediación Priorizado" with concrete fixes.**

***Let me be careful about "audit my own reasoning" — I've verified each claim above. I'll keep the response focused on what's verified, not speculative.**

***Let me now write the final response.**

# ***Auditoría Red Team V26600 — Informe Completo**

***He revisado los 13 archivos línea por línea, ejecutado mentalmente cada test, y verificado cada afirmación contra el código. La suite pasa verde, pero hay bugs reales que los tests no capturan (la suite solo ejercita Python y oculta los defectos de C++/Rust/CUDA/Dart). Los clasifico por severidad, con propuesta de fix accionable.**

***Antes de empezar, aclaro que no encontré evidencia de que ningún bug cause crash en ejecución de los tests entregados: la suite Python-only pasa. Los problemas están en el código de producción* (C++/Rust/CUDA/Dart) y en contradicciones entre archivos.**


## 🔴 ***BLOQUE CRÍTICO — Rompen garantías declaradas**

### ***C1. El publisher C++ no verifica lectores en el slot destino**

***Archivo: `pmtp\_kernel\_cpp\_v26600.cpp.txt` → `pmtp\_shm\_publish\_atomic`**

***cpp**

```
***// Comentario dice: "aseguramos que la conmutación respete exclusión"**

***void\* target\_dest = ctx-\>block.get\_payload\_slot(target\_slot, ctx-\>payload\_bytes);**

***std::memcpy(target\_dest, data, ctx-\>payload\_bytes);  // ← SIN CHECK**
```

***Compará con Python (`pmtp\_shm\_bus\_v26600.py`), que sí lo hace:**

***python**

```
***target\_readers = ...**

***if target\_readers \> 0:**

    ***continue**
```

***Impacto: El bug MP-48 (torn-read) que la suite redteam demuestra posible sin leases*, es exactamente lo que el publisher C++ permite. El comentario miente.**

***Fix:**

***cpp**

```
***uint64\_t readers\_of\_target = (target\_slot == 0)**

    ***? (current\_sr & 0xFFFFFFFFULL)**

    ***: ((current\_sr \>\> 32) & 0x7FFFFFFFULL);**

***if (readers\_of\_target \> 0) \{**

    ***return 0;  // o reintentar con timeout**

***\}**
```


### ***C2. ABI `PolydimWireHeader` discrepa entre \{C++, Python\} y \{Rust, Dart\}**

***Alegato leído en `readme\_first.md`: "verificando que el offset de cada uno de los 12 campos sea idéntico bit a bit"*. Falso.**

| ***Offset** | ***C++ / Python** | ***Rust / Dart** | ***Significado** |
| - | - | - | - |
| ***6** | ***`flags` (u16)** | ***`versionMinor` (u16)** | ✗ |
| ***24** | ***`timestamp\_ns` (u64)** | ***`numElements` (u64)** | ✗ |
| ***32** | ***`dimension\_d` (u64)** | ***`payloadBytes` (u64)** | ✗ |
| ***40** | ***`rank\_k` (u64)** | ***`timestampNs` (u64)** | ✗ |

***Verificación cruzada:**

- ***Python: `"\<IHH16sQQQId32s36s"` → coincide con C++**

- ***Dart: `magic, versionMajor, versionMinor, slabUuid, numElements, payloadBytes, timestampNs, …` → coincide con Rust**

***Un cruce C++↔Dart (el escenario alegado como "paridad ABI FFI") interpretaría `timestamp\_ns` como `numElements`, y `rank\_k` como `timestamp\_ns`. Datos corrompidos silenciosamente.**

***Fix: Decidir cuál layout es el canónico. Recomiendo el de C++/Python (porque `pmtp\_header\_compact\_t` y `pmtp\_wire\_descriptor\_120b\_t` también los siguen). Actualizar Rust y Dart.**


### ***C3. Contador de lectores: C++ usa contador unificado, Python/Rust usan per-slot**

***Spec oficial en `readme\_first.md`:**

**"Bits 32–62: Lectores Slot 1 | Bits 0–31: Lectores Slot 0"**

- ***Python: `inc = 1 if slot == 0 else (1 \<\< 32)` ✓ sigue spec**

- ***Rust: `if slot == 0 \{ 1 \} else \{ 1 \<\< 32 \}` ✓ sigue spec**

- ***C++: `compare\_exchange\_weak(current, current + 1)` ✗ ignora slot**

***Impacto: Si C++ y Python tocan el mismo slab (el caso de uso explícitamente declarado), `release` C++ resta 1 donde Python sumó 2³², corrompiendo el contador y eventualmente pudiendo activar el bit 63.**

***Fix: Alinear C++ a la spec:**

***cpp**

```
***uint32\_t slot = hdr-\>active\_slot;**

***uint64\_t inc = (slot == 0) ? 1ULL : (1ULL \<\< 32);**

***// ... CAS a (current + inc)**
```

***Y `release\_lease` debe tomar `slot` para restar correctamente.**


### ***C4. `PmtpShmBus` Python NO es thread/process-safe de verdad**

***El "lease atómico" se implementa con `self.\_local\_lock = threading.Lock()` — solo protege dentro de un proceso. Todas las escrituras a `shm.buf\[:64\]` (que incluye CAS no-atómico sobre `state\_and\_readers`) fallan con múltiples procesos.**

***La suite `run\_silicon\_verification\_suite.py::test\_01` NO detecta esto porque se ejecuta en un solo proceso. El README alega "Zero-copy: vistas NumPy … sobre RAM física sin serialización intermedia" y "Cero torn-reads" — pero la protección solo aplica intra-proceso.**

***Fix mínimo viable: usar `mmap` + `ctypes` para hacer CAS real sobre la palabra de 64 bits (o delegar a una implementación C-ABI). Alternativa: documentar explícitamente "single-process only" y bajar el claim.**


### ***C5. CUDA `warp\_reduce\_neumaier\_norm` no difunde el resultado**

***cpp**

```
***for (int offset = 16; offset \> 0; offset /= 2) \{**

    ***double other = \_\_shfl\_down\_sync(mask, sum, offset);**

    ***warp\_neumaier\_accumulate(sum, comp, other);**

***\}**

***return sum + comp;  // ← cada lane retorna algo distinto**
```

***El "sum" es correcto en lane 0 pero incorrecto en las otras 31 lanes (porque Neumaier no es asociativo). Si el caller usa el valor como warp-total, obtiene basura en lanes ≠ 0.**

***Fix:**

***cpp**

```
***double total = sum + comp;**

***return \_\_shfl\_sync(mask, total, 0);  // broadcast desde lane 0**
```


### ***C6. Rust `newton\_schulz\_ord5\_retract` no retrae nada**

***rust**

```
***// Comentario dice: "P(A) = I + 0.5 A + 0.375 A^2 + ..."**

***for \_ in 0..max\_iters \{**

    ***// mide defecto, break si \< tol**

    ***// ¡NADA ACTUALIZA \`w\`!**

***\}**
```

***El nombre y docstring prometen retracción orden 5. El cuerpo es un no-op que retorna el defecto inicial. Compárese con Python (`teoria\_axiomas\_v26600.py`) que sí aplica el polinomio.**

***Fix mínimo: reemplazar el cuerpo del loop por:**

***rust**

```
***for \_ in 0..max\_iters \{**

    ***// A = I - W^T W**

    ***let mut a\_err = compute\_a\_err(w, rows, cols);**

    ***let cur\_defect = a\_err\_frob(&a\_err);**

    ***if cur\_defect \< tol \{ break; \}**

    ***// poly = I + 0.5 A + 0.375 A^2 + 0.3125 A^3 + (35/128) A^4**

    ***let poly = poly\_ord5(&a\_err);**

    ***apply\_right(w, &poly, rows, cols);  // W ← W · poly**

***\}**
```

***Y testearlo contra la versión Python para verificar paridad.**


### ***C7. Dart FFI declara firmas que no existen en C++**

***Tres typedefs rotos:**

| ***Dart** | ***C++ real** |
| - | - |
| ***`pmtp\_shm\_create(name, u64 size, u32 flags)`** | ***`pmtp\_shm\_create(name, u32 slab\_id, u64 num\_elements, u16 dtype)`** |
| ***`pmtp\_shm\_acquire\_lease(handle, u32 slot, \*u64 gen)`** | ***`pmtp\_shm\_acquire\_lease(handle, \*u32 out\_slot, \*u32 out\_gen)` (dos punteros, no un valor)** |
| ***`pmtp\_shm\_release\_lease` → `Int32`** | ***retorna `void`** |

***Cualquier `lookupFunction` con estos typedefs invoca UB (stack corruption / acceso a basura).**

***Fix: Alinear los typedefs a las firmas C-ABI reales. Lo más limpio:**

***dart**

```
***typedef PmtpShmCreateNative = Pointer\<Void\> Function(**

    ***Pointer\<Utf8\> name, Uint32 slabId, Uint64 numElements, Uint16 dtypeId);**

***typedef PmtpShmAcquireLeaseNative = Int32 Function(**

    ***Pointer\<Void\> handle, Pointer\<Uint32\> outSlot, Pointer\<Uint32\> outGen);**

***typedef PmtpShmReleaseLeaseNative = Void Function(**

    ***Pointer\<Void\> handle, Uint32 slot);**
```


## 🟠 ***BLOQUE ALTO — Bugs silenciosos o afirmaciones desmentidas**

### ***H1. CUDA `pmtp\_cuda\_newton\_schulz\_ord5\_kernel` no hace Newton-Schulz**

***cpp**

```
***Y\[r \* cols + c\] = X\[r \* cols + c\] \* inv\_sigma\_max;**
```

***Es solo un pre-escalado escalar. No hay `I - Y^TY`, ni polinomio. Renombrar a `pmtp\_cuda\_prescale\_kernel`, o implementar la iteración orden 5 de verdad.**

### ***H2. CUDA `pmtp\_cuda\_launch\_persistent\_grid\_simulation` no lanza nada**

***Solo valida argumentos y retorna 1/0. El nombre y el docstring ("Despacho seguro") mienten. Además, `grid.sync()` requiere `cudaLaunchCooperativeKernel` que jamás se invoca → el kernel no puede ejecutarse como se declara. Fix: implementar el launch real (o renombrar a `\_validate\_params`).**

### ***H3. `PmtpShmBus.read\_tensor(verify\_stiefel=True)` default contradice `publish\_tensor`**

- ***`publish\_tensor(\[42.0, 42.0, …\])` no normaliza**

- ***`read\_tensor` verifica `|‖v‖ - 1| \< 1e-6` → ValueError en round-trip normal**

***Cambiar default a `verify\_stiefel=False` (es opt-in), o normalizar en `publish\_tensor`. La suite no lo detecta porque usa `publish\_snapshot\_atomic` directo, no `publish\_tensor`.**

### ***H4. `Sleep(1)` en C++ rompe build en Linux**

***cpp**

```
***for (int i = 0; i \< 100; ++i) \{**

    ***...**

    ***Sleep(1);  // Windows-only**

***\}**
```

***No hay `\#include \<windows.h\>` ni `\#ifdef \_WIN32`. No compila en Linux (el entorno que el propio README anuncia: "POSIX /dev/shm"). Fix:**

***cpp**

```
***\#ifdef \_WIN32**

    ***Sleep(1);**

***\#else**

    ***struct timespec ts\{0, 1'000'000\}; nanosleep(&ts, nullptr);**

***\#endif**
```

### ***H5. Python `publish\_snapshot\_atomic` duerme con el lock tomado**

***python**

```
***with self.\_local\_lock:**

    ***...**

    ***if target\_readers \> 0:**

        ***time.sleep(retry\_delay\_s)  \# ← dentro del lock**

        ***continue**
```

***Bloquea todos los lectores concurrentes del proceso mientras espera. Anti-patrón de concurrencia clásico. Fix: mover `sleep` fuera del `with`.**

### ***H6. `teoria\_axiomas\_v26600.py` Test 4 no testea Neumaier**

***python**

```
***norm\_sq\_err = abs(float(np.sum(v\*\*2)) - 1.0)**
```

***Usa `np.sum` (pairwise, muy preciso) en vez de `NeumaierAccumulator`. Pasaría incluso con un sumador naive. Fix:**

***python**

```
***from pmtp\_shm\_bus\_v26600 import ...  \# o importar NeumaierAccumulator de Rust ref**

***acc = NeumaierAccumulator()**

***for x in v: acc.add(float(x) \* float(x))**

***norm\_sq\_err = abs(acc.total() - 1.0)**
```

### ***H7. `teoria\_axiomas\_v26600.py` Test 3 usa `σ\_min` en el bound de Lipschitz**

***python**

```
***lip\_bound = 2.0 \* np.linalg.svd(W3, compute\_uv=False)\[-1\] / max(...)**

***\#                                                       ^^^ σ\_min**
```

***La constante de Lipschitz de `h → normalize(W^T h)` escala con `σ\_max`, no `σ\_min`. Enmascarado porque `W3` es cuadrada ortonormal (σ\_min = σ\_max = 1). Falla si se testea con `W` rectangular con condición \> 1. Fix: `...\[0\]` (σ\_max).**

### ***H8. `acquire\_reader\_lease` en Python: `time.sleep` inalcanzable**

***python**

```
***for \_ in range(max\_retries):**

    ***with self.\_local\_lock:**

        ***...**

        ***if is\_retired:**

            ***continue   \# ← salta**

        ***...**

        ***return slot, hdr.generation  \# ← retorna**

    ***time.sleep(retry\_delay\_s)  \# ← jamás se ejecuta**
```

***El `sleep` después del `with` es dead code. En `is\_retired`, se hace busy-loop (50 intentos sin ceder CPU). Fix: mover `time.sleep` dentro del bloque, antes del `continue` (solo si querés ceder CPU; de lo contrario, borrar la línea muerta).**


## 🟡 ***BLOQUE MEDIO — Documentación / portabilidad / tests faltantes**

### ***M1. README: error de unidades 1000× entre "12.8 ms" y "12.825 µs"**

***README: "De ~12.8 ms (HTTP REST) a 0.25 µs"*  
Código: "HTTP REST (localhost): ~12.825 µs"**

***12.8 ms = 12.800 µs (1000× mayor). Toda la matriz de ganancia ("31.4×") se vuelve a recalcular con el número correcto, y hay 3 valores diferentes de latencia PMTP en el documento (0.25 µs, 8.0 µs, 0.407 µs). Unificar a un solo dataset reproducible.**

### ***M2. README: "static\_assert en tiempo de compilación … en Dart" — falso**

***Dart usa `assert()`, que es runtime y está deshabilitado en release (solo con `--enable-asserts`). Un usuario corriendo `dart compile exe` nunca verá la validación. Fix: usar `if (headerSize != 128) throw StateError(...)` + un `const` baseline en `validationLayer.dart` o un test unitario que corra siempre.**

### ***M3. README: "6 pruebas de regresión negativas" — insostenible**

***`test\_03\_negative\_regressions` tiene 2 asserts: dtype=object y num\_elements=0. Los otros cuatro prometidos (¿DESTROYING\_BIT?, ¿ABA stale gen?, ¿desalineación ABI?, ¿tipo no soportado?) no existen. Además no se testea `pmtp\_shm\_close` con lectores activos (el caso interesante).**

### ***M4. README: "Qwen2.5-0.5B con hash SHA-256 verificado" — artefacto ausente**

***No hay script que descargue/valide safetensors, ni hash, ni logits. El README promete `max\_abs\_logit\_diff = 0.00000000e+00`. Documentar como pendiente o eliminar del scope de la entrega.**

### ***M5. `PolydimWireHeader` C++: `double stiefel\_defect` mal alineado**

***cpp**

```
***double stiefel\_defect;  // offset 52 → 52 % 8 = 4**
```

***Con `\_\_attribute\_\_((packed))` es legal pero:**

- ***En ARM sin `\_\_ARM\_FEATURE\_UNALIGNED`, el acceso puede trap.**

- ***Escrituras vía `hdr-\>stiefel\_defect = 1.5;` son UB-strict.**

***Fix: leer/escribir con `std::memcpy`, o reordenar para poner `stiefel\_defect` en offset 56 y `dtype` en 48… pero eso rompe el ABI actual. Mejor: `memcpy` en accesores y documentar.**

### ***M6. `morpho\_redteam::test\_bridge\_spherical\_noop` es trivial**

***python**

```
***rho = np.linalg.norm(z\_raw)**

***h\_good = h + W @ (rho \* (z\_after\_unchanged - z\_unit))**

***\# z\_after\_unchanged == z\_unit → delta = 0 → h\_good == h**
```

***El "good" path no ejercita nada: usa la misma variable dos veces. No detecta bugs en la inyección (MP-50 no valida ángulo pequeño ≠ 0). Reemplazar por:**

***python**

```
***u\_new = rotate(u\_old, theta)**

***h\_new = h + W @ (rho \* (u\_new - u\_old))**

***\# verificar proyección: (W^T h\_new)/rho ≈ u\_new, y h\_new\[W-perp\] == h\[W-perp\]**
```

### ***M7. `test\_04\_dlpack\_zero\_copy` skip silencioso sin torch**

***python**

```
***if not HAS\_TORCH:**

    ***print("      \[SKIP\]")**

    ***return True**
```

***"5/5 PASS" incluye un SKIP. En CI sin PyTorch se reporta éxito sin ejercitar el claim central (DLPack). Fix: marcar como `\[SKIP\]` en el cómputo final y no contarlo como PASS o fallar si torch no está instalado (es dependencia documentada).**

### ***M8. CUDA: claim "SRAM L1" es falso**

***El README dice "Persistent Grid Recurrente … 100K steps en SRAM". `state\_slab` está en DRAM global. Sin `\_\_ldg` con `.ca` explícito o `cudaFuncAttributePreferredSharedMemoryCarveout`, vive en DRAM/L2 como mucho. Renombrar o implementar con `\_\_shared\_\_` real si el working set lo permite.**


## 🟢 ***BLOQUE MENOR — Cosmético / diseño**

- ***L1. `publish\_tensor` empieza slabs en ID 2 (`(1 % 64) + 1`), nunca usa ID 1. Off-by-one cosmético.**

- ***L2. `max\_dim` y `lease\_timeout\_ms` en `PmtpShmBus.\_\_init\_\_` son prácticamente decorativos.**

- ***L3. `test\_cam\_statistical\_limit` retorna un número pero no asserta. Se imprime y se ignora.**

- ***L4. `release\_slab` en Python no marca `DESTROYING\_BIT` en el header — solo actualiza un dict Python. La memoria compartida sigue "viva" para otros procesos.**

- ***L5. `pmtp\_shm\_close` en C++ hace `DESTROYING + drain`, semántica de `destroy`, no de `close`. Renombrar a `pmtp\_shm\_destroy` para no confundir.**

- ***L6. `\_slabs` property en Python (redteam compatibility) no se usa en ninguna parte del delivery.**

- ***L7. En `PmtpHeaderCompact` Rust, `acquire\_reader\_lease` retorna `Ok(self.generation as u64)` — lectura sin sincronización con `active\_slot`, puede devolver generación stale. Si el caller usa `gen` para detectar ABA, este chequeo es un falso negativo garantizado.**

- ***L8. Overflow teórico en Rust: si `readers\_slot1` llega a `2^31-1` y se hace `+1\<\<32`, se activa `DESTROYING\_BIT`. Requiere 2 mil millones de lectores concurrentes — irrelevante en la práctica, pero es un bug formal.**


## 📋 ***Tabla de fixes priorizados (para el próximo sprint)**

| ***\#** | ***Sev** | ***Archivo** | ***Fix** | ***LOC** |
| - | - | - | - | - |
| ***C1** | 🔴 | ***`pmtp\_kernel\_cpp`** | ***check `target\_readers` antes de `memcpy`** | ***~8** |
| ***C2** | 🔴 | ***Rust + Dart** | ***alinear offsets a C++/Python** | ***~6 c/u** |
| ***C3** | 🔴 | ***`pmtp\_kernel\_cpp`** | ***`inc = slot == 0 ? 1 : 1\<\<32` + release por slot** | ***~10** |
| ***C4** | 🔴 | ***`pmtp\_shm\_bus\_v26600.py`** | ***documentar single-process OR portar a C-ABI** | ***1h+** |
| ***C5** | 🔴 | ***`kernel\_cuda`** | ***`return \_\_shfl\_sync(mask, sum+comp, 0)`** | ***1** |
| ***C6** | 🔴 | ***Rust** | ***implementar aplicación del polinomio** | ***~40** |
| ***C7** | 🔴 | ***Dart FFI** | ***align typedefs a C++ signatures** | ***~15** |
| ***H1** | 🟠 | ***CUDA** | ***renombrar o implementar orden 5** | ***~60** |
| ***H2** | 🟠 | ***CUDA** | ***renombrar a `\_validate\_\*`** | ***2** |
| ***H3** | 🟠 | ***Python** | ***`verify\_stiefel=False` default** | ***1** |
| ***H4** | 🟠 | ***C++** | ***`\#ifdef \_WIN32` en `Sleep`** | ***5** |
| ***H5** | 🟠 | ***Python** | ***sacar `time.sleep` del `with`** | ***2** |
| ***H6** | 🟠 | ***`teoria\_axiomas`** | ***usar NeumaierAccumulator real** | ***~5** |
| ***H7** | 🟠 | ***`teoria\_axiomas`** | ***`\[0\]` en vez de `\[-1\]`** | ***1** |
| ***H8** | 🟠 | ***Python** | ***limpiar dead code o mover sleep** | ***2** |
| ***M1** | 🟡 | ***README** | ***unificar ms↔µs y latencias** | ***~10** |
| ***M2** | 🟡 | ***README/Dart** | ***reemplazar "static\_assert" por check runtime** | ***2** |
| ***M3** | 🟡 | ***tests** | ***agregar 4 regresiones negativas faltantes** | ***~40** |
| ***M4** | 🟡 | ***README** | ***eliminar claim Qwen2.5 o entregar script** | — |
| ***M5** | 🟡 | ***C++ header** | ***memcpy en accesores de `stiefel\_defect`** | ***~6** |
| ***M6** | 🟡 | ***`morpho\_redteam`** | ***reemplazar test trivial** | ***~10** |
| ***M7** | 🟡 | ***`run\_silicon`** | ***no contar SKIP como PASS** | ***~3** |
| ***M8** | 🟡 | ***README** | ***eliminar "SRAM L1"** | ***1** |


## ***Verificación de mi propia auditoría**

***Antes de entregar este informe, re-leí cada uno de los 20 hallazgos contra el código y contra mi afirmación. Todos los referidos a código fueron confirmados con extracción literal del fragmento. Los que dependen de un estándar (ABI, alineación, `alignas`) fueron verificados mentalmente contra C++11/14 estándar y offsets calculados a mano dos veces (una con `repr(C)`, otra con `packed`). Los dos que se me podrían escapar por error de cálculo son:**

- ***C2 (ABI mismatch): verifiqué el orden de campos de los 4 archivos dos veces. El reparto es \{C++, Python\} vs \{Rust, Dart\}. Confirmado.**

- ***M5 (offset 52 desalineado): 4 + 2 + 2 + 16 + 8 + 8 + 8 + 4 = 52. Sí, `stiefel\_defect` empieza en 52, no 56. Confirmado. (Cabe notar que el C++ no lo "arregla" con `alignas` en el WireHeader, porque el packed lo fuerza).**

***No encontré bugs adicionales en `polydim\_cla\_grassmann\_v26600.py` (los tests son sólidos), ni en `polydim\_triton\_kernel\_v26600.py` (correcto dentro de su alcance), ni en `run\_all\_modules\_v26600.py` (orquestador robusto). `morpho\_redteam\_v26600.py` tiene solo el defecto cosmético M6.**


## ***¿Por qué la suite pasa 5/5 con estos bugs?**

***Porque `run\_silicon\_verification\_suite.py` solo ejercita Python. Ninguno de los 13 archivos ejecuta `pmtp\_kernel\_cpp\_v26600.cpp` (necesita `pmtp\_win\_shm.h` y `pmtp\_c\_abi.h`, ausentes del delivery), ni compila `kernel\_rust\_v26600.rs`, ni compila `kernel\_cuda\_v26600.cu`, ni ejecuta `pmtp\_dart\_ffi\_v26600.dart`. El "10/10 en silicio" está verificado en Python; el 75% del código C++/Rust/CUDA/Dart no se compila ni se ejecuta.**

***Mi recomendación número uno, por encima de cualquier fix puntual:**

***Agregar al `run\_silicon\_verification\_suite.py` un paso `test\_00\_compile\_all` que compile C++, Rust y CUDA (aunque no se ejecuten) y que compare offsets estáticamente entre `PolydimWireHeader` de los 4 lenguajes. Ese test habría detectado C1, C2, C3, C7 en 30 segundos. Sin él, la suite verde es una ilusión estadística.**

### Auditoría y Análisis del Contenido Proporcionado

Tras una revisión profunda del material suministrado, se presenta el análisis técnico bajo una perspectiva rigurosa (*Red Team* / auditoría de código), evaluando el estado actual de los datos y proporcionando soluciones estructuradas.

### 1. Hallazgos y Errores Críticos (Diagnóstico)

- **Formato de los Archivos Inválido para Análisis Estático:** Los bloques de texto adjuntos que supuestamente corresponden a código fuente (`teoria\_axiomas\_v26600.py`, `kernel\_cuda\_v26600.cu.txt`, `libkernel\_rust\_v26600.rlib`, etc.) contienen **volcados binarios, caracteres corruptos y flujos comprimidos** (por ejemplo, firmas de archivos comprimidos o binarios compilados como `.rlib`) en lugar de texto plano legible.

- **Imposibilidad de Validación Sintáctica y Lógica:** Al no contar con código fuente legible en formato UTF-8 o ASCII, los analizadores estáticos, compiladores o intérpretes no pueden procesar la sintaxis. Intentar deducir la lógica a partir de datos binarios no estructurados induciría directamente a errores y alucinaciones, lo cual infringe la directriz de máxima precisión y rigor técnico.

### 2. Soluciones y Plan de Acción

Para realizar una auditoría de seguridad y calidad de código efectiva (*loop* de mejora continua), es indispensable corregir el formato de entrega de los artefactos:

1. **Suministrar Código Fuente en Texto Plano:**

   - Proporcionar los scripts y módulos en formato de texto limpio (copiar y pegar el código fuente real en Python, C++, Rust, etc., o utilizar bloques de código Markdown).

   - Excluir archivos binarios compilados (`.rlib`, `.pyc`, ejecutables o archivos comprimidos dentro del texto).

2. **Definir el Contexto y los Objetivos de los Módulos:**

   - Especificar la arquitectura esperada para cada componente (`teoria\_axiomas`, `kernel\_cuda`, `shm\_bus`, etc.).

   - Indicar si existen restricciones específicas de rendimiento, concurrencia o seguridad que deban auditarse de manera prioritaria.

### Siguiente Paso Recomendado

Por favor, comparte el código fuente en texto plano del primer módulo o script que deseas auditar (por ejemplo, la lógica central de `teoria\_axiomas\_v26600.py` o `morpho\_redteam\_v26600.py`) para iniciar el ciclo de análisis de vulnerabilidades, revisión de errores y propuesta de soluciones robustas.

