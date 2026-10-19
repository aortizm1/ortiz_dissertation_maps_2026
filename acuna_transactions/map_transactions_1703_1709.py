#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Map 1.1 — Luis de Acuña's formal credit exchanges from Nóvita, 1703–1709.

Template for the series of Acuña transaction maps (1698–1721). Each line joins
Acuña's location (Nóvita) to the city where the act was notarized; colour is the
type of transaction, width its value in pesos, and the label its year. An inset
zooms in on the first stretch of the route to Cartago, up the Tamaná from Nóvita:
Acuña's mine, the other mines active at the time and the indigenous towns with
mines.

Data: data/events.csv (curated from the author's relational database, with the author's
corrections), data/places.csv, data/mining_areas.csv (approximate areas of
unmapped mines, from the author), data/roads.geojson (author's ArcGIS Online routes
layer), data/dem_corridor_90m.tif (made by fetch_corridor_dem.py). Base: basemap.py (same style as the introduction map).

Run:  ../.venv/bin/python map_transactions_1703_1709.py
Out:  outputs/map_transactions_1703_1709.png (300 dpi) and .pdf
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("outputs", exist_ok=True)

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Patch, ConnectionPatch
import basemap as bm

PERIOD = (1703, 1709)
YEAR_BOUNDS = 1709                      # audiencia boundaries drawn for this year
FRAME = dict(lon=(-77.9, -73.6), lat=(3.3, 6.2))
CORRIDOR = dict(lon=(-76.665, -76.365), lat=(4.875, 5.025))   # the Tamaná stretch of the route, inset

# ---- transaction types: colour and legend label ----
TYPES = {
    "foundation of chaplaincy":       dict(color="#7b5ea7", label="Foundation of a chaplaincy"),
    "debt":                           dict(color="#2a9d8f", label="Debt"),
    "surety":                         dict(color="#3d5a80", label="Surety (bond)"),
    "purchase of enslaved":           dict(color="#9e1b32", label="Purchase of enslaved people"),
    "purchase of enslaved on credit": dict(color="#e0828f", label="Purchase of enslaved people on credit"),
}
def width(pesos):                       # line width (pt) by value, area-like (square root)
    return 0.8 + 2.9 * np.sqrt(pesos / 10355.0)

# ---- places: which appear, and how ----
ROUTE = dict(color="#333333", linewidth=0.95, linestyle=(0, (2.5, 1.8)), zorder=6)
AUD_COLOR = "#8f8a80"                    # lighter than the routes: context, not the subject

SHOW_MAIN = ["novita", "quibdo", "tado", "cartago", "santafe", "anserma", "cali", "ibague", "honda"]
SHOW_PANEL = ["novita", "los_brazos", "las_juntas", "cartago"]
# mines: (place, offset in points, alignment); Acuña's mine is filled and its label bold
MINES = [("mina_salto", True, (2, -9), "center"), ("yali", False, (0, 6), "center"),
         ("quebrada_larga", False, (-4, 9), "center")]   # far offsets get a leader line
MINE_LABEL = dict(fontsize=5.9, style="italic", color="#8a3d0c")
PLACE_STYLE = {
    "base":     dict(marker="o", s=70, fc="#111111", ec="white", lw=1.0),
    "mine":     dict(marker="^", s=62, fc="#d9661f", ec="white", lw=0.8),     # Acuña's mine: filled
    "real":     dict(marker="^", s=62, fc="white",   ec="#d9661f", lw=1.2),     # other mines: hollow, same size
    "pueblo":   dict(marker="s", s=24, fc="white",   ec="#555555", lw=1.0),
    "city":     dict(marker="o", s=30, fc="#6f6f6f", ec="white", lw=0.7),
    "notary":   dict(marker="o", s=52, fc="#c08a1e", ec="#3a3a3a", lw=0.9),
}
ROLE = {"novita": "base", "mina_salto": "mine", "yali": "real", "los_brazos": "pueblo",
        "las_juntas": "pueblo", "sipi": "pueblo", "tado": "pueblo"}
MINE_AREA = dict(facecolor="#d9661f", alpha=0.16, edgecolor="none", zorder=6)
MINE_EDGE = dict(facecolor="none", edgecolor="#d9661f", linewidth=0.7, linestyle=(0, (2, 1.5)), zorder=6)
LABEL = {   # offset in points, alignment
    "novita": (-7, 0, "right"), "quibdo": (6, 0, "left"), "tado": (6, 0, "left"),
    "cartago": (6, -6, "left"), "santafe": (7, 0, "left"), "anserma": (6, 0, "left"),
    "cali": (6, 0, "left"), "ibague": (6, -3, "left"), "honda": (6, 0, "left"),
}
PANEL_LABEL = {
    "novita": (-8, -6, "right"), "los_brazos": (7, -6, "left"),
    "las_juntas": (-8, 7, "right"), "sipi": (7, 0, "left"), "cartago": (-8, -7, "right"),
}
LABEL_AT = {15: 0.45, 13: 0.62}      # where along a flow its year label sits (0-1)
# flow bends (fraction of chord length) so the Cartago lines fan out in date order
BEND = {14: 0.95, 16: 0.58, 32: 0.26, 15: -0.06, 13: -0.32, 23: -0.58}

ev = pd.read_csv("data/events.csv")
ev = ev[(ev.year >= PERIOD[0]) & (ev.year <= PERIOD[1])].sort_values("date")
pl = pd.read_csv("data/places.csv").set_index("place_id")
P = {k: (r.lon, r.lat) for k, r in pl.iterrows()}
roads = gpd.read_file("data/roads.geojson")

fig, ax, ax_leg = bm.page(FRAME, leg_h=0.95)
bm.base(ax, FRAME, YEAR_BOUNDS, rivers_ne=("Cauca", "Magdalena", "Atrato"), rivers_osm=("San Juan", "Tamaná"),
        aud_color=AUD_COLOR, aud_lw=1.0)
roads.plot(ax=ax, **ROUTE)

# relief and river labels
bm.relief_label(ax, -76.30, 5.75, "Cordillera Occidental", 80)
bm.relief_label(ax, -75.45, 5.60, "Cordillera Central", 84)
bm.relief_label(ax, -73.95, 5.55, "Cordillera Oriental", 55)
bm.river_label(ax, -76.80, 5.95, "Atrato River", 70)
bm.river_label(ax, -76.20, 4.25, "Cauca River", 62)
bm.river_label(ax, -74.83, 4.35, "Magdalena River", 80)
bm.river_label(ax, -76.95, 4.55, "San Juan River", 58)

# ---- flows ----
def curve(a, b, bend, n=80):
    """Quadratic curve from a to b, bowed sideways by `bend` x chord (in true-scale units)."""
    k = np.cos(np.radians(np.mean(FRAME["lat"])))
    (x0, y0), (x1, y1) = (a[0] * k, a[1]), (b[0] * k, b[1])
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    t = np.linspace(0, 1, n)[:, None]
    pts = (1 - t) ** 2 * np.array([x0, y0]) + 2 * (1 - t) * t * np.array([cx, cy]) + t ** 2 * np.array([x1, y1])
    return pts[:, 0] / k, pts[:, 1]

halo = [pe.withStroke(linewidth=2.2, foreground="white")]
for _, e in ev.iterrows():
    st = TYPES[e.event_type]
    xs, ys = curve(P[e.acuna_place], P[e.event_place], BEND[e.event_id])
    lw = width(e.value_pesos)
    ax.plot(xs, ys, color="white", lw=lw + 1.6, alpha=0.85, solid_capstyle="round", zorder=7)
    ax.plot(xs, ys, color=st["color"], lw=lw, solid_capstyle="round", zorder=7)
    i = int(len(xs) * LABEL_AT.get(e.event_id, 0.5))
    txt = str(e.year)
    ax.text(xs[i], ys[i], txt, fontsize=5.8, weight="bold", color=st["color"], ha="center",
            va="center", path_effects=halo, zorder=9)

# ---- places ----
def mark(a, key, role, labels, size=7.2, bold=False):
    st = PLACE_STYLE[role]
    lon, lat = P[key]
    a.scatter([lon], [lat], marker=st["marker"], s=st["s"], facecolor=st["fc"], edgecolor=st["ec"],
              linewidth=st["lw"], zorder=10)
    if key in labels:
        dx, dy, ha = labels[key]
        a.annotate(pl.loc[key, "display"], (lon, lat), textcoords="offset points", xytext=(dx, dy),
                   ha=ha, va="center", fontsize=size, weight="bold" if bold else "normal",
                   color=bm.INK, path_effects=halo, zorder=11)

notaries = set(ev.event_place)
for key in SHOW_MAIN:
    role = ROLE.get(key, "notary" if key in notaries else "city")
    mark(ax, key, role, LABEL, bold=(key in notaries or key == "novita"))

# the corridor panel's extent, marked on the main map
ax.add_patch(Rectangle((CORRIDOR["lon"][0], CORRIDOR["lat"][0]), np.ptp(CORRIDOR["lon"]), np.ptp(CORRIDOR["lat"]),
                       fill=False, edgecolor=bm.INK, linewidth=0.8, linestyle=(0, (1, 1.2)), zorder=9))

# ---- inset: the Tamaná stretch of the route ----
c_w = 0.43                                                    # fraction of the map width
c_h = c_w * (np.ptp(CORRIDOR["lat"]) / np.ptp(CORRIDOR["lon"])) / np.cos(np.radians(np.mean(CORRIDOR["lat"]))) \
      * fig._layout["map_w"] / fig._layout["map_h"]
axc = ax.inset_axes([0.012, 0.012, c_w, c_h])
axc.set_zorder(20)
# light lines joining the zoom rectangle to the inset, drawn low so routes, flows, labels and icons cover them
_ix, _iy = 0.012, 0.012 + c_h                                  # inset top edge, map-axes fraction
for lon_c, fx in ((CORRIDOR["lon"][0], _ix), (CORRIDOR["lon"][1], _ix + c_w)):
    ax.plot([lon_c, FRAME["lon"][0] + fx * np.ptp(FRAME["lon"])],
            [CORRIDOR["lat"][0], FRAME["lat"][0] + _iy * np.ptp(FRAME["lat"])],
            color="#9a968e", lw=0.55, zorder=3.5, solid_capstyle="butt")
bm.base(axc, CORRIDOR, YEAR_BOUNDS, rivers_ne=("Cauca",), rivers_osm=("San Juan", "Tamaná", "Ingará"),
        aud_color=AUD_COLOR, aud_lw=1.0, dem_path="data/dem_corridor_90m.tif", relief_alpha=0.5)
roads.plot(ax=axc, **ROUTE)
roads[roads.route == "cartago-novita"].plot(ax=axc, color=ROUTE["color"], linewidth=1.6,
                                            linestyle=ROUTE["linestyle"], zorder=6)

# approximate mining areas (mines the author knows of but has not mapped individually)
areas = pd.read_csv("data/mining_areas.csv")
areas = areas[(areas.active_from <= PERIOD[1]) & (areas.active_to >= PERIOD[0])]
riv_all = gpd.read_file(bm.rp("osm/pacific_rivers.shp"))
shapes = []
for _, a in areas.iterrows():
    if a.kind == "place":
        geom = gpd.GeoSeries(gpd.points_from_xy([P[a.ref][0]], [P[a.ref][1]]), crs=4326)
    else:
        geom = riv_all[riv_all.name == a.ref].geometry.reset_index(drop=True).set_crs(4326, allow_override=True)
    shapes.append(geom.to_crs(3116).buffer(a.radius_km * 1000).to_crs(4326).iloc[0])
mine_areas = gpd.GeoSeries(shapes, crs=4326)
mine_areas.plot(ax=axc, **MINE_AREA)
mine_areas.plot(ax=axc, **MINE_EDGE)
for key in SHOW_PANEL:
    role = ROLE.get(key, "notary" if key in notaries else "city")
    mark(axc, key, role, PANEL_LABEL, size=6.8, bold=(key in ("novita", "cartago")))
for key, acuna, (dx, dy), ha in MINES:
    st = PLACE_STYLE["mine" if acuna else "real"]
    lon, lat = P[key]
    axc.scatter([lon], [lat], marker=st["marker"], s=st["s"], facecolor=st["fc"], edgecolor=st["ec"],
                linewidth=st["lw"], zorder=10)
    name = {"mina_salto": "Nuestra Señora de\nChiquinquirá del Salto",
            "quebrada_larga": "Quebrada Larga\nmine"}.get(key, pl.loc[key, "display"])
    axc.annotate(name, (lon, lat), textcoords="offset points", xytext=(dx, dy), ha=ha,
                 va="top" if dy < 0 else "bottom", weight="bold" if acuna else "normal",
                 path_effects=halo, zorder=11, linespacing=1.0, **MINE_LABEL,
                 arrowprops=dict(arrowstyle="-", color="#8a3d0c", lw=0.5, shrinkA=0, shrinkB=4)
                 if abs(dx) + abs(dy) > 20 else None)
bm.river_label(axc, -76.53, 5.012, "Tamaná River", 6, size=6)
axc.text(0.0, 1.015, "Up the Tamaná from Nóvita", transform=axc.transAxes, ha="left", va="bottom",
         fontsize=6.6, weight="bold", color=bm.INK, path_effects=halo, zorder=12)
bm.scale_bar(axc, CORRIDOR, 5, x_frac=0.03, y_frac=0.07, size=6)

# where the route leaves the inset: a short arrow and "to Cartago"
from shapely.geometry import box as _box
_route = roads[roads.route == "cartago-novita"].geometry.iloc[0]
_edge = _box(*[CORRIDOR["lon"][0], CORRIDOR["lat"][0], CORRIDOR["lon"][1], CORRIDOR["lat"][1]]).exterior
_hit = _route.intersection(_edge)
_pts = [g for g in getattr(_hit, "geoms", [_hit])]
_exit = max(_pts, key=lambda g: g.x)                          # the crossing furthest east
_inner = _route.intersection(_box(CORRIDOR["lon"][0], CORRIDOR["lat"][0], CORRIDOR["lon"][1], CORRIDOR["lat"][1]))
_d = _route.project(_exit)                                    # a point a little back along the route
_back = min((_route.interpolate(_d - 0.012), _route.interpolate(_d + 0.012)),
            key=lambda q: 0 if _inner.buffer(1e-6).contains(q) else 1)
# "to Cartago" with its arrow, inside the box, level with where the route leaves it
_y = (_exit.y - CORRIDOR["lat"][0]) / np.ptp(CORRIDOR["lat"])
_y = min(max(_y - 0.07, 0.06), 0.9)
axc.annotate("", xy=(0.985, _y), xytext=(0.905, _y), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="-|>", color=bm.INK, lw=1.0, mutation_scale=8), zorder=12)
axc.text(0.9, _y, "to Cartago", transform=axc.transAxes, ha="right", va="center", fontsize=6,
         style="italic", color=bm.INK, path_effects=halo, zorder=12)
for sp in axc.spines.values():
    sp.set_linewidth(0.9)

bm.scale_bar(ax, FRAME, 50, x_frac=0.82, y_frac=0.875)

# ---- legend strip: two halves inside one frame the width of the map ----
blank = Line2D([], [], color="none", label=" ")
HA = [Line2D([0], [0], color=st["color"], lw=2.4, label=st["label"]) for st in TYPES.values()]
HA += [Line2D([0], [0], color="#8a8a8a", lw=width(v), solid_capstyle="butt", label=f"{v:,} pesos")
       for v in (500, 3000, 10000)] + [blank, blank]
def sym(role, lab):
    st = PLACE_STYLE[role]
    return Line2D([0], [0], marker=st["marker"], color="none", markerfacecolor=st["fc"],
                  markeredgecolor=st["ec"], markeredgewidth=st["lw"], markersize=6.5, label=lab)
HB = [sym("base", "Acuña's base (Nóvita)"), sym("mine", "Acuña's mine"), sym("real", "Other mine"),
      sym("pueblo", "Indigenous town"),
      Patch(facecolor=(0.851, 0.4, 0.122, 0.16), edgecolor="#d9661f", linewidth=0.7, linestyle=(0, (2, 1.5)),
            label="Mining area (approximate)"),
      sym("notary", "Where the act was notarized"), sym("city", "Other cities"),
      Line2D([0], [0], color=ROUTE["color"], lw=ROUTE["linewidth"], linestyle=ROUTE["linestyle"],
             label="Route (river or land trail)"),
      Line2D([0], [0], color=AUD_COLOR, lw=1.0, linestyle=(0, (6, 3)), label=f"Audiencia boundary, {YEAR_BOUNDS}"),
      blank]
kw = dict(ncol=2, fontsize=6.4, frameon=False, labelspacing=0.6, handletextpad=0.45, handlelength=2.0,
          columnspacing=0.9, borderaxespad=0)
ax_leg.add_artist(ax_leg.legend(handles=HA, loc="center left", bbox_to_anchor=(0.012, 0.5), **kw))
ax_leg.legend(handles=HB, loc="center right", bbox_to_anchor=(0.99, 0.5), **kw)
ax_leg.add_patch(Rectangle((0, 0), 1, 1, transform=ax_leg.transAxes, fill=False,
                           edgecolor="#3a3a3a", linewidth=1.1, clip_on=False))

bm.title(fig, f"Map 1.1  Credit exchanges arranged by Don Luis de Acuña from Chocó, {PERIOD[0]}–{PERIOD[1]}", size=9.4)
fig.canvas.draw()
bm.north_arrow(ax, 0.965, 0.84, length=0.07)
bm.curved_text(fig, ax, [(-77.75, 4.55), (-77.72, 5.05), (-77.72, 5.55), (-77.76, 6.05)],
               "PACIFIC OCEAN", **bm.SEA_STYLE)

fig.savefig("outputs/map_transactions_1703_1709.png", dpi=300, facecolor="white")
fig.savefig("outputs/map_transactions_1703_1709.pdf", facecolor="white")
print("wrote outputs/map_transactions_1703_1709.png/.pdf  %.2f x %.2f in" % (bm.PAGE_W, fig._layout["fig_h"]))
