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
Patricia Asprilla from local knowledge, on which many colonial names survive (Laida
Patricia Asprilla, "¿Cómo viven los habitantes del corregimiento de Urabá del
municipio de Nóvita?", monograph, Universidad Católica de Pereira, 2017, 15). The
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

## Taparral river (feature `Taparral` in `osm/pacific_rivers.shp`)

OpenStreetMap does not map the Río Taparral. The line is the main channel derived
from the Copernicus GLO-90 elevation model (D8 flow path computed with pysheds),
from its head about 4.4 km north of Sipí down to its confluence with the OpenStreetMap
Río Cajón (about 4.806°N, 76.679°W), smoothed (Chaikin, two passes); 20.5 km.
Position: about ±300 m.

## Map 3.1: mining camps (`ponton/data/places.csv`)

The camps are those of the partidos of Nóvita (14 camps) and Cajón (6) in the 1755
mining census. Fifteen of the twenty are located and drawn; Sesego, not in the
census, is drawn as a hollow triangle because Chapter 3 discusses it. The table
`census_1755_novita_cajon_table.csv` gives each camp's status. Opogodó and Tajuatú
are located (OpenStreetMap localities on the rivers of those names) but lie north of
the area the chapter discusses, so they are left off (`places_not_mapped.csv`, with
Yalí, known only from the undated *Compendiosa noticia* and a record of 1780 naming
Doña Thomasa de Ibargüen as its owner, AGN, Colonia, Cruzadas, SC.20, 4, D.17). The second La Concepción
del Salto (Francisco Gómez de la Asperilla), San Cayetano, and Nuestra Señora del
Socorro y Sitio del Milagro could not be located.

Positions come from the author's mines table (from the archival sources named in the
`source` column), from the order in which the *Compendiosa noticia* (456–458) walks
the parishes along the Tamaná and the Cajón, and from surviving stream names in
OpenStreetMap. Along the Tamaná they were checked against a community map of the
river by Laida Patricia Asprilla (see above), whose walking times up the river from Nóvita are
close to proportional to the OpenStreetMap river distance (about 0.3 km per minute)
and whose order of places matches it. Guarabal ("Pie del Salto de Guarabal") is placed
just below the rapid that map calls El Salto, about 21.6 km above Nóvita. All
positions are approximate, at best to within about 1 km. On the map, Sed de Cristo
and San Lorenzo, less than 1 km apart, are drawn about 0.9 km apart so their symbols
do not overlap; the data keep the recorded coordinates.

Symbol size: four classes of enslaved workers in 1755 (under 20, 20–59, 60–149, 150 or
more), with breaks in gaps in the counts of the mapped camps.

## Map 3.1: mazamorrero areas (`ponton/data/mazamorrero_areas_display.geojson`)

Where: the *Compendiosa noticia* (456–457) names free mazamorreros on the Río
Taparral ("que más abajo se incorpora al Cajón"), on the Río Negro, and "en el
intermedio" of the Quebrada del Tigresito. How large: the 1788 tax records count 52
mazamorreros in the Taparral (partido of Cajón; f. 297r–v) and 50 in the jurisdiction
of Nóvita, Río Negro and the Tigresito together (f. 309r–v). The Nóvita figure is not
divided by site; the author's working split is 25 on the Río Negro and 15 on the
Tigresito. The Río Negro area is the author's sketch (2.58 km², outline smoothed);
the Tigresito area covers the middle course of the OpenStreetMap Quebrada Tigresito,
220 m either side (1.12 km²). Their pooled density, 0.092 km² per person, sizes the
Taparral area: 52 × 0.092 = 4.81 km², a corridor 300 m either side of the river over
7.7 km, centred on Diego Ibo de Thovar's camp. The areas show where and roughly how
many people worked, not surveyed extents. The author's original sketches are in
`sketch_layers.geojson` (the Cajón–Popayán layers there are not used).

## Map 3.1: route to Sipí (`ponton/data/roads_ponton.geojson`)

The routes of `roads.geojson`, except that the Cajón–Sipí leg runs down the Cajón to
the mouth of the Taparral, up the Taparral to its head, and overland to Sipí, after
the *Compendiosa noticia*: "por él es camino a Sipí, así de agua como de tierra".
The Acuña maps keep the original line.

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
