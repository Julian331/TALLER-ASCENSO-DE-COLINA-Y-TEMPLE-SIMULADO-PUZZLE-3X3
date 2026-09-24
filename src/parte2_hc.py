"""Parte 2: ascenso de colinas, evaluado EXACTAMENTE sobre los 181 440 estados.

HC sin reinicios es determinista (D11), así que no se muestrea: se ejecuta desde
cada estado resoluble. Comprueba además las afirmaciones teóricas:
  T1. evaluaciones ≤ 3·h(s0) + 2              (cota de costo)
  T2. éxito ⇒ h(s0) = d*(s0) y camino óptimo  (consecuencia de Δh = ±1)
y mide la barrera de escape de los estados donde HC falla.
"""
import json
import os
import random
import time
from collections import Counter, defaultdict

from ground_truth import bfs_from_goal
from hc import descent
from landscape import minimax_barrier
from puzzle import manhattan

os.makedirs("../resultados", exist_ok=True)
dist = bfs_from_goal()

# --- HC exacto ------------------------------------------------------------------
t0 = time.perf_counter()
por_d = defaultdict(lambda: [0, 0])          # d* -> [exitos, total]
evals_por_h = defaultdict(list)              # h0 -> lista de evaluaciones
h_igual_d = Counter()                        # d* -> nº estados con h = d*
fallos, minimos_alcanzados = [], Counter()
exceso_max = -10**9
total_evals = 0
for s, d in dist.items():
    h0 = manhattan(s)
    sf, hf, ev, pasos, _ = descent(s)
    total_evals += ev
    ok = hf == 0
    por_d[d][0] += ok
    por_d[d][1] += 1
    evals_por_h[h0].append(ev)
    h_igual_d[d] += (h0 == d)
    if h0 > 0:
        exceso_max = max(exceso_max, ev - 3 * h0)
    if ok:
        # T2: el camino tiene h0 pasos y no puede ser más corto que d*.
        assert pasos == h0 == d, (s, pasos, h0, d)
    else:
        fallos.append(s)
        minimos_alcanzados[sf] += 1
t_hc = time.perf_counter() - t0

n = len(dist)
exitos = sum(v[0] for v in por_d.values())
print(f"HC exacto: {exitos}/{n} éxitos = {100 * exitos / n:.2f} %  "
      f"({total_evals} evaluaciones, {t_hc:.1f} s, "
      f"{1e6 * t_hc / total_evals:.2f} µs/evaluación)")
assert exceso_max <= 2
print(f"T1 OK  máx(evals − 3·h0) = {exceso_max}  → evals ≤ 3·h(s0) + 2")
print("T2 OK  todo éxito tiene h(s0) = d*(s0) y camino de longitud óptima")
n_hd = sum(h_igual_d.values())
print(f"       estados con h = d*: {n_hd} ({100 * n_hd / n:.2f} %) — cota superior del éxito")
print(f"       de ellos HC resuelve {exitos} ({100 * exitos / n_hd:.1f} %)")
print(f"       mínimos locales distintos donde termina HC: {len(minimos_alcanzados)}")

