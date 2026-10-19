# -*- coding: utf-8 -*-
"""
Shared base map for the Acuña transaction maps.

It reproduces the style of the introduction map (map_intro_viceroyalty.py), so every
map in the series reads the same: hillshaded relief from dem.tif, muted blue rivers
with a light casing, audiencia seams as dashed lines on land only, grayscale land and
sea, curved sea labels, a scale bar, and a page layout for a 6.5 x 9 in text block
with the legend as a strip under the map.

Paths are relative to the Thesis Maps folder (one level up), where the shared data
lives: dem.tif, hgis/, ne/, osm/.
"""
import os
import unicodedata
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import shapely
from shapely.geometry import box, LineString
from shapely.ops import unary_union
from matplotlib.colors import LightSource

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rp(*p):
    return os.path.join(ROOT, *p)

# ---- palette (same as the introduction map) ----
LAND = "#eceae6"; OCEAN = "#f7f8f9"; RIVERBLUE = "#6f8ea6"; RIVERLABEL = "#56718a"
AUD_LINE = "#333333"; COAST = "#9a9a9a"; INK = "#242424"; RELIEF_LABEL = "#6a665f"
SEA_STYLE = dict(spacing=1.25, fontsize=7, weight="bold", color="#5b6b77", alpha=0.85, zorder=5)
PAGE_W = 6.5                       # text block width, inches (US Letter, 1 in margins)


def page(frame, title_h=0.32, leg_h=0.9, gap=0.10, bot=0.04, margin=0.08, panel=None, panel_gap=0.12):
    """Figure sized to the text width: title, map (true aspect), optional full-width panel
    (a second frame, e.g. a corridor zoom) under the map, and the legend strip at the bottom.
    Returns fig, ax, ax_leg, or fig, ax, ax_panel, ax_leg when `panel` is given."""
    map_w = PAGE_W - 2 * margin
    def h(fr):
        return map_w * (np.ptp(fr["lat"]) / np.ptp(fr["lon"])) / np.cos(np.radians(np.mean(fr["lat"])))
    map_h = h(frame)
    pan_h = h(panel) if panel else 0.0
    fig_h = title_h + map_h + (panel_gap + pan_h if panel else 0) + gap + leg_h + bot
    fig = plt.figure(figsize=(PAGE_W, fig_h))
    x, w = margin / PAGE_W, map_w / PAGE_W
    y_leg = bot
    y_pan = bot + leg_h + gap
    y_map = y_pan + (pan_h + panel_gap if panel else 0)
    ax = fig.add_axes([x, y_map / fig_h, w, map_h / fig_h])
    ax_leg = fig.add_axes([x, y_leg / fig_h, w, leg_h / fig_h]); ax_leg.axis("off")
    fig._layout = dict(margin=margin, fig_h=fig_h, map_w=map_w, map_h=map_h, pan_h=pan_h)
    if panel:
        ax_pan = fig.add_axes([x, y_pan / fig_h, w, pan_h / fig_h])
        return fig, ax, ax_pan, ax_leg
    return fig, ax, ax_leg


def title(fig, text, size=10.5):
    L = fig._layout
    fig.text(L["margin"] / PAGE_W, 1 - 0.06 / L["fig_h"], text, ha="left", va="top",
             fontsize=size, weight="bold", color=INK, linespacing=1.15)


def slice_terr(year, level):
    t = gpd.read_file(rp("hgis/terr/territorios-2019-03-28.shp"))
    t["START"] = t["START"].astype(int); t["END_"] = t["END_"].astype(int)
    return t[(t["Nivel"] == level) & (t["START"] <= year) & (t["END_"] >= year)]


