"""import streamlit as st
import os
import getpass
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chat_models import init_chat_model


# Embeddings & Vector DB initialisieren
embedding = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")
vectordb = Chroma(
    persist_directory="chroma_langchain_db",
    embedding_function=embedding,
)
retriever = vectordb.as_retriever()

# Google Gemini Modell laden
model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

# RAG Chain erstellen
qa_chain = RetrievalQA.from_chain_type(
    llm=model,
    retriever=retriever,
    return_source_documents=True
)

# Streamlit UI
st.title("🔍 Dokumenten-Chatbot mit Google Gemini")
query = st.text_input("❓ Frage zu deinen Dokumenten:")

if query:
    with st.spinner("Suche Antwort..."):
        result = qa_chain(query)
        st.markdown("### 🧠 Antwort")
        st.write(result["result"])

        st.markdown("### 📄 Quellen")
        for doc in result["source_documents"]:
            st.markdown(f"- `{doc.metadata}`"
from langgraph.checkpoint.memory import MemorySaver

import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.agents import create_react_agent

# Embeddings & Retriever initialisieren
embedding = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")
vectordb = Chroma(persist_directory="chroma_langchain_db", embedding_function=embedding)
retriever = vectordb.as_retriever()

# Chatmodell laden
llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

# Retriever-Tool definieren
retriever_tool = {
    "name": "Retriever",
    "description": "Verwende dieses Tool, um Informationen aus Dokumenten zu finden",
    "func": retriever.get_relevant_documents
}

# MemorySaver initialisieren (speichert automatisch persistiert in default Pfad)
memory = MemorySaver()

# Agent mit Memory initialisieren
agent_executor = create_react_agent(llm, [retriever_tool], memory=memory)

# Streamlit UI
st.title("🔍 Dokumenten-Chatbot mit Agent & Memory (persistiert)")

query = st.text_input("❓ Frage zu deinen Dokumenten:")

if query:
    with st.spinner("Suche Antwort..."):
        result = agent_executor.run(query)
        st.markdown("### 🧠 Antwort")
        st.write(result))"""

from langgraph.checkpoint.memory import MemorySaver

import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.agents import create_react_agent

# Embeddings & Retriever initialisieren
embedding = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")
vectordb = Chroma(persist_directory="chroma_langchain_db", embedding_function=embedding)
retriever = vectordb.as_retriever()

# Chatmodell laden
llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

# Retriever-Tool definieren
retriever_tool = {
    "name": "Retriever",
    "description": "Verwende dieses Tool, um Informationen aus Dokumenten zu finden",
    "func": retriever.get_relevant_documents
}

# MemorySaver initialisieren mit Persistenzordner
memory = MemorySaver(persist_directory="checkpoint_dir")

# Agent mit Memory initialisieren
agent_executor = create_react_agent(llm, [retriever_tool], memory=memory)

st.title("🔍 Dokumenten-Chatbot mit Agent & Memory (persistiert)")

# Chatverlauf aus dem Memory laden (Liste von Messages)
chat_history = memory.load()  # Dict mit "messages" Schlüssel

if "messages" not in chat_history:
    chat_history["messages"] = []

# Bisherige Nachrichten anzeigen
st.markdown("### 💬 Chatverlauf")
for msg in chat_history["messages"]:
    role = msg.get("role", "unknown")
    content = msg.get("content", "")
    if role == "human":
        st.markdown(f"**User:** {content}")
    elif role == "ai":
        st.markdown(f"**Bot:** {content}")

query = st.text_input("❓ Frage zu deinen Dokumenten:")

if query:
    with st.spinner("Suche Antwort..."):
        # Agent mit der neuen Eingabe ausführen
        result = agent_executor.run(query)

        # Ergebnis anzeigen
        st.markdown("### 🧠 Antwort")
        st.write(result)

        # Nach der Antwort Chatverlauf neu laden und anzeigen
        chat_history = memory.load()
        st.markdown("### 💬 Aktualisierter Chatverlauf")
        for msg in chat_history["messages"]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if role == "human":
                st.markdown(f"**User:** {content}")
            elif role == "ai":
                st.markdown(f"**Bot:** {content}")