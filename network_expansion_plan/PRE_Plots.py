import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. Daten laden ---
excel_datei = 'geokodiert_zugestimmt.xlsx'
df = pd.read_excel(excel_datei)

# --- 2. Metriken definieren ---
metrics = [
    'Leitungslänge in km',
    'Übertragungskapazität in MVA',
    'Kosten in Mio.€'
]

# --- 3. Aggregationen berechnen ---
summary_all = df[metrics].sum().reset_index()
summary_all.columns = ['Kennzahl', 'Gesamtwert']
summary_all['Gesamtwert'] = summary_all['Gesamtwert'].round(2)

summary_per_vnb = df.groupby('VNB-Name')[metrics].sum().reset_index()
summary_per_vnb[metrics] = summary_per_vnb[metrics].round(2)

summary_by_date = df.groupby('Zeithorizont')[metrics].sum().reset_index()
summary_by_date[metrics] = summary_by_date[metrics].round(2)

# --- 4. Balkendiagramme je Kennzahl (je VNB) mit Fußnote ---
# 4.1 Kosten
fig_costs_vnb = px.bar(
    summary_per_vnb,
    x='VNB-Name', y='Kosten in Mio.€',
    title='Summe angegebener Kosten* in Mio.€ je VNB'
)
fig_costs_vnb.update_layout(
    xaxis_tickangle=-45,
    yaxis_title='Summe angegebener Kosten in Mio.€',
    annotations=[
        dict(
            text='*Für einen Teil der Maßnahmen liegen keine Kostenangaben vor.<br>Zudem variiert die Vollständigkeit der Angaben zwischen den Verteilnetzbetreibern erheblich.',
            xref='paper', yref='paper',
            x=0, y=1.08,
            showarrow=False,
            font=dict(size=12, color='gray'),
            align='left'
        )
    ]
)
fig_costs_vnb.write_html('plot_kosten_je_vnb.html')
fig_costs_vnb.show()

# 4.2 Übertragungskapazität
fig_capacity_vnb = px.bar(
    summary_per_vnb,
    x='VNB-Name', y='Übertragungskapazität in MVA',
    title='Summe angegebene Übertragungskapazität* in MVA je VNB'
)
fig_capacity_vnb.update_layout(
    xaxis_tickangle=-45,
    yaxis_title='Summe angegebene Übertragungskapazität in MVA',
    annotations=[
        dict(
            text='*Für einen Teil der Maßnahmen liegen keine Übertragungskapazitäten vor.<br>Zudem variiert die Vollständigkeit der Angaben zwischen den Verteilnetzbetreibern erheblich.',
            xref='paper', yref='paper',
            x=0, y=1.08,
            showarrow=False,
            font=dict(size=12, color='gray'),
            align='left'
        )
    ]
)
fig_capacity_vnb.write_html('plot_kapazitaet_je_vnb.html')
fig_capacity_vnb.show()

# 4.3 Leitungslänge
fig_length_vnb = px.bar(
    summary_per_vnb,
    x='VNB-Name', y='Leitungslänge in km',
    title='Summe angegebene Leitungslänge* in km je VNB'
)
fig_length_vnb.update_layout(
    xaxis_tickangle=-45,
    yaxis_title='Summe angegebene Leitungslänge in km',
    annotations=[
        dict(
            text='*Für einen Teil der Maßnahmen liegen keine Leitungslängen vor.<br>Zudem variiert die Vollständigkeit der Angaben zwischen den Verteilnetzbetreibern erheblich.',
            xref='paper', yref='paper',
            x=0, y=1.08,
            showarrow=False,
            font=dict(size=12, color='gray'),
            align='left'
        )
    ]
)
fig_length_vnb.write_html('plot_leitungslänge_je_vnb.html')
fig_length_vnb.show()

# --- 5. Treemap der Kostenverteilung ---
fig_treemap = px.treemap(
    summary_per_vnb,
    path=['VNB-Name'],
    values='Kosten in Mio.€',
    title='Kostenverteilung der angegebenen Kosten* je VNB'
)
fig_treemap.data[0].texttemplate = "%{label}<br>%{value:.2f} Mio €"
fig_treemap.update_layout(
    annotations=[
        dict(
            text='*Für einen Teil der Maßnahmen liegen keine Kostenangaben vor.<br>Zudem variiert die Vollständigkeit der Angaben zwischen den Verteilnetzbetreibern erheblich.',
            xref='paper', yref='paper',
            x=0, y=1.08,
            showarrow=False,
            font=dict(size=12, color='gray'),
            align='left'
        )
    ]
)
fig_treemap.write_html('plot_treemap_kostenverteilung.html')
fig_treemap.show()

# --- 6. Tabellen: Gesamtsummen und Sammelstatistik je VNB ---
fig_table_all = go.Figure(data=[go.Table(
    header=dict(values=list(summary_all.columns),
                fill_color='paleturquoise', align='left'),
    cells=dict(
        values=[summary_all['Kennzahl'], summary_all['Gesamtwert']],
        fill_color='lavender', align='left', format=[None, '.2f']
    )
)])
fig_table_all.update_layout(title='Gesamtsummen aller Kennzahlen')
fig_table_all.write_html('tabelle_gesamtsummen.html')
fig_table_all.show()

fig_table_vnb = go.Figure(data=[go.Table(
    header=dict(values=['VNB-Name'] + metrics,
                fill_color='paleturquoise', align='left'),
    cells=dict(
        values=[summary_per_vnb[col] for col in ['VNB-Name'] + metrics],
        fill_color='lavender', align='left', format=['', '.2f', '.2f', '.2f']
    )
)])
fig_table_vnb.update_layout(title='Sammelstatistik je VNB-Name')
fig_table_vnb.write_html('tabelle_sammelstatistik_je_vnb.html')
fig_table_vnb.show()

# --- 7. Balkendiagramme je Kennzahl nach Fertigstellungsjahr ---
footnotes = {
    'Leitungslänge in km': '*Für einen Teil der Maßnahmen liegen keine Leitungslängen vor.<br>Zudem variiert die Vollständigkeit der Angaben zwischen den Verteilnetzbetreibern erheblich.',
    'Übertragungskapazität in MVA': '*Für einen Teil der Maßnahmen liegen keine Übertragungskapazitäten vor.<br>Zudem variiert die Vollständigkeit der Angaben zwischen den Verteilnetzbetreibern erheblich.',
    'Kosten in Mio.€': '*Für einen Teil der Maßnahmen liegen keine Kostenangaben vor.<br>Zudem variiert die Vollständigkeit der Angaben zwischen den Verteilnetzbetreibern erheblich.'
}

for metric in metrics:
    fig = px.bar(
        summary_by_date,
        x='Zeithorizont', y=metric,
        title=f"Summe angegebener {metric}* nach Fertigstellungsjahr"
    )
    fig.update_layout(
        xaxis_title='Fertigstellungsjahr',
        yaxis_title=f"Summe angegebener {metric}",
        annotations=[
            dict(
                text=footnotes[metric],
                xref='paper', yref='paper',
                x=0, y=1.08,
                showarrow=False,
                font=dict(size=12, color='gray'),
                align='left'
            )
        ]
    )
    filename = f'plot_{metric.replace(" ", "_").replace("ä", "ae").replace("ü", "ue").replace("ö", "oe").replace(".", "").replace("€", "eur")}_nach_zeithorizont.html'
    fig.write_html(filename)
    fig.show()