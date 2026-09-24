"""Temple simulado sobre el puzle 8 con h = Manhattan.

Como ΔE ∈ {-1,+1}, la regla de Metropolis se reduce a:
    ΔE = -1 → se acepta;   ΔE = +1 → se acepta con p(T) = e^(-1/T).
La dinámica depende de T solo a través de p. De ahí la calibración:
    T = -1/ln p,   T0 = -1/ln p0,   Tf = -1/ln pf,   α = (Tf/T0)^(1/(K-1)),
con K = B - 1 iteraciones (una evaluación inicial + una por iteración).

Decisiones:
- Vecino: uniforme entre los movimientos legales (2, 3 o 4 según el hueco).
- Se detiene al llegar a h = 0: h ≥ 0, así que es el óptimo global y se reconoce.
- Programa geométrico que ocupa exactamente el presupuesto.
- L = iteraciones por temperatura: la temperatura se actualiza cada L
  iteraciones con factor α^L, de modo que T0 y Tf no dependen de L.
"""
import math

from puzzle import ADJ, manhattan, delta_h, move


def calibrar(p0, pf, K):
    T0, Tf = -1 / math.log(p0), -1 / math.log(pf)
    alpha = (Tf / T0) ** (1 / (K - 1)) if K > 1 else 1.0
    return T0, alpha, Tf


def simulated_annealing(s0, budget, rng, p0, pf, L=1, trace=None):
    T0, alpha, _ = calibrar(p0, pf, budget - 1)
    aL = alpha ** L
    s, b = s0, s0.index(0)
    h = manhattan(s0)
    evals = 1
    camino = [s0]
    T = T0
    p = math.exp(-1.0 / T)
    it = 0
    while h > 0 and evals < budget:
        q = rng.choice(ADJ[b])
        d = delta_h(s, b, q)
        evals += 1
        acepta = d < 0 or rng.random() < p
        if acepta:
            s = move(s, b, q)
            b = q
            h += d
            camino.append(s)
        if trace is not None:
            trace.append((T, d > 0, acepta, h))
        it += 1
        if it % L == 0:
            T *= aL
            p = math.exp(-1.0 / T)
    return {"exito": h == 0, "evals": evals, "camino": camino}
