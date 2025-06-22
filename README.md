# Network Expansion Plan  
**Development of a map of network expansion plans**

---

## Verwendung  
### Usage  
**Vor Programmstart**  
**Before program start**  
Legen Sie die GeoJSON- und Excel-Datei (z.&nbsp;B. `geokodiert_zugestimmt.xlsx`) lokal im Projektverzeichnis ab.  
*Place the GeoJSON and Excel file (e.g. `geokodiert_zugestimmt.xlsx`) locally in the project directory.*

### Foliumwebapp.py  
Startet die Geokodierung der Tabelle im vorgegebenen Format und erzeugt die Dateien `output_fail` und `output_geokodiert`.  
Aus `output_geokodiert` werden interaktive Karten mit Layern und einer Download-Option erstellt.  
*Starts geocoding of the table in the specified format and creates the files `output_fail` and `output_geokodiert`.  
Interactive maps with layers and a download option are generated from `output_geokodiert`.*

**Ausführung / Execution**

```bash
python network_expansion_plan/Foliumwebapp.py
```

Die Karten werden als HTML-Dateien im Projektverzeichnis gespeichert.  
Zusätzlich werden nach VNB sortierte CSV-Dateien erzeugt.  
*The maps are saved as HTML files in the project directory.  
CSV files sorted by DSO (VNB) are also generated.*

### FWA_Plots.py  
Erstellt statistische Auswertungen und Plots aus den Netzausbaudaten bzw. aus `output_geokodiert`.  
*Creates statistical evaluations and plots from the network-expansion data or from `output_geokodiert`.*

**Ausführung / Execution**

```bash
python network_expansion_plan/FWA_Plots.py
```

---

## Projektstruktur  
### Project Structure  

```
network_expansion_plan/
├── Foliumwebapp.py        Interaktive Karten und Geokodierung
├── FWA_Plots.py           Statistische Auswertungen und Plots
docs/                      Projektdokumentation
vnb_csv/                   Exportierte CSV-Dateien pro VNB
2_deutschland.geo.json     GeoJSON mit Bundesländern
geokodiert_VNB.xlsx        Beispiel-Eingabedatei
```

*Legend*  
`Foliumwebapp.py` – Interactive maps & geocoding  
`FWA_Plots.py` – Statistical evaluations & plots  
`docs/` – Project documentation  
`vnb_csv/` – Exported CSV files per DSO  
`2_deutschland.geo.json` – GeoJSON of German federal states  
`geokodiert_zugestimmt.xlsx` – Sample input file  

---

## Beispiele  
### Examples  

Nach dem Ausführen von `Foliumwebapp.py` findest du / After running `Foliumwebapp.py` you will find

* `interaktive_karte_kosten.html` — *interactive_map_costs.html*  
* `interaktive_karte_uebertragung.html` — *interactive_map_transmission.html*  
* `interaktive_karte_leitung.html` — *interactive_map_line_length.html*

Im Ordner `vnb_csv/` werden CSV-Dateien für jeden VNB erzeugt.  
*CSV files for each DSO are generated in the `vnb_csv/` folder.*

---

## API-Dokumentation  
### API Documentation  

### Foliumwebapp.py  
#### `geocode_and_map(...)`  
Hauptfunktion für Geokodierung, Datenprüfung und Kartenerstellung.  
Unterstützt Layer für Kosten, Übertragungskapazität und Leitungslänge.  
*Main function for geocoding, data validation and map creation.  
Supports layers for costs, transmission capacity and line length.*

### FWA_Plots.py  
Erzeugung von Balkendiagrammen, Tree Map und Tabellen  
*Generates bar charts, a treemap and tables*

- Summe angegebener Kosten in Mio. € je VNB – *Total stated costs (million €) per DSO*  
- Summe angegebene Übertragungskapazität in MVA je VNB – *Total stated transmission capacity (MVA) per DSO*  
- Summe angegebene Leitungslänge in km je VNB – *Total stated line length (km) per DSO*  
- Summe angegebener Kosten in Mio. € nach Fertigstellungsjahr – *Total stated costs (million €) by completion year*  
- Summe angegebener Übertragungskapazität in MVA nach Fertigstellungsjahr – *Total stated transmission capacity (MVA) by completion year*  
- Summe angegebener Leitungslänge in km nach Fertigstellungsjahr – *Total stated line length (km) by completion year*  
- Kostenverteilung der angegebenen Kosten in Mio. € je VNB – *Cost distribution (million €) per DSO*  
- Sammelstatistik je VNB-Name – *Aggregate statistics per DSO name*  
- Gesamtsummen aller Kennzahlen – *Overall totals of all key figures*

---

## Fehlerbehebung  
### Troubleshooting  

* **Geokodierung schlägt fehl:** Prüfe Internetverbindung, Tabellenformat, Pfad zum Projektverzeichnis und installierte Abhängigkeiten.  
  * **Geocoding fails:** Check internet connection, table format, project-directory path and installed dependencies.*

* **Karten werden nicht angezeigt:** Stelle sicher, dass alle Abhängigkeiten installiert sind und die GeoJSON-Datei vorhanden ist.  
  * **Maps are not displayed:** Ensure all dependencies are installed and the GeoJSON file exists.*

---

## Beitrag leisten  
### Contributing  

Dieser Abschnitt lädt dazu ein, aktiv zur Weiterentwicklung des Projekts beizutragen.  
Sie können Änderungsvorschläge als Pull Requests einreichen oder Issues eröffnen,  
um Anregungen oder Fehlerberichte zu liefern und auch auf Fehler im Skript hinzuweisen.  
*This section invites you to actively contribute to the project’s further development.  
You can submit change proposals as pull requests or open issues to provide suggestions or bug reports and to point out script errors.*

---

## Lizenz / Nutzungsbedingungen  
### License / Terms of Use  

Nutzung des Codes und der Datei in GitHub erfolgt unter der MIT-Lizenz.  
*Use of the code and files on GitHub is under the MIT License.*

Lizenz-/Nutzungsvereinbarung der ohnehin öffentlich zugänglichen Daten nach Rücksprache mit bestimmten VNB.  
*Licensing/usage agreement for publicly available data is subject to consultation with specific DSOs.*

---

## Haftungsausschluss  
### Disclaimer  

Der Code sowie die bereitgestellten Karten, Daten und Statistiken werden ohne Gewähr hinsichtlich Richtigkeit, Vollständigkeit und Aktualität zur Verfügung gestellt.  
*The code and the provided maps, data and statistics are supplied without warranty as to accuracy, completeness or timeliness.*
