# Laboratorio: ascenso de colinas vs temple simulado en el puzle 3×3

Comparación de ascenso de colinas (HC) y temple simulado (SA) en el puzle 8
con heurística Manhattan, cada algoritmo en su mejor configuración y con el
mismo presupuesto de evaluaciones, más el análisis de complejidad
computacional. Todos los parámetros se eligen con el mismo protocolo de
calibración, en un conjunto de instancias distinto del de prueba.

## Requisitos

- Python 3.9 o superior
- `matplotlib` (solo para las figuras)

```bash
pip install matplotlib
```

## Ejecución

Todos los scripts se ejecutan desde `src/`, en este orden:

```bash
cd src
python3 verificar_parte1.py          # representación + BFS: 7 comprobaciones
python3 parte2_hc.py                 # HC simple y estocástico, exactos sobre los 181 440 estados
python3 parte3a_equilibrio.py        # equilibrio exacto del SA en función de p
python3 parte3b_calibracion.py       # calibración de HC y SA, 5 presupuestos (≈4 min)
python3 parte3c_iteraciones_por_T.py # comprobación de L (iteraciones por temperatura)
python3 parte4_experimento.py        # 50 000 ejecuciones en el conjunto de prueba (≈1 min)
python3 analisis.py                  # comparación pareada -> resultados/resumen.json
python3 figuras.py                   # figuras -> resultados/f*.pdf y f*.png
```

Todo es determinista (un generador con semilla fija por ejecución): al
repetir el pipeline completo, las ejecuciones y los JSON salen idénticos. Solo
cambian los tiempos de reloj.

## Informe

```bash
cd informe && pdflatex informe.tex && pdflatex informe.tex
```

Si Latin Modern está instalado (MiKTeX, TeX Live completo, Overleaf), se usa
con codificación T1; si no, el documento compila con Computer Modern.

## Estructura

```
src/
  puzzle.py                   estado, movimientos, Manhattan (completa e incremental), paridad
  ground_truth.py             BFS desde la meta -> d*(s) para todos los estados
  hc.py                       HC simple, estocástico (con éxito exacto) y con reinicios
  sa.py                       SA con programa calibrado por (p0, pf) y presupuesto; L iteraciones por T
  landscape.py                altura de barrera (Dijkstra minimax)
  instancias.py               bandas de d*, conjuntos de calibración y prueba disjuntos
  metricas.py                 longitud de camino sin ciclos (borrado de bucles)
  verificar_parte1.py         comprobaciones de la representación
  parte2_hc.py                HC exacto, cota 3h+2, subidas obligatorias u
  parte3a_equilibrio.py       π_p(s) ∝ deg(s)·p^h(s), verificado con cadenas largas
  parte3b_calibracion.py      rejillas de HC (variante × k) y SA (p0 × pf) por presupuesto
  parte3c_iteraciones_por_T.py  L ∈ {1, 10, 50}
  parte4_experimento.py       comparación a presupuesto igualado
  analisis.py                 resumen con diferencias pareadas por instancia
  figuras.py                  6 figuras
resultados/                   JSON, CSV de ejecuciones, figuras, logs
informe/                      informe.tex, informe.pdf, img/logo_usa.png
```
