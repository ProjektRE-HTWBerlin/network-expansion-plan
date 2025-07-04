import camelot
import os
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import re

# === Konfiguration ===
TESSDATA_DIR = '/usr/local/share/tessdata'  # typischer Ort nach brew install tesseract-lang

# === Funktion zur OCR-Umwandlung ===
def ocr_pdf_to_text(pdf_path, temp_dir):
    lang_path = os.path.join(TESSDATA_DIR, "deu.traineddata")
    if not os.path.exists(lang_path):
        raise FileNotFoundError(
            f"❌ Sprachdatei 'deu.traineddata' nicht gefunden unter {TESSDATA_DIR}.\n"
            f"👉 Lade sie herunter von https://github.com/tesseract-ocr/tessdata und speichere sie dort."
        )

    images = convert_from_path(pdf_path)
    text_pages = []
    for i, image in enumerate(images):
        try:
            config = f"--tessdata-dir {TESSDATA_DIR} --psm 6"
            text = pytesseract.image_to_string(image, lang='deu', config=config)
            text_pages.append(text)
        except pytesseract.TesseractError as ocr_err:
            print(f"❌ OCR-Fehler auf Seite {i+1}: {ocr_err}")
    return "\n".join(text_pages)

# Hauptverarbeitung, hier den Eingabeordner anpassen
input_dir = "Bsp.:/Users/user/Desktop/Projekt RE/Stromnetz_Berlin"  # Ordner mit PDFs!
output_dir = "output"
temp_dir = "temp"

os.makedirs(output_dir, exist_ok=True)
os.makedirs(temp_dir, exist_ok=True)

pdf_files = [f for f in os.listdir(input_dir) if f.endswith(".pdf")]

if not pdf_files:
    print("⚠️  Keine PDF-Dateien im Eingabeordner gefunden.")
else:
    for file in pdf_files:
        input_path = os.path.join(input_dir, file)
        output_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.xlsx")
        print(f"📄 Verarbeite: {file}")

        try:
            tables = camelot.read_pdf(input_path, pages='all', flavor='lattice')

            if len(tables) == 0:
                print(f"⚠️  Keine Tabellen gefunden. Versuche OCR für {file} …")
                ocr_text = ocr_pdf_to_text(input_path, temp_dir)

                # Zeilenweise aufteilen und strukturieren
                lines = ocr_text.split('\n')
                lines = [line for line in lines if line.strip() != ""]
                rows = [re.split(r'\s{2,}', line.strip()) for line in lines]

                ocr_df = pd.DataFrame(rows)
                csv_file_path = os.path.join(temp_dir, f"{os.path.splitext(file)[0]}_ocr.csv")

                try:
                    ocr_df.to_csv(csv_file_path, index=False, encoding='utf-8')
                    print(f"✅ OCR abgeschlossen. CSV-Datei gespeichert unter: {csv_file_path}")
                except Exception as e:
                    print(f"❌ Fehler beim Schreiben der OCR-CSV-Datei für {file}: {e}")
            else:
                print(f"➡️  {len(tables)} Tabellen gefunden. Zusammenführen und Exportieren nach Excel …")
                combined_df = pd.concat([table.df for table in tables], ignore_index=True)

                # Kodierungsprobleme beheben
                for col in combined_df.columns:
                    combined_df[col] = combined_df[col].apply(
                        lambda x: x.encode('utf-8', errors='replace').decode('utf-8', errors='replace') if isinstance(x, str) else x
                    )

                # Sortierung nach 'VNB-Name' und zweiter Spalte, falls vorhanden
                if 'VNB-Name' in combined_df.columns and len(combined_df.columns) > 1:
                    zweite_spalte = combined_df.columns[1]
                    combined_df = combined_df.sort_values(by=['VNB-Name', zweite_spalte], kind='stable')

                combined_df.to_excel(output_path, index=False, engine='openpyxl')
                print(f"✅ Fertig: {output_path}\n")
        except Exception as e:
            print(f"❌ Fehler beim Verarbeiten von {file}: {e}")