"""Parte 4: comparación en el conjunto de PRUEBA, cada algoritmo en su mejor
configuración para cada presupuesto (elegida en calibración).

500 instancias (100 por banda de d*) × 10 semillas × 5 presupuestos × 2
algoritmos = 50 000 ejecuciones. Una fila por ejecución en CSV. Las mismas
instancias para los dos algoritmos: la comparación es pareada por instancia.
"""
import csv
import json
import random
import time
import tracemalloc

from ground_truth import bfs_from_goal
from hc import hc_restarts
from instancias import conjuntos, banda_de, PRUEBA_SEMILLAS
from metricas import longitud_sin_ciclos
from puzzle import manhattan
from sa import simulated_annealing

dist = bfs_from_goal()
_, prueba = conjuntos(dist)
eleg = json.load(open("../resultados/calibracion.json"))["elegidos"]
PRES = [100, 300, 1000, 3000, 10000]


def algoritmos(B):
    h, s = eleg[str(B)]["hc"], eleg[str(B)]["sa"]
    est = h["variante"] == "estocastico"
    return {
        "HC": lambda x, r: hc_restarts(x, B, r, k=h["k"], estocastico=est),
        "SA": lambda x, r: simulated_annealing(x, B, r, s["p0"], s["pf"]),
    }


filas = []
t_ini = time.perf_counter()
for B in PRES:
    for nombre, f in algoritmos(B).items():
        for i, s in enumerate(prueba):
            d = dist[s]
            for sem in range(PRUEBA_SEMILLAS):
                rng = random.Random(f"prueba|{B}|{nombre}|{i}|{sem}")
                t0 = time.perf_counter()
                r = f(s, rng)
                dt = time.perf_counter() - t0
                ok = r["exito"]
                filas.append({
                    "B": B, "alg": nombre, "inst": i, "d": d, "banda": banda_de(d),
                    "h0": manhattan(s), "semilla": sem, "exito": int(ok),
                    "evals": r["evals"],
                    "cruda": len(r["camino"]) - 1 if ok else "",
                    "simple": longitud_sin_ciclos(r["camino"]) if ok else "",
                    "t": dt,
                })
        print(f"B={B:6d} {nombre} listo ({time.perf_counter() - t_ini:.0f} s)", flush=True)

with open("../resultados/corridas.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(filas[0]))
    w.writeheader()
    w.writerows(filas)
print(f"{len(filas)} ejecuciones guardadas")

# Memoria pico de una ejecución (B = 10 000, instancia más difícil), incluido el
# camino que se almacena para medir su calidad (sin él, el estado es O(1)).
s = max(prueba, key=lambda x: dist[x])
mem = {}
for nombre, f in algoritmos(10000).items():
    tracemalloc.start()
    f(s, random.Random(0))
    mem[nombre] = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
tracemalloc.start()
bfs_from_goal()
mem["BFS"] = tracemalloc.get_traced_memory()[1]
tracemalloc.stop()
print("Memoria pico (bytes):", mem)
json.dump(mem, open("../resultados/memoria.json", "w"))
