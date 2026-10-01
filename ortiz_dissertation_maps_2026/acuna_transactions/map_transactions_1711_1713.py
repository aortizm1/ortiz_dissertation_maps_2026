#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Map 2.1 — Purchases of enslaved people by Don Luis de Acuña, 1711–1713.

Same conventions as Map 1.1: each line joins where Acuña was (the Nóvita region; the
1712 vale was written at his mine, El Salto) to the city where the purchase was made;
colour = type, width = value in pesos, label = month and year. A zoom-in on Nóvita
and his mine, El Salto, shows which purchase was arranged from the mine (the 1712
vale) and which from the town.

Data: data/events_ch2.csv (map 2.1 rows, checked with the author), data/places.csv,
data/roads.geojson. Base: basemap.py.

Run:  ../.venv/bin/python map_transactions_1711_1713.py
Out:  outputs/map_transactions_1711_1713.png (300 dpi) and .pdf
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("outputs", exist_ok=True)

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import basemap as bm

YEAR_BOUNDS = 1712
FRAME = dict(lon=(-78.7, -74.6), lat=(2.25, 5.42))
ZOOM = dict(lon=(-76.665, -76.535), lat=(4.918, 4.985))       # Nóvita and El Salto

TYPES = {   # Map 1.1 colours
    "purchase of enslaved":           dict(color="#9e1b32", label="Purchase of enslaved people"),
    "purchase of enslaved on credit": dict(color="#e0828f", label="Purchase of enslaved people on credit"),
}
def width(pesos):                       # Map 1.1 scale
    return 0.8 + 2.9 * np.sqrt(pesos / 10355.0)

# bend of each line (fraction of the chord), so the Cartago lines fan out in date order
BEND = {17: 0.80, 5: 0.52, 19: 0.26, 20: 0.02, 21: -0.22, 18: -0.46, 28: -0.22}
LABEL_AT = {21: 0.55}

ROUTE = dict(color="#333333", linewidth=0.95, linestyle=(0, (2.5, 1.8)), zorder=6)
AUD_COLOR = "#8f8a80"
PLACE_STYLE = {
    "base":   dict(marker="o", s=70, fc="#111111", ec="white", lw=1.0),
    "mine":   dict(marker="^", s=62, fc="#d9661f", ec="white", lw=0.8),
    "pueblo": dict(marker="s", s=24, fc="white", ec="#555555", lw=1.0),
    "city":   dict(marker="o", s=30, fc="#6f6f6f", ec="white", lw=0.7),
    "notary": dict(marker="o", s=52, fc="#c08a1e", ec="#3a3a3a", lw=0.9),
}
SHOW = {   # key: (role, label offset)
    "novita":  ("base", (-8, -4, "right")), "tado":    ("pueblo", (6, 0, "left")),
    "cartago": ("notary", (7, -5, "left")), "popayan": ("notary", (7, 0, "left")),
    "anserma": ("city", (6, 0, "left")),    "cali":    ("city", (6, 0, "left")),
    "ibague":  ("city", (6, -3, "left")),
}
DISPLAY = {"novita": "Nóvita"}

ev = pd.read_csv("data/events_ch2.csv")
ev = ev[ev["map"] == 2.1].sort_values("date")
pl = pd.read_csv("data/places.csv").set_index("place_id")
P = {k: (r.lon, r.lat) for k, r in pl.iterrows()}
roads = gpd.read_file("data/roads.geojson")
halo = [pe.withStroke(linewidth=2.2, foreground="white")]

fig, ax, ax_leg = bm.page(FRAME, leg_h=0.8)
bm.base(ax, FRAME, YEAR_BOUNDS, rivers_ne=("Cauca", "Magdalena", "Atrato"), rivers_osm=("San Juan", "Tamaná"),
        aud_color=AUD_COLOR, aud_lw=1.0)
roads.plot(ax=ax, **ROUTE)
bm.relief_label(ax, -76.95, 3.55, "Cordillera Occidental", 72)
bm.relief_label(ax, -75.60, 3.40, "Cordillera Central", 70)
bm.river_label(ax, -76.34, 3.85, "Cauca River", 62)
bm.river_label(ax, -77.05, 4.35, "San Juan River", 60)

