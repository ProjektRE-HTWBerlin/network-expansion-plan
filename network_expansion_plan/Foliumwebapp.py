# Importiert notwendige Bibliotheken für Datenverarbeitung, Geokodierung, Mapping und Visualisierung
import os
import re
import certifi
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
from shapely.geometry import Point
import html
import matplotlib.pyplot as plt
import time
import json

# Stellt sicher, dass das SSL-Zertifikat korrekt gesetzt ist
os.environ['SSL_CERT_FILE'] = certifi.where()


# Prüft, ob ein Wert ungültig ist (leer, "k.A.", etc.)
def is_invalid(value):
    if pd.isna(value):
        return True
    value = str(value).strip().lower()
    return value in ['', 'nan', 'k.a.', 'k.a', 'ka', 'none']


# Konvertiert Werte zu Float und behandelt ungültige Einträge
def to_number(val):
    try:
        if is_invalid(val):
            return 0.0
        return float(str(val).replace(',', '.'))
    except Exception:
        return 0.0


# Erstellt eine Adresse für die Geokodierung (Ort oder Bundesland)
def geocode_address(row, geocode):
    if not is_invalid(row.get('Ort / Trasse', None)):
        return geocode(f"{row['Ort / Trasse']}, Deutschland")
    else:
        return geocode(f"{row['Bundesland']}, Deutschland")


# Lädt Excel-Datei und ergänzt Latitude/Longitude durch Geokodierung
def load_and_geocode(input_excel, geocode):
    df = pd.read_excel(input_excel)
    num_cols = ['Leitungslänge in km', 'Übertragungskapazität in MVA', 'Kosten in Mio.€']
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].map(to_number)
    if not {'latitude', 'longitude'}.issubset(df.columns):
        df['location'] = df.apply(lambda row: geocode_address(row, geocode), axis=1)
        df['latitude'] = df['location'].apply(lambda loc: loc.latitude if loc else np.nan)
        df['longitude'] = df['location'].apply(lambda loc: loc.longitude if loc else np.nan)
    else:
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    return df

# Fügt einen Toggle-Button hinzu, um alle VNBs anzuzeigen oder auszublenden
def add_toggle_all_button(map_object):
    toggle_script = """
    <script>
    function toggleLayers(action) {
        var checkboxes = document.querySelectorAll('.leaflet-control-layers-overlays .leaflet-control-layers-selector');
        checkboxes.forEach(function(checkbox) {
            if (checkbox.checked !== action) {
                checkbox.click();
            }
        });
    }
    </script>
    <div style="position: fixed; bottom: 70px; left: 50px; z-index: 1000;">
        <button onclick="toggleLayers(true)">Alle VNB einblenden</button>
        <button onclick="toggleLayers(false)">Alle VNB ausblenden</button>
    </div>
    """
    map_object.get_root().html.add_child(folium.Element(toggle_script))

# Erzeugt einen sicheren Dateinamen aus einem gegebenen VNB-Namen
def safe_filename(name):
    # Erlaubt nur Buchstaben, Zahlen, Unterstrich, Punkt und Bindestrich
    return re.sub(r'[^A-Za-z0-9_.-]', '_', name)

# Hauptfunktion, die die Geokodierung und Kartenerstellung durchführt
def geocode_and_map(
        input_excel: str,
        input_excel2: str = None,
        output_excel: str = "output_geokodiert.xlsx",
        output_failure: str = "output_failure.xlsx",
        output_map: str = "interaktive_karte_kosten.html",
        bundesland_geojson: str = "2_deutschland.geo.json"
):
    geolocator = Nominatim(user_agent="geo_map_app", timeout=60)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3)

# Lädt die Excel-Datei und führt die Geokodierung durch
    df1 = load_and_geocode(input_excel, geocode)
    if input_excel2:
        df2 = load_and_geocode(input_excel2, geocode)
        df = pd.concat([df1, df2], ignore_index=True)
    else:
        df = df1

# GeoDataFrame erstellen und Geometrie hinzufügen
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[
            Point(lon, lat) if not np.isnan(lat) and not np.isnan(lon) else None
            for lon, lat in zip(df['longitude'], df['latitude'])
        ],
        crs="EPSG:4326"
    )

