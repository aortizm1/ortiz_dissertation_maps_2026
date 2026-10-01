#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Map 1.2 — Don Luis de Acuña's financial and debt transactions in the city of Santafé, 1710.

Same layout as Map 1.1: a main map and a smaller zoom-in.
  - Main map: the usual route from Acuña's mine (El Salto, Nóvita) to Santafé by
    Cartago and Ibagué (his own route is not documented), and the forced journey of
    Maria, Joseph de Tapia and Thomas, likely taken back to the mine.
  - Zoom into Santafé (inset, lower right): the acts, with Acuña on the left, the
    notaries in the middle and the other parties on the right, in date order.
    Colour = type, width = value in pesos, as in Map 1.1; only icons and names.

Data: data/events.csv (1710 rows), data/actors_1710.csv, data/places.csv,
data/roads.geojson. Base: basemap.py.

Run:  ../.venv/bin/python map_transactions_1710.py
Out:  outputs/map_transactions_1710.png (300 dpi) and .pdf
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("outputs", exist_ok=True)

import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Polygon, Rectangle, ConnectionPatch
import basemap as bm

YEAR = 1710
FRAME = dict(lon=(-77.1, -73.7), lat=(3.05, 5.40))
JOURNEY = ["cartago-novita", "ibague-cartago", "santafe-tocaima-ibague"]
INSET = [0.37, 0.015, 0.618, 0.415]          # zoom into Santafé, in map-axes fraction

TYPES = {   # Map 1.1 colours
    "purchase of enslaved":     dict(color="#9e1b32", label="Purchase of an enslaved person"),
    "surety":                   dict(color="#3d5a80", label="Surety (bond)"),
    "foundation of chaplaincy": dict(color="#7b5ea7", label="Foundation of a chaplaincy"),
    "loan":                     dict(color="#2a9d8f", label="Debt (obligación)"),
}
def width(pesos):                       # Map 1.1 scale
    return 0.8 + 2.9 * np.sqrt(pesos / 10355.0)

MINE = dict(marker="^", s=62, fc="#d9661f", ec="white", lw=0.8)
NOTARY = dict(fc="#c08a1e", ec="#3a3a3a")
JOURNEY_STYLE = dict(color="#1f1f1f", lw=1.8)
FORCED = dict(color="#9e1b32", lw=1.8, ls=(0, (3, 2)))   # same width as the route
ROUTE = dict(color="#8a857a", linewidth=0.75, linestyle=(0, (2.5, 1.8)), zorder=6)
AUD_COLOR = "#8f8a80"
halo = [pe.withStroke(linewidth=2.2, foreground="white")]
halo_strong = [pe.withStroke(linewidth=3.2, foreground="white")]

ev = pd.read_csv("data/events.csv")
ev = ev[ev.year == YEAR].merge(pd.read_csv("data/actors_1710.csv"), on="event_id").sort_values("date")
ev = ev.reset_index(drop=True)
pl = pd.read_csv("data/places.csv").set_index("place_id")
P = {k: (r.lon, r.lat) for k, r in pl.iterrows()}
roads = gpd.read_file("data/roads.geojson")

fig, ax, ax_leg = bm.page(FRAME, leg_h=0.72)

# ---------------------------------------------------------------- main map: the route
bm.base(ax, FRAME, YEAR, rivers_ne=("Cauca", "Magdalena"), rivers_osm=("San Juan", "Tamaná"),
        aud_color=AUD_COLOR, aud_lw=1.0)
roads.plot(ax=ax, **ROUTE)
bm.relief_label(ax, -76.66, 3.85, "Cordillera Occidental", 78)
bm.relief_label(ax, -75.33, 4.95, "Cordillera Central", 84)
bm.relief_label(ax, -74.30, 5.05, "Cordillera Oriental", 58)
bm.river_label(ax, -76.36, 3.75, "Cauca River", 72)
bm.river_label(ax, -74.87, 5.02, "Magdalena River", 80)

coords, here = [], shapely.Point(P["mina_salto"])
for name in JOURNEY:
    c = list(roads[roads.route == name].geometry.iloc[0].coords)
    if here.distance(shapely.Point(c[-1])) < here.distance(shapely.Point(c[0])):
        c = c[::-1]
    coords += c; here = shapely.Point(c[-1])
