"""Puzle 8: representación, movimientos, heurística Manhattan y resolubilidad.

Estado: tupla de 9 enteros en orden de filas; 0 es el hueco.
Meta:   (1, 2, 3,
         4, 5, 6,
         7, 8, 0)
"""

N = 3
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# ADJ[p] = casillas vecinas de la posición p (a donde puede ir el hueco).
ADJ = []
for p in range(N * N):
    r, c = divmod(p, N)
    vecinos = []
    if r > 0:     vecinos.append(p - N)
    if r < N - 1: vecinos.append(p + N)
    if c > 0:     vecinos.append(p - 1)
    if c < N - 1: vecinos.append(p + 1)
    ADJ.append(tuple(vecinos))

# MD[t][p] = distancia Manhattan de la ficha t en la posición p a su casilla meta.
# El hueco (t = 0) no cuenta: MD[0][p] = 0 para todo p.
_meta_pos = {t: i for i, t in enumerate(GOAL)}
MD = [[0] * (N * N) for _ in range(N * N)]
for t in range(1, N * N):
    gr, gc = divmod(_meta_pos[t], N)
    for p in range(N * N):
        r, c = divmod(p, N)
        MD[t][p] = abs(r - gr) + abs(c - gc)


def manhattan(s):
    """h(s) completa, O(n^2). Solo se usa al iniciar una corrida y para verificar."""
    return sum(MD[t][p] for p, t in enumerate(s))


def delta_h(s, blank, q):
    """Cambio de h al mover el hueco de `blank` a `q`, O(1).

    La ficha t = s[q] pasa de q a blank; es la única que cambia de lugar.
    """
    t = s[q]
    return MD[t][blank] - MD[t][q]


def move(s, blank, q):
    """Tablero resultante de mover el hueco de `blank` a `q`."""
    l = list(s)
    l[blank], l[q] = l[q], l[blank]
    return tuple(l)


def neighbors(s, blank=None):
    """Genera (q, s') para cada movimiento legal. q es la nueva posición del hueco."""
    if blank is None:
        blank = s.index(0)
    for q in ADJ[blank]:
        yield q, move(s, blank, q)


def inversions(s):
    fichas = [t for t in s if t != 0]
    return sum(1 for i in range(len(fichas)) for j in range(i + 1, len(fichas))
               if fichas[i] > fichas[j])


def solvable(s):
    """Con ancho impar (3), s es alcanzable desde GOAL si y solo si su número de
    inversiones tiene la misma paridad que el de GOAL (que es 0)."""
    return inversions(s) % 2 == 0


def show(s):
    return "\n".join(" ".join(str(t) if t else "_" for t in s[r * N:(r + 1) * N])
                     for r in range(N))
