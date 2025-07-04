import pandas as pd

# Datei einlesen
df = pd.read_excel('Bsp.:geokodiert_VNB.xlsx')

# Namen der zweiten Spalte (z.B. 'Teilnetzgebiet') anpassen
zweite_spalte = df.columns[1]

# Werte der zweiten Spalte bereinigen (optional, verbessert Sortierung)
df[zweite_spalte] = df[zweite_spalte].astype(str).str.strip()

# Nach 'VNB-Name' und dann nach der zweiten Spalte sortieren
df_sorted = df.sort_values(by=['VNB-Name', zweite_spalte], kind='stable')

# Sortierte Tabelle speichern
df_sorted.to_excel('geokodiert_sortiert.xlsx', index=False)