def base(ax, frame, year, rivers_ne=("Cauca", "Magdalena", "Atrato"),
         rivers_osm=("San Juan", "Tamaná"), vert_exag=2.5, relief_alpha=0.55, aud_color=AUD_LINE, aud_lw=1.1, dem_path=None):
    """Land, sea, relief, audiencia seams (for `year`), rivers and coast."""
    fr = box(frame["lon"][0], frame["lat"][0], frame["lon"][1], frame["lat"][1])
    ax.set_facecolor(LAND)
    ocean = gpd.clip(gpd.read_file(rp("ne/ne_10m_ocean.shp"), bbox=fr.bounds), fr)
    if len(ocean):
        ocean.plot(ax=ax, facecolor=OCEAN, edgecolor="none", zorder=1)

    # relief
    dem_path = dem_path or rp("dem.tif")
    if relief_alpha > 0 and os.path.exists(dem_path):
        import rasterio
        from rasterio.mask import mask
        with rasterio.open(dem_path) as src:
            dem, t = mask(src, [fr], crop=True, nodata=np.nan)
            dem = dem[0].astype(float)
        dy = abs(t[4]) * 111320; dx = t[0] * 111320 * np.cos(np.radians(np.mean(frame["lat"])))
        hs = LightSource(azdeg=315, altdeg=45).hillshade(np.where(np.isfinite(dem), dem, 0.0),
                                                        vert_exag=vert_exag, dx=dx, dy=dy)
        hs = np.ma.masked_where(~np.isfinite(dem), hs)
        ext = [t[2], t[2] + t[0] * dem.shape[1], t[5] + t[4] * dem.shape[0], t[5]]
        ax.imshow(hs, extent=ext, cmap="gray", alpha=relief_alpha, zorder=3, origin="upper",
                  interpolation="bilinear")

    # audiencia seams on land only (not the coast, the frame, or the edge of the HGIS extract)
    aud = gpd.clip(slice_terr(year, "Audiencia"), fr)
    skip = unary_union([ocean.union_all().buffer(0.03) if len(ocean) else box(0, 0, 0, 0), fr.exterior.buffer(0.01),
                        LineString([(-70.0, -6.0), (-70.0, 13.0)]).buffer(0.03)])
    seams = shapely.line_merge(unary_union(list(aud.boundary)).difference(skip))
    seams = gpd.GeoSeries([g for g in getattr(seams, "geoms", [seams]) if g.length > 0.15 and not g.is_empty],
                          crs=aud.crs)
    if len(seams):
        seams.plot(ax=ax, color="white", linewidth=2.6, alpha=0.75, zorder=4)
        seams.plot(ax=ax, color=aud_color, linewidth=aud_lw, linestyle=(0, (6, 3)), zorder=4)

    # rivers: Natural Earth main rivers + OpenStreetMap Pacific-side rivers
    riv = gpd.read_file(rp("ne/ne_10m_rivers_lake_centerlines.shp"), bbox=fr.bounds)
    riv = gpd.clip(riv[riv["name"].isin(rivers_ne)], fr)
    pac = gpd.read_file(rp("osm/pacific_rivers.shp"))
    pac = gpd.clip(pac[pac["name"].map(lambda n: unicodedata.normalize("NFC", n)).isin(rivers_osm)], fr)
    for r_, lw in ((riv, 1.4), (pac, 0.95)):
        if len(r_):
            r_.plot(ax=ax, color="white", linewidth=lw + 1.4, alpha=0.6, zorder=5)
            r_.plot(ax=ax, color=RIVERBLUE, linewidth=lw, zorder=5)
    coast = gpd.clip(gpd.read_file(rp("ne/ne_10m_coastline.shp"), bbox=fr.bounds), fr)
    if len(coast):
        coast.plot(ax=ax, color=COAST, linewidth=0.8, zorder=6)

    ax.set_xlim(*frame["lon"]); ax.set_ylim(*frame["lat"])
    ax.set_aspect(1.0 / np.cos(np.radians(np.mean(frame["lat"]))))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#3a3a3a"); s.set_linewidth(1.1)
    return fr


