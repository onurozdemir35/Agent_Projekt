from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
import os

def load_documents_from_directory(directory):
    """Load documents from a directory and its subdirectories."""
    all_docs = []
    for company in os.listdir(directory):
        company_path = os.path.join(directory, company)
        if os.path.isdir(company_path):
            for file in os.listdir(company_path):
                if file.endswith(".pdf"):
                    loader = PyPDFLoader(os.path.join(company_path, file))
                    docs = loader.load()
                    for d in docs:
                        d.metadata["company"] = company
                        d.metadata["filename"] = file
                    all_docs.extend(docs)
    return all_docs

docs = load_documents_from_directory("data")

embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embedding)
vectorstore.save_local("index/multimodal_index")