# Taller 1: Algoritmos Paralelos

> Infraestructuras Paralelas y Distribuidas (750023C) — 2026-2

**Profesor:** Manuel Alejandro Pastrana, PhD
**Estudiante:** Andrés Gerardo González Rosero

---

## Parte 1: Preguntas Conceptuales

### 1. Motivación para la Programación Paralela

La programación paralela es fundamental en la informática moderna porque, desde hace más de una década, el aumento de la velocidad del hardware ya no proviene principalmente de subir la frecuencia de reloj de un único núcleo (ese camino chocó con límites térmicos y de consumo energético), sino de añadir más núcleos y unidades de procesamiento. Si el software se sigue escribiendo de forma puramente secuencial, no aprovecha ese hardware adicional y el rendimiento se estanca aunque se compren procesadores más potentes. Paralelizar permite dividir un problema en partes que se ejecutan simultáneamente, reduciendo el tiempo total de cómputo y permitiendo procesar volúmenes de datos que serían inviables de forma secuencial.

Algunas áreas donde la programación paralela es esencial:

- Cómputo científico y simulaciones (clima, dinámica de fluidos, física de partículas), donde se resuelven millones de ecuaciones simultáneamente.
- Entrenamiento e inferencia de modelos de inteligencia artificial y aprendizaje profundo, que dependen de operaciones matriciales masivamente paralelas en GPU.
- Procesamiento de imágenes, video y gráficos por computador (renderizado en tiempo real).
- Bases de datos y sistemas distribuidos que atienden miles de solicitudes concurrentes (por ejemplo, motores de búsqueda o plataformas de comercio electrónico).
- Procesamiento de big data (frameworks como Spark o Hadoop, que reparten el trabajo entre múltiples nodos).

### 2. Conceptos Fundamentales

La analogía de los cocineros y los clientes ilustra bien la diferencia entre trabajo secuencial y trabajo paralelo. Imaginemos un restaurante con un solo cocinero: cada pedido se atiende uno tras otro, así que si llegan diez clientes, el décimo debe esperar a que se preparen los nueve pedidos anteriores. El tiempo total crece proporcionalmente al número de clientes. Ahora imaginemos el mismo restaurante con varios cocineros trabajando en paralelo: cada cocinero puede tomar un pedido distinto y prepararlo al mismo tiempo que los demás, por lo que varios clientes son atendidos simultáneamente y el tiempo total de espera se reduce. Sin embargo, la analogía también revela las limitaciones reales del paralelismo: si todos los cocineros necesitan usar el mismo horno (un recurso compartido), tendrán que turnarse para esa parte de la tarea —igual que varios hilos que deben sincronizarse para acceder a un recurso compartido—, y si la cocina es muy pequeña, agregar más cocineros de los que caben deja de ayudar e incluso puede estorbar (overhead de coordinación).

La computación paralela ha evolucionado de forma progresiva: en sus inicios (décadas de 1960-1980) estaba reservada a supercomputadoras y clústeres especializados de altísimo costo, usados casi exclusivamente en investigación militar y científica. Con la llegada de los procesadores multinúcleo a los computadores personales (mediados de la década de 2000), el paralelismo dejó de ser exclusivo de la supercomputación y se volvió parte del hardware cotidiano. Paralelamente, las tarjetas gráficas (GPU) evolucionaron de procesar solo gráficos a convertirse en unidades de cómputo paralelo de propósito general (GPGPU), impulsando el auge actual de la inteligencia artificial. Hoy el paralelismo está presente en todos los niveles: desde varios núcleos en un teléfono móvil hasta clústeres de miles de nodos en la nube, y los lenguajes y frameworks modernos (como `concurrent.futures` en Python, OpenMP, MPI o CUDA) buscan hacer ese paralelismo accesible a cualquier desarrollador.

### 3. Patrones de Programación Paralela

