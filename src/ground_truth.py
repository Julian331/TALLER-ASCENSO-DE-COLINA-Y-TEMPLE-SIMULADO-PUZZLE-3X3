"""Verdad de terreno: d*(s) para todo estado alcanzable, por BFS desde la meta.

Los movimientos son reversibles, así que la distancia desde la meta es la
distancia hasta la meta. Una sola pasada da d* para los 181 440 estados.
"""
from collections import deque

from puzzle import GOAL, neighbors


def bfs_from_goal():
    """Devuelve dict estado -> d*. Guarda O(|S|) estados: es el costo de memoria
    con el que se compara la búsqueda local (D4)."""
    dist = {GOAL: 0}
    cola = deque([GOAL])
    while cola:
        s = cola.popleft()
        d = dist[s] + 1
        for _, v in neighbors(s):
            if v not in dist:
                dist[v] = d
                cola.append(v)
    return dist
