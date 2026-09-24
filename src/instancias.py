"""Muestra estratificada por d*, con conjuntos de calibración y prueba disjuntos.

Cinco bandas de d*; en cada una se muestrea uniformemente entre sus estados.
Tamaños (justificados en el informe): la varianza del éxito ENTRE instancias es
cientos de veces la varianza entre semillas de una misma instancia, así que la
precisión se compra con instancias, no con semillas.
  calibración: 20 instancias por banda × 5 semillas
  prueba:     100 instancias por banda × 10 semillas
Los parámetros de ambos algoritmos se eligen en calibración y se reportan en
prueba, para no ajustar al conjunto con el que se compara.
"""
import random

BANDAS = [(0, 10), (11, 15), (16, 20), (21, 25), (26, 31)]
CALIB_POR_BANDA, CALIB_SEMILLAS = 20, 5
PRUEBA_POR_BANDA, PRUEBA_SEMILLAS = 100, 10


def banda_de(d):
    for i, (a, b) in enumerate(BANDAS):
        if a <= d <= b:
            return i


def muestrear(dist, por_banda, seed, excluir=()):
    rng = random.Random(seed)
    excluir = set(excluir)
    out = []
    for a, b in BANDAS:
        pool = sorted(s for s, d in dist.items() if a <= d <= b and d > 0 and s not in excluir)
        out += rng.sample(pool, por_banda)
    return out


def conjuntos(dist):
    prueba = muestrear(dist, PRUEBA_POR_BANDA, seed=2026)
    calibracion = muestrear(dist, CALIB_POR_BANDA, seed=7, excluir=prueba)
    return calibracion, prueba
