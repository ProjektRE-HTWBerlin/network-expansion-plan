#  Projektbeschreibung / Project description: 
## **DE:** Digitalisierung und Visualisierung der in den Netzausbauplänen, der Verteilnetzbetreiber, enthaltenen Daten

## **EN:** Digitalization and Visualization of the Data Contained in the Grid Expansion Plans of Distribution System Operators

## Zielsetzung / Objective

**DE:**  
Ziel dieses Projekts ist die statistische und anschauliche Darstellung der veröffentlichten Netzausbaupläne 
der veröffentlichungspflichtigen Verteilnetzbetreiber (VNB) in Deutschland. 
Dabei wird ein gebietsübergreifender Vergleich angestrebt. 
Zudem soll eine tabellarische Vorlage zur Veröffentlichung solcher Daten erstellt werden, um Transparenz zu fördern. 
Langfristig soll das Projekt einen Beitrag zur Digitalisierung im Netzbereich für öffentliche Zwecke leisten.

**EN:**  
The aim of this project is to provide a statistical and visual representation of the published grid expansion plans of 
distribution system operators (DSOs) in Germany who are legally obligated to publish such plans. 
The goal is to enable a cross-regional comparison. Additionally, a tabular template is proposed to encourage structured 
publication of such data and to support digitalization efforts in the energy grid sector for public interest.

---

## Kontaktaufnahme & Datenbeschaffung / Contact & Data Acquisition

**DE:**  
Vor Beginn der Auswertung wurden alle 86 für das Projekt relevanten Verteilnetzbetreiber per E-Mail kontaktiert. 
Ziel war es, die Zustimmung zur Nutzung der ohnehin öffentlich zugänglichen Daten einzuholen. 
Alle verwendeten Daten stammen von der Webseite [https://www.vnbdigital.de/service/region](https://www.vnbdigital.de/service/region), 
aus dem Bereich „Regionalszenarien → Regionen → Veröffentlichungspflichtige Verteilnetzbetreiber → PDF Netzausbaupläne“.  
Nach Rücksprache mit den Netzbetreibern wurde die Zustimmung für die in der Datei `geokodiert_zugestimmt.xlsx` 
enthaltenen VNB-Informationen erteilt.

**EN:**  
Prior to data evaluation, all 86 distribution system operators relevant to this project were contacted via email to 
obtain explicit permission to use their publicly available data. 
All utilized data was sourced from the official platform [https://www.vnbdigital.de/service/region](https://www.vnbdigital.de/service/region), 
from the section “Regional Scenarios → Regions → Obligated DSOs → PDF Expansion Plans”.  
Following confirmation, all DSOs listed in the file `geokodiert_zugestimmt.xlsx` granted permission for unrestricted data usage.

---

## Qualität der Ausgangsdaten (seitens VNB) / Data Quality (DSO Perspective)

**DE:**  
Die PDF-Dokumente der Netzausbaupläne zeigen eine hohe Heterogenität hinsichtlich Formatierung, Tabellenstruktur und Begriffsverwendung. 
Tabellenköpfe, Maßeinheiten und die Beschreibung der Maßnahmen unterscheiden sich deutlich voneinander. 
Dies erschwert eine automatische oder direkte Vergleichbarkeit der Datensätze.

**EN:**  
The PDF documents from DSOs exhibit considerable heterogeneity in formatting, table structure, and terminology. 
Table headers, units of measurement, and descriptions of activities vary significantly, 
making automated or direct comparison across DSOs difficult.

---

##️ Datenaufbereitung / Data Preparation

**DE:**  
Da die vorliegenden Netzausbaupläne ausschließlich im PDF-Format veröffentlicht wurden und somit nicht maschinenlesbar waren, 
wurde auf kombinierte Methoden der Text- bzw. Bilderkennung zurückgegriffen. 
Unter anderem kamen ChatGPT (GPT: „Netzausbauextraktor“) und selbstgeschriebene Python-Tools wie `pdf2excel` und `pdf2csv` zum Einsatz. 
Ziel war es, die Informationen zu extrahieren und in strukturierter, maschinenlesbarer Form weiterverarbeiten zu können.

**EN:**  
Since the expansion plans were only available as non-machine-readable PDF files, various methods of text recognition were applied. 
Tools included ChatGPT (GPT:"Grid Expansion Extractor") and Python scripts like `pdf2excel` and `pdf2csv`. 
The objective was to extract structured information that could be used for further automated processing.

---

## Qualität der aufbereiteten Daten / Data Quality (Processed Data)

**DE:**  
Aufgrund der großen Datenmenge und der Verwendung künstlicher Intelligenz kann eine vollständige Fehlerfreiheit nicht garantiert werden. 
Die eingesetzten Skripte liefen nicht durchgehend stabil. Hinzu kamen Informationsverluste infolge der Standardisierung sowie Probleme beim Geocoding, 
sofern kein konkreter Ort oder keine eindeutige Trasseninformation durch den VNB angegeben oder in der verwendeten `2_deutschland.geo.json`-Datei auffindbar war.

**EN:**  
Due to the volume of data and the use of artificial intelligence, errors in the processed dataset cannot be ruled out. 
The applied scripts did not operate without flaws. Additional issues arose during data standardization and geolocation matching, 
particularly where no specific location or path information was provided or could not be found in the `2_deutschland.geo.json` file.

---

## Vereinheitlichung der Daten / Data Harmonization

**DE:**  
Zur besseren Vergleichbarkeit wurden gemeinsame Parameter definiert, die in den meisten Tabellen der VNB vorkamen. 
Wo keine Daten verfügbar waren, wurden die Zellen mit `0` oder `k.A.` (keine Angabe) ausgefüllt. 
Besonders bei der Spalte *Ort / Trasse* wurde mit Bezug auf Aussagen der VNB (“kritischer Infrastruktur“) 
bewusst auf eine genauere Aufschlüsselung verzichtet.
Beim Zeithorizont wurde ausschließlich das Jahr der geplanten Fertigstellung berücksichtigt.

**EN:**  
To enable better comparison, a set of common parameters was defined based on fields recurring in most DSO tables. 
Missing values were represented as `0` or `n/a`. For the *Location / Line* column, 
precise tracing details were intentionally omitted due to infrastructure sensitivity concerns. 
The completion year was extracted as the temporal reference for each measure.

**Verwendete Parameter / Parameters used:**

- VNB-Name / DSO name  
- Teilnetzgebiet / Sub-network  
- Bundesland / Federal state  
- Ort / Trasse / Location / Line  
- Netzebene / Voltage level  
- Art der Maßnahme / Type of measure  
- Leitungslänge in km / Line length (km)  
- Übertragungskapazität in MVA / Transmission capacity (MVA)  
- Netzkomponenten / Network components  
- Projektstatus / Project status  
- Zeithorizont / Completion year  
- Kosten in Mio. € / Estimated cost (Mio. €)

---

## Beispielhafte Einträge / Example Entries

| VNB-Name        | Teilnetzgebiet | Bundesland         | Ort / Trasse       | Netzebene | Maßnahme                                             | Leitung (km) | Kapazität (MVA) | Komponenten                | Status               | Jahr | Kosten (Mio. €) |
|-----------------|----------------|---------------------|---------------------|------------|------------------------------------------------------|----------------|-------------------|-----------------------------|------------------------|------|------------------|
| AVU Netz GmbH   | West           | Nordrhein-Westfalen | US Henrichshütte   | HS/MS      | Neubau UW                                            | 0              | 40                | UW                          | im Bau               | 2026 | 0                |
| AVU Netz GmbH   | West           | Nordrhein-Westfalen | US Hattingen       | HS/MS      | Neubau UW, Trafo, Schaltanlage                      | 0              | 40                | UW, Trafo, Schaltanlage     | vorgesehene Maßnahme  | 2032 | 0                |
| AVU Netz GmbH   | West           | Nordrhein-Westfalen | Gevelsberg         | HS/MS      | Ertüchtigung Trafo                                   | 0              | 9                 | Trafo                       | vorgesehene Maßnahme  | 2027 | 0                |
| AVU Netz GmbH   | West           | Nordrhein-Westfalen | Schwelm            | HS/MS      | Ertüchtigung UW                                      | 0              | 0                 | UW                          | vorgesehene Maßnahme  | 2027 | 0                |

---

## Python-Skripte: Handhabung & Hinweise

### Folium Web App

**DE:**  
Die Folium Web App arbeitet ausschließlich mit einer Excel‑Eingabedatei, deren Spaltenstruktur unverändert bleiben muss, weil mangelnde Freiheitsgrade im Skript sonst zu Laufzeitfehlern führen können.
Diese Excel‑Datei muss gemeinsam mit dem Python‑Skript **im selben Verzeichnis** liegen, damit das Programm darauf zugreifen kann. 
Außerdem muss sich dort die Datei **`2_deutschland.geo.json`** befinden, da sie die Referenz für das Geokodieren der Ortsangaben bildet.

Nach dem Start liest das Skript die Spalte **„Ort/Trasse“** aus. Findet es für einen Eintrag einen passenden Ortsnamen in der Geo‑JSON, wird dieser geokodiert und erscheint sowohl:

* auf der **interaktiven Folium‑Karte** (die als HTML im Browser geöffnet wird) und  
* in der Datei **`output_geokodiert.xlsx`**.

Wird kein Treffer erzielt, schreibt das Skript den entsprechenden Datensatz in **`output_failure.xlsx`**; auf der Karte erscheint dieser Punkt selbstverständlich nicht.

Ist in der Spalte „Ort/Trasse“ der Platzhalter **„k.A.“ (keine Angabe)** eingetragen, ordnet das Programm die Zeile dem jeweiligen **Bundesland** zu. Dabei gehen alle Parameter verloren, die sich nicht sinnvoll summieren lassen (beispielsweise *Netzebene*, *Art der Maßnahme* oder *Projektstatus*). 
Für die Sammel‑ und Summenstatistik bleiben in diesem Fall lediglich **Leitungslänge**, **Übertragungskapazität** und **Kosten** erhalten. 
Gleichwohl fließen alle Datensätze mit präzisen Ortsangaben ebenfalls in diese Sammel- bzw. Summenstatistik ein. (WICHTIG für die Interpretation!).

Die fertige Karte bietet oben rechts eine Layer‑Auswahl der vertretenen VNB, mit dem sich die Daten einzelner VNB ein‑ oder ausblenden lassen. 
Zusätzlich können die angezeigten Datensätze nach VNB gruppiert und als CSV‑Datei heruntergeladen werden, falls noch keine sortierte CSV vorliegt.

**EN:** 
The Folium Web App works exclusively with an Excel input file whose column structure must remain unchanged, as limited flexibility within the script could otherwise lead to runtime errors.
This Excel file must be located in the same directory as the Python script so that the program can access it.
Additionally, the file 2_deutschland.geo.json must also be present in this directory, as it serves as the reference for geocoding the location entries.

After launching, the script reads the “Ort/Trasse” (Location/Line) column. If it finds a matching location in the GeoJSON file, that location is geocoded and will appear:

on the interactive Folium map (opened as an HTML file in the browser), and
in the file output_geokodiert.xlsx.
If no match is found, the script writes the corresponding data entry into output_failure.xlsx. This entry will naturally not appear on the map.

If the “Ort/Trasse” column contains the placeholder “k.A.” (i.e., no information), the program assigns the row to the corresponding federal state (“Bundesland”).
In doing so, all parameters that cannot be meaningfully aggregated (e.g., voltage level, type of measure, or project status) are discarded.
Only line length, transmission capacity, and costs remain in this case and are included in the summary statistics.
Nevertheless, all entries with precise location information are also included in these aggregated statistics.
(Important for proper interpretation!)

The completed map includes a layer selection menu in the top-right corner, allowing users to toggle the visibility of each represented DSO.
Additionally, the displayed datasets can be grouped by DSO and exported as a CSV file, in case no sorted CSV version exists yet.
---

### FWA Plots (Folium Web App Plots)

**DE:**  
Das Skript `FWA_Plots.py` generiert einfache Diagramme und statistische Auswertungen auf Basis derselben Eingabedatei.  
Zu beachten ist, dass lediglich rund 65% der veröffentlichungspflichtigen VNB in der Datei enthalten sind.  
Die übrigen Daten könnten jedoch theoretisch mittels KI oder anderer Programme ergänzt werden, 
um eine vollständigere Übersicht zu ermöglichen für nicht-öffentliche Zwecke.

**EN:**  
The `FWA_Plots.py` script generates basic visualizations and statistical summaries based on the same Excel input.  
Only about 65% of legally obligated DSOs are currently covered.  
The remaining data could theoretically be added using AI methods or other programs to improve the overall dataset for internal purposes.