Los patrones de programación paralela son importantes porque encapsulan soluciones probadas a problemas recurrentes de paralelización (por ejemplo, map-reduce, fork-join, pipeline, productor-consumidor), evitando que cada desarrollador tenga que resolver desde cero problemas ya conocidos como condiciones de carrera, interbloqueos (deadlocks) o balanceo de carga. Usar un patrón adecuado ayuda a razonar sobre la corrección del programa, porque el patrón ya define claramente qué partes son independientes y cuáles requieren sincronización.

Beneficios de utilizar patrones y frameworks paralelos:

- Reducen errores de concurrencia (condiciones de carrera, deadlocks) porque implementan la sincronización de forma probada y encapsulada.
- Aumentan la productividad: el desarrollador expresa el problema a un nivel más alto (por ejemplo, "map" sobre una colección) sin gestionar manualmente hilos o procesos.
- Facilitan la portabilidad: el mismo patrón puede ejecutarse sobre distintos backends (hilos, procesos, GPU, clúster) sin cambiar la lógica del problema.
- Mejoran la escalabilidad, ya que muchos frameworks ajustan automáticamente el número de tareas al hardware disponible.
- Facilitan el mantenimiento y la legibilidad del código, al usar abstracciones reconocibles en lugar de sincronización manual dispersa por todo el programa.

### 4. Ley de Amdahl

La Ley de Amdahl establece que la mejora máxima de rendimiento que se puede obtener al paralelizar un programa está limitada por la fracción del programa que es inherentemente secuencial (no paralelizable). Formalmente, si f es la fracción del tiempo de ejecución que no se puede paralelizar y N es el número de procesadores, la aceleración (speedup) máxima teórica es:

$$
\text{Speedup}(N) = \frac{1}{f + \frac{1 - f}{N}}
$$

A medida que N crece, el término (1-f)/N tiende a cero, por lo que el speedup se aproxima asintóticamente a 1/f, sin importar cuántos procesadores se agreguen. Esto significa que incluso una porción secuencial pequeña (por ejemplo, un 10%) limita drásticamente la ganancia posible: con f = 0.1, el speedup máximo teórico nunca supera 10x, sin importar si se usan 100 o 10.000 núcleos.

Implicaciones para la optimización de programas paralelos:

- El primer paso para optimizar no es "agregar más hilos", sino identificar y reducir la porción secuencial del algoritmo (inicialización, E/S, secciones críticas, sincronización).
- Existe un punto de retorno decreciente: agregar más recursos de cómputo más allá de cierto número de procesadores deja de traducirse en mejoras notables.
- Justifica por qué, en problemas con partes secuenciales significativas, conviene enfocar el esfuerzo de ingeniería en rediseñar el algoritmo (para reducir f) en lugar de simplemente escalar el hardware.
- Complementa a la Ley de Gustafson, que matiza a Amdahl considerando que, en la práctica, al tener más procesadores también se suele aumentar el tamaño del problema, lo que puede hacer que la fracción secuencial relativa disminuya.

### 5. Trampas Seriales

Las "trampas seriales" (serial traps) son puntos dentro de un programa paralelo que, de forma no evidente, obligan a que ciertas operaciones se ejecuten en orden estrictamente secuencial, anulando parcial o totalmente el beneficio del paralelismo, o incluso produciendo resultados incorrectos. Un ejemplo clásico —y el que se trabaja en este taller— es imprimir resultados directamente desde dentro de cada hilo o proceso: como la salida estándar (stdout) es un recurso compartido, varias tareas escribiendo en paralelo pueden entrelazar sus líneas de forma desordenada o incluso corrupta, y además el orden de impresión terminaría dependiendo del orden de finalización de cada tarea (no determinista), en vez del orden lógico esperado. Otros ejemplos típicos de trampas seriales son: usar una variable acumuladora compartida sin sincronización, depender de un recurso de E/S compartido (archivo, socket, base de datos) sin coordinación, o encadenar tareas que en apariencia son independientes pero en realidad comparten estado mutable.

Identificarlas y evitarlas es importante porque:

- Una trampa serial no detectada puede introducir condiciones de carrera y bugs intermitentes, muy difíciles de reproducir y depurar, ya que dependen del orden de ejecución del sistema operativo en cada corrida.
- Incluso sin producir errores de corrección, una trampa serial puede serializar de facto una sección de código que se pretendía paralela, destruyendo la ganancia de rendimiento esperada (efectivamente aumentando la fracción f de la Ley de Amdahl).
- Evitarlas desde el diseño (por ejemplo, separando cómputo de E/S, como se hace en este taller) es mucho más barato que corregirlas después de que el programa ya está en producción.

### 6. Work-Span

En el modelo de análisis de algoritmos paralelos Work-Span (también llamado modelo work-depth):

- **Work (trabajo, T1):** es el tiempo total que tomaría ejecutar todo el algoritmo en un único procesador; equivale a la suma de todas las operaciones realizadas por todas las tareas, sin importar si podrían ejecutarse en paralelo. Es una medida de la cantidad total de cómputo.
- **Span (envergadura o profundidad, T∞):** es el tiempo mínimo de ejecución posible si se dispusiera de un número infinito de procesadores; corresponde a la longitud de la cadena más larga de operaciones que dependen unas de otras (la ruta crítica). Representa el límite inferior teórico de tiempo, sin importar cuántos recursos se agreguen.

El Span se relaciona directamente con la ruta crítica de un programa paralelo: es, por definición, la duración de esa ruta crítica, es decir, la secuencia de tareas dependientes entre sí más larga dentro del grafo de dependencias del programa. Aunque se agreguen procesadores adicionales, ninguna ejecución puede ser más rápida que el Span, porque las tareas de la ruta crítica deben ejecutarse necesariamente en orden. Por esto, el speedup máximo alcanzable con P procesadores está acotado por Work/Span (T1/T∞), y reducir el Span —acortando las cadenas de dependencia— es, junto con reducir el Work, una de las dos estrategias fundamentales para mejorar el rendimiento de un algoritmo paralelo.

### 7. Memoria compartida, localidad y cache

En arquitecturas de memoria compartida, todos los núcleos o hilos acceden al mismo espacio de direcciones, lo que evita la necesidad de copiar o transmitir explícitamente los datos entre tareas (como sí ocurre en sistemas de memoria distribuida, donde hay que enviar mensajes). Esto puede acelerar la ejecución porque el acceso a datos compartidos es directo y rápido, pero introduce el riesgo de condiciones de carrera cuando varios hilos leen y escriben la misma dirección de memoria sin sincronización adecuada. La localidad de referencia (temporal: reutilizar datos recientemente accedidos; espacial: acceder a datos cercanos en memoria) es clave para el rendimiento porque los procesadores modernos son mucho más rápidos que la memoria principal (RAM): un algoritmo que reutiliza datos que ya están en la jerarquía de memoria cercana al procesador evita esperas costosas de acceso a memoria.

La cache juega un papel central en esta optimización: es una memoria pequeña y muy rápida ubicada entre el procesador y la RAM, que guarda copias de los datos usados recientemente. Cuando un dato solicitado ya está en cache (cache hit), el acceso es órdenes de magnitud más rápido que ir hasta la RAM; cuando no lo está (cache miss), el procesador debe esperar un acceso mucho más lento. En programación paralela esto tiene una implicación adicional: si varios núcleos modifican con frecuencia variables que están en la misma línea de cache (aunque sean variables lógicamente distintas), se produce un fenómeno llamado "false sharing", donde el hardware de coherencia de cache invalida constantemente esa línea entre núcleos, degradando el rendimiento incluso si no hay una verdadera dependencia de datos. Por eso, diseñar algoritmos paralelos con buena localidad y evitando false sharing es tan importante como repartir bien el trabajo entre procesadores.

---

## Parte 2: Reto de Programación — Fibonacci Paralelo

### Resumen de la solución

El código completo se entrega en el archivo `fibonacci_paralelo.py` (adjunto / alojado en el repositorio indicado al final de este documento). A continuación se resume el diseño y se responde a las preguntas adicionales solicitadas.

### Estructura del programa