j = shapely.LineString(coords)
jx, jy = np.array(j.coords).T
ax.plot(jx, jy, color="white", lw=JOURNEY_STYLE["lw"] + 2.2, alpha=0.9, solid_capstyle="round", zorder=7)
ax.plot(jx, jy, solid_capstyle="round", zorder=7, **JOURNEY_STYLE)
for f in (0.18, 0.44, 0.66, 0.88):
    a, b = j.interpolate(f - 0.004, normalized=True), j.interpolate(f + 0.004, normalized=True)
    ax.annotate("", xy=(b.x, b.y), xytext=(a.x, a.y), zorder=8,
                arrowprops=dict(arrowstyle="-|>", color=JOURNEY_STYLE["color"], lw=1.2, mutation_scale=15))
back = j.simplify(0.01).offset_curve(-0.05)
back = max(getattr(back, "geoms", [back]), key=lambda g: g.length)
bx, by = np.array(back.coords).T
ax.plot(bx, by, zorder=7, **FORCED)
for f in (0.3, 0.58, 0.84):
    a, b = back.interpolate(f + 0.004, normalized=True), back.interpolate(f - 0.004, normalized=True)
    ax.annotate("", xy=(b.x, b.y), xytext=(a.x, a.y), zorder=8,
                arrowprops=dict(arrowstyle="-|>", color=FORCED["color"], lw=1.1, mutation_scale=13))
# the two journey labels share one format: Arial (Helvetica metrics; its bold italic is installed as
# separate files, unlike Apple's Helvetica), whose capital J stays legible at small sizes
JOURNEY_LABEL = dict(family="Arial", fontsize=6.8, style="italic", weight="bold",
                     path_effects=halo_strong, zorder=9, linespacing=1.05)
ax.annotate("Don Luis de Acuña's likely route\nto Santafé", P["cartago"],
            textcoords="offset points", xytext=(4, 20), ha="center", va="bottom", color="#111111", **JOURNEY_LABEL)
ax.text(-76.12, 4.66, "Maria, Joseph de Tapia and Thomas,\nlikely taken to the mine", ha="center",
        va="top", color="#7a1427", **JOURNEY_LABEL)
for key, off in (("cartago", (6, 6, "left")), ("ibague", (6, 6, "left")), ("anserma", (6, 0, "left")),
                 ("honda", (6, 0, "left")), ("tado", (6, 0, "left"))):
    lon, lat = P[key]
    mk = "s" if key == "tado" else "o"
    ax.scatter([lon], [lat], marker=mk, s=26 if mk == "o" else 22, facecolor="#6f6f6f" if mk == "o" else "white",
               edgecolor="white" if mk == "o" else "#555555", linewidth=0.8, zorder=10)
    ax.annotate(pl.loc[key, "display"], (lon, lat), textcoords="offset points", xytext=off[:2], ha=off[2],
                va="center", fontsize=7, color=bm.INK, path_effects=halo, zorder=11)
# Nóvita and the mine (about 3 km apart): smaller symbols so they sit together
lon, lat = P["novita"]
ax.scatter([lon], [lat], marker="o", s=18, facecolor="#6f6f6f", edgecolor="white", linewidth=0.6, zorder=10)
ax.annotate("Nóvita", (lon, lat), textcoords="offset points", xytext=(-5, 6), ha="right", va="bottom",
            fontsize=7, color=bm.INK, path_effects=halo, zorder=11)
lon, lat = P["mina_salto"]
ax.scatter([lon], [lat], zorder=10, marker=MINE["marker"], s=40, facecolor=MINE["fc"],
           edgecolor=MINE["ec"], linewidth=MINE["lw"])
ax.annotate("El Salto", (lon, lat), textcoords="offset points", xytext=(0, -8),
            ha="center", va="top", fontsize=6.6, style="italic", weight="bold", color="#8a3d0c",
            path_effects=halo, zorder=11)
lon, lat = P["santafe"]
ax.scatter([lon], [lat], marker="o", s=52, facecolor=NOTARY["fc"], edgecolor=NOTARY["ec"], linewidth=0.9, zorder=10)
ax.annotate("Santafé", (lon, lat), textcoords="offset points", xytext=(-10, 10), ha="right", va="center",
            fontsize=7.4, weight="bold", color=bm.INK, path_effects=halo, zorder=11)
bm.scale_bar(ax, FRAME, 50, x_frac=0.03, y_frac=0.05)

# ---------------------------------------------------------------- zoom into Santafé: the acts
axd = ax.inset_axes(INSET); axd.set_zorder(20)
W = fig._layout["map_w"] * INSET[2]; H = fig._layout["map_h"] * INSET[3]      # inches
axd.set_xlim(0, W); axd.set_ylim(0, H); axd.set_xticks([]); axd.set_yticks([])
axd.set_facecolor("#fbfaf8")
for s_ in axd.spines.values():
    s_.set_edgecolor("#3a3a3a"); s_.set_linewidth(0.9)
