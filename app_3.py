import os
import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage, HumanMessage

# --- Setup ---
st.set_page_config(page_title="📄 Dokumenten-Chatbot", layout="wide")
st.title("🔍 Dokumenten-Chatbot mit LangGraph & Memory")

CHROMA_DIR = "chroma_langchain_db"

# --- Prüfung auf Vektordatenbank ---
if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
    st.error("⚠️ Die Vektor-Datenbank wurde nicht gefunden oder ist leer. Bitte führe zuerst `data_loader_2.py` aus.")
    st.stop()

# --- Initialisierung von Komponenten ---
@st.cache_resource
def init_components():
    embeddings = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")
    vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    retriever = vectordb.as_retriever()

    llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

    retriever_tool = create_retriever_tool(
        retriever,
        name="retrieve_documents",
        description="Durchsuche die Dokumente nach relevanten Informationen.",
    )

    memory_saver = InMemorySaver()
    agent = create_react_agent(model=llm, tools=[retriever_tool], checkpointer=memory_saver)

    return agent, memory_saver

agent_executor, memory_saver = init_components()

# --- Chatverlauf in Session State ---
if "message_history" not in st.session_state:
    st.session_state.message_history = []

# --- Chatverlauf anzeigen ---
st.markdown("### 💬 Chatverlauf")
for msg in st.session_state.message_history:
    # Unterstützt sowohl dict als auch AIMessage/HumanMessage
    if isinstance(msg, dict):
        role = msg.get("role", "user")
        content = msg.get("content", "")
    else:
        role = msg.role if hasattr(msg, "role") else "user"
        content = msg.content if hasattr(msg, "content") else ""

    if role == "human":
        st.markdown(f"**👤 User:** {content}")
    elif role == "ai":
        st.markdown(f"**🤖 Bot:** {content}")

# --- Nutzereingabe ---
query = st.text_input("❓ Deine Frage zu den Dokumenten:")

if query:
    with st.spinner("🔄 Verarbeite Anfrage..."):
        # Nutzer-Nachricht hinzufügen
        st.session_state.message_history.append(HumanMessage(content=query))

        # Agent ausführen
        for chunk in agent_executor.stream(
            {"messages": st.session_state.message_history},
            config={"configurable": {"thread_id": "1"}},
            stream_mode="values",
        ):
            latest = chunk["messages"][-1]
            st.session_state.message_history.append(latest)

        # Antwort anzeigen
        st.markdown("### 🧠 Antwort")
        st.markdown(latest.content if hasattr(latest, "content") else "Keine Antwort gefunden.")

        # Aktualisierter Verlauf
        st.markdown("### 💬 Aktualisierter Chatverlauf")
        for msg in st.session_state.message_history:
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
            else:
                role = msg.role if hasattr(msg, "role") else "user"
                content = msg.content if hasattr(msg, "content") else ""

            if role == "human":
                st.markdown(f"**👤 User:** {content}")
            elif role == "ai":
                st.markdown(f"**🤖 Bot:** {content}")