"""Figuras del informe (PDF vectorial para LaTeX + PNG de vista previa).

Colores: paleta categórica validada en orden fijo (azul = HC, aqua = SA); rampa
secuencial azul para magnitudes ordenadas (presupuestos, mapas de calor). Cada
serie lleva además marcador propio, para no depender solo del color.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

OUT = "../resultados"
os.makedirs(OUT, exist_ok=True)
R2 = json.load(open(f"{OUT}/parte2.json"))
R3a = json.load(open(f"{OUT}/parte3a.json"))
CAL = json.load(open(f"{OUT}/calibracion.json"))
RS = json.load(open(f"{OUT}/resumen.json"))

INK, INK2, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
COL = {"HC": "#2a78d6", "SA": "#1baf7a"}
MK = {"HC": "o", "SA": "^"}
NOMBRE = {"HC": "HC (mejor configuración)", "SA": "SA (mejor configuración)"}
RAMPA = ["#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#104281"]
AZUL = LinearSegmentedColormap.from_list(
    "azul", ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"])
ZONA = "#eef4fc"
PRES = [100, 300, 1000, 3000, 10000]
BANDAS = ["d* ≤ 10", "d* 11–15", "d* 16–20", "d* 21–25", "d* 26–31"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": BASE,
    "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "legend.frameon": False, "figure.dpi": 150, "savefig.bbox": "tight",
    "axes.titlesize": 9.5, "axes.titlecolor": INK, "lines.linewidth": 1.8,
    "pdf.fonttype": 42,
})


def guardar(fig, nombre):
    fig.savefig(f"{OUT}/{nombre}.pdf")
    fig.savefig(f"{OUT}/{nombre}.png", dpi=160)
    plt.close(fig)


# F1 — Conteo empírico de evaluaciones de HC contra la cota 3h+2 ----------------
ev = {int(h): v for h, v in R2["evals_por_h"].items()}
hs = sorted(ev)
fig, ax = plt.subplots(figsize=(4.6, 2.9))
ax.plot(hs, [3 * h + 2 for h in hs], color=MUTED, lw=1.2, ls="--")
ax.text(hs[-1], 3 * hs[-1] + 2, "cota 3h₀+2", color=INK2, ha="right", va="bottom", fontsize=8)
ax.plot(hs, [ev[h][1] for h in hs], color=COL["HC"], marker="o", ms=3.5, label="máximo observado")
ax.plot(hs, [ev[h][0] for h in hs], color=COL["HC"], alpha=0.55, marker="o", ms=3.5, label="media")
ax.set_xlabel("h(s₀) (Manhattan inicial)")
ax.set_ylabel("evaluaciones de h")
ax.legend(loc="upper left")
ax.set_title("HC simple sin reinicios, los 181 440 estados", loc="left")
guardar(fig, "f1_hc_evaluaciones")

# F2 — Equilibrio exacto E_p[h] y π_p(meta) en función de p ---------------------
p = [c[0] for c in R3a["curva"]]
Eh = [c[1] for c in R3a["curva"]]
Pm = [c[2] for c in R3a["curva"]]
elegidos_p = sorted({v["sa"]["p0"] for v in CAL["elegidos"].values()} |
                    {v["sa"]["pf"] for v in CAL["elegidos"].values()})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.6))
for ax, y, lab in ((a1, Eh, "E_p[h] en equilibrio"), (a2, Pm, "π_p(meta) en equilibrio")):
    ax.axvspan(0.05, 0.5, color=ZONA, lw=0)
    ax.plot(p, y, color=INK2)
    ax.set_xscale("log")
    ax.set_xlabel("p = e^(−1/T)   (escala log)")
    ax.set_title(lab, loc="left")
    for pe in elegidos_p:
        ax.axvline(pe, color=COL["SA"], lw=0.9, ls=":")
a1.axhline(R3a["Eh_unif"], color=MUTED, lw=0.9, ls=":")
a1.text(0.0012, R3a["Eh_unif"] + 0.3, "caminata aleatoria", color=INK2, fontsize=7.5)
a2.text(0.12, 0.93, "zona útil", color=INK2, fontsize=7.5, ha="center")
a2.text(0.34, 0.55, "p elegidos\nen calibración", color=INK2, fontsize=7, ha="left")
guardar(fig, "f2_equilibrio")

# F3 — Calibración de HC: éxito vs k, por variante y presupuesto ----------------
fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.7), sharey=True)
for ax, var, tit in ((axs[0], "simple", "Bajada simple + reinicios"),
                     (axs[1], "estocastico", "Bajada estocástica + reinicios")):
    ks = sorted({int(k.split("|")[2]) for k in CAL["hc"] if k.split("|")[1] == var})
    for B, c in zip(PRES, RAMPA):
        ax.plot(ks, [CAL["hc"][f"{B}|{var}|{k}"][0] for k in ks], color=c, marker="o", ms=3.5,
                label=f"B = {B}")
    e = [(CAL["elegidos"][str(B)]["hc"], B) for B in PRES]
    for (h, B), c in zip(e, RAMPA):
        if h["variante"] == var:
            ax.plot([h["k"]], [h["exito"]], marker="o", ms=8, mfc="none", mec=INK, mew=1.2)
    ax.set_xscale("symlog", linthresh=2)
    ax.set_xticks(ks, [str(k) for k in ks])
    ax.set_xlabel("k (pasos de la perturbación)")
    ax.set_title(tit, loc="left")
axs[0].set_ylabel("éxito (calibración)")
axs[1].legend(loc="upper left", fontsize=7.5)
guardar(fig, "f3_calibracion_hc")

# F4 — Mapas de calor de la calibración del SA ----------------------------------
P0 = [0.905, 0.7, 0.5, 0.37, 0.3, 0.2, 0.15, 0.1, 0.05]
PF = [0.5, 0.37, 0.3, 0.2, 0.15, 0.1, 0.05, 0.01, 0.001]
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.9), constrained_layout=True)
for ax, B in zip(axs, (100, 1000, 10000)):
    M = [[CAL["sa"].get(f"{B}|{p0}|{pf}", [float("nan")])[0] for pf in PF] for p0 in P0]
    vmax = max(v for fila in M for v in fila if v == v)
    im = ax.imshow(M, cmap=AZUL, vmin=0, vmax=vmax, aspect="auto")
    e = CAL["elegidos"][str(B)]["sa"]
    i, j = P0.index(e["p0"]), PF.index(e["pf"])
    ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, ec=INK, lw=1.4))
    ax.set_xticks(range(len(PF)), [str(x) for x in PF], rotation=90, fontsize=7)
    ax.set_yticks(range(len(P0)), [str(x) for x in P0], fontsize=7)
    ax.grid(False)
    ax.set_xlabel("p_f")
    ax.set_title(f"B = {B}  (máx {vmax:.2f})", loc="left")
    cb = fig.colorbar(im, ax=ax, shrink=0.8)
    cb.ax.tick_params(labelsize=7, color=MUTED)
    cb.outline.set_visible(False)
axs[0].set_ylabel("p₀")
guardar(fig, "f4_calibracion_sa")

# F5 — Éxito vs presupuesto: todas las instancias y por banda --------------------
fig, axs = plt.subplots(2, 3, figsize=(7.2, 4.6), sharex=True, sharey=True)
grupos = [("todas", "Todas las instancias")] + [(str(b), BANDAS[b]) for b in range(5)]
for ax, (g, tit) in zip(axs.flat, grupos):
    for a in ("HC", "SA"):
        m = [RS["exito"][f"{B}|{a}|{g}"][0] for B in PRES]
        se = [RS["exito"][f"{B}|{a}|{g}"][1] for B in PRES]
        ax.errorbar(PRES, m, yerr=[1.96 * s for s in se], color=COL[a], marker=MK[a], ms=4.5,
                    capsize=0, elinewidth=0.9, label=NOMBRE[a])
    ax.set_xscale("log")
    ax.set_xlim(70, 14000)
    ax.set_xticks(PRES, ["100", "300", "1k", "3k", "10k"])
    ax.minorticks_off()
    ax.set_title(tit, loc="left")
    ax.set_ylim(-0.03, 1.03)
for ax in axs[1]:
    ax.set_xlabel("presupuesto B (evaluaciones, log)")
for ax in axs[:, 0]:
    ax.set_ylabel("tasa de éxito")
h, l = axs[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.04), fontsize=8)
fig.tight_layout(rect=(0, 0.04, 1, 1))
guardar(fig, "f5_exito_presupuesto")

# F6 — Calidad del camino vs presupuesto ------------------------------------------
fig, ax = plt.subplots(figsize=(4.8, 3.0))
for a in ("HC", "SA"):
    cr = [RS["camino"][f"{B}|{a}"]["cruda_med"] for B in PRES]
    si = [RS["camino"][f"{B}|{a}"]["simple_med"] for B in PRES]
    ax.plot(PRES, cr, color=COL[a], marker=MK[a], ms=4.5, label=f"{a}: cruda")
    ax.plot(PRES, si, color=COL[a], marker=MK[a], ms=4.5, ls="--", mfc="white",
            label=f"{a}: sin ciclos")
ax.axhline(1, color=MUTED, lw=0.8)
ax.set_xscale("log")
ax.set_xticks(PRES, ["100", "300", "1k", "3k", "10k"])
ax.minorticks_off()
ax.set_yscale("log")
ax.set_xlabel("presupuesto B (evaluaciones, log)")
ax.set_ylabel("mediana de longitud / d*  (log)")
ax.set_title("Longitud del camino entre los éxitos", loc="left")
ax.legend(loc="upper left", fontsize=7.5)
guardar(fig, "f6_calidad_camino")
print("figuras listas")
