import os
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


os.environ['SSL_CERT_FILE'] = certifi.where()

def is_invalid(value):
    if pd.isna(value):
        return True
    value = str(value).strip().lower()
    return value in ['', 'nan', 'k.a.', 'k.a', 'ka', 'none']

def to_number(val):
    try:
        if is_invalid(val):
            return 0
        return float(str(val).replace(',', '.'))
    except Exception:
        return 0

def geocode_address(row, geocode):
    if not is_invalid(row.get('Ort / Trasse', None)):
        return geocode(row['Ort / Trasse'] + ", Deutschland")
    else:
        return geocode(row['Bundesland'] + ", Deutschland")

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

def geocode_and_map(
    input_excel: str,
    input_excel2: str = None,
    output_excel: str = "output_geokodiert.xlsx",
    output_failure: str = "output_failure.xlsx",
    output_map: str = "interaktive_karte.html",
    bundesland_geojson: str = "2_deutschland.geo.json"
):
    geolocator = Nominatim(user_agent="geo_map_app", timeout=60)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3)

    df1 = load_and_geocode(input_excel, geocode)

    if input_excel2:
        df2 = load_and_geocode(input_excel2, geocode)
        df = pd.concat([df1, df2], ignore_index=True)
    else:
        df = df1

    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) if not np.isnan(xy[0]) and not np.isnan(xy[1]) else None
                  for xy in zip(df['longitude'], df['latitude'])],
        crs="EPSG:4326"
    )

    bundeslaender_gdf = gpd.read_file(bundesland_geojson, encoding='utf-8')[['name', 'geometry']]
    gdf = gpd.sjoin(gdf, bundeslaender_gdf, how='left', predicate='within')
    gdf['passt'] = gdf['name'] == gdf['Bundesland']

    df_valid = gdf[gdf['passt'] == True].copy()
    df_invalid = gdf[gdf['passt'] == False].copy()

    df_valid.drop(columns=['geometry', 'index_right', 'name'], inplace=True, errors='ignore')
    df_invalid.drop(columns=['geometry', 'index_right', 'name'], inplace=True, errors='ignore')

    if 'Bundesland' not in df_valid.columns:
        print("❌ Fehler: Die Spalte 'Bundesland' fehlt in df_valid.")
        print("🔍 Verfügbare Spalten:", df_valid.columns.tolist())
        print("ℹ️ Wahrscheinlich wurde sie vorher nicht korrekt zugeordnet. Prüfe die Geokodierung und GeoJSON-Zuordnung.")
        return

    df_valid.to_excel(output_excel, index=False)
    df_invalid.to_excel(output_failure, index=False)

    vnb_names = df_valid['VNB-Name'].unique()
    cmap = plt.colormaps.get_cmap('tab20')
    vnb_color_map = {name: f'#{int(255*r):02x}{int(255*g):02x}{int(255*b):02x}'
                     for name, (r, g, b, _) in zip(vnb_names, cmap(np.linspace(0, 1, len(vnb_names))))}

    popup_order = [
        'Bundesland',
        'Ort / Trasse',
        'Netzebene',
        'Art der Maßnahme',
        'Netzkomponente',
        'Projektstatus',
        'Zeithorizont',
        'Leitungslänge in km',
        'Übertragungskapazität in MVA',
        'Kosten in Mio.€',
        'VNB-Name',
        'latitude',
        'longitude'
    ]

    karte = folium.Map(location=[51.0, 10.0], zoom_start=6, tiles="OpenStreetMap")

    # --- Bundesland-Polygone einfärben mit aggregierten Daten ---
    df_ohne_ort = df_valid[df_valid['Ort / Trasse'].apply(is_invalid)]

    if 'Bundesland' not in df_ohne_ort.columns or df_ohne_ort.empty:
        print("⚠️ Kein Eintrag ohne 'Ort / Trasse' mit gültigem 'Bundesland' zum Aggregieren vorhanden.")
        df_bundesland = pd.DataFrame(columns=['Bundesland', 'Leitungslänge in km', 'Übertragungskapazität in MVA', 'Kosten in Mio.€'])
    else:
        df_bundesland = df_ohne_ort.groupby('Bundesland').agg({
            'Leitungslänge in km': 'sum',
            'Übertragungskapazität in MVA': 'sum',
            'Kosten in Mio.€': 'sum'
        }).reset_index()

    bundeslaender_gdf = bundeslaender_gdf.merge(df_bundesland, left_on='name', right_on='Bundesland', how='left')

    def style_function(feature):
        if feature['properties']['Kosten in Mio.€'] is not None:
            return {
                'fillColor': '#ffcc00',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6
            }
        else:
            return {
                'fillColor': 'grey',
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.2
            }

    folium.GeoJson(
        bundeslaender_gdf,
        name="Bundesländer",
        tooltip=folium.features.GeoJsonTooltip(
            fields=['name', 'Leitungslänge in km', 'Übertragungskapazität in MVA', 'Kosten in Mio.€'],
            aliases=['Bundesland', 'Leitungslänge', 'Kapazität', 'Kosten'],
            localize=True
        ),
        style_function=style_function
    ).add_to(karte)

    marker_cluster = MarkerCluster().add_to(karte)
    df_orte = df_valid[~df_valid['Ort / Trasse'].apply(is_invalid)]
    for _, row in df_orte.iterrows():
        vnb = row['VNB-Name']
        farbe = vnb_color_map.get(vnb, '#3186cc')
        popup = "<br>".join([
            f"<b>{html.escape(str(col))}:</b> {html.escape(str(row[col]))}"
            for col in popup_order if col in row.index and not is_invalid(row[col])
        ])
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=9,
            color=farbe,
            fill=True,
            fill_color=farbe,
            fill_opacity=0.8,
            popup=folium.Popup(popup, max_width=400),
            tooltip=row.get('Ort / Trasse', row['Bundesland'])
        ).add_to(marker_cluster)

    karte.save(output_map)
    print(f"✔️ Geokodierte Datei gespeichert: {output_excel}")
    print(f"✔️ Fehlermeldung gespeichert: {output_failure}")
    print(f"✔️ Interaktive Karte gespeichert als: {output_map}")

if __name__ == "__main__":
    start = time.time()
    geocode_and_map("/Users/maxicolin/PycharmProjects/PythonProject/geokodiert_gesamt.xlsx")
    end = time.time()
    mins, secs = divmod(int(end - start), 60)
    print(f"⏱️ Laufzeit: {mins:02d}:{secs:02d} Minuten:Sekunden")
