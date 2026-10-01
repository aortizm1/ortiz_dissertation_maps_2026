#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Map 2.2 — Financial transactions, powers of attorney, and sales made by Don Luis de
Acuña while in Chocó, 1715–1717.

Same conventions as Maps 1.1 and 1.2: each line joins the place in Chocó where Acuña
wrote the document to the city where it was used or notarized; colour = type, width =
value in pesos (a thin dashed line for the power of attorney, which has no value),
label = month and year. The spread of starting points, from Tamaná and Los Brazos in
Nóvita to his mine on the Naurita and Quibdó in Citará, shows his move north. A
zoom-in shows Citará: Quibdó, Lloró, Bebará, his mine on the Naurita and his fields
on the Neguá.

Data: data/events_ch2.csv (map 2.2 rows), data/places.csv, data/roads.geojson.

Run:  ../.venv/bin/python map_transactions_1715_1717.py
Out:  outputs/map_transactions_1715_1717.png (300 dpi) and .pdf
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("outputs", exist_ok=True)

import unicodedata
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import basemap as bm

YEAR_BOUNDS = 1715
FRAME = dict(lon=(-78.9, -73.45), lat=(3.2, 6.25))
ZOOM = dict(lon=(-76.86, -76.42), lat=(5.44, 5.96))           # Citará (Quibdó, Lloró, the Naurita)

TYPES = {   # Map 1.1 / 1.2 colours where the type is shared
    "power of attorney":                   dict(color="#555555", label="Power of attorney (no value)", dash=True),
    "demand for loan":                     dict(color="#c9a227", label="Request for a loan (letter)"),
    "loan":                                dict(color="#5f8a3a", label="Loan"),
    "debt acknowledgment (obligación)":    dict(color="#2a9d8f", label="Debt acknowledgment (obligación)"),
    "sale of enslaved":                    dict(color="#6b1020", label="Sale of enslaved people (Acuña as seller)"),
}
def width(pesos):                       # Map 1.1 scale
    return 0.8 + 2.9 * np.sqrt(pesos / 10355.0)

BEND = {2: 0.16, 8: 0.28, 11: 0.22, 1: 0.07, 6: -0.28, 30: -0.30}
LABEL_AT = {2: 0.55, 8: 0.62, 11: 0.60, 1: 0.55, 6: 0.5, 30: 0.5}

ROUTE = dict(color="#333333", linewidth=0.95, linestyle=(0, (2.5, 1.8)), zorder=6)
AUD_COLOR = "#8f8a80"
PLACE_STYLE = {
    "mine":   dict(marker="^", s=62, fc="#d9661f", ec="white", lw=0.8),
    "real":   dict(marker="^", s=62, fc="white", ec="#d9661f", lw=1.2),
    "pueblo": dict(marker="s", s=24, fc="white", ec="#555555", lw=1.0),
    "city":   dict(marker="o", s=30, fc="#6f6f6f", ec="white", lw=0.7),
    "origin": dict(marker="o", s=44, fc="#111111", ec="white", lw=0.9),
    "notary": dict(marker="o", s=52, fc="#c08a1e", ec="#3a3a3a", lw=0.9),
    "fields": dict(marker="D", s=20, fc="#d9c27a", ec="#6b5a1e", lw=0.7),
}
SHOW = {
    "naurita":    ("mine",   None),   "quibdo":  ("city", (-7, -3, "right")),
    "tado":       ("pueblo", (-7, 0, "right")), "tamana":  ("real",   None),
    "los_brazos": ("pueblo", (2, -8, "left")),  "novita":  ("city",   (-7, 0, "right")),
    "santafe":    ("notary", (7, 0, "left")),   "cartago": ("notary", (7, -5, "left")),
    "cali":       ("notary", (7, 0, "left")),   "ibague":  ("city",   (6, -3, "left")),
}
DISPLAY = {"naurita": "his mine on the Naurita", "tamana": "Tamaná mining camp"}

ev = pd.read_csv("data/events_ch2.csv")
ev = ev[ev["map"] == 2.2].sort_values("date")
pl = pd.read_csv("data/places.csv").set_index("place_id")
P = {k: (r.lon, r.lat) for k, r in pl.iterrows()}
roads = gpd.read_file("data/roads.geojson")
# main map only: Tamaná sits about 2 km from Los Brazos, so its symbol is nudged north-east
# (cartographic displacement) to keep the two apart; the zoom and data keep true positions
PM = dict(P); PM["tamana"] = (P["tamana"][0] + 0.06, P["tamana"][1] + 0.05)
halo = [pe.withStroke(linewidth=2.2, foreground="white")]

fig, ax, ax_leg = bm.page(FRAME, leg_h=1.05, title_h=0.48)
bm.base(ax, FRAME, YEAR_BOUNDS, rivers_ne=("Cauca", "Magdalena", "Atrato"), rivers_osm=("San Juan", "Tamaná"),
        aud_color=AUD_COLOR, aud_lw=1.0)
