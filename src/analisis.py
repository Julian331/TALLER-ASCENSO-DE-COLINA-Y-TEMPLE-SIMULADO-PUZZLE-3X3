"""Resumen de la parte 4: tablas para el informe y datos para las figuras.

La unidad independiente es la instancia. Para cada instancia se calcula su tasa
de éxito (10 semillas); la comparación HC vs SA es PAREADA: diferencia de tasas
en la misma instancia, media y error estándar sobre instancias.
"""
import csv
import json
import statistics as st
from collections import defaultdict

from instancias import BANDAS

filas = list(csv.DictReader(open("../resultados/corridas.csv")))
for f in filas:
    for k in ("B", "inst", "d", "banda", "h0", "exito", "evals"):
        f[k] = int(f[k])
    f["t"] = float(f["t"])
    for k in ("cruda", "simple"):
        f[k] = int(f[k]) if f[k] != "" else None

PRES, ALGS = [100, 300, 1000, 3000, 10000], ["HC", "SA"]
tasa = defaultdict(list)                      # (B, alg, inst) -> éxitos
banda_inst = {}
por = defaultdict(list)                       # (B, alg) -> filas
for f in filas:
    tasa[(f["B"], f["alg"], f["inst"])].append(f["exito"])
    banda_inst[f["inst"]] = f["banda"]
    por[(f["B"], f["alg"])].append(f)
tasa = {k: sum(v) / len(v) for k, v in tasa.items()}
insts = sorted(banda_inst)


def media_ee(xs):
    return st.mean(xs), st.stdev(xs) / len(xs) ** 0.5


res = {"exito": {}, "dif": {}, "camino": {}, "evals_exito": {}, "us_eval": {}}
print("Éxito (media sobre instancias ± EE) y diferencia pareada SA − HC")
for B in PRES:
    for grupo in [None] + list(range(5)):
        sel = [i for i in insts if grupo is None or banda_inst[i] == grupo]
        g = "todas" if grupo is None else str(grupo)
        for a in ALGS:
            res["exito"][f"{B}|{a}|{g}"] = media_ee([tasa[(B, a, i)] for i in sel])
        dif = [tasa[(B, "SA", i)] - tasa[(B, "HC", i)] for i in sel]
        m, se = media_ee(dif)
        res["dif"][f"{B}|{g}"] = [m, se, m / se if se > 0 else float("inf")]
    hc, sa, d = res["exito"][f"{B}|HC|todas"], res["exito"][f"{B}|SA|todas"], res["dif"][f"{B}|todas"]
    print(f"  B={B:6d}  HC {hc[0]:.3f}±{hc[1]:.3f}  SA {sa[0]:.3f}±{sa[1]:.3f}  "
          f"SA−HC {d[0]:+.3f}±{d[1]:.3f} (z={d[2]:+.1f})")
    print("           por banda SA−HC: " + "  ".join(
        f"{res['dif'][f'{B}|{b}'][0]:+.2f}(z={res['dif'][f'{B}|{b}'][2]:+.1f})" for b in range(5)))

print("\nÉxito por banda")
for B in PRES:
    print(f"  B={B:6d}  " + "  ".join(
        f"[{lo}-{hi}] HC {res['exito'][f'{B}|HC|{b}'][0]:.2f} SA {res['exito'][f'{B}|SA|{b}'][0]:.2f}"
        for b, (lo, hi) in enumerate(BANDAS)))

print("\nCalidad del camino entre los éxitos (longitud / d*): mediana cruda | sin ciclos | % óptimos")
for B in PRES:
    for a in ALGS:
        ok = [r for r in por[(B, a)] if r["exito"]]
        cr = [r["cruda"] / r["d"] for r in ok]
        si = [r["simple"] / r["d"] for r in ok]
        opt = sum(r["simple"] == r["d"] for r in ok) / len(ok)
        res["camino"][f"{B}|{a}"] = {"cruda_med": st.median(cr), "simple_med": st.median(si),
                                     "cruda_q": [st.quantiles(cr, n=4)[0], st.quantiles(cr, n=4)[2]],
                                     "simple_q": [st.quantiles(si, n=4)[0], st.quantiles(si, n=4)[2]],
                                     "frac_optimo": opt, "n": len(ok)}
        print(f"  B={B:6d} {a}  {st.median(cr):6.2f} | {st.median(si):5.2f} | {100 * opt:5.1f} %  (n={len(ok)})")

print("\nEvaluaciones hasta el éxito (mediana) y µs por evaluación")
for B in PRES:
    for a in ALGS:
        rs = por[(B, a)]
        ok = [r["evals"] for r in rs if r["exito"]]
        us = 1e6 * sum(r["t"] for r in rs) / sum(r["evals"] for r in rs)
        res["evals_exito"][f"{B}|{a}"] = st.median(ok)
        res["us_eval"][f"{B}|{a}"] = us
        print(f"  B={B:6d} {a}  mediana {st.median(ok):7.1f}   {us:.2f} µs/eval")

res["memoria"] = json.load(open("../resultados/memoria.json"))
res["n_instancias"] = len(insts)
res["n_ejecuciones"] = len(filas)
json.dump(res, open("../resultados/resumen.json", "w"), indent=1)