def river_label(ax, lon, lat, text, rot, size=6.3):
    ax.text(lon, lat, text, rotation=rot, ha="center", va="center", fontsize=size,
            style="italic", color=RIVERLABEL, zorder=5)


def relief_label(ax, lon, lat, text, rot, size=6.6):
    ax.text(lon, lat, text, rotation=rot, rotation_mode="anchor", ha="center", va="center",
            fontsize=size, style="italic", color=RELIEF_LABEL, zorder=5)


def scale_bar(ax, frame, km, x_frac=0.03, y_frac=0.93, size=7):
    lat0 = np.mean(frame["lat"])
    deg = km / (111.32 * np.cos(np.radians(lat0)))
    sx = frame["lon"][0] + x_frac * np.ptp(frame["lon"]); sy = frame["lat"][0] + y_frac * np.ptp(frame["lat"])
    tick = 0.012 * np.ptp(frame["lat"])
    ax.plot([sx, sx + deg], [sy, sy], color=INK, lw=2.4, solid_capstyle="butt", zorder=10)
    for xx in (sx, sx + deg):
        ax.plot([xx, xx], [sy - tick, sy + tick], color=INK, lw=1.2, zorder=10)
    ax.text(sx + deg / 2, sy + 1.6 * tick, f"{km} km", ha="center", va="bottom", fontsize=size, zorder=10)


def north_arrow(ax, x, y, length=0.06, size=10):
    """Arrow in axes fraction coordinates, from (x, y) up by `length`."""
    ax.annotate("", xy=(x, y + length), xytext=(x, y), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2), zorder=10)
    ax.text(x, y + length + 0.005, "N", transform=ax.transAxes, ha="center", va="bottom",
            fontsize=size, weight="bold", zorder=10)


def curved_text(fig, ax, pts, text, spacing=1.12, align="center", **kw):
    """Write text letter by letter along a smooth path of (lon, lat) points, centred on it.
    Call after fig.canvas.draw() so the layout is fixed."""
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    xy = np.array(pts, float)
    t = np.linspace(0, 1, len(xy)); tt = np.linspace(0, 1, 400)
    path = np.c_[np.interp(tt, t, xy[:, 0]), np.interp(tt, t, xy[:, 1])]
    k = np.ones(25) / 25
    path = np.c_[[np.convolve(np.pad(c, 12, mode="edge"), k, mode="same")[12:-12] for c in path.T]].T
    disp = ax.transData.transform(path)
    seg = np.hypot(*np.diff(disp, axis=0).T); arc = np.r_[0, np.cumsum(seg)]
    fp = FontProperties(size=kw.get("fontsize", 9), weight=kw.get("weight", "normal"), style=kw.get("style", "normal"))
    px = fig.dpi / 72.0
    em = fp.get_size_in_points() * px
    track = (spacing - 1.0) * em
    # advance of each letter = running width of the text up to it (keeps the font's own
    # spacing and kerning), plus even tracking between letters
    rend = fig.canvas.get_renderer()                               # widths in display pixels
    run = [0.0] + [rend.get_text_width_height_descent(text[:j + 1].replace(" ", "\u00a0"), fp, ismath=False)[0]
                   for j in range(len(text))]
    widths = [run[j + 1] - run[j] + track for j in range(len(text))]
    pos = 0.0 if align == "start" else (arc[-1] - sum(widths)) / 2
    for c, w in zip(text, widths):
        mid = pos + w / 2
        i = np.searchsorted(arc, mid).clip(1, len(arc) - 1)
        x, y = np.interp(mid, arc, disp[:, 0]), np.interp(mid, arc, disp[:, 1])
        ang = np.degrees(np.arctan2(disp[i, 1] - disp[i - 1, 1], disp[i, 0] - disp[i - 1, 0]))
        lon, lat = ax.transData.inverted().transform((x, y))
        ax.text(lon, lat, c, rotation=ang, rotation_mode="anchor", ha="center", va="center", **kw)
        pos += w
