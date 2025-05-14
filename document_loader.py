import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_split_documents(data_dir="./data", chunk_size=500, chunk_overlap=100):
    """Loads and splits text and PDF documents from a directory and its subdirectories."""
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"The directory '{data_dir}' does not exist. Please create it and add .txt or .pdf files.")

    docs = []
    for root, _, files in os.walk(data_dir):  # Recursively traverse directories
        for filename in files:
            path = os.path.join(root, filename)
            try:
                if filename.endswith(".txt"):
                    loader = TextLoader(path, encoding="utf-8")
                elif filename.endswith(".pdf"):
                    loader = PyPDFLoader(path)
                else:
                    print(f"⚠️ Skipping unsupported file format: {filename}")
                    continue

                loaded_docs = loader.load()
                for doc in loaded_docs:
                    doc.metadata["source"] = os.path.relpath(path, data_dir)  # Relative path for metadata
                docs.extend(loaded_docs)
            except Exception as e:
                print(f"❌ Error loading the file {filename}: {e}")
                continue

    if len(docs) == 0:
        print("❌ No valid files were found in the directory.")
        return []

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    print(f"✅ {len(chunks)} chunks were loaded and split.")
    return chunks

if __name__ == "__main__":
    chunks = load_and_split_documents()
    if chunks:
        print(f"First chunk: {chunks[0].page_content[:100]}...")
    else:
        print("No chunks were generated.")