roads.plot(ax=ax, **ROUTE)
bm.relief_label(ax, -76.15, 4.35, "Cordillera Occidental", 70)
bm.relief_label(ax, -75.45, 3.75, "Cordillera Central", 72)
bm.relief_label(ax, -74.25, 5.55, "Cordillera Oriental", 58)
bm.river_label(ax, -76.2, 3.55, "Cauca River", 72)
bm.river_label(ax, -74.83, 5.85, "Magdalena River", 80)

def curve(a, b, bend, n=80):
    k = np.cos(np.radians(np.mean(FRAME["lat"])))
    (x0, y0), (x1, y1) = (a[0] * k, a[1]), (b[0] * k, b[1])
    cx, cy = (x0 + x1) / 2 - (y1 - y0) * bend, (y0 + y1) / 2 + (x1 - x0) * bend
    t = np.linspace(0, 1, n)[:, None]
    p = (1 - t) ** 2 * np.array([x0, y0]) + 2 * (1 - t) * t * np.array([cx, cy]) + t ** 2 * np.array([x1, y1])
    return p[:, 0] / k, p[:, 1]

for _, e in ev.iterrows():
    st = TYPES[e.event_type]
    xs, ys = curve(PM[e.from_place], PM[e.to_place], BEND[e.event_id])
    if st.get("dash"):
        ax.plot(xs, ys, color="white", lw=2.2, alpha=0.85, zorder=7)
        ax.plot(xs, ys, color=st["color"], lw=0.9, ls=(0, (3, 2)), zorder=7)
    else:
        lw = width(e.value_pesos)
        ax.plot(xs, ys, color="white", lw=lw + 1.6, alpha=0.85, solid_capstyle="round", zorder=7)
        ax.plot(xs, ys, color=st["color"], lw=lw, solid_capstyle="round", zorder=7)
    i = int(len(xs) * LABEL_AT.get(e.event_id, 0.5))
    ax.text(xs[i], ys[i], e.label, fontsize=5.8, weight="bold", color=st["color"], ha="center", va="center",
            path_effects=halo, zorder=9)

def mark(a, key, role, lab, size=7.0, pos=None):
    st = PLACE_STYLE[role]; lon, lat = (pos or P)[key]
    a.scatter([lon], [lat], marker=st["marker"], s=st["s"], facecolor=st["fc"], edgecolor=st["ec"],
              linewidth=st["lw"], zorder=10)
    if lab:
        dx, dy, ha = lab
        mine = role in ("mine", "real")
        a.annotate(DISPLAY.get(key, pl.loc[key, "display"]), (lon, lat), textcoords="offset points",
                   xytext=(dx, dy), ha=ha, va="center", fontsize=size - (0.6 if mine else 0),
                   style="italic" if mine else "normal", color="#8a3d0c" if mine else bm.INK,
                   weight="bold" if role in ("notary", "mine") else "normal", path_effects=halo, zorder=11)

for key, (role, lab) in SHOW.items():
    mark(ax, key, role, lab, pos=PM)

# ---- zoom-in on Citará, over the Pacific, joined by light lines to its rectangle
ax.add_patch(Rectangle((ZOOM["lon"][0], ZOOM["lat"][0]), np.ptp(ZOOM["lon"]), np.ptp(ZOOM["lat"]), fill=False,
                       edgecolor=bm.INK, linewidth=0.8, linestyle=(0, (1, 1.2)), zorder=9))
z_h = 0.50                                                    # fraction of map height
z_w = z_h * fig._layout["map_h"] / fig._layout["map_w"] * np.ptp(ZOOM["lon"]) / np.ptp(ZOOM["lat"]) \
      * np.cos(np.radians(np.mean(ZOOM["lat"])))
IN = [0.012, 0.425, z_w, z_h]
axz = ax.inset_axes(IN); axz.set_zorder(20)
for lat_c, fy in ((ZOOM["lat"][1], IN[1] + IN[3]), (ZOOM["lat"][0], IN[1])):
    ax.plot([ZOOM["lon"][0], FRAME["lon"][0] + (IN[0] + IN[2]) * np.ptp(FRAME["lon"])],
            [lat_c, FRAME["lat"][0] + fy * np.ptp(FRAME["lat"])], color="#9a968e", lw=0.55, zorder=3.5)
bm.base(axz, ZOOM, YEAR_BOUNDS, rivers_ne=(), rivers_osm=("Atrato", "Neguá", "Naurita", "Quito", "Andágueda"),
        aud_color=AUD_COLOR, aud_lw=1.0, dem_path=None, relief_alpha=0.5)
roads.plot(ax=axz, **ROUTE)
for key, role, lab in (("quibdo", "city", (-7, 0, "right")), ("lloro", "pueblo", (6, -3, "left")),
                       ("naurita", "mine", None), ("negua_fields", "fields", None)):
    mark(axz, key, role, lab, size=6.2)
