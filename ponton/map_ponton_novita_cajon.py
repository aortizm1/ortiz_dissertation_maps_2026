#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Map 3.1 — Areas of gold mining exploitation by mine owners and free black independent
miners in the jurisdictions of Nóvita and Cajón, ca. 1755–1790.

The world in which Melchor Pontón lived and worked: the titled mining camps, sized by
the number of enslaved workers in the 1755 census, with Santa Bárbara, where he was
the enslaved captain, highlighted; the camp of a free African man, Diego Ibo de
Thovar, on the Taparral; and the areas where free mazamorreros (independent miners)
worked, recorded when they paid mining taxes.

Data: data/places.csv, data/census_1755_mining_camps.csv, data/sketch_layers.geojson
(the author's ArcGIS sketches), data/roads_ponton.geojson (routes from ../acuna_transactions/data/roads.geojson; the
Cajón–Sipí leg redrawn along the Cajón and the Taparral after the Compendiosa noticia).
Base: ../acuna_transactions/basemap.py (same style as the other maps).

Run:  ../.venv/bin/python map_ponton_novita_cajon.py
Out:  outputs/map_ponton_novita_cajon.png (300 dpi) and .pdf
"""
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("outputs", exist_ok=True)
sys.path.insert(0, os.path.join("..", "acuna_transactions"))

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
import basemap as bm

YEAR = 1760
FRAME = dict(lon=(-76.765, -76.385), lat=(4.672, 5.028))
DEM = os.path.join("..", "acuna_transactions", "data", "dem_corridor_90m.tif")

MINE_C = "#d9661f"          # mining camps (as in the Acuña maps)
FREE_C = "#1b7f74"          # free black miners: Thovar's camp and the mazamorrero areas
OTHER_C = "#5f5f5f"         # labels of camps in the 1755 census not discussed in the chapter
ROUTE = dict(color="#333333", linewidth=0.9, linestyle=(0, (2.5, 1.8)), zorder=6)
halo = [pe.withStroke(linewidth=2.4, foreground="white")]

CLASSES = [(20, 30, "Under 20 enslaved workers"), (60, 75, "20–59"), (150, 150, "60–149"),
           (float("inf"), 250, "150 or more")]   # upper bound, marker area (pt²), legend label
def size(n):                # marker area by class of enslaved workers (breaks fall in gaps in the 1755 counts)
    return next(a for top, a, _ in CLASSES if n < top)

pl = pd.read_csv("data/places.csv")
# mazamorrero areas as drawn on the map: located from the Compendiosa noticia and sized by the
# mazamorreros taxed in 1788 (originals kept in data/sketch_layers.geojson)
maz = gpd.read_file("data/mazamorrero_areas_display.geojson")
maz["label"] = maz.layer.map({"Taparral-Mazamorreros": "Taparral", "Rio Negro - Mazamorreros": "Río Negro",
                              "Tigresito - Mazamorreros": "Tigresito"})
roads = gpd.read_file("data/roads_ponton.geojson")

fig, ax, ax_leg = bm.page(FRAME, leg_h=1.0, title_h=0.48)
bm.base(ax, FRAME, YEAR, rivers_ne=(),
        rivers_osm=("San Juan", "Tamaná", "Cajón", "Negro", "Taparral", "Quebrada Nóvita", "Quebrada Torrá", "Ingará",
                    "Quebrada Tigresito", "Quebrada Santa Bárbara"),
        dem_path=DEM, relief_alpha=0.5)
roads.plot(ax=ax, **ROUTE)

# mazamorrero areas
maz.plot(ax=ax, facecolor=FREE_C, alpha=0.22, edgecolor="none", zorder=6)
maz.plot(ax=ax, facecolor="none", edgecolor=FREE_C, linewidth=0.9, hatch="....", zorder=6)
MAZ_LABEL = {"Taparral": (-76.652, 4.722, "left"), "Río Negro": (-76.614, 4.893, "left"),
             "Tigresito": (-76.526, 4.912, "left")}
for _, r in maz.iterrows():
    x, y, ha = MAZ_LABEL[r.label]
    ax.text(x, y, f"{r.label}\nmazamorreros", fontsize=6.4, style="italic", color=FREE_C, weight="bold",
            ha=ha, va="center", path_effects=halo, zorder=11, linespacing=1.0)

# places
LABEL = {   # offset in points, alignment
    "santa_barbara": (-10, -1, "right"), "sed_de_cristo": (0, 8, "center"), "el_salto": (-6, -5, "right"),
    "torra": (8, 0, "left"), "el_playon": (-11, -1, "right"), "san_jose": (-8, 0, "right"), "san_lorenzo": (8, -5, "left"),
    "tamana": (0, 7, "center"), "aguaclara": (-7, -3, "right"), "el_caucho": (-7, 1, "right"),
    "sesego": (0, 6, "center"), "taparral": (8, 2, "left"),
    "novita": (8, -3, "left"), "los_brazos": (6, 8, "left"), "las_juntas": (-6, 0, "right"),
    "el_cajon": (8, 3, "left"), "santa_rita": (-7, -1, "right"), "sb_bola": (8, -4, "left"), "sb_arriba": (7, 2, "left"),
    "guarabal": (7, -1, "left"), "vigia": (6, 0, "left"),
}
# display positions for camps within about 1 km of each other (all positions are approximate);
# the data keep the recorded coordinates
NUDGE = {"sed_de_cristo": (-0.0085, 0.0015), "san_lorenzo": (0.0, -0.0075)}
for pid, (dx_, dy_) in NUDGE.items():
    pl.loc[pl.place_id == pid, "lon"] += dx_
    pl.loc[pl.place_id == pid, "lat"] += dy_
for _, p in pl.iterrows():
    k = p.kind
    if k == "free_mine":                    # white backing so it reads over the hatched area
        ax.scatter([p.lon], [p.lat], marker="^", s=size(p.enslaved_1755) + 60, facecolor="white",
                   edgecolor="none", zorder=9.5)
    if k in ("mine", "ponton_mine", "free_mine"):
        ax.scatter([p.lon], [p.lat], marker="^", s=size(p.enslaved_1755), facecolor=MINE_C,
                   edgecolor="white", linewidth=0.8, zorder=10)
    elif k == "mine_nocensus":
        ax.scatter([p.lon], [p.lat], marker="^", s=34, facecolor="white", edgecolor=MINE_C, linewidth=1.3, zorder=10)
    elif k == "town":
        ax.scatter([p.lon], [p.lat], marker="o", s=42, facecolor="#111111", edgecolor="white", linewidth=0.9, zorder=10)
    elif k == "indigenous":
        ax.scatter([p.lon], [p.lat], marker="s", s=26, facecolor="white", edgecolor="#555555", linewidth=1.0, zorder=10)
    elif k == "fort":
        ax.scatter([p.lon], [p.lat], marker="P", s=30, facecolor="#555555", edgecolor="white", linewidth=0.6, zorder=10)
    dx, dy, ha = LABEL.get(p.place_id, (7, 0, "left"))
    if k == "ponton_mine":
        txt, kw = f"Santa Bárbara\n({p.owner_label})", dict(fontsize=6.8, style="italic", color=MINE_C, weight="bold")
    elif k == "free_mine":
        txt, kw = "Diego Ibo de Thovar\n(free African)", dict(fontsize=6.4, style="italic", color=FREE_C, weight="bold")
    elif k.startswith("mine"):
        # mine name and the owner's surname (places.csv owner_label: 1755 census, or chapter 3 for the
        # mines of Don Juan de Bonilla and his partner Don Francisco Rivas)
        txt, kw = p.display, (dict(fontsize=6.6, color=bm.INK, weight="bold") if p.in_chapter
                              else dict(fontsize=6.2, color=OTHER_C))
        if isinstance(p.owner_label, str):
            txt += f"\n({p.owner_label})"
    else:
        txt, kw = p.display, dict(fontsize=6.8, color=bm.INK, weight="bold" if k == "town" else "normal")
    va = "bottom" if dy > 4 else "top" if dy < -4 else "center"     # two-line labels grow away from the marker
    ax.annotate(txt, (p.lon, p.lat), textcoords="offset points", xytext=(dx, dy), ha=ha, va=va,
                path_effects=halo, zorder=11, linespacing=1.0, **kw)

bm.river_label(ax, -76.44, 4.968, "Tamaná River", 8)
bm.river_label(ax, -76.742, 4.822, "Cajón River", 25)
bm.river_label(ax, -76.596, 4.918, "Río Negro", 62)
bm.river_label(ax, -76.700, 4.797, "Taparral River", -62)
bm.river_label(ax, -76.735, 4.975, "San Juan River", 75)

# ---------------------------------------------------------------- legend
def tri(fc, ec, n, lab, lw=0.8, cap=None):
    ms = np.sqrt(size(n)) if cap is None else cap
    return Line2D([0], [0], marker="^", color="none", markerfacecolor=fc, markeredgecolor=ec,
                  markeredgewidth=lw, markersize=ms, label=lab)
blank = Line2D([], [], color="none", label=" ")
H1 = [tri(MINE_C, "white", 0, "Camp discussed in the chapter", cap=8),
      tri(MINE_C, "white", 0, "Other camp in the 1755 census", cap=8),
      Line2D([0], [0], marker="^", color="none", markerfacecolor="white", markeredgecolor=MINE_C,
             markeredgewidth=1.3, markersize=np.sqrt(34), label="Mine not in the 1755 census"),
      Patch(facecolor=(0.106, 0.498, 0.455, 0.22), edgecolor=FREE_C, hatch="....",
            label="Area worked by free mazamorreros")]
H2 = [tri("#9a9a9a", "white", top - 1 if top < 1e9 else 999, lab) for top, _, lab in CLASSES]
H3 = [Line2D([0], [0], marker="o", color="none", markerfacecolor="#111111", markeredgecolor="white",
             markersize=6.5, label="Town"),
      Line2D([0], [0], marker="s", color="none", markerfacecolor="white", markeredgecolor="#555555",
             markersize=5.5, label="Indigenous town"),
      Line2D([0], [0], marker="P", color="none", markerfacecolor="#555555", markeredgecolor="white",
             markersize=6, label="Defensive post (vigía)"),
      Line2D([0], [0], color=ROUTE["color"], lw=ROUTE["linewidth"], ls=ROUTE["linestyle"],
             label="Route (river or land trail)")]
kw = dict(fontsize=6.2, frameon=False, labelspacing=0.9, handletextpad=0.6, borderaxespad=0)
leg1 = ax_leg.legend(handles=H1, loc="center left", bbox_to_anchor=(0.012, 0.5), **kw)
leg1.get_texts()[0].set_weight("bold")                 # label styles as on the map
leg1.get_texts()[1].set_color(OTHER_C)
ax_leg.add_artist(leg1)
ax_leg.add_artist(ax_leg.legend(handles=H2, loc="center left", bbox_to_anchor=(0.46, 0.5),
                                **{**kw, "labelspacing": 1.2}))   # room for the largest triangles
ax_leg.legend(handles=H3, loc="center left", bbox_to_anchor=(0.73, 0.5), **kw)
ax_leg.add_patch(Rectangle((0, 0), 1, 1, transform=ax_leg.transAxes, fill=False, edgecolor="#3a3a3a",
                           linewidth=1.1, clip_on=False))

bm.title(fig, "Map 3.1  Areas of gold mining exploitation by mine owners and free black independent\n"
              "miners in the jurisdictions of Nóvita and Cajón, ca. 1755–1790", size=9.0)
fig.canvas.draw()
bm.scale_bar(ax, FRAME, 5, x_frac=0.03, y_frac=0.05)
bm.north_arrow(ax, 0.965, 0.04, length=0.06)
fig.savefig("outputs/map_ponton_novita_cajon.png", dpi=300, facecolor="white")
fig.savefig("outputs/map_ponton_novita_cajon.pdf", facecolor="white")
print("wrote outputs/map_ponton_novita_cajon.png/.pdf  %.2f x %.2f in" % (bm.PAGE_W, fig._layout["fig_h"]))
