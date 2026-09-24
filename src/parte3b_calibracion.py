"""Parte 3b: calibración de AMBOS algoritmos en el conjunto de CALIBRACIÓN.

Mismo protocolo para los dos: para cada presupuesto B se prueban todas las
configuraciones de una rejilla y se elige la de mayor tasa de éxito.
  HC:  bajada simple con k ∈ {2,5,10,20,40};
       bajada estocástica con k ∈ {0,2,5,10,20,40} (k = 0: repetir la bajada
       desde s0, que solo tiene sentido si la bajada es aleatoria).
  SA:  (p0, pf) en una rejilla 9 × 9 con pf ≤ p0 que cubre de sobra la zona
       útil derivada del equilibrio (0.05 ≤ p ≤ 0.5); p0 = pf es temperatura
       constante. Enfriar (pf < p0) y no enfriar compiten en igualdad.
Semillas: random.Random(cadena), determinista entre ejecuciones.
"""
import json
import statistics as st
import sys
import time
import random

from ground_truth import bfs_from_goal
from hc import hc_restarts
from instancias import conjuntos, CALIB_SEMILLAS
from sa import simulated_annealing

PRES = [100, 300, 1000, 3000, 10000]
P0 = [0.905, 0.7, 0.5, 0.37, 0.3, 0.2, 0.15, 0.1, 0.05]
PF = [0.5, 0.37, 0.3, 0.2, 0.15, 0.1, 0.05, 0.01, 0.001]
HC_CONF = [("simple", k) for k in (2, 5, 10, 20, 40)] + \
          [("estocastico", k) for k in (0, 2, 5, 10, 20, 40)]

dist = bfs_from_goal()
calib, _ = conjuntos(dist)


def evaluar(f, etiqueta):
    """Tasa de éxito media sobre instancias y su error estándar."""
    tasas = []
    for i, s in enumerate(calib):
        ok = 0
        for sem in range(CALIB_SEMILLAS):
            ok += f(s, random.Random(f"{etiqueta}|{i}|{sem}"))["exito"]
        tasas.append(ok / CALIB_SEMILLAS)
    return st.mean(tasas), st.stdev(tasas) / len(tasas) ** 0.5


res = {"hc": {}, "sa": {}, "elegidos": {}}
t0 = time.perf_counter()
for B in PRES:
    for var, k in HC_CONF:
        est = var == "estocastico"
        res["hc"][f"{B}|{var}|{k}"] = evaluar(
            lambda s, r: hc_restarts(s, B, r, k=k, estocastico=est), f"hc|{B}|{var}|{k}")
    for p0 in P0:
        for pf in PF:
            if pf <= p0:
                res["sa"][f"{B}|{p0}|{pf}"] = evaluar(
                    lambda s, r: simulated_annealing(s, B, r, p0, pf), f"sa|{B}|{p0}|{pf}")
    hc_b = max(((v[0], k) for k, v in res["hc"].items() if k.startswith(f"{B}|")))
    sa_b = max(((v[0], k) for k, v in res["sa"].items() if k.startswith(f"{B}|")))
    _, var, k = hc_b[1].split("|")
    _, p0, pf = sa_b[1].split("|")
    res["elegidos"][B] = {"hc": {"variante": var, "k": int(k), "exito": hc_b[0],
                                 "ee": res["hc"][hc_b[1]][1]},
                          "sa": {"p0": float(p0), "pf": float(pf), "exito": sa_b[0],
                                 "ee": res["sa"][sa_b[1]][1]}}
    print(f"B={B:6d}  HC: {var} k={k} → {hc_b[0]:.3f}   "
          f"SA: p0={p0} pf={pf} → {sa_b[0]:.3f}   ({time.perf_counter() - t0:.0f} s)")
    sys.stdout.flush()

print("\nHC por configuración (éxito en calibración):")
print("  variante      k " + "".join(f"{B:>8d}" for B in PRES))
for var, k in HC_CONF:
    print(f"  {var:12s} {k:2d} " + "".join(f"{res['hc'][f'{B}|{var}|{k}'][0]:8.3f}" for B in PRES))

for B in PRES:
    print(f"\nSA, B = {B} (filas p0, columnas pf)")
    print("   p0\\pf " + "".join(f"{pf:>7}" for pf in PF))
    for p0 in P0:
        print(f"  {p0:6.3f} " + "".join(
            f"{res['sa'][f'{B}|{p0}|{pf}'][0]:7.3f}" if f"{B}|{p0}|{pf}" in res["sa"] else "      -"
            for pf in PF))

json.dump(res, open("../resultados/calibracion.json", "w"), indent=1)
