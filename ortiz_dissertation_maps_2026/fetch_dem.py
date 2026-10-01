#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build dem.tif for the introduction map from the Copernicus GLO-90 DEM.

Reads the public cloud optimized GeoTIFFs on AWS anonymously (no account),
mosaics and resamples them onto a 0.003 degree grid (about 330 m) in EPSG:4326,
masks the ocean with the Natural Earth 10m ocean polygon, and writes a float32
single band GeoTIFF with NaN as nodata. Also writes outputs/dem_preview.png.

    python fetch_dem.py
"""
import os, math
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.transform import from_origin
from rasterio.warp import reproject
import geopandas as gpd
from shapely.geometry import box
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

BOX = (-80.6, -1.3, -69.9, 11.4)       # required coverage (intro map frame -80.45..-70.05, -1.0..11.2)
MARGIN = 0.2
RES = 0.003                            # degrees, about 330 m
URL = ("https://copernicus-dem-90m.s3.amazonaws.com/"
       "Copernicus_DSM_COG_30_{ns}{lat:02d}_00_{ew}{lon:03d}_00_DEM/"
       "Copernicus_DSM_COG_30_{ns}{lat:02d}_00_{ew}{lon:03d}_00_DEM.tif")

W, S, E, N = BOX[0] - MARGIN, BOX[1] - MARGIN, BOX[2] + MARGIN, BOX[3] + MARGIN
nx, ny = round((E - W) / RES), round((N - S) / RES)
dst_t = from_origin(W, N, RES, RES)
out = np.full((ny, nx), np.nan, dtype="float32")

def tile_url(lat0, lon0):
    return URL.format(ns="N" if lat0 >= 0 else "S", lat=abs(lat0),
                      ew="E" if lon0 >= 0 else "W", lon=abs(lon0))

used, missing = 0, 0
for lat0 in range(math.floor(S), math.ceil(N)):
    for lon0 in range(math.floor(W), math.ceil(E)):
        url = tile_url(lat0, lon0)
        try:
            # overview_level=0 is the first overview (about 180 m), plenty for 330 m
            src = rasterio.open("/vsicurl/" + url, overview_level=0)
        except rasterio.errors.RasterioIOError:
            missing += 1                  # open ocean: no tile published
            continue
        with src:
            buf = np.full((ny, nx), np.nan, dtype="float32")
            reproject(src.read(1).astype("float32"), buf,
                      src_transform=src.transform, src_crs=src.crs,
                      src_nodata=src.nodata, dst_transform=dst_t,
                      dst_crs="EPSG:4326", dst_nodata=np.nan,
                      resampling=Resampling.average)
        ok = np.isfinite(buf)
        out[ok] = buf[ok]
        used += 1
        print(f"  {os.path.basename(url)}")
print(f"tiles used: {used}, not published (ocean): {missing}")

# mask ocean with the Natural Earth polygon (Copernicus fills the sea with 0)
ocean = gpd.read_file("ne/ne_10m_ocean.shp", bbox=(W, S, E, N)).clip(box(W, S, E, N))
sea = geometry_mask(ocean.geometry, out_shape=out.shape, transform=dst_t, invert=True)
out[sea] = np.nan

prof = dict(driver="GTiff", height=ny, width=nx, count=1, dtype="float32",
            crs="EPSG:4326", transform=dst_t, nodata=np.nan, compress="deflate",
            predictor=3, tiled=True, blockxsize=512, blockysize=512)
with rasterio.open("dem.tif", "w", **prof) as dst:
    dst.write(out, 1)
    dst.update_tags(SOURCE="Copernicus GLO-90 DEM (COP-DEM_GLO-90), ESA / Airbus, "
                    "via AWS Open Data s3://copernicus-dem-90m",
                    RESAMPLING=f"average to {RES} deg", UNITS="meters")

with rasterio.open("dem.tif") as d:
    a = d.read(1)
    print("extent (W,S,E,N):", tuple(round(v, 4) for v in d.bounds))
    print("pixel size (deg):", d.res, f"(~{d.res[0] * 111320:.0f} m)")
    print("size (px):", d.width, "x", d.height, " CRS:", d.crs, " nodata:", d.nodata)
    print("elevation min/max (m): %.0f / %.0f" % (np.nanmin(a), np.nanmax(a)))
    print("file size: %.1f MB" % (os.path.getsize("dem.tif") / 1e6))

# quick hillshade preview
ls = LightSource(azdeg=315, altdeg=45)
dx = RES * 111320 * math.cos(math.radians((S + N) / 2)); dy = RES * 111320
hs = ls.hillshade(np.nan_to_num(out, nan=0.0), vert_exag=2, dx=dx, dy=dy)
hs = np.ma.masked_where(~np.isfinite(out), hs)
fig, ax = plt.subplots(figsize=(6, 9))
ax.imshow(hs, cmap="gray", extent=[W, E, S, N])
ax.set_aspect(1 / math.cos(math.radians((S + N) / 2)))
ax.set_title("dem.tif hillshade preview (Copernicus GLO-90, ~330 m)", fontsize=9)
fig.savefig("outputs/dem_preview.png", dpi=150, bbox_inches="tight")
print("wrote outputs/dem_preview.png")