def curve(a, b, bend, n=80):
    k = np.cos(np.radians(np.mean(FRAME["lat"])))
    (x0, y0), (x1, y1) = (a[0] * k, a[1]), (b[0] * k, b[1])
    cx, cy = (x0 + x1) / 2 - (y1 - y0) * bend, (y0 + y1) / 2 + (x1 - x0) * bend
    t = np.linspace(0, 1, n)[:, None]
    p = (1 - t) ** 2 * np.array([x0, y0]) + 2 * (1 - t) * t * np.array([cx, cy]) + t ** 2 * np.array([x1, y1])
    return p[:, 0] / k, p[:, 1]

CURVES = []
for _, e in ev.iterrows():
    st = TYPES[e.event_type]; lw = width(e.value_pesos)
    xs, ys = curve(P[e.from_place], P[e.to_place], BEND[e.event_id])
    CURVES.append((xs, ys, st["color"], lw))
    ax.plot(xs, ys, color="white", lw=lw + 1.6, alpha=0.85, solid_capstyle="round", zorder=7)
    ax.plot(xs, ys, color=st["color"], lw=lw, solid_capstyle="round", zorder=7)
    i = int(len(xs) * LABEL_AT.get(e.event_id, 0.5))
    ax.text(xs[i], ys[i], e.label, fontsize=5.8, weight="bold", color=st["color"], ha="center", va="center",
            path_effects=halo, zorder=9)

for key, (role, (dx, dy, ha)) in SHOW.items():
    st = PLACE_STYLE[role]; lon, lat = P[key]
    ax.scatter([lon], [lat], marker=st["marker"], s=st["s"], facecolor=st["fc"], edgecolor=st["ec"],
               linewidth=st["lw"], zorder=10)
    txt = DISPLAY.get(key, pl.loc[key, "display"])
    mine = role == "mine"
    ax.annotate(txt, (lon, lat), textcoords="offset points", xytext=(dx, dy), ha=ha, va="center",
                fontsize=6.4 if mine else 7.2, style="italic" if mine else "normal",
                color="#8a3d0c" if mine else bm.INK, weight="bold" if role in ("base", "notary") or mine else "normal",
                path_effects=halo, zorder=11, linespacing=1.05)

# ---- zoom-in: Nóvita and his mine, El Salto (over the Pacific), with the start of each line
from matplotlib.patches import Rectangle as _R
ax.add_patch(_R((ZOOM["lon"][0], ZOOM["lat"][0]), np.ptp(ZOOM["lon"]), np.ptp(ZOOM["lat"]), fill=False,
                edgecolor=bm.INK, linewidth=0.8, linestyle=(0, (1, 1.2)), zorder=9))
z_w = 0.31
z_h = z_w * fig._layout["map_w"] / fig._layout["map_h"] * np.ptp(ZOOM["lat"]) / np.ptp(ZOOM["lon"]) \
      / np.cos(np.radians(np.mean(ZOOM["lat"])))
IN = [0.012, 0.93 - z_h, z_w, z_h]
for lat_c, fy in ((ZOOM["lat"][1], IN[1] + IN[3]), (ZOOM["lat"][0], IN[1])):
    ax.plot([ZOOM["lon"][0], FRAME["lon"][0] + (IN[0] + IN[2]) * np.ptp(FRAME["lon"])],
            [lat_c, FRAME["lat"][0] + fy * np.ptp(FRAME["lat"])], color="#9a968e", lw=0.55, zorder=3.5)
axz = ax.inset_axes(IN); axz.set_zorder(20)
bm.base(axz, ZOOM, YEAR_BOUNDS, rivers_ne=(), rivers_osm=("San Juan", "Tamaná"), aud_color=AUD_COLOR,
        dem_path="data/dem_corridor_90m.tif", relief_alpha=0.5)
roads.plot(ax=axz, **ROUTE)
for xs, ys, col, lw in CURVES:
    axz.plot(xs, ys, color="white", lw=lw + 1.6, alpha=0.85, solid_capstyle="round", zorder=7)
    axz.plot(xs, ys, color=col, lw=lw, solid_capstyle="round", zorder=7)
