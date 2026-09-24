"""Calidad del camino (D7)."""


def longitud_sin_ciclos(camino):
    """Borrado de bucles: al revisitar un estado se descarta el tramo intermedio.
    El resultado es un camino simple de s0 a la meta contenido en el recorrido."""
    pila, idx = [], {}
    for s in camino:
        if s in idx:
            i = idx[s]
            for t in pila[i + 1:]:
                del idx[t]
            del pila[i + 1:]
        else:
            idx[s] = len(pila)
            pila.append(s)
    return len(pila) - 1