# Bundesland Polygon-Daten laden und mit den Geodaten verbinden
    bundeslaender_gdf = gpd.read_file(bundesland_geojson, encoding='utf-8')[['name', 'geometry']]

    gdf = gpd.sjoin(gdf, bundeslaender_gdf, how='left', predicate='within')
    gdf['passt'] = gdf['name'] == gdf['Bundesland']
    df_valid = gdf[gdf['passt']].drop(columns=['geometry', 'index_right', 'name'], errors='ignore')
    df_invalid = gdf[~gdf['passt']].drop(columns=['geometry', 'index_right', 'name'], errors='ignore')

# Ergebnisse in Excel-Dateien speichern
    df_valid.to_excel(output_excel, index=False)
    df_invalid.to_excel(output_failure, index=False)

# Aggregation der Daten nach Bundesland
    if df_valid.empty or 'Bundesland' not in df_valid.columns:
        df_bundesland = pd.DataFrame(
            columns=['Bundesland', 'Leitungslänge in km', 'Übertragungskapazität in MVA', 'Kosten in Mio.€'])
    else:
        df_bundesland = (
            df_valid
            .groupby('Bundesland')[['Leitungslänge in km', 'Übertragungskapazität in MVA', 'Kosten in Mio.€']]
            .sum()
            .reset_index()
        )

