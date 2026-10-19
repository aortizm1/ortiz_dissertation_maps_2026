#!/usr/bin/env python3
"""90 m relief (Copernicus GLO-90, full resolution) for the Nóvita–Cartago corridor panel.
Writes data/dem_corridor_90m.tif (EPSG:4326, float32, NaN nodata). Run once."""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")
import numpy as np, rasterio
from rasterio.merge import merge
BOX = (-77.0, 4.5, -75.7, 5.15)
URL = ("/vsicurl/https://copernicus-dem-90m.s3.amazonaws.com/Copernicus_DSM_COG_30_N{lat:02d}_00_W{lon:03d}_00_DEM/"
       "Copernicus_DSM_COG_30_N{lat:02d}_00_W{lon:03d}_00_DEM.tif")
srcs = [rasterio.open(URL.format(lat=la, lon=lo)) for la in (4, 5) for lo in (76, 77)]
arr, tr = merge(srcs, bounds=BOX, nodata=np.nan, dtype="float32")
prof = dict(driver="GTiff", width=arr.shape[2], height=arr.shape[1], count=1, dtype="float32",
            crs="EPSG:4326", transform=tr, nodata=np.nan, compress="deflate", predictor=3)
with rasterio.open("data/dem_corridor_90m.tif", "w", **prof) as d:
    d.write(arr[0], 1)
print("wrote data/dem_corridor_90m.tif", arr.shape, np.nanmin(arr), np.nanmax(arr))
