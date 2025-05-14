from data_extrahieren import get_all_documents

documents = get_all_documents()

print(f"\n✅ {len(documents)} Dokumente geladen.")

for i, doc in enumerate(documents[:3]):
    print(f"\n📄 {doc['company']}: {doc['file']}")
    print(f"Text: {len(doc['text'])} Zeichen | Tabellen: {len(doc['tables'])}")
