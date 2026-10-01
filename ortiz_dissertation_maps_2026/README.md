# Replication package: maps of Don Luis de Acuña's credit exchanges, New Granada, 1703–1717

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23073508.svg)]
(https://doi.org/10.5281/zenodo.23073508)

This repository rebuilds five maps from Amanda Carolina Ortiz Molina's dissertation,
*A World of Credit: A Social and Economic History of New Granada's Colonial Life in
the Eighteenth Century* (working title): an introduction locator and four maps of the
notarized credit exchanges of the mine owner and official Don Luis de Acuña y
Berrío (Chapters 1 and 2). Every map is produced by a Python script from the data
in this repository and openly licensed base data.

| Map | Script | Output |
| --- | --- | --- |
| Introduction: places of the dissertation in the Viceroyalty of New Granada, c. 1726 | `map_intro_viceroyalty.py` | `outputs/map_intro_viceroyalty.png` / `.pdf` |
| Map 1.1 Credit exchanges arranged by Don Luis de Acuña from Chocó, 1703–1709 | `acuna_transactions/map_transactions_1703_1709.py` | `acuna_transactions/outputs/map_transactions_1703_1709.png` / `.pdf` |
| Map 1.2 Don Luis de Acuña's financial and debt transactions in the city of Santafé, 1710 | `acuna_transactions/map_transactions_1710.py` | `.../map_transactions_1710.png` / `.pdf` |
| Map 2.1 Purchases of enslaved people by Don Luis de Acuña, 1711–1713 | `acuna_transactions/map_transactions_1711_1713.py` | `.../map_transactions_1711_1713.png` / `.pdf` |
| Map 2.2 Financial transactions, powers of attorney, and sales made by Don Luis de Acuña while in Chocó, 1715–1717 | `acuna_transactions/map_transactions_1715_1717.py` | `.../map_transactions_1715_1717.png` / `.pdf` |

The outputs committed here are the versions used in the dissertation, so a rebuild
can be compared against them.

## How to read the transaction maps

Each line joins the place where Acuña was when the act was arranged or written to
the city where it was notarized or used. Colour gives the type of act, line width
its value in pesos (square-root scale, same in all maps), and the label on the line
its year or date. The lines are not movements of money or people. On Map 1.2 the
black line is the usual route from Nóvita to Santafé (his own route is not
documented) and the dashed line the likely forced journey of the three people he
bought there. Insets zoom in on the Nóvita mining district (Maps 1.1 and 2.1), the
acts in Santafé (Map 1.2) and Citará (Map 2.2).

## Rebuilding the maps

Tested with Python 3.9 on macOS. From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python fetch_dem.py                              # relief, all maps (downloads ~140 tiles, a few minutes)
.venv/bin/python acuna_transactions/fetch_corridor_dem.py  # 90 m relief for the Nóvita insets
.venv/bin/python map_intro_viceroyalty.py
.venv/bin/python acuna_transactions/map_transactions_1703_1709.py
.venv/bin/python acuna_transactions/map_transactions_1710.py
.venv/bin/python acuna_transactions/map_transactions_1711_1713.py
.venv/bin/python acuna_transactions/map_transactions_1715_1717.py
```

The two fetch scripts download the Copernicus GLO-90 elevation tiles anonymously
from the public AWS Open Data bucket and write `dem.tif` and
`acuna_transactions/data/dem_corridor_90m.tif` (not committed; they are rebuilt).
Each map script writes its PNG (300 dpi) and PDF. Map 1.2's two journey labels use
Arial; on systems without it matplotlib substitutes a default font.

## Repository contents

| Path | What it is |
| --- | --- |
| `acuna_transactions/data/events.csv` | Acts of 1703–1710 (Maps 1.1, 1.2): date, type, value in pesos, Acuña's place, place of the act, corrections in `note`. |
| `acuna_transactions/data/events_ch2.csv` | Acts of 1711–1717 (Maps 2.1, 2.2), same structure plus line labels. |
| `acuna_transactions/data/actors_1710.csv` | Notaries and other parties of the 1710 acts (Map 1.2). |
| `acuna_transactions/data/places.csv` | Places used, with display names, coordinates and the source of each coordinate. |
| `acuna_transactions/data/mining_areas.csv` | Approximate areas of mines known from the sources but not individually located (Map 1.1 inset). |
| `acuna_transactions/data/roads.geojson` | River and land routes reconstructed by the author, with the sources of each route. |
| `acuna_transactions/basemap.py` | Shared base map: relief, rivers, audiencia boundaries, labels, layout. |
| `hgis/` | HGIS de las Indias territories and gazetteer (2019 release), clipped to New Granada; full 1718–1749 viceroyalty outline. |
| `ne/` | Natural Earth coastline, ocean, rivers (1:10m) and land (1:50m). |
| `osm/pacific_rivers.shp` | Pacific-side rivers from OpenStreetMap; the Naurita derived from the elevation model (see `DATA_NOTES.md`). |
| `resolve_place.py` | Helper to look up a place in the HGIS gazetteer. |
| `CORRECTIONS.md` | Every change made to the author's research database extract, and why. |
| `DATA_NOTES.md` | How derived features were made (routes, Naurita, Quebrada Larga, mining areas) and their accuracy. |

## Where the transaction data come from

The acts were recorded by the author from notarial and judicial records in the
Archivo General de la Nación (Bogotá), the Archivo Histórico de Cartago, the Archivo
Central del Cauca (Popayán) and the Archivo Histórico de Cali, into a relational
research database. The CSV files here are a curated extract of that database:
only the acts drawn on the maps, with errors corrected after checking against the
archival documents and the dissertation text. The database itself is not part of
this package. Each correction is listed in `CORRECTIONS.md`; archival references
for each map are in the map captions in the dissertation.

## Data sources and licences

| Source | Used for | Licence and credit |
| --- | --- | --- |
| Werner Stangl, ed., *HGIS de las Indias*, release of 28 March 2019, Harvard Dataverse, https://doi.org/10.7910/DVN/YPEU5E | Places, audiencia and viceroyalty boundaries | CC BY 4.0. Files here are clipped and simplified extracts. |
| European Space Agency, *Copernicus Global Digital Elevation Model (GLO-90)*, https://doi.org/10.5069/G9028PQB | Relief (downloaded by the fetch scripts); Naurita channel | © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018 provided under COPERNICUS by the European Union and ESA; all rights reserved. |
| Natural Earth, https://www.naturalearthdata.com/ | Coastline, ocean, main rivers, South America outline | Public domain. |
| OpenStreetMap contributors, https://www.openstreetmap.org, extracted via the Overpass API, September 2026 | Pacific-side rivers (`osm/pacific_rivers.shp`) | © OpenStreetMap contributors, ODbL 1.0. This file is released under the ODbL. |
| Author's reconstruction | Routes (`roads.geojson`), transaction tables | CC BY 4.0 (see `LICENSE-DATA.md`). |

## Licences

Code: MIT (`LICENSE`). Data created by the author: CC BY 4.0. Third-party data keep
their own licences, listed above and in `LICENSE-DATA.md`.

## How to cite

Ortiz Molina, Amanda Carolina. 2026. *Replication package: maps of Don Luis de Acuña's credit exchanges, New Granada, 1703–1717*. Zenodo. https://doi.org/10.5281/zenodo.23073508. Code: https://github.com/aortizm1/ortiz_dissertation_maps_2026.

See also `CITATION.cff`.

## Note on AI assistance

The maps were designed by the author and produced in Python (matplotlib, geopandas,
rasterio). The code was written with the assistance of Claude Opus 5.5 (Anthropic),
an AI model, under the author's direction; all data, sources, cartographic decisions
and interpretations are the author's own.