axd.text(0.0, H + 0.04, "Acuña's notarized activities in Santafé", fontsize=6.6, weight="bold",
         color=bm.INK, ha="left", va="bottom", path_effects=halo, zorder=12)

n = len(ev)
rows_y = np.linspace(H - 0.17, 0.15, n)
X_ACU, X_NOT, X_END = 0.28, 1.02, 2.30
NOT = {"Esteban Gallo": dict(r=0.12), "Miguel Severino de Castellanos": dict(r=0.08)}
g_rows = [y for y, e in zip(rows_y, ev.itertuples()) if e.notary == "Esteban Gallo"]
NOT["Esteban Gallo"]["y"] = float(np.mean(g_rows)) + 0.2
NOT["Miguel Severino de Castellanos"]["y"] = 0.28
Y_ACU = float(np.mean(rows_y)) + 0.1

def link(x0, y0, x1, y1, color, lw):
    t = np.linspace(0, 1, 60); xm = (x0 + x1) / 2
    xs = (1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * xm + 3 * (1 - t) * t ** 2 * xm + t ** 3 * x1
    ys = (1 - t) ** 3 * y0 + 3 * (1 - t) ** 2 * t * y0 + 3 * (1 - t) * t ** 2 * y1 + t ** 3 * y1
    axd.plot(xs, ys, color="white", lw=lw + 1.6, alpha=0.85, solid_capstyle="round", zorder=3)
    axd.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=3)
    return xs, ys

def icon(kind, x, y, c, k=0.75):
    if kind == "church":
        axd.add_patch(Rectangle((x - 0.012 * k / 0.75, y - 0.07 * k), 0.024 * k / 0.75, 0.14 * k, color=c, zorder=6))
        axd.add_patch(Rectangle((x - 0.05 * k, y + 0.012 * k), 0.1 * k, 0.026 * k, color=c, zorder=6))
    elif kind == "court":
        axd.plot([x, x], [y - 0.07 * k, y + 0.055 * k], color=c, lw=1.1, zorder=6)
        axd.plot([x - 0.065 * k, x + 0.065 * k], [y + 0.05 * k, y + 0.05 * k], color=c, lw=1.1, zorder=6)
        axd.plot([x - 0.03 * k, x + 0.03 * k], [y - 0.07 * k, y - 0.07 * k], color=c, lw=1.1, zorder=6)
        for sx in (-0.065 * k, 0.065 * k):
            axd.add_patch(Polygon([(x + sx - 0.03 * k, y - 0.015 * k), (x + sx + 0.03 * k, y - 0.015 * k),
                                   (x + sx, y + 0.05 * k)], closed=True, fill=False, edgecolor=c, lw=0.7, zorder=6))
            axd.add_patch(Polygon([(x + sx - 0.034 * k, y - 0.015 * k), (x + sx + 0.034 * k, y - 0.015 * k),
                                   (x + sx, y - 0.042 * k)], closed=True, color=c, zorder=6))
    elif kind == "mint":                         # a gold doblón
        axd.add_patch(Circle((x, y), 0.075 * k / 0.75 * 0.8, facecolor="#d4a52a", edgecolor="#8a6414", lw=0.8, zorder=6))
        axd.add_patch(Rectangle((x - 0.009, y - 0.035), 0.018, 0.07, color="#8a6414", zorder=7))
        axd.add_patch(Rectangle((x - 0.035, y - 0.009), 0.07, 0.018, color="#8a6414", zorder=7))
    elif kind == "seller":
        axd.add_patch(Circle((x, y), 0.035, facecolor="white", edgecolor="#555555", lw=0.8, zorder=6))

fan = np.linspace(0.08, -0.08, n)
for k, (y, e) in enumerate(zip(rows_y, ev.itertuples())):
    st = TYPES[e.event_type]; lw = width(e.value_pesos); nd = NOT[e.notary]
    link(X_ACU + 0.09, Y_ACU + fan[k], X_NOT - nd["r"], nd["y"] + fan[k] * 0.7, st["color"], lw)
    xs, ys = link(X_NOT + nd["r"], nd["y"] + fan[k] * 0.7, X_END - 0.1, y, st["color"], lw)
    d = pd.Timestamp(e.date)
    i = int(len(xs) * 0.80)                    # the date on the line, as the years in Map 1.1
    axd.text(xs[i], y, f"{d.day} {d.strftime('%B')}", fontsize=5.3, weight="bold", color=st["color"],
             ha="center", va="center", path_effects=halo, zorder=9)
    if e.party_icon != "seller":
        icon(e.party_icon, X_END, y, st["color"])
    enslaved = e.event_type == "purchase of enslaved"
    axd.text(X_END + (0.02 if enslaved else 0.12), y, e.short_label.replace("\\n", "\n"), fontsize=5.5,
             weight="normal", color=bm.INK, ha="left", va="center",
             linespacing=1.0, zorder=7)

