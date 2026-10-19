# Corrections to the research database extract

The transaction tables in `acuna_transactions/data/` were taken from an extract of
the author's relational research database (`events_events_places_join`, May 2024)
and then checked against the archival documents and the dissertation text. The
database itself is not included. This file lists every value that differs from the
extract, and every act left out, so the curated tables can be traced back to it.

`event_id` is the database's event identifier, kept unchanged in the CSV files.

## Values and dates

| event_id | Act | Field | Database | Corrected | Basis |
| --- | --- | --- | --- | --- | --- |
| 15 | Purchase of 17 enslaved people on credit, Cartago, 30 Mar 1709 | value | 9,265 pesos | 10,355 pesos | Author, from the notarial record |
| 32 | Surety for Miguel Gómez de la Asperilla, Cartago | date | "1707-0-20" (invalid) | 19 Feb 1709 | Author, from the notarial record |
| 32 | same | value | none | 3,000 pesos | Author |
| 26 | Surety for Tomás Romero, Santafé, 31 Mar 1710 | value | 12,000 pesos | 6,000 pesos | Court-ordered guarantee covering both guarantors (author) |
| 1 | Loan from the capital of a chaplaincy, 5 Dec 1715 | value | 944 pesos | 994 pesos | Author, from the record |
| 6 | Obligación to Joseph de Los Santos, Los Brazos, 23 Dec 1715 | value | none | 9,900 pesos | The outstanding debt recognized in the act (author) |
| 30 | Sale of four enslaved men, 15 Apr 1717 | value | none | 2,080 pesos | 520 pesos each, from the record |

## Where Acuña was (start of each line)

| event_id | Act | Database | Used on the map | Basis |
| --- | --- | --- | --- | --- |
| 17, 20, 21 | Purchases in Cartago, Jul 1711 and Dec 1712 | Quibdó ("potential" location) | Nóvita | All 1711–1713 purchases were arranged from the Nóvita region (author) |
| 19 | Purchase in Cartago, Sep 1712 | Cartago | Nóvita | same |
| 28 | Purchase in Popayán, Jan 1712 | Quibdó ("potential") | Nóvita | same |
| 18 | Purchase in Cartago, 28 Apr 1713 | Quibdó | Nóvita | He became Lieutenant of Citará only by mid-1714 (author; Chapter 2) |
| 5 | Purchase of 18 enslaved people on credit, May 1712 | Naurita mine | El Salto mine, Nóvita | The vale was written at El Salto (author; AGN, Miscelánea, SC.39, 28, 15, f. 206r) |
| 30 | Sale of four enslaved men, Apr 1717 | Quibdó; place of the act Quibdó | written at Tadó; notarized in Cali | Author; Archivo Histórico de Cali, Notaría 2 |
| 1, 11 | Loans arranged in Santafé, Sep and Dec 1715 | Quibdó ("potential") | Quibdó | Confirmed by the author |

## Acts not drawn

| event_id | Act | Reason |
| --- | --- | --- |
| 7, 9 | Family relations (brother, cousin) | Not transactions |
| 10 | Loan with no date or value | The same request for a loan as event 8 (letter to his cousin, Aug 1715); drawn once |
| 29 | Foundation of a patrimony, Tadó / Cali, 1716 | Not discussed in the dissertation text |

## Places

| Place | Change | Basis |
| --- | --- | --- |
| Acuña's mine, Nuestra Señora de Chiquinquirá del Salto | 4.947964°N, 76.579153°W | acc.civil.minas.8170 (author's mines table) |
| Anserma | 5.231°N, 75.786°W (author's choice) | HGIS dates the Anserma site near Cartago from 1722; the earlier site is used for 1703–1717 |
| Quebrada Larga mine | approximate position | See `DATA_NOTES.md` |
| Tamaná mining camp (Map 2.2 main map only) | symbol displaced about 6 km north-east | Cartographic displacement to keep it apart from Los Brazos, 2 km away; data keep the true position |

Names of the enslaved people bought in 1710 (Maria, Joseph de Tapia, Thomas), of the
other parties, and of the notaries in `actors_1710.csv` come from the notarial
records (AGN, Notaría Segunda, vols. 98–106) as cited in the dissertation.