# Karte erstellen und die Bundesländer als Choropleth-Layer hinzufügen
    def create_map(choropleth_col, fill_color, output_map):
        karte = folium.Map(location=[51.0, 10.0], zoom_start=6, tiles="OpenStreetMap")
        # Choropleth-Layer NICHT im LayerControl anzeigen (control=False)
        folium.Choropleth(
            geo_data=bundeslaender_gdf,
            name=f"{choropleth_col} Choropleth",
            data=df_bundesland,
            columns=["Bundesland", choropleth_col],
            key_on="feature.properties.name",
            fill_color=fill_color,
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=choropleth_col,
            control=False
        ).add_to(karte)

        # Bundesland-Statistiken für Popups vorbereiten
        bundesland_stats = df_bundesland.set_index('Bundesland').to_dict(orient='index')
        def style_function(feature):
            return {'fillOpacity': 0, 'weight': 0}

        def popup_function(feature):
            name = feature['properties']['name']
            stats = bundesland_stats.get(name)
            if stats:
                return folium.Popup(
                    f"<b>{name}</b><br>"
                    f"Kosten: {stats['Kosten in Mio.€']:.2f} Mio.€<br>"
                    f"Übertragungskapazität: {stats['Übertragungskapazität in MVA']:.2f} MVA<br>"
                    f"Leitungslänge: {stats['Leitungslänge in km']:.2f} km",
                    max_width=300
                )
            else:
                return folium.Popup(f"<b>{name}</b><br>Keine Daten", max_width=200)

        with open(bundesland_geojson, encoding='utf-8') as f:
            geojson_data = json.load(f)
        for feature in geojson_data['features']:
            popup = popup_function(feature)
            folium.GeoJson(
                feature,
                style_function=style_function,
                highlight_function=lambda x: {'weight': 2, 'color': 'blue'},
                tooltip=feature['properties']['name'],
                popup=popup,
                control=False
            ).add_to(karte)

        # VNBs als CircleMarker hinzufügen
        vnb_names = df_valid['VNB-Name'].unique()
        cmap = plt.get_cmap('tab20')
        vnb_color_map = {
            name: f'#{int(255 * r):02x}{int(255 * g):02x}{int(255 * b):02x}'
            for name, (r, g, b, _) in zip(vnb_names, cmap(np.linspace(0, 1, len(vnb_names))))
        }
        popup_order = [
            'Bundesland', 'Ort / Trasse', 'Netzebene', 'Art der Maßnahme', 'Netzkomponente',
            'Projektstatus', 'Zeithorizont', 'Leitungslänge in km',
            'Übertragungskapazität in MVA', 'Kosten in Mio.€', 'VNB-Name', 'latitude', 'longitude'
        ]

        # CSV-Ordner anlegen
        csv_dir = "vnb_csv"
        os.makedirs(csv_dir, exist_ok=True)
        download_links = []
        for vnb in vnb_names:
            vnb_fg = folium.FeatureGroup(name=f"VNB: {vnb}", show=False)
            marker_cluster = MarkerCluster(
                maxClusterRadius=120,
                disableClusteringAtZoom=12,
                spiderfyOnMaxZoom=True,
                showCoverageOnHover=True,
                zoomToBoundsOnClick=True
            ).add_to(vnb_fg)
            vnb_rows = df_valid[df_valid['VNB-Name'] == vnb]
            color = vnb_color_map.get(vnb, '#3186cc')
            for _, row in vnb_rows.iterrows():
                if not is_invalid(row.get('Ort / Trasse', None)):
                    popup = "<br>".join(
                        f"<b>{html.escape(col)}:</b> {html.escape(str(row[col]))}"
                        for col in popup_order if col in row and not is_invalid(row[col])
                    )
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=7,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.8,
                        popup=folium.Popup(popup, max_width=400),
                        tooltip=row.get('Ort / Trasse', row['Bundesland'])
                    ).add_to(marker_cluster)
            vnb_fg.add_to(karte)
            # Sicheren Dateinamen erzeugen und Verzeichnis sicherstellen
            csv_filename = f"{safe_filename(vnb)}.csv"
            csv_path = os.path.join(csv_dir, csv_filename)
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            vnb_rows.to_csv(csv_path, index=False)
            # Link für Overlay
            download_links.append(f'<option value="{csv_dir}/{csv_filename}">{vnb}</option>')

        # Gesamt-CSV erzeugen
        gesamt_csv = os.path.join(csv_dir, "Alle_VNBs.csv")
        df_valid.to_csv(gesamt_csv, index=False)
        download_links.insert(0, f'<option value="{csv_dir}/Alle_VNBs.csv">Alle VNBs (Gesamt)</option>')

        # HTML-Overlay für Download-Links mit Button und Abstand zu den anderen Buttons
        download_html = f"""
        <div style="position: fixed; bottom: 17px; left: 50px; z-index: 1000; background: white; padding: 8px; border-radius: 6px;">
            <label for="vnb_csv_select"><b>VNB-CSV herunterladen:</b></label>
            <select id="vnb_csv_select">
                <option value="">Bitte wählen ...</option>
                {''.join(download_links)}
            </select>
            <button id="vnb_csv_download_btn" style="margin-left:8px;">Download</button>
        </div>
        <script>
        document.getElementById('vnb_csv_download_btn').onclick = function() {{
            var sel = document.getElementById('vnb_csv_select');
            if(sel.value) {{
                var link = document.createElement('a');
                link.href = sel.value;
                link.download = sel.options[sel.selectedIndex].text + ".csv";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }}
        }};
        </script>
        """
        karte.get_root().html.add_child(folium.Element(download_html))

        folium.LayerControl(collapsed=True).add_to(karte)
        add_toggle_all_button(karte)
        karte.save(output_map)
# Karten für verschiedene Kennzahlen erstellen
    create_map("Kosten in Mio.€", "YlOrRd", "interaktive_karte_kosten.html")
    create_map("Übertragungskapazität in MVA", "Blues", "interaktive_karte_uebertragung.html")
    create_map("Leitungslänge in km", "Greens", "interaktive_karte_leitung.html")
# Abschlussausgaben
    print(f"✔️ Geokodierte Datei: {output_excel}")
    print(f"✔️ Fehlerdatei: {output_failure}")
    print(f"✔️ Interaktive Karte (Kosten): interaktive_karte_kosten.html")
    print(f"✔️ Interaktive Karte (Übertragung): interaktive_karte_uebertragung.html")
    print(f"✔️ Interaktive Karte (Leitung): interaktive_karte_leitung.html")

# Zeitmessung, Ausführung der Hauptfunktion und Eingabe Dateipfad
if __name__ == "__main__":
    start = time.time()
    geocode_and_map("Bsp.: /Users/user/PycharmProjects/PythonProject/geokodiert_gesamt.xlsx")
    end = time.time()
    mins, secs = divmod(int(end - start), 60)
    print(f"⏱️ Laufzeit: {mins:02d}:{secs:02d} Minuten:Sekunden")