axd.add_patch(Circle((X_ACU, Y_ACU), 0.09, facecolor="#111111", edgecolor="white", lw=1.0, zorder=6))
axd.text(X_ACU, Y_ACU - 0.13, "Acuña", fontsize=6.0, weight="bold", color=bm.INK, ha="center", va="top")
for name, nd in NOT.items():
    axd.add_patch(Circle((X_NOT, nd["y"]), nd["r"], facecolor=NOTARY["fc"], edgecolor=NOTARY["ec"], lw=1.0, zorder=6))
    axd.text(X_NOT, nd["y"] - nd["r"] - 0.03, "Notary " + name.replace("Miguel Severino de Castellanos",
             "Miguel Severino\nde Castellanos"), fontsize=5.2, color=bm.INK, ha="center", va="top",
             linespacing=1.0, path_effects=halo, zorder=8)

# the zoom circle around Santafé, joined to the inset
R = 0.13
ax.add_patch(Circle(P["santafe"], R, fill=False, edgecolor=bm.INK, lw=0.9, zorder=9))
for side, fx in ((-1, INSET[0] + 0.55 * INSET[2]), (1, INSET[0] + INSET[2])):   # light, under everything else
    ax.plot([P["santafe"][0] + side * R, FRAME["lon"][0] + fx * np.ptp(FRAME["lon"])],
            [P["santafe"][1], FRAME["lat"][0] + (INSET[1] + INSET[3]) * np.ptp(FRAME["lat"])],
            color=bm.INK, lw=0.7, zorder=8.5, solid_capstyle="butt")   # darker: this area is less crowded

# ---------------------------------------------------------------- legend: map items left, transactions right
def sym(marker, fc, ec, lab, ms=6.5):
    return Line2D([0], [0], marker=marker, color="none", markerfacecolor=fc, markeredgecolor=ec,
                  markersize=ms, label=lab)
HM = [sym("^", MINE["fc"], "white", "Acuña's mine"),
      sym("o", NOTARY["fc"], NOTARY["ec"], "Santafé"),
      sym("o", "#6f6f6f", "white", "Other cities", 5.5),
      sym("s", "white", "#555555", "Indigenous town", 5),
      Line2D([0], [0], label="Acuña's likely route", **JOURNEY_STYLE),
      Line2D([0], [0], color=FORCED["color"], lw=FORCED["lw"], ls=FORCED["ls"], label="Forced journey (likely)"),
      Line2D([0], [0], color=ROUTE["color"], lw=ROUTE["linewidth"], ls=ROUTE["linestyle"], label="Other routes"),
      Line2D([0], [0], color=AUD_COLOR, lw=1.0, ls=(0, (6, 3)), label=f"Audiencia boundary, {YEAR}")]
HT = [Line2D([0], [0], color=st["color"], lw=2.4, label=st["label"]) for st in TYPES.values()]
HT += [Line2D([0], [0], color="#8a8a8a", lw=width(v), solid_capstyle="round", label=f"{v:,} pesos")
       for v in (500, 3000, 10000)]
kw = dict(fontsize=6.1, frameon=False, labelspacing=0.5, handletextpad=0.45, handlelength=2.0,
          columnspacing=1.2, borderaxespad=0)
ax_leg.add_artist(ax_leg.legend(handles=HM, loc="center left", bbox_to_anchor=(0.012, 0.5), ncol=2, **kw))
ax_leg.legend(handles=HT, loc="center left", bbox_to_anchor=(INSET[0] + 0.035, 0.5), ncol=2, **kw)
ax_leg.add_patch(Rectangle((0, 0), 1, 1, transform=ax_leg.transAxes, fill=False,
                           edgecolor="#3a3a3a", linewidth=1.1, clip_on=False))

bm.title(fig, "Map 1.2  Don Luis de Acuña's financial and debt transactions in the city of Santafé, 1710", size=8.6)
fig.canvas.draw()
bm.north_arrow(ax, 0.215, 0.035, length=0.06)
fig.savefig("outputs/map_transactions_1710.png", dpi=300, facecolor="white")
fig.savefig("outputs/map_transactions_1710.pdf", facecolor="white")
print("wrote outputs/map_transactions_1710.png/.pdf  %.2f x %.2f in" % (bm.PAGE_W, fig._layout["fig_h"]))
