import os
import fitz
import pdfplumber
import pandas as pd
import pickle

DATA_DIR = "data"
CACHE_FILE = "extracted_documents_2.pkl"

def extract_tables_from_pdf(pdf_path):
    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            raw_tables = page.extract_tables()
            current_table = []

            for table in raw_tables:
                if table:
                    df = pd.DataFrame(table)
                    # Prüfen: ist es nur eine Zeile? (oft zerschnitten)
                    if len(df) == 1:
                        current_table.append(df)
                    else:
                        # Falls vorher Mini-Tabellen gesammelt wurden: zusammenfassen
                        if current_table:
                            combined = pd.concat(current_table, ignore_index=True)
                            all_tables.append(combined)
                            current_table = []
                        all_tables.append(df)

            # Ende der Seite: übrig gebliebene Mini-Tabellen anhängen
            if current_table:
                combined = pd.concat(current_table, ignore_index=True)
                all_tables.append(combined)

    return all_tables


def extract_all_documents():
    documents = []
    for company in os.listdir(DATA_DIR):
        company_path = os.path.join(DATA_DIR, company)
        if not os.path.isdir(company_path):
            continue
        for filename in os.listdir(company_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(company_path, filename)
                print(f"🔍 Lade: {file_path}")
                text = extract_tables_from_pdf(file_path)
                tables = extract_tables_from_pdf(file_path)
                documents.append({
                    "company": company,
                    "file": filename,
                    "text": text,
                    "tables": tables
                })
    return documents

def get_all_documents():
    if os.path.exists(CACHE_FILE):
        print(" Lade aus Cache:", CACHE_FILE)
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    else:
        print(" Extrahiere neu aus PDFs...")
        documents = extract_all_documents()
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(documents, f)
        print(" Cache gespeichert:", CACHE_FILE)
        return documents