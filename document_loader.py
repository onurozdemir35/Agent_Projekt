import os
from concurrent.futures import ThreadPoolExecutor
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def process_file(path, data_dir):
    """Process a single file and return its loaded documents or an error."""
    try:
        if path.endswith(".txt"):
            loader = TextLoader(path, encoding="utf-8")
        elif path.endswith(".pdf"):
            loader = PyPDFLoader(path)
        else:
            return "skipped", path  # Unsupported file format

        loaded_docs = loader.load()
        for doc in loaded_docs:
            doc.metadata["source"] = os.path.relpath(path, data_dir)  # Relative path for metadata
        return "success", loaded_docs
    except Exception as e:
        return "failed", (path, str(e))  # Return the error message

def load_and_split_documents(data_dir="./data", chunk_size=500, chunk_overlap=100, max_workers=4):
    """Loads and splits text and PDF documents from a directory and its subdirectories."""
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"The directory '{data_dir}' does not exist. Please create it and add .txt or .pdf files.")

    docs = []
    skipped_files = []
    failed_files = []

    # Collect all file paths
    file_paths = []
    for root, _, files in os.walk(data_dir):
        for filename in files:
            file_paths.append(os.path.join(root, filename))

    # Process files in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(lambda path: process_file(path, data_dir), file_paths)

    # Handle results
    for status, result in results:
        if status == "success":
            docs.extend(result)
        elif status == "skipped":
            skipped_files.append(result)
        elif status == "failed":
            failed_files.append(result)

    if len(docs) == 0:
        print("❌ No valid files were found in the directory.")
        return []

    splitter = (chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    print(f"✅ {len(chunks)} chunks were loaded and split.")

    # Print the list of skipped files
    if skipped_files:
        print("\n⚠️ The following files were skipped due to unsupported formats:")
        for skipped_file in skipped_files:
            print(f" - {skipped_file}")

    # Print the list of failed files
    if failed_files:
        print("\n❌ The following files could not be processed due to errors:")
        for failed_file, error in failed_files:
            print(f" - {failed_file}: {error}")

    return chunks

if __name__ == "__main__":
    chunks = load_and_split_documents(max_workers=8)  # Adjust max_workers based on your CPU cores
    if chunks:
        print(f"First chunk: {chunks[0].page_content[:100]}...")
    else:
        print("No chunks were generated.")