- `fibonacci(n)`: calcula el n-ésimo número de Fibonacci de forma recursiva. Es la unidad de trabajo que se distribuye entre las tareas paralelas.
- `calcular_fibonacci_paralelo(n_elementos, executor_type)`: construye un pool de trabajadores (hilos o procesos, según el parámetro) y les asigna el cálculo de `fibonacci(i)` para cada i entre 0 y n_elementos-1.
- `imprimir_resultados(...)`: único punto del programa que escribe en stdout, después de que todas las tareas han terminado y sus resultados están ordenados.
- `calcular_fibonacci_secuencial(...)`: versión de referencia sin paralelismo, usada para comparar tiempos.

### 1. ¿Cuáles ciclos `for` consideré paralelizables? ¿Por qué?

El ciclo que construye la lista/diccionario de futures —uno por cada valor de i en `range(n_elementos)`— es el que se paraleliza, delegando cada iteración a `executor.submit(fibonacci, i)`. Es paralelizable porque cada iteración es completamente independiente de las demás: `fibonacci(i)` no lee ni modifica ningún estado compartido con `fibonacci(j)`, y no existe ningún acumulador ni dependencia de orden entre iteraciones (cumple la propiedad de ser "embarrassingly parallel"). En cambio, el ciclo que recorre `as_completed(futures)` para recolectar los resultados y el ciclo final que los imprime se dejan secuenciales de forma deliberada: su cuerpo es trivial (una asignación o un print), por lo que paralelizarlos no traería ninguna ganancia real y, en el caso de la impresión, paralelizarlo introduciría precisamente la trampa serial que el taller pide evitar.

### 2. ¿Cómo evité las trampas seriales, especialmente en la impresión de resultados?

La estrategia fue separar completamente el cómputo de la E/S: ninguna tarea enviada al executor (`fibonacci`) contiene una sola instrucción de `print`. Cada tarea solo calcula y retorna un valor entero. Los resultados se van almacenando en una lista pre-dimensionada (`resultados = [0] * n_elementos`), indexando cada resultado en su posición correcta según el índice original i (no según el orden de llegada de `as_completed`). Solo después de que el bloque `with executor_type() as executor:` termina —es decir, cuando todas las tareas ya concluyeron— se llama a `imprimir_resultados()`, que es la única función del programa que escribe en stdout, y lo hace de forma secuencial y ordenada por índice. Así se evita tanto el entrelazado de líneas en consola como la impresión en un orden no determinista.

### 3. ¿Qué impacto tuvo la paralelización en el rendimiento del cálculo de Fibonacci?

Al ejecutar el script en este entorno (con un solo núcleo lógico disponible, según `os.cpu_count()`), la versión secuencial resultó más rápida que ambas versiones paralelas, y `ProcessPoolExecutor` fue la más lenta de las tres. Esto no es un error, sino una ilustración directa de la Ley de Amdahl y del modelo Work-Span: cuando N=20 valores de Fibonacci pequeños, el Work total es muy bajo (cada `fibonacci(i)` con i≤19 toma microsegundos), mientras que el overhead de crear hilos o procesos, serializar argumentos y sincronizar resultados es comparativamente alto. Con `ProcessPoolExecutor` el costo es aún mayor porque cada proceso hijo requiere su propio intérprete de Python. En una máquina con varios núcleos físicos y con valores de N más grandes (donde el Work por tarea crece exponencialmente por la recursión naive), se esperaría que `ProcessPoolExecutor` sí muestre una ganancia real, mientras que `ThreadPoolExecutor` seguiría limitado por el GIL de Python al tratarse de una carga puramente CPU-bound.

### 4. ¿Qué limitaciones encontré al intentar paralelizar el cálculo?