for key, role, txt, off, ha in (("novita", "base", "Nóvita", (-8, 0), "right"),
                                ("mina_salto", "mine", "his mine,\nEl Salto", (0, -9), "center")):
    st = PLACE_STYLE[role]; lon, lat = P[key]
    axz.scatter([lon], [lat], marker=st["marker"], s=st["s"], facecolor=st["fc"], edgecolor=st["ec"],
                linewidth=st["lw"], zorder=10)
    mine = role == "mine"
    axz.annotate(txt, (lon, lat), textcoords="offset points", xytext=off, ha=ha, va="top" if mine else "center",
                 fontsize=6.4, weight="bold", style="italic" if mine else "normal",
                 color="#8a3d0c" if mine else bm.INK, path_effects=halo, zorder=11, linespacing=1.0)
axz.text(0.0, 1.03, "Acuña in Nóvita and El Salto", transform=axz.transAxes, ha="left", va="bottom",
         fontsize=6.4, weight="bold", color=bm.INK, path_effects=halo, zorder=12)
bm.scale_bar(axz, ZOOM, 2, x_frac=0.05, y_frac=0.08, size=5.5)
for sp in axz.spines.values():
    sp.set_linewidth(0.9)

# ---- legend
blank = Line2D([], [], color="none", label=" ")
HA = [Line2D([0], [0], color=st["color"], lw=2.4, label=st["label"]) for st in TYPES.values()]
HA += [Line2D([0], [0], color="#8a8a8a", lw=width(v), solid_capstyle="round", label=f"{v:,} pesos")
       for v in (500, 3000, 10000)] + [blank]
def sym(role, lab):
    st = PLACE_STYLE[role]
    return Line2D([0], [0], marker=st["marker"], color="none", markerfacecolor=st["fc"], markeredgecolor=st["ec"],
                  markeredgewidth=st["lw"], markersize=6.5, label=lab)
HB = [sym("base", "Acuña's base (Nóvita)"), sym("mine", "Acuña's mine"), sym("pueblo", "Indigenous town"),
      sym("notary", "Where the purchase was made"), sym("city", "Other cities"),
      Line2D([0], [0], color=ROUTE["color"], lw=ROUTE["linewidth"], ls=ROUTE["linestyle"],
             label="Route (river or land trail)"),
      Line2D([0], [0], color=AUD_COLOR, lw=1.0, ls=(0, (6, 3)), label=f"Audiencia boundary, {YEAR_BOUNDS}"),
      blank]
HA = [HA[0], HA[1], blank, HA[2], HA[3], HA[4]]     # column 1: types; column 2: widths
kw = dict(ncol=2, fontsize=6.4, frameon=False, labelspacing=0.55, handletextpad=0.45, handlelength=2.0,
          columnspacing=0.9, borderaxespad=0)
ax_leg.add_artist(ax_leg.legend(handles=HA, loc="center left", bbox_to_anchor=(0.012, 0.5), **kw))
ax_leg.legend(handles=HB, loc="center right", bbox_to_anchor=(0.99, 0.5), **kw)
ax_leg.add_patch(Rectangle((0, 0), 1, 1, transform=ax_leg.transAxes, fill=False, edgecolor="#3a3a3a",
                           linewidth=1.1, clip_on=False))

bm.title(fig, "Map 2.1  Purchases of enslaved people by Don Luis de Acuña, 1711–1713", size=9.4)
fig.canvas.draw()
bm.scale_bar(ax, FRAME, 50, x_frac=0.80, y_frac=0.90)
bm.north_arrow(ax, 0.965, 0.86, length=0.06)
bm.curved_text(fig, ax, [(-78.6, 2.55), (-78.3, 2.9), (-78.1, 3.3), (-78.02, 3.75)], "PACIFIC OCEAN", **bm.SEA_STYLE)
fig.savefig("outputs/map_transactions_1711_1713.png", dpi=300, facecolor="white")
fig.savefig("outputs/map_transactions_1711_1713.pdf", facecolor="white")
print("wrote outputs/map_transactions_1711_1713.png/.pdf  %.2f x %.2f in" % (bm.PAGE_W, fig._layout["fig_h"]))