# zoom labels in the same plain style as Quibdó (the rivers are named on the map, so no "river")
for key, txt, off, ha, va in (("naurita", "Acuña's mine\nin the Naurita", (0, 7), "center", "bottom"),
                              ("negua_fields", "Acuña's fields\non the Neguá", (-8, 10), "right", "top")):
    axz.annotate(txt, P[key], textcoords="offset points", xytext=off, ha=ha, va=va, fontsize=6.2,
                 color=bm.INK, path_effects=halo, zorder=11, linespacing=1.0)
bm.river_label(axz, -76.60, 5.585, "Atrato", -40, size=5.6)
bm.river_label(axz, -76.625, 5.808, "Neguá", 15, size=5.2)
bm.river_label(axz, -76.531, 5.851, "Naurita", 0, size=5.2)
bm.river_label(axz, -76.72, 5.52, "Quito", 70, size=5.4)
axz.text(0.0, 1.015, "Citará", transform=axz.transAxes, ha="left", va="bottom", fontsize=6.6, weight="bold",
         color=bm.INK, path_effects=halo, zorder=12)
bm.scale_bar(axz, ZOOM, 10, x_frac=0.06, y_frac=0.04, size=5.5)
for sp in axz.spines.values():
    sp.set_linewidth(0.9)

# ---- legend: map items left, document types right
def sym(role, lab):
    st = PLACE_STYLE[role]
    return Line2D([0], [0], marker=st["marker"], color="none", markerfacecolor=st["fc"], markeredgecolor=st["ec"],
                  markeredgewidth=st["lw"], markersize=6.5, label=lab)
HM = [sym("notary", "Where it was used or notarized"),
      sym("mine", "Acuña's mine"), sym("real", "Mining camp"), sym("pueblo", "Indigenous town"),
      sym("fields", "Acuña's fields (approximate)"), sym("city", "Other cities"),
      Line2D([0], [0], color=ROUTE["color"], lw=ROUTE["linewidth"], ls=ROUTE["linestyle"], label="Route"),
      Line2D([0], [0], color=AUD_COLOR, lw=1.0, ls=(0, (6, 3)), label=f"Audiencia boundary, {YEAR_BOUNDS}")]
HT = []
for st in TYPES.values():
    HT.append(Line2D([0], [0], color=st["color"], lw=0.9 if st.get("dash") else 2.4,
                     ls=(0, (3, 2)) if st.get("dash") else "-", label=st["label"]))
blank = Line2D([], [], color="none", label=" ")
HT += [Line2D([0], [0], color="#8a8a8a", lw=width(v), solid_capstyle="round", label=f"{v:,} pesos")
       for v in (1000, 3000, 10000)] + [blank] * 2                # col 1: types, col 2: widths
kw = dict(fontsize=5.9, frameon=False, labelspacing=0.45, handletextpad=0.45, handlelength=2.0,
          columnspacing=0.9, borderaxespad=0)
ax_leg.add_artist(ax_leg.legend(handles=HM, loc="center left", bbox_to_anchor=(0.01, 0.5), ncol=2, **kw))
ax_leg.legend(handles=HT, loc="center right", bbox_to_anchor=(0.995, 0.5), ncol=2, **kw)
ax_leg.add_patch(Rectangle((0, 0), 1, 1, transform=ax_leg.transAxes, fill=False, edgecolor="#3a3a3a",
                           linewidth=1.1, clip_on=False))

bm.title(fig, "Map 2.2  Financial transactions, powers of attorney, and sales\n"
              "made by Don Luis de Acuña while in Chocó, 1715–1717", size=9.4)
fig.canvas.draw()
bm.scale_bar(ax, FRAME, 50, x_frac=0.80, y_frac=0.90)
bm.north_arrow(ax, 0.965, 0.84, length=0.08)
# Tamaná label along the start of its own line (the Jul 1715 power of attorney), just above it
_e = ev[ev.event_id == 2].iloc[0]
_xs, _ys = curve(PM[_e.from_place], PM[_e.to_place], BEND[2])
_n = len(_xs)
bm.curved_text(fig, ax, list(zip(_xs[int(_n*0.06):int(_n*0.62)], _ys[int(_n*0.06):int(_n*0.62)] + 0.055)),
               "Tamaná mining camp", align="start", spacing=1.05, fontsize=6.2, style="italic", weight="semibold",
               color="#8a3d0c", zorder=11)
bm.curved_text(fig, ax, [(-78.75, 3.35), (-78.35, 3.55), (-78.0, 3.85), (-77.75, 4.2)], "PACIFIC OCEAN", **bm.SEA_STYLE)
fig.savefig("outputs/map_transactions_1715_1717.png", dpi=300, facecolor="white")
fig.savefig("outputs/map_transactions_1715_1717.pdf", facecolor="white")
print("wrote outputs/map_transactions_1715_1717.png/.pdf  %.2f x %.2f in" % (bm.PAGE_W, fig._layout["fig_h"]))
