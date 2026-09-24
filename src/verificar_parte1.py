"""Parte 1: verificación de la representación y de la verdad de terreno.

Cada comprobación contrasta el código con un hecho conocido o con una
afirmación de D0. Si alguna falla, hay un error en puzzle.py o ground_truth.py.
"""
import time
import tracemalloc
from collections import Counter
from itertools import permutations

from puzzle import GOAL, manhattan, delta_h, neighbors, solvable
from ground_truth import bfs_from_goal

# --- BFS, con tiempo y memoria pico -------------------------------------------
tracemalloc.start()
t0 = time.perf_counter()
dist = bfs_from_goal()
t_bfs = time.perf_counter() - t0
_, pico = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"BFS: {len(dist)} estados, {t_bfs:.2f} s, memoria pico {pico / 2**20:.1f} MiB")

# 1. Tamaño del espacio alcanzable = 9!/2, y coincide con el criterio de paridad.
assert len(dist) == 181_440
resolubles = {p for p in permutations(range(9)) if solvable(p)}
assert resolubles == set(dist), "paridad de inversiones no coincide con alcanzabilidad"
print("OK  alcanzables = 181 440 = 9!/2, y coinciden con el criterio de paridad")

# 2. Distancia máxima conocida del puzle 8: 31 movimientos, 2 estados.
hist = Counter(dist.values())
dmax = max(hist)
assert dmax == 31 and hist[31] == 2
print(f"OK  d* máximo = {dmax} ({hist[31]} estados)")

# 3. Todo movimiento cambia h en exactamente ±1, y delta_h coincide con recalcular.
deltas = Counter()
for s in dist:
    b = s.index(0)
    hs = manhattan(s)
    for q, v in neighbors(s, b):
        dh = delta_h(s, b, q)
        assert dh == manhattan(v) - hs
        deltas[dh] += 1
assert set(deltas) == {-1, +1}
print(f"OK  Δh ∈ {{-1,+1}} en los {sum(deltas.values())} pares (estado, movimiento); "
      f"incremental = recálculo")

# 4. h ≤ d* (detector de errores, no justificación: ver D8).
assert all(manhattan(s) <= d for s, d in dist.items())
# 5. Consecuencia de 3: h(s) y d*(s) tienen la misma paridad.
assert all((d - manhattan(s)) % 2 == 0 for s, d in dist.items())
print("OK  h ≤ d* en todo estado, y d* − h siempre es par")

# 6. Con d* como objetivo no hay mínimos locales: todo s ≠ meta tiene un vecino con d*−1.
assert all(any(dist[v] == d - 1 for _, v in neighbors(s))
           for s, d in dist.items() if s != GOAL)
print("OK  con d* como objetivo, todo estado tiene un vecino que mejora")

# 7. Adelanto del paisaje con Manhattan: mínimos locales estrictos
#    (h > 0 y ningún vecino con h menor). Sin mesetas, "no mejora" = "todos empeoran".
minimos = [s for s in dist
           if s != GOAL and all(manhattan(v) > manhattan(s) for _, v in neighbors(s))]
print(f"    mínimos locales estrictos de Manhattan: {len(minimos)} "
      f"({100 * len(minimos) / len(dist):.2f} % de los estados)")

print("\nDistribución de d*:")
for d in range(dmax + 1):
    print(f"  {d:2d}: {hist[d]:6d}")
media = sum(d * c for d, c in hist.items()) / len(dist)
print(f"  media = {media:.2f}")
