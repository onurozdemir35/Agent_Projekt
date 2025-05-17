# summarizer.py
import json
from model import model  # Vorgefertigtes LLM-Modell
from prompt_utils import build_missing_prompt  # Prompt-Funktion für fehlende Items

def summarize_pdf(file_name, toc_text, missing_items_string):
    """
    Erstellt ein Prompt zur Zusammenfassung eines PDF-Berichts, basierend auf dem Inhaltsverzeichnis und fehlenden Items.
    """
    missing_prompt = build_missing_prompt(file_name, missing_items_string)

    prompt = f"""
    Unten finden Sie das Inhaltsverzeichnis dieses Berichts:

    {toc_text}

    {missing_prompt}

    Bitte fassen Sie jeden Punkt ausführlich zusammen.
    """

    response = model.invoke(prompt)
    return response.content

if __name__ == "__main__":
    print("🚀 summarizer.py gestartet")

    # Lade die extrahierten Daten aus JSON
    with open("structured_data.json") as f:
        data = json.load(f)

    from toc_utils import extract_toc_from_data  # Gibt das Inhaltsverzeichnis für eine Datei zurück
    from csv import DictReader

    # Lese CSV mit den fehlenden Items
    with open("missing_items_summary.csv") as f:
        reader = DictReader(f)
        rows = list(reader)

    # Prüfe bereits vorhandene Zusammenfassungen
    try:
        with open("summaries.jsonl", encoding="utf-8") as f:
            existing = {json.loads(line)["file"] for line in f}
    except FileNotFoundError:
        existing = set()

    print(f"📄 Gesamtanzahl CSV-Einträge: {len(rows)}")
    print(f"🧾 Bereits vorhandene Zusammenfassungen: {len(existing)}")

    for row in rows:
        file = row["file"]

        if row["missing_count"] == "0":
            print(f"⏩ {file} übersprungen (keine fehlenden Items).")
            continue

        if file in existing:
            print(f"✅ {file} wurde bereits zusammengefasst.")
            continue

        missing = row["missing_items"]
        toc_text = extract_toc_from_data(data, file)

        if not toc_text:
            print(f"⚠️ TOC nicht gefunden: {file}")
            continue

        print(f"\n📄 Zusammenfassung wird erstellt für: {file}")
        print(f"🧩 Fehlende Items: {missing}")
        print(f"📚 Beispiel TOC:", toc_text[:200])

        try:
            result = summarize_pdf(file, toc_text, missing)
        except Exception as e:
            print(f"❌ Fehler: Zusammenfassung für {file} fehlgeschlagen -> {e}")
            continue

        with open("summaries.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"file": file, "summary": result}, ensure_ascii=False) + "\n")

        print(f"📝 Zusammenfassung abgeschlossen: {file}")