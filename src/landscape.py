"""Análisis exacto del paisaje de Manhattan sobre los 181 440 estados.

Barrera de escape: B(s) = mínimo, sobre todos los caminos de s a la meta, de
la h máxima que se alcanza en el camino. La barrera b(s) = B(s) - h(s) es
cuánto hay que subir obligatoriamente para llegar a la meta desde s. Para HC
es infranqueable si b > 0; para SA fija cuántos empeoramientos seguidos
necesita aceptar. Se calcula con un Dijkstra "minimax" desde la meta
(el grafo es no dirigido).
"""
import heapq

from puzzle import GOAL, manhattan, neighbors


def minimax_barrier(states):
    h = {s: manhattan(s) for s in states}
    B = {GOAL: 0}
    heap = [(0, GOAL)]
    done = set()
    while heap:
        key, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        for _, v in neighbors(u):
            nk = max(key, h[v])
            if nk < B.get(v, 1 << 30):
                B[v] = nk
                heapq.heappush(heap, (nk, v))
    return {s: B[s] - h[s] for s in states}, h
