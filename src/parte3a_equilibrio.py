"""Parte 3a: distribución de equilibrio del SA a temperatura fija, calculada exacta.

A T fija, el SA es una cadena de Markov (Metropolis). La propuesta elige
uniforme entre deg(s) vecinos (deg = 2, 3 o 4 según el hueco), así que el
balance detallado da
        π_p(s) ∝ deg(s) · p^h(s),   p = e^(-1/T).
Con los 181 440 estados se calcula exacto E_p[h] y π_p(meta) para cada p.
Esto dice, antes de ejecutar, en qué rango de p el SA "ve" el objetivo.
Se verifica con una cadena larga a p fija.
"""
import json
import math
import random
from collections import Counter

from ground_truth import bfs_from_goal
from puzzle import ADJ, GOAL, manhattan, delta_h, move

dist = bfs_from_goal()
c = Counter((manhattan(s), len(ADJ[s.index(0)])) for s in dist)   # (h, deg) -> nº
g = Counter()
for (h, _), n in c.items():
    g[h] += n
print("Densidad de estados g(h) (nº de tableros con Manhattan h):")
print("  " + ", ".join(f"{h}:{g[h]}" for h in sorted(g)))


def equilibrio(p):
    Z = sum(n * deg * p ** h for (h, deg), n in c.items())
    Eh = sum(n * deg * h * p ** h for (h, deg), n in c.items()) / Z
    Pmeta = 2 * 1 / Z                      # la meta tiene el hueco en esquina: deg = 2
    return Eh, Pmeta


ps = [i / 1000 for i in range(1, 1000)]
curva = [(p, *equilibrio(p)) for p in ps]
Eh_unif = equilibrio(1.0)[0]
print(f"\nE[h] con p = 1 (caminata aleatoria): {Eh_unif:.2f}")
print("   p       T      E_p[h]   π_p(meta)")
for p in (0.905, 0.7, 0.5, 0.37, 0.3, 0.2, 0.15, 0.1, 0.05, 0.02, 0.01, 0.001):
    Eh, Pm = equilibrio(p)
    print(f"  {p:5.3f}  {-1 / math.log(p):6.3f}  {Eh:7.2f}   {Pm:.4f}")


def umbral(f, objetivo):
    """Mayor p con f(p) <= objetivo (f creciente en p)."""
    mejor = None
    for p, Eh, Pm in curva:
        if f(Eh, Pm) <= objetivo:
            mejor = p
    return mejor


p_media = umbral(lambda Eh, Pm: -Pm, -0.5)         # π(meta) ≥ 0.5
p_uno = umbral(lambda Eh, Pm: Eh, 1.0)             # E[h] ≤ 1
p_rompe = umbral(lambda Eh, Pm: Eh, Eh_unif - 1)   # E[h] un punto bajo el azar
print(f"\nE[h] se separa del azar (≤ {Eh_unif - 1:.1f}) para p ≤ {p_rompe:.3f}  (T ≤ {-1 / math.log(p_rompe):.2f})")
print(f"E[h] ≤ 1                      para p ≤ {p_uno:.3f}  (T ≤ {-1 / math.log(p_uno):.3f})")
print(f"π(meta) ≥ 0.5                 para p ≤ {p_media:.3f}  (T ≤ {-1 / math.log(p_media):.3f})")

# --- Verificación: cadena larga a p fija ---------------------------------------
rng = random.Random(1)
for p in (0.3, 0.1):
    s = GOAL
    b = s.index(0)
    h = 0
    hist = Counter()
    pasos = 2_000_000
    for i in range(pasos):
        q = rng.choice(ADJ[b])
        d = delta_h(s, b, q)
        if d < 0 or rng.random() < p:
            s = move(s, b, q)
            b = q
            h += d
        hist[h] += 1
    Eh_emp = sum(k * v for k, v in hist.items()) / pasos
    Eh_teo, Pm_teo = equilibrio(p)
    print(f"verificación p={p}: E[h] teórico {Eh_teo:.3f} vs cadena {Eh_emp:.3f}; "
          f"π(meta) teórico {Pm_teo:.4f} vs cadena {hist[0] / pasos:.4f}")

json.dump({"g": dict(sorted(g.items())), "curva": curva, "Eh_unif": Eh_unif,
           "p_rompe": p_rompe, "p_uno": p_uno, "p_media": p_media},
          open("../resultados/parte3a.json", "w"))