# --- Barreras de escape --------------------------------------------------------
barrera, hmap = minimax_barrier(list(dist))
b_fallos = Counter(barrera[s] for s in fallos)
b_todos = Counter(barrera.values())
# Coherencia: si HC tiene éxito, recorrió un camino monótono → barrera 0.
set_fallos = set(fallos)
assert all(barrera[s] == 0 for s in dist if s not in set_fallos)
# --- Subidas obligatorias u(s) = (d* − h)/2 -------------------------------------
# Un camino de longitud L con a subidas y L−a bajadas cumple (L−a) − a = h(s),
# así que a = (L − h)/2 y el mínimo es u(s) = (d* − h)/2 (entero por la paridad).
# Consecuencia: existe una bajada monótona ⇔ u = 0 ⇔ h = d*.
u = {s: (d - manhattan(s)) // 2 for s, d in dist.items()}
assert all(u[s] == 0 for s in dist if s not in set_fallos)
u_todos, u_fallos = Counter(u.values()), Counter(u[s] for s in fallos)
print("\nSubidas obligatorias u(s) = (d* − h)/2")
print("  u    todos   estados donde HC falla")
for k in sorted(u_todos):
    print(f"  {k:2d} {u_todos[k]:8d} {u_fallos.get(k, 0):8d}")
media_u = sum(u.values()) / n
print(f"  media u = {media_u:.2f}")
n_fallo_u0 = u_fallos.get(0, 0)
print(f"  fallos con u = 0 (había bajada monótona, el desempate fijo la perdió): {n_fallo_u0}")
print("\nAltura de barrera b(s) = (h máx. obligatoria en el camino a la meta) − h(s)")
print("  b    todos   estados donde HC falla")
for b in sorted(b_todos):
    print(f"  {b:2d} {b_todos[b]:8d} {b_fallos.get(b, 0):8d}")

# --- HC estocástico: probabilidad de éxito exacta y verificación ---------------
from hc import exito_estocastico_exacto
from instancias import BANDAS, banda_de
P = exito_estocastico_exacto(dist)
p_est = sum(P.values()) / n
print(f"\nHC estocástico (una bajada): éxito exacto = {100 * p_est:.2f} %  "
      f"(simple: {100 * exitos / n:.2f} %, techo u = 0: {100 * n_hd / n:.2f} %)")
# Coherencia con el corolario: P > 0 solo donde u = 0.
assert all(P[s] == 0 for s in dist if u[s] > 0)
# Verificación por simulación en estados con 0 < P < 1.
rng = random.Random(0)
intermedios = [s for s in dist if 0 < P[s] < 1]
muestra = rng.sample(intermedios, 40)
err = []
for s in muestra:
    ok = sum(descent(s, rng=rng)[1] == 0 for _ in range(2000))
    err.append(abs(ok / 2000 - P[s]))
print(f"verificación: 40 estados × 2000 bajadas, error máx. |sim − exacto| = {max(err):.3f}")
# Por banda de d*: simple, estocástico y techo.
banda_hc = {}
for bi, (lo, hi) in enumerate(BANDAS):
    est = [s for s in dist if lo <= dist[s] <= hi and dist[s] > 0]
    simple = sum(descent(s)[1] == 0 for s in est) / len(est)
    estoc = sum(P[s] for s in est) / len(est)
    techo = sum(u[s] == 0 for s in est) / len(est)
    banda_hc[bi] = [simple, estoc, techo]
    print(f"  d* {lo:2d}-{hi:2d}: simple {simple:.3f}  estocástico {estoc:.3f}  techo {techo:.3f}")
pasos_medios = sum(descent(s)[3] for s in dist) / n
print(f"pasos medios de una bajada simple: {pasos_medios:.2f}")

json.dump({
    "exito_por_d": {d: v for d, v in sorted(por_d.items())},
    "h_igual_d_por_d": dict(sorted(h_igual_d.items())),
    "evals_por_h": {h: [sum(v) / len(v), max(v), min(v), len(v)]
                    for h, v in sorted(evals_por_h.items())},
    "barrera_todos": dict(sorted(b_todos.items())),
    "barrera_fallos": dict(sorted(b_fallos.items())),
    "u_todos": dict(sorted(u_todos.items())),
    "u_fallos": dict(sorted(u_fallos.items())),
    "media_u": media_u, "fallos_u0": n_fallo_u0,
    "max_exceso_evals": exceso_max,
    "exitos": exitos, "n": n, "n_h_igual_d": n_hd,
    "minimos_distintos": len(minimos_alcanzados),
    "us_por_eval": 1e6 * t_hc / total_evals,
    "exito_estocastico": p_est, "banda_hc": banda_hc, "pasos_medios": pasos_medios,
}, open("../resultados/parte2.json", "w"), indent=1)
