"""Parte 3c: iteraciones por temperatura L ∈ {1, 10, 50}.

Argumento: con el presupuesto fijo, T0 y Tf quedan fijados por (p0, pf); L solo
cambia cómo se escalonan las mismas temperaturas entre ambos extremos. Si la
configuración óptima es de temperatura casi constante, L no puede importar.
Se comprueba en el conjunto de calibración con:
  (a) la configuración elegida para cada presupuesto;
  (b) una configuración que sí enfría (p0 = 0.5, pf = 0.01), donde L podría
      notarse. Si tampoco importa ahí, L no es un parámetro relevante.
"""
import json
import random
import statistics as st

from ground_truth import bfs_from_goal
from instancias import conjuntos, CALIB_SEMILLAS
from sa import simulated_annealing

dist = bfs_from_goal()
calib, _ = conjuntos(dist)
eleg = json.load(open("../resultados/calibracion.json"))["elegidos"]
LS = [1, 10, 50]
out = {}
for B in (100, 300, 1000, 3000, 10000):
    e = eleg[str(B)]["sa"]
    for nombre, p0, pf in (("elegida", e["p0"], e["pf"]), ("enfria", 0.5, 0.01)):
        fila = []
        for L in LS:
            tasas = []
            for i, s in enumerate(calib):
                ok = sum(simulated_annealing(s, B, random.Random(f"L|{B}|{nombre}|{L}|{i}|{m}"),
                                             p0, pf, L=L)["exito"] for m in range(CALIB_SEMILLAS))
                tasas.append(ok / CALIB_SEMILLAS)
            fila.append((st.mean(tasas), st.stdev(tasas) / len(tasas) ** 0.5))
        out[f"{B}|{nombre}"] = {"p0": p0, "pf": pf, "L": dict(zip(LS, fila))}
        print(f"B={B:6d} {nombre:8s} (p0={p0}, pf={pf}): " +
              "  ".join(f"L={L}: {m:.3f}±{se:.3f}" for L, (m, se) in zip(LS, fila)))
json.dump(out, open("../resultados/iteraciones_por_T.json", "w"), indent=1)