- El Global Interpreter Lock (GIL) de Python impide que varios hilos ejecuten bytecode de Python en verdadero paralelo, por lo que `ThreadPoolExecutor` no acelera cómputo puro; solo es útil para tareas que liberan el GIL (E/S, algunas extensiones en C).
- `ProcessPoolExecutor` sí logra paralelismo real de CPU, pero paga el costo de arrancar procesos independientes y serializar (pickle) los argumentos y resultados entre procesos, lo que añade overhead constante por tarea.
- La granularidad del problema importa: con valores pequeños de n, el trabajo de cada tarea es menor que el overhead de repartirla, por lo que el paralelismo resulta contraproducente (coincide con lo observado en la sección anterior).
- El número de núcleos físicos disponibles en la máquina es un límite duro: no importa cuántos hilos/procesos se lancen, el speedup real está acotado por el hardware (y, en este entorno de prueba, por un único núcleo lógico disponible).
- El algoritmo recursivo naive de Fibonacci recalcula subproblemas (no usa memoización), así que el Work crece exponencialmente con n; paralelizar por valor de i no corrige esa ineficiencia algorítmica interna, solo distribuye el trabajo ya de por sí redundante entre varios núcleos.

### 5. ¿Cómo escalaría la solución con más hilos/procesos o un N más grande?

Con un N más grande, el Work por tarea individual (`fibonacci(i)` para i grandes) crece exponencialmente debido a la recursión naive, por lo que el tiempo de cómputo de cada tarea empezaría a dominar claramente sobre el overhead fijo de crear y coordinar procesos; en ese régimen, `ProcessPoolExecutor` debería mostrar una ganancia de rendimiento clara frente a la versión secuencial, y esa ganancia debería seguir la Ley de Amdahl: acotada por la fracción secuencial del programa (creación del pool, recolección final, impresión) y, en la práctica, por el número de núcleos físicos disponibles. Aumentar el número de workers más allá del número de núcleos físicos no aporta paralelismo adicional real (solo agrega cambios de contexto), así que la estrategia de escalado correcta sería fijar `max_workers` cerca de `os.cpu_count()` y, adicionalmente, incorporar memoización (por ejemplo con `functools.lru_cache`) dentro de cada tarea para reducir el Work redundante de la recursión, combinando así una optimización algorítmica con la paralelización estructural.

### Código completo

