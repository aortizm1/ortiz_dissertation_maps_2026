#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Introduction map — places of the dissertation, framed by the Viceroyalty of
New Granada (established 1726). Grayscale base. Colour is reserved for the
place markers so the reader's eye goes to the places.

Terrain: if a DEM GeoTIFF is present at DEM_PATH it is hillshaded under the map
(real relief). Otherwise a generalised grey relief is drawn from the cordillera
spines, clearly a schematic stand-in, not measured topography.

Boundaries: HGIS 'territorios' (Virreinato + Audiencia), sliced to YEAR.
Coast / ocean / main rivers: Natural Earth 10m (folder ne/). Pacific rivers around
La Cruz: OpenStreetMap (folder osm/). Places: HGIS gazetteer.
"""
import os as _bos
_bos.chdir(_bos.path.dirname(_bos.path.abspath(__file__)))
_bos.makedirs('outputs', exist_ok=True)

import os
import unicodedata
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.colors import LightSource
import geopandas as gpd
from shapely.geometry import box, LineString

YEAR = 1726
FRAME = dict(lon=(-80.45, -70.05), lat=(-1.0, 11.2))
VICE_FULL = "hgis/virreinato_nueva_granada_1718-1749.gpkg"   # uncut outline, for the locator inset
LAND_50 = "ne/ne_50m_land/ne_50m_land.shp"                     # continent outline, for the inset
TERR = "hgis/terr/territorios-2019-03-28.shp"
PAC_RIVERS = "osm/pacific_rivers.shp"
PAC_KEEP = ["San Juan", "Dagua", "Tamaná", "Neguá", "Naurita"]   # Nóvita on the Tamaná, La Cruz on the Dagua;
# the Naurita joins the lower Neguá, which joins the Atrato below Quibdó
DEM_PATH = "dem.tif"          # drop a GeoTIFF here for a real hillshade

# ---------------------------------------------------------------- places
PLACES = {
    "Santafé de Bogotá": (-74.075,  4.597, "capital"),
    "Quito":              (-78.512, -0.220, "audiencia"),
    "Popayán":            (-76.606,  2.442, "provincial"),
    "Nóvita":             (-76.606,  4.955, "mining"),
    "Quibdó":             (-76.658,  5.687, "mining"),
    "Cartago":            (-75.912,  4.747, "town"),
    "Cali":               (-76.532,  3.451, "town"),
    "La Cruz":            (-77.003,  3.817, "mining"),  # pueblo, partido de Raposo (Pacific)
    "Cartagena":          (-75.551, 10.423, "port"),
    "Zipaquirá":          (-74.004,  5.024, "salt"),
    "Nemocón":            (-73.878,  5.067, "salt"),
}
LABEL = {
    "Santafé de Bogotá": (8, -3, "left"), "Quito": (9, 3, "left"),
    "Popayán": (9, 0, "left"), "Nóvita": (-7, -3, "right"), "Quibdó": (0, 10, "center"),
    "Cartago": (0, -10, "center"), "Cali": (0, -10, "center"),
    "La Cruz": (-7, 0, "right"), "Ibagué": (0, -10, "center"),
    "Honda": (0, 10, "center"), "Cartagena": (8, 0, "left"),
    "Zipaquirá": (-7, -5, "right"), "Nemocón": (7, 0, "left"),
}
SEATS = {
    "Quito":              ("seat of the\nAudiencia de Quito", 9, -13),
    "Santafé de Bogotá": ("seat of the Audiencia de Santafé", 8, -15),
}
CAT_STYLE = {
    "capital":    dict(marker="*", s=260, fc="#b8860b", ec="#2b2b2b", lw=0.9, label="Viceregal capital (court + mint)"),
    "audiencia":  dict(marker="s", s=76,  fc="#111111", ec="white",   lw=1.0, label="Audiencia seat"),
    "provincial": dict(marker="s", s=56,  fc="#555555", ec="white",   lw=0.9, label="Provincial capital"),
    "mining":     dict(marker="^", s=84,  fc="#d9661f", ec="white",   lw=0.8, label="Gold-mining frontier"),
    "salt":       dict(marker="D", s=56,  fc="#1b6f6a", ec="white",   lw=0.8, label="Highland salt town"),
    "port":       dict(marker="o", s=64,  fc="#274b6d", ec="white",   lw=0.9, label="Port"),
    "town":       dict(marker="o", s=34,  fc="#6f6f6f", ec="white",   lw=0.7, label="Other cities"),
}
CORDILLERAS = {
    "Cordillera Occidental": ([(-77.2,1.3),(-76.9,2.6),(-76.5,3.9),(-76.2,5.1),(-76.15,6.3),(-76.4,7.4),(-76.7,8.2)], (-76.32,6.85, 80)),
    "Cordillera Central":    ([(-76.5,1.8),(-76.05,3.1),(-75.65,4.3),(-75.45,5.3),(-75.45,6.3),(-75.65,7.3),(-75.9,8.3)], (-75.28,6.9, 84)),
    "Cordillera Oriental":   ([(-76.4,1.7),(-75.7,2.7),(-75.0,3.7),(-74.2,4.6),(-73.6,5.6),(-73.0,6.6),(-72.6,7.5)], (-73.10,6.05, 52)),
}
WATER_LABELS = [
    (-76.98, 6.6, "Atrato River", 62, False),
    (-75.80, 6.9, "Cauca River", 80, False),
    (-74.50, 6.7, "Magdalena River", 74, False),
    (-76.83, 3.915, "Dagua River", -12, False),
    (-76.30, 5.085, "Tamaná River", 4, False),
]

# grayscale palette
LAND = "#eceae6"; OCEAN = "#f7f8f9"; RIVERBLUE = "#6f8ea6"
VICE_HI = "#8e8a82"; INSET_LAND = "#dcd9d3"
AUD_LINE = "#333333"; COAST = "#9a9a9a"; INK = "#242424"

fr = box(FRAME["lon"][0], FRAME["lat"][0], FRAME["lon"][1], FRAME["lat"][1])
terr = gpd.read_file(TERR)
terr["START"] = terr["START"].astype(int); terr["END_"] = terr["END_"].astype(int)
def slice_level(level, name=None):
    s = terr[(terr["Nivel"] == level) & (terr["START"] <= YEAR) & (terr["END_"] >= YEAR)]
    if name:
        s = s[s["Nombre"].str.contains(name, case=False, na=False)]
    return gpd.clip(s, fr)
vice = slice_level("Virreinato", "Granada")
aud = slice_level("Audiencia")

ocean = gpd.clip(gpd.read_file("ne/ne_10m_ocean.shp", bbox=fr.bounds), fr)
coast = gpd.clip(gpd.read_file("ne/ne_10m_coastline.shp", bbox=fr.bounds), fr)
riv = gpd.read_file("ne/ne_10m_rivers_lake_centerlines.shp", bbox=fr.bounds)
riv = gpd.clip(riv[riv["name"].isin(["Cauca", "Magdalena", "Atrato"])], fr)
# Pacific-side rivers from OpenStreetMap (osm/pacific_rivers.shp). The file also holds
# Calima, Anchicaya, Raposo, Cajambre, Yurumangui, Naya, Condoto, Sipi, Iro, Andagueda,
# Quito; add a name to PAC_KEEP to draw it. The Naurita is traced (see SOURCES.txt).
riv_pac = gpd.read_file(PAC_RIVERS)
riv_pac = gpd.clip(riv_pac[riv_pac["name"].map(lambda n: unicodedata.normalize("NFC", n)).isin(PAC_KEEP)], fr)

# page layout for a 6.5 x 9 in text block: title, map, legend strip (all in inches)
FIG_W, M = 6.5, 0.08
MAP_W = FIG_W - 2 * M
MAP_H = MAP_W * (np.ptp(FRAME["lat"]) / np.ptp(FRAME["lon"])) / np.cos(np.radians(np.mean(FRAME["lat"])))
TITLE_H, GAP, LEG_H, BOT = 0.32, 0.10, 0.80, 0.04
FIG_H = TITLE_H + MAP_H + GAP + LEG_H + BOT
fig = plt.figure(figsize=(FIG_W, FIG_H))
ax = fig.add_axes([M / FIG_W, (BOT + LEG_H + GAP) / FIG_H, MAP_W / FIG_W, MAP_H / FIG_H])
ax_leg = fig.add_axes([M / FIG_W, BOT / FIG_H, MAP_W / FIG_W, LEG_H / FIG_H]); ax_leg.axis("off")
fig.patch.set_facecolor("white"); ax.set_facecolor(LAND)
ocean.plot(ax=ax, facecolor=OCEAN, edgecolor="none", zorder=1)
vice.plot(ax=ax, facecolor=LAND, edgecolor="none", zorder=2)

# ---- terrain ----
have_dem = os.path.exists(DEM_PATH)
if have_dem:
    import rasterio
    from rasterio.mask import mask
    with rasterio.open(DEM_PATH) as src:
        dem, dtrans = mask(src, [fr], crop=True, nodata=np.nan)
        dem = dem[0].astype(float)
    ls = LightSource(azdeg=315, altdeg=45)
    # pixel spacing in meters so vert_exag is a true exaggeration factor
    dy_m = abs(dtrans[4]) * 111320
    dx_m = dtrans[0] * 111320 * np.cos(np.radians(np.mean(FRAME["lat"])))
    hs = ls.hillshade(np.where(np.isfinite(dem), dem, 0.0), vert_exag=2.5, dx=dx_m, dy=dy_m)
    hs = np.ma.masked_where(~np.isfinite(dem), hs)     # no shading over the sea
    ext = [dtrans[2], dtrans[2] + dtrans[0] * dem.shape[1],
           dtrans[5] + dtrans[4] * dem.shape[0], dtrans[5]]
    ax.imshow(hs, extent=ext, cmap="gray", alpha=0.55, zorder=3, origin="upper")
else:
    # generalised grey relief from the cordillera spines (schematic stand-in)
    for nm, (pts, lab) in CORDILLERAS.items():
        line = LineString(pts)
        for w, col, a in [(0.26, "#dcd9d3", 0.75), (0.16, "#ccc8c1", 0.75), (0.07, "#bab5ad", 0.8)]:
            gpd.GeoSeries([line.buffer(w)], crs=vice.crs).clip(vice).plot(
                ax=ax, facecolor=col, edgecolor="none", alpha=a, zorder=3)

for nm, (pts, lab) in CORDILLERAS.items():
    ax.text(lab[0], lab[1], nm, rotation=lab[2], rotation_mode="anchor", ha="center",
            va="center", fontsize=6.6, style="italic", color="#6a665f", zorder=5)

# white halo under the dashes so the boundary lifts off the hillshade
# audiencia edges on land only: drop the stretches that trace the coast or the map
# edge, and merge the pieces so the dash pattern runs evenly
import shapely
from shapely.ops import unary_union
_clip_edge = LineString([(-70.0, -6.0), (-70.0, 13.0)]).buffer(0.03)   # where the HGIS extract was cut
_skip = unary_union([ocean.union_all().buffer(0.03), fr.exterior.buffer(0.01), _clip_edge])
seams = shapely.line_merge(unary_union(list(aud.boundary)).difference(_skip))
seams = gpd.GeoSeries([g for g in getattr(seams, "geoms", [seams]) if g.length > 0.15],
                      crs=aud.crs)          # drop slivers left where the HGIS coast differs
seams.plot(ax=ax, color="white", linewidth=2.6, alpha=0.75, zorder=4)
seams.plot(ax=ax, color=AUD_LINE, linewidth=1.1, linestyle=(0, (6, 3)), zorder=4)
for r_, lw in ((riv, 1.4), (riv_pac, 0.95)):          # light casing, then the river
    r_.plot(ax=ax, color="white", linewidth=lw + 1.4, alpha=0.6, zorder=5)
    r_.plot(ax=ax, color=RIVERBLUE, linewidth=lw, zorder=5)
coast.plot(ax=ax, color=COAST, linewidth=0.8, zorder=6)

for lon, lat, txt, rot, sea in WATER_LABELS:
    ax.text(lon, lat, txt, rotation=rot, ha="center", va="center",
            fontsize=9 if sea else 6.3, style="normal" if sea else "italic",
            color="#5b6b77" if sea else "#56718a",
            weight="bold" if sea else "normal", alpha=0.85 if sea else 1.0, zorder=5)

for name, (lon, lat, cat) in PLACES.items():
    st = CAT_STYLE[cat]
    ax.scatter([lon], [lat], marker=st["marker"], s=st["s"], facecolor=st["fc"],
               edgecolor=st["ec"], linewidth=st["lw"], zorder=11)
    dx, dy, ha = LABEL.get(name, (8, 0, "left"))
    disp = "Quibdó (Citará)" if name == "Quibdó" else name
    weight = "bold" if cat in ("capital", "audiencia") else "semibold"
    # labels in front of rivers, routes and boundaries, with a white halo so nothing cuts them
    ax.annotate(disp, (lon, lat), textcoords="offset points", xytext=(dx, dy),
                ha=ha, va="center", fontsize=7.6, weight=weight, color="#111111", zorder=12,
                path_effects=[pe.withStroke(linewidth=2.6, foreground="white")])
    if name in SEATS:
        txt, sdx, sdy = SEATS[name]
        ax.annotate(txt, (lon, lat), textcoords="offset points", xytext=(sdx, sdy),
                    ha="left", va="center", fontsize=5.9, style="italic", color="#3d392f", zorder=12,
                    path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])

ax.set_xlim(*FRAME["lon"]); ax.set_ylim(*FRAME["lat"])
ax.set_aspect(1.0 / np.cos(np.radians(np.mean(FRAME["lat"]))))
for s in ax.spines.values():
    s.set_edgecolor("#3a3a3a"); s.set_linewidth(1.1)
ax.set_xticks([]); ax.set_yticks([])

km = 200; deg = km / (111.32 * np.cos(np.radians(np.mean(FRAME["lat"]))))
sx, sy = FRAME["lon"][0] + 0.35, FRAME["lat"][1] - 0.6
ax.plot([sx, sx + deg], [sy, sy], color=INK, lw=2.4, solid_capstyle="butt", zorder=10)
for xx in (sx, sx + deg):
    ax.plot([xx, xx], [sy - 0.1, sy + 0.1], color=INK, lw=1.2, zorder=10)
ax.text(sx + deg / 2, sy + 0.16, f"{km} km", ha="center", va="bottom", fontsize=7)

handles = [Line2D([0], [0], marker="s", color="none", markerfacecolor=VICE_HI,
                  markeredgecolor="none", markersize=10, label="Viceroyalty of New Granada (inset)"),
           Line2D([0], [0], color=AUD_LINE, lw=1.1, linestyle=(0, (6, 3)), label="Audiencia boundary")]
handles += [Line2D([0], [0], marker=s["marker"], color="none", markerfacecolor=s["fc"],
                   markeredgecolor=s["ec"], markersize=11 if s["marker"] == "*" else 7.5,
                   label=s["label"]) for s in CAT_STYLE.values()]
leg = ax_leg.legend(handles=handles, loc="center", bbox_to_anchor=(0, 0, 1, 1), mode="expand",
                    ncol=3, fontsize=7.3, frameon=True, edgecolor="#3a3a3a", fancybox=False,
                    borderpad=0.7, labelspacing=0.6, handletextpad=0.5, borderaxespad=0)
leg.get_frame().set_linewidth(1.1)

# ---- locator inset: South America and the Caribbean, the viceroyalty highlighted ----
IN_LON, IN_LAT = (-93.0, -33.0), (-57.0, 24.0)
in_aspect = 1.0 / np.cos(np.radians(np.mean(IN_LAT)))
in_w = 0.215                                                   # fraction of the map width
in_h = in_w * MAP_W * (np.ptp(IN_LAT) / np.ptp(IN_LON)) * in_aspect / MAP_H
axi = ax.inset_axes([1 - in_w - 0.012, 0.012, in_w, in_h])
axi.set_facecolor(OCEAN)
gpd.read_file(LAND_50, bbox=(IN_LON[0], IN_LAT[0], IN_LON[1], IN_LAT[1])).plot(
    ax=axi, facecolor=INSET_LAND, edgecolor="#b5b1aa", linewidth=0.3)
gpd.read_file(VICE_FULL).plot(ax=axi, facecolor=VICE_HI, edgecolor="#5f5b54", linewidth=0.4)
axi.add_patch(plt.Rectangle((FRAME["lon"][0], FRAME["lat"][0]), np.ptp(FRAME["lon"]), np.ptp(FRAME["lat"]),
                            fill=False, edgecolor=INK, linewidth=0.9))
axi.set_xlim(*IN_LON); axi.set_ylim(*IN_LAT); axi.set_aspect(in_aspect)
axi.set_xticks([]); axi.set_yticks([])
for sp in axi.spines.values():
    sp.set_edgecolor("#3a3a3a"); sp.set_linewidth(0.9)

fig.text(M / FIG_W, 1 - 0.06 / FIG_H, f"Places of the dissertation in the Viceroyalty of New Granada, c. {YEAR}",
         ha="left", va="top", fontsize=10.5, weight="bold", color=INK)
fig.canvas.draw()                                   # fix the layout before placing by display units

# north arrow just above the inset, at its right side
lb = axi.get_window_extent().transformed(ax.transAxes.inverted())
ax_x = lb.x1 - 0.04
ax.annotate("", xy=(ax_x, lb.y1 + 0.065), xytext=(ax_x, lb.y1 + 0.018), xycoords="axes fraction",
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
ax.text(ax_x, lb.y1 + 0.07, "N", transform=ax.transAxes, ha="center", va="bottom",
        fontsize=10, weight="bold")

def curved_text(ax, pts, text, spacing=1.12, **kw):
    """Write text letter by letter along a smooth path of (lon, lat) points, centred on it."""
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    xy = np.array(pts, float)
    t = np.linspace(0, 1, len(xy)); tt = np.linspace(0, 1, 400)
    path = np.c_[np.interp(tt, t, xy[:, 0]), np.interp(tt, t, xy[:, 1])]
    k = np.ones(25) / 25                                         # smooth the polyline
    path = np.c_[[np.convolve(np.pad(c, 12, mode="edge"), k, mode="same")[12:-12] for c in path.T]].T
    disp = ax.transData.transform(path)
    seg = np.hypot(*np.diff(disp, axis=0).T); arc = np.r_[0, np.cumsum(seg)]
    fp = FontProperties(size=kw.get("fontsize", 9), weight=kw.get("weight", "normal"))
    px = fig.dpi / 72.0
    em = fp.get_size_in_points() * px
    track = (spacing - 1.0) * em                                 # even gap between letters
    widths = [(0.55 * em if c == " " else TextPath((0, 0), c, prop=fp).get_extents().width * px)
              + track for c in text]
    start = (arc[-1] - sum(widths)) / 2
    pos = start
    for c, w in zip(text, widths):
        mid = pos + w / 2
        i = np.searchsorted(arc, mid).clip(1, len(arc) - 1)
        x, y = np.interp(mid, arc, disp[:, 0]), np.interp(mid, arc, disp[:, 1])
        ang = np.degrees(np.arctan2(disp[i, 1] - disp[i - 1, 1], disp[i, 0] - disp[i - 1, 0]))
        lon, lat = ax.transData.inverted().transform((x, y))
        ax.text(lon, lat, c, rotation=ang, rotation_mode="anchor", ha="center", va="center", **kw)
        pos += w

# Caribbean Sea, curving along the coast south-west of Cartagena (reads from the south-west)
# sea labels share one style: bold, letter-spaced, curving along the coast, reading upward
SEA_STYLE = dict(spacing=1.25, fontsize=7, weight="bold", color="#5b6b77", alpha=0.85, zorder=5)
curved_text(ax, [(-77.60, 8.95), (-77.05, 9.50), (-76.60, 10.05), (-76.30, 10.55), (-76.15, 11.00)],
            "CARIBBEAN SEA", **SEA_STYLE)
curved_text(ax, [(-80.05, 1.10), (-79.60, 2.40), (-79.20, 3.70), (-78.95, 5.00), (-78.85, 6.00)],
            "PACIFIC OCEAN", **SEA_STYLE)
plt.savefig("outputs/map_intro_viceroyalty.png", dpi=300, facecolor="white")   # fixed 6.5 in wide page
plt.savefig("outputs/map_intro_viceroyalty.pdf", facecolor="white")
print("wrote map_intro_viceroyalty.png/.pdf  %.2f x %.2f in  | DEM used:" % (FIG_W, FIG_H), have_dem)
