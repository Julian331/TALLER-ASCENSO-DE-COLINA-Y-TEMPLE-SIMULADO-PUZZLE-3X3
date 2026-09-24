"""Ascenso de colinas: variantes simple, más pronunciado (equivalente), estocástica
y con reinicios.

- Simple: primer vecino que mejora, en orden fijo ADJ[b] (arriba, abajo,
  izquierda, derecha del hueco). Determinista → evaluable exactamente.
- Más pronunciado: con Δh ∈ {-1,+1} toda mejora vale -1, así que con el mismo
  orden de desempate recorre los mismos tableros que la simple y evalúa más
  vecinos. No se implementa aparte: queda dominada.
- Estocástica: evalúa los vecinos y elige uniformemente entre los que mejoran.
- Con reinicios: tras cada bajada fallida, caminata aleatoria de k pasos desde s0
  (sin retroceso inmediato; cada paso cuesta una evaluación) y nueva bajada.
  Con la bajada estocástica tiene sentido k = 0 (repetir la bajada desde s0).

Unidad de costo: 1 evaluación = h de un tablero candidato (h(s0) al inicio y
cada Δh). Se omite siempre el movimiento que deshace el anterior (Δh = +1).
"""
from puzzle import ADJ, manhattan, delta_h, move


def descent(s, budget=None, keep_path=False, h=None, evals=0, prev_blank=None,
            rng=None):
    """Una bajada desde s. rng=None → simple; rng → estocástica.

    Devuelve (s_final, h_final, evals, pasos, camino).
    """
    b = s.index(0)
    if h is None:
        h = manhattan(s)
        evals += 1
    path = [s] if keep_path else None
    pasos = 0
    while h > 0:
        if rng is None:                       # --- simple: primera mejora
            q_mejor = None
            for q in ADJ[b]:
                if q == prev_blank:
                    continue
                if budget is not None and evals >= budget:
                    return s, h, evals, pasos, path
                evals += 1
                if delta_h(s, b, q) < 0:
                    q_mejor = q
                    break
        else:                                 # --- estocástica: todas las mejoras
            mejoras = []
            for q in ADJ[b]:
                if q == prev_blank:
                    continue
                if budget is not None and evals >= budget:
                    return s, h, evals, pasos, path
                evals += 1
                if delta_h(s, b, q) < 0:
                    mejoras.append(q)
            q_mejor = rng.choice(mejoras) if mejoras else None
        if q_mejor is None:
            break                             # mínimo local
        s = move(s, b, q_mejor)
        prev_blank, b = b, q_mejor
        h -= 1
        pasos += 1
        if keep_path:
            path.append(s)
    return s, h, evals, pasos, path


def hc_restarts(s0, budget, rng, k=10, estocastico=False):
    """HC con reinicios dentro de un presupuesto de evaluaciones.

    Devuelve dict con exito, evals, camino (desde s0) y reinicios.
    """
    drng = rng if estocastico else None
    s, h, evals, _, path = descent(s0, budget=budget, keep_path=True, rng=drng)
    h0 = manhattan(s0)
    reinicios = 0
    while h > 0 and evals < budget:
        reinicios += 1
        w, b, hw, prev = s0, s0.index(0), h0, None
        walk = [s0]
        for _ in range(k):
            if evals >= budget:
                break
            q = rng.choice([q for q in ADJ[b] if q != prev])
            evals += 1
            hw += delta_h(w, b, q)
            w = move(w, b, q)
            prev, b = b, q
            walk.append(w)
            if hw == 0:
                break
        if hw == 0:
            s, h, path = w, 0, walk
            break
        if evals >= budget:
            break
        s, h, evals, _, dpath = descent(w, budget=budget, keep_path=True, h=hw,
                                        evals=evals, prev_blank=prev, rng=drng)
        path = walk + dpath[1:]
    return {"exito": h == 0, "evals": evals, "camino": path, "reinicios": reinicios}


def exito_estocastico_exacto(dist):
    """P(éxito) exacta de UNA bajada estocástica desde cada estado.

    P(meta) = 1; si s no tiene vecinos que mejoren, P(s) = 0; si no,
    P(s) = promedio de P(s') sobre los vecinos que mejoran (h(s') = h(s) - 1).
    Se resuelve en orden creciente de h. En la primera bajada no hay movimiento
    anterior, así que se consideran todos los vecinos; en los pasos siguientes
    el inverso nunca mejora, así que excluirlo no cambia el conjunto de mejoras.
    """
    from puzzle import neighbors
    hs = {s: manhattan(s) for s in dist}
    P = {}
    for s in sorted(dist, key=hs.get):
        if hs[s] == 0:
            P[s] = 1.0
            continue
        mej = [v for _, v in neighbors(s) if hs[v] < hs[s]]
        P[s] = sum(P[v] for v in mej) / len(mej) if mej else 0.0
    return P