```python
"""
Taller 1: Algoritmos Paralelos
Curso: Infraestructuras Paralelas y Distribuidas (750023C)
Reto: Cálculo paralelo de números de Fibonacci con concurrent.futures

Autor: Andrés Gerardo González Rosero
"""

import time
import concurrent.futures
import os

N = 20  # Cantidad de números de Fibonacci a calcular (0..N-1)


def fibonacci(n: int) -> int:
    """
    Calcula el n-ésimo número de Fibonacci de forma recursiva (naive).

    NOTA SOBRE PARALELIZACIÓN INTERNA:
    La recursión de esta función NO se paraleliza. Cada llamada
    fibonacci(n-1) depende únicamente de datos que ella misma genera,
    pero el árbol de recursión tiene demasiadas llamadas pequeñas y de
    corta duración. Crear un hilo/proceso por cada llamada generaría
    overhead de planificación mucho mayor que el trabajo útil realizado
    (el "trabajo" de cada nodo es ínfimo comparado con el costo de
    lanzar una tarea paralela). Por eso la unidad de paralelización
    elegida es "cada valor de n" y no "cada llamada recursiva".
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def calcular_fibonacci_paralelo(n_elementos: int, executor_type) -> list:
    """
    Calcula los primeros `n_elementos` números de Fibonacci en paralelo.

    CICLO FOR #1 (SÍ paralelizable):
        La construcción de la lista de futures, uno por cada valor de i,
        es perfectamente paralelizable: fibonacci(i) es independiente de
        fibonacci(j) para todo i != j. No hay dependencias de datos entre
        iteraciones (no hay lectura/escritura compartida, no hay
        acumuladores) → cumple la condición de "embarrassingly parallel".

    CICLO FOR #2 (recolección de resultados, NO paralelizable en la
    práctica):
        Recorrer `as_completed(futures)` para recoger los resultados sí
        es un ciclo for, pero su cuerpo (asignar resultados[i] = valor)
        es una operación de escritura sobre una estructura compartida.
        Aunque técnicamente cada escritura es a un índice distinto y
        podría hacerse en paralelo sin condición de carrera real, no
        tiene sentido paralelizarla: el "trabajo" de cada iteración es
        trivial (una asignación), así que el overhead de coordinación
        superaría cualquier beneficio. Se deja secuencial a propósito.
    """
    inicio = time.perf_counter()
    resultados = [0] * n_elementos

    # --- Ciclo paralelizable: se delega a un pool de procesos/hilos ---
    with executor_type() as executor:
        futures = {
            executor.submit(fibonacci, i): i for i in range(n_elementos)
        }

        # --- Ciclo de recolección: secuencial a propósito ---
        # Trampa serial evitada: NO se hace print() dentro de cada hilo.
        # Cada tarea (fibonacci) solo calcula y retorna un valor; no
        # escribe a stdout ni comparte estado mutable con otras tareas.
        # El main process/thread es el único que escribe en resultados[]
        # y el único que imprimirá, más adelante, de forma ordenada.
        for future in concurrent.futures.as_completed(futures):
            i = futures[future]
            resultados[i] = future.result()

    fin = time.perf_counter()
    tiempo_ejecucion = fin - inicio

    return resultados, tiempo_ejecucion


def imprimir_resultados(resultados: list, tiempo_ejecucion: float, etiqueta: str) -> None:
    """
    Única responsable de escribir en stdout.

    TRAMPA SERIAL EVITADA:
    Si cada worker imprimiera su propio resultado apenas terminara,
    el orden de salida dependería del orden de finalización de las
    tareas (no determinista) y, con ProcessPoolExecutor, los procesos
    hijos ni siquiera comparten el buffer de stdout del proceso padre
    de forma segura (puede haber líneas entrelazadas). La solución:
    los workers NUNCA imprimen; solo devuelven datos. Un único punto
    (esta función, ejecutada en el proceso/hilo principal) imprime
    todo al final, ya ordenado por índice.
    """
    print(f"\n--- {etiqueta} ---")
    for i, valor in enumerate(resultados):
        print(f"fibonacci({i}) = {valor}")
    print(f"Tiempo de ejecución: {tiempo_ejecucion:.4f} segundos")
    print(f"Núcleos disponibles en esta máquina: {os.cpu_count()}")


def calcular_fibonacci_secuencial(n_elementos: int) -> tuple:
    """Versión puramente secuencial, usada solo como referencia comparativa."""
    inicio = time.perf_counter()
    resultados = [fibonacci(i) for i in range(n_elementos)]
    fin = time.perf_counter()
    return resultados, fin - inicio


if __name__ == "__main__":
    # Línea base secuencial (sin paralelismo) para poder comparar.
    resultados_seq, tiempo_seq = calcular_fibonacci_secuencial(N)
    imprimir_resultados(resultados_seq, tiempo_seq, "Secuencial")

    # ThreadPoolExecutor: como fibonacci() es una función 100% CPU-bound
    # y escrita en Python puro, el GIL impide el paralelismo real entre
    # hilos durante el cómputo. Se incluye solo para comparar.
    resultados_hilos, tiempo_hilos = calcular_fibonacci_paralelo(
        N, concurrent.futures.ThreadPoolExecutor
    )
    imprimir_resultados(resultados_hilos, tiempo_hilos, "Paralelo (ThreadPoolExecutor)")

    # ProcessPoolExecutor: cada número de Fibonacci se calcula en un
    # proceso independiente, con su propio intérprete y su propio GIL,
    # por lo que sí hay paralelismo real de CPU en varios núcleos.
    resultados_procesos, tiempo_procesos = calcular_fibonacci_paralelo(
        N, concurrent.futures.ProcessPoolExecutor
    )
    imprimir_resultados(resultados_procesos, tiempo_procesos, "Paralelo (ProcessPoolExecutor)")

    print("\n=== Resumen comparativo ===")
    print(f"Secuencial:        {tiempo_seq:.4f} s")
    print(f"ThreadPoolExecutor: {tiempo_hilos:.4f} s")
    print(f"ProcessPoolExecutor:{tiempo_procesos:.4f} s")
```
