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