# Notes on derived data

How the features that are not taken directly from a published dataset were made,
and how accurate they are.

## Routes (`acuna_transactions/data/roads.geojson`)

Thirteen river and land routes drawn by the author in ArcGIS Online from Orian
Jiménez's map of Chocó's mining districts, Enrique White's *Carta geográfica de la
Intendencia del Chocó*, Antonio Cuervo's *Colección de documentos inéditos sobre la
geografía y la historia de Colombia*, AGN, Sección Mapas y Planos 4, ref. 539a
(1774), and the works on the Quindío and central New Granada roads named in each
feature's `source` field. They are approximate reconstructions, adequate at the
scale of the maps. The Santafé–Cartago–Quibdó segments agree closely with the
independent reconstruction of the official mail route (from 1776) in HGIS de las
Indias, *correos terrestres*.

## Naurita river (feature `Naurita` in `osm/pacific_rivers.shp`)

OpenStreetMap does not map the Naurita; it records only the locality Boca de
Naurita (5.873°N, 76.581°W), where it meets the Neguá. The line is the stream
channel derived from the Copernicus GLO-90 elevation model (flow directions and
flow accumulation computed with pysheds; channels with more than 300 upstream 90 m
cells), following the branch that leaves the Neguá at Boca de Naurita, then
smoothed. Only the lower course (about 8 km) is drawn. Position: about ±300 m. The
OpenStreetMap line named "Río Neguá" continued up this branch; it was cut at the
confluence and only the lower Neguá is kept under that name.

## Quebrada Larga mine (`places.csv`, `quebrada_larga`)

Located with a community map of the Tamaná river and its tributaries drawn by Laida
Patricia Asprilla from local knowledge, on which many colonial names survive. The
map gives walking times up the river from Nóvita. Two places on it also have
coordinates in the author's mines table: Agua Clara (37 min; 4.919297°N,
76.558524°W) and Sed de Cristo (65 min; 4.962673°N, 76.508163°W). The Quebrada
Larga (59 min) is placed on the OpenStreetMap Tamaná at the same proportion of the
river distance between them, (59 − 37) / (65 − 37) = 0.79, giving 4.9506°N,
76.5177°W. Approximate: walking time is not strictly proportional to distance. The
community map itself is not included.

## Mining areas (`mining_areas.csv`)

Circles of 2.5–3 km around Nóvita, Los Brazos and Las Juntas mark mines that the
sources place in or around these settlements without giving their sites. They
indicate presence, not extent.

## His fields on the Neguá (`places.csv`, `negua_fields`)

Placed on the lower Neguá near the confluence with the Naurita, following the
dissertation's description of his corn and plantain fields on the Neguá. Approximate.

## Base data processing

- HGIS de las Indias territories and gazetteer: clipped to 84°W–70°W, 6°S–13°N,
  reduced to the civil administrative levels used, geometry simplified to about
  500 m. The viceroyalty outline (`hgis/virreinato_nueva_granada_1718-1749.gpkg`)
  is the unclipped 1718–1749 Nueva Granada polygon, simplified to about 1 km.
- OpenStreetMap rivers: ways merged per river, unconnected fragments dropped
  (including the separate Río San Juan of Antioquia), simplified to about 200 m. The
  Atrato in the Citará inset is the OpenStreetMap line; elsewhere Natural Earth is used.
- Relief: Copernicus GLO-90 tiles averaged to 0.003° (about 330 m) for the main maps;
  full 90 m for the Nóvita insets. Rivers and coast follow present-day courses; the
  maps assume the main rivers ran in roughly the same beds in the eighteenth century.
