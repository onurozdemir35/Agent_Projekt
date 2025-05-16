import os
import pickle
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_community.embeddings import SentenceTransformerEmbeddings

from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
print("✅ GPU aktiv:", torch.cuda.is_available())
print("📍 Modellgerät:", model.device)


# Laden von Umgebungsvariablen
load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


def load_data(file_path="extracted_documents_2.pkl"):
    """
    Lädt die extrahierten PDF-Daten aus einer Pickle-Datei.
    :param file_path: Pfad zur Pickle-Datei
    :return: Liste von extrahierten Dokument-Daten
    """
    with open(file_path, "rb") as f:
        return pickle.load(f)

def build_documents(extracted_data):
    """
    Wandelt die extrahierten Tabellen aus DataFrames in LangChain Document-Objekte um.
    Dabei werden Metadaten (Firma, Datei, Tabellenindex) hinzugefügt.
    :param extracted_data: Liste mit extrahierten Daten
    :return: Liste von Document-Objekten
    """
    documents = []
    for entry in extracted_data:
        company = entry["company"]
        file = entry["file"]
        tables = entry["tables"]

        for i, df in enumerate(tables):
            try:
                # DataFrame in Markdown-Text umwandeln, für bessere Lesbarkeit
                content = df.to_markdown(index=False)
            except Exception:
                # Falls Markdown fehlschlägt, konvertiere einfach in String
                content = str(df)

            # Document-Objekt erstellen mit Text und Metadaten
            documents.append(Document(
                page_content=content,
                metadata={"company": company, "file": file, "table_index": i}
            ))
    return documents

def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    """
    Zerlegt die Dokumente in kleinere Text-Chunks, um Speicher- und Suchbarkeit zu optimieren.
    :param documents: Liste von Document-Objekten
    :param chunk_size: maximale Größe eines Chunks in Zeichen
    :param chunk_overlap: Überlappung zwischen den Chunks (in Zeichen)
    :return: Liste von geteilten Chunks als Document-Objekte
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(documents)
    print(f"✅ {len(chunks)} Chunks erzeugt.")
    return chunks

#def init_embeddings():
#    """
#  Lädt das SentenceTransformer Modell auf der GPU (wenn verfügbar) und erstellt LangChain Embeddings.
#   :return: Embeddings-Objekt
#   """
#   print("⏳ Lade SentenceTransformer mit GPU...")
#   sbert_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", device="cuda")
#   embeddings = HuggingFaceEmbeddings(model=sbert_model)
#  print("✅ Embeddings initialisiert.")
#   return embeddings

#def init_embeddings():
#def init_embeddings():
#    print("⏳ Lade SentenceTransformer mit GPU...")
#    sbert_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", device="cuda")
#    embeddings = SentenceTransformerEmbeddings(model=sbert_model)
#    return embeddings
def init_embeddings():
    print("⏳ Initialisiere SentenceTransformerEmbeddings mit GPU...")
    embeddings = SentenceTransformerEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    return embeddings
   
def init_vector_store(embeddings):
    """
    Initialisiert die Chroma Vektor-Datenbank mit dem gegebenen Embeddings-Modell.
    :param embeddings: Embeddings-Objekt
    :return: Chroma Vector Store Objekt
    """
    vector_store = Chroma(
        collection_name="example_collection",              # Name der Kollektion in der DB
        embedding_function=embeddings,                      # Embeddings-Funktion zum Vektorisieren
        persist_directory="./chroma_langchain_db",         # Lokaler Speicherort der DB
    )
    return vector_store

def save_documents_in_batches(documents, vector_store, batch_size=5000):
    """
    Speichert die Dokument-Chunks stückweise in die Vektor-Datenbank, um Speicherprobleme bei großen Datenmengen zu vermeiden.
    :param documents: Liste von Document-Chunks
    :param vector_store: Chroma Vektor-Datenbank-Instanz
    :param batch_size: Anzahl Chunks pro Batch
    """
    total = len(documents)
    print(f"⏳ Speichere {total} Chunks in Batches von {batch_size} ...")
    for i in range(0, total, batch_size):
        batch = documents[i : i + batch_size]
        vector_store.add_documents(batch)
        print(f"✅ Batch {i // batch_size + 1} mit {len(batch)} Chunks hinzugefügt.")
    print("✅ Alle Chunks erfolgreich in Chroma gespeichert.")

def search_in_vector_store(vector_store, query, k=3):
    """
    Führt eine Ähnlichkeitssuche in der Vektor-Datenbank durch.
    :param vector_store: Chroma Vektor-Datenbank-Instanz
    :param query: Suchanfrage als Text
    :param k: Anzahl der Top-Treffer
    """
    print(f"🔍 Suche nach: {query}")
    results = vector_store.similarity_search(query, k=k)
    for i, doc in enumerate(results, 1):
        print(f"\n🔎 Treffer {i}:")
        print(doc.page_content)
        print("📎 Metadaten:", doc.metadata)

def main():
    # 1. Lade die extrahierten Daten
    extracted_data = load_data()
    
    # 2. Erstelle Document-Objekte aus den extrahierten Tabellen
    documents = build_documents(extracted_data)
    
    # 3. Teile die Dokumente in handliche Chunks
    chunks = chunk_documents(documents)
    
    # 4. Lade das Embeddings-Modell auf der GPU
    embeddings = init_embeddings()
    
    # 5. Initialisiere die Vektor-Datenbank
    vector_store = init_vector_store(embeddings)
    
    # 6. Speichere die Chunks in Batches, um Speicherprobleme zu vermeiden
    save_documents_in_batches(chunks, vector_store, batch_size=5000)
    
    # 7. Beispielhafte Suche in der Vektor-Datenbank
    query = "Wie hoch war der Gewinn 2022?"
    search_in_vector_store(vector_store, query)

if __name__ == "__main__":
    main()
