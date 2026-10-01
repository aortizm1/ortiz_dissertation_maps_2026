#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resolve a place name to HGIS gazetteer coordinates (region NGR / QUI).

    python resolve_place.py "Novita"                 # all matches
    python resolve_place.py "La Cruz" -77.0 3.8       # nearest to a hint lon/lat

Prints candidates with their coordinates so you can drop them into a map's
PLACES dict. The gazetteer is continent-wide in the full dataset; here it is
already filtered to New Granada (NGR) and Quito (QUI).
"""
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import geopandas as gpd

if len(sys.argv) < 2:
    print(__doc__); sys.exit(0)

name = sys.argv[1]
g = gpd.read_file("hgis/gaz/gazetteer-2019-03-28.shp")
s = g["nombre"].astype(str)
h = g["nombrehoy"].astype(str)
v = g["variantes"].astype(str)
m = g[s.str.contains(name, case=False, na=False) |
      h.str.contains(name, case=False, na=False) |
      v.str.contains(name, case=False, na=False)].copy()

if len(sys.argv) >= 4:
    hlon, hlat = float(sys.argv[2]), float(sys.argv[3])
    m["_d"] = ((m["lon"] - hlon) ** 2 + (m["lat"] - hlat) ** 2) ** 0.5
    m = m.sort_values("_d")

if len(m) == 0:
    print(f'no match for "{name}" in the NGR/QUI gazetteer')
else:
    for _, r in m.head(10).iterrows():
        print("%-34.34s hoy=%-14.14s %-12.12s %-8.8s (%.3f, %.3f)" % (
            r["nombre"], str(r["nombrehoy"]), str(r["provincia_"]),
            str(r["categoria"]), r["lon"], r["lat"]))
