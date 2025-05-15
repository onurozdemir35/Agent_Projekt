import fitz
from data_extrahieren import get_all_documents
from tabulate import tabulate

documents = get_all_documents()

print(f"\n✅ {len(documents)} Dokumente geladen.")

# Buscar el documento específico
target_file = "10q-1q-2024-Apple.pdf"
target_table_index = 1  # Índice de la tabla (0 para la primera tabla, 1 para la segunda, etc.)

# Filtrar el documento deseado
target_doc = next((doc for doc in documents if doc["file"] == target_file), None)

if target_doc:
    print(f"\n📄 {target_doc['company']}: {target_doc['file']}")
    print(f"Text: {len(target_doc['text'])} Zeichen | Tabellen: {len(target_doc['tables'])}")

    if len(target_doc["tables"]) > target_table_index:
        table = target_doc["tables"][target_table_index]
        print(f"\n📊 Tabla {target_table_index + 1} del archivo {target_file}:")
        if not table.empty:  # Verifica si el DataFrame no está vacío
            print(tabulate(table, headers="keys", tablefmt="grid"))
        else:
            print("    (Tabla vacía)")
    else:
        print(f"\nEl archivo {target_file} no tiene una tabla número {target_table_index + 1}.")
else:
    print(f"\nEl archivo {target_file} no fue encontrado en los documentos cargados.")
