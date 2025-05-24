# # from langchain.agents import AgentExecutor, create_react_agent
# # from langchain_core.prompts import ChatPromptTemplate
# # from langchain_core.tools import Tool
# # from langchain_google_genai import ChatGoogleGenerativeAI
# # from langchain_huggingface import HuggingFaceEmbeddings
# # from langchain_chroma import Chroma
# # from langchain.chains import RetrievalQA
# # from typing import Optional
# # import os
# # from dotenv import load_dotenv

# # load_dotenv()

# # # 1. Initialisierung mit bestehender ChromaDB
# # def load_existing_vectorstore():
# #     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
# #     return Chroma(
# #         collection_name="example_collection",
# #         embedding_function=embeddings,
# #         persist_directory="./chroma_langchain_db"
# #     )

# # # 2. LLM (Gemini Flash 2)
# # llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# # # 3. Tools für den Agenten
# # def setup_tools(vectorstore: Optional[Chroma] = None):
# #     # Tool 1: Dokumentenabfrage (nur wenn ChromaDB existiert)
# #     rag_tool = None
# #     if vectorstore:
# #         qa_chain = RetrievalQA.from_chain_type(
# #             llm=llm,
# #             chain_type="stuff",
# #             retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),  # k erhöht
# #             verbose=True
# #         )
# #         # Debug: Zeige die gefundenen Passagen an
# #         def debug_qa_chain_run(query):
# #             result = qa_chain.run(query)
# #             print("[DEBUG] RetrievalQA result:", result)
# #             return result
# #         rag_tool = Tool(
# #             name="document_search",
# #             func=debug_qa_chain_run,
# #             description=(
# #                 "Nutze dieses Tool für alle Fragen, die sich auf Inhalte, Zahlen, Tabellen oder Text aus den gespeicherten Unternehmensdokumenten beziehen. "
# #                 "Das Tool durchsucht die ChromaDB nach relevanten Passagen aus Finanzberichten, 10-K/10-Qs und anderen gespeicherten PDFs. "
# #                 "Bevorzuge dieses Tool bei allen dokumentenbezogenen Fragen!"
# #             )
# #         )
    
# #     # Tool 2: Allgemeiner Chat
# #     general_tool = Tool(
# #         name="general_chat",
# #         func=lambda q: llm.invoke(f"Antworte natürlich auf: {q}").content,
# #         description="Für allgemeine Unterhaltungen und Fragen ohne Dokumentenbezug."
# #     )
    
# #     return [t for t in [general_tool, rag_tool] if t is not None]

# # # 4. ReAct-Agent erstellen
# # def create_agent(tools: list):
# #     prompt = ChatPromptTemplate.from_template("""
# #     Beantworte die folgende Frage als ReAct-Agent. Nutze IMMER zuerst das Tool 'document_search', wenn die Frage sich auf Dokumente, Zahlen, Tabellen oder Inhalte aus Finanzberichten bezieht. Nur wenn keine relevante Information gefunden wird, nutze 'general_chat'.

# #     Verfügbare Tools: {tools}
# #     Tool-Namen: {tool_names}

# #     Verlauf der bisherigen Konversation (nutze diesen Kontext, um vage oder referenzielle Fragen wie 'im gleichen Jahr' oder 'und bei Google?' korrekt zu beantworten):
# #     {history}

# #     Frage: {input}

# #     Denke laut nach und folge diesem Format:
# #     Thought: Beschreibe deinen Gedankengang.
# #     Action: <wähle einen Tool-Namen oder schreibe 'Final Answer'>
# #     Action Input: <Eingabe für das Tool, falls verwendet>
# #     Observation: <Ergebnis des Tools, wird vom System eingefügt>
# #     ... (wiederhole Thought/Action/Action Input/Observation nach Bedarf)
# #     Thought: Ich habe genug Informationen gesammelt.
# #     Final Answer: <deine abschließende Antwort>

# #     {agent_scratchpad}
# #     """)
    
# #     agent_executor = AgentExecutor(
# #         agent=create_react_agent(llm, tools, prompt),
# #         tools=tools,
# #         verbose=True,
# #         handle_parsing_errors=True
# #     )
# #     agent_executor.name = "rag_agent"
# #     return agent_executor

# # # 5. Hauptfunktion
# # if __name__ == "__main__":
# #     # ChromaDB laden (falls existiert)
# #     try:
# #         vectorstore = load_existing_vectorstore()
# #         print("ChromaDB erfolgreich geladen")
# #     except Exception as e:
# #         print(f"Warnung: ChromaDB konnte nicht geladen werden - {str(e)}")
# #         vectorstore = None

# #     # Agent initialisieren
# #     tools = setup_tools(vectorstore)
# #     agent = create_agent(tools)

# #     # Nachrichtenverlauf initialisieren
# #     history = []
# #     history_file = "chat_history.txt"

# #     # Interaktive Schleife
# #     print("\nAgent ist bereit (CTRL+C zum Beenden)")
# #     while True:
# #         try:
# #             query = input("\nFrage: ").strip()
# #             if query.lower() in ["exit", "quit"]:
# #                 break

# #             # Verlauf an den Agenten übergeben
# #             history.append({"role": "user", "content": query})
# #             response = agent.invoke({"input": query, "history": history})
# #             print("\nAntwort:", response["output"])
# #             history.append({"role": "assistant", "content": response["output"]})

# #             # Speichere den Verlauf nach jeder Runde
# #             with open(history_file, "w", encoding="utf-8") as f:
# #                 for msg in history:
# #                     f.write(f"{msg['role']}: {msg['content']}\n")

# #         except KeyboardInterrupt:
# #             break
# #         except Exception as e:
# #             print(f"Fehler: {str(e)}")
# from langchain.agents import AgentExecutor, create_react_agent
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.tools import Tool
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma
# from langchain.chains import RetrievalQA
# from typing import Optional
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # === 1. Vektorstore laden ===
# def load_existing_vectorstore():
#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
#     return Chroma(
#         collection_name="example_collection",
#         embedding_function=embeddings,
#         persist_directory="./chroma_langchain_db"
#     )

# # === 2. LLM initialisieren ===
# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# # === 3. Tools definieren ===
# def setup_tools(vectorstore: Optional[Chroma] = None):
#     rag_tool = None
#     if vectorstore:
#         qa_chain = RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type="stuff",
#             retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
#             return_source_documents=True,
#             verbose=True
#         )

#         def debug_qa_chain_run(query):
#             result = qa_chain.invoke({"query": query})
#             print("[DEBUG] Quellen:", [doc.metadata.get("source", "Unbekannt") for doc in result['source_documents']])
#             return result["result"]

#         rag_tool = Tool(
#             name="document_search",
#             func=debug_qa_chain_run,
#             description="Für dokumentenbasierte Fragen zu Zahlen, Text oder Fakten aus Unternehmensberichten."
#         )

#     general_tool = Tool(
#         name="general_chat",
#         func=lambda q: llm.invoke(f"Antworte natürlich auf: {q}").content,
#         description="Für allgemeine Fragen ohne Dokumentenbezug oder Smalltalk."
#     )

#     return [t for t in [general_tool, rag_tool] if t is not None]

# # === 4. ReAct-Agent mit 'Final Answer:' ===
# def create_agent(tools: list):
#     prompt = ChatPromptTemplate.from_template("""
# Beantworte die folgende Frage als ReAct-Agent. Nutze IMMER zuerst das Tool 'document_search', wenn die Frage sich auf Dokumente, Zahlen, Tabellen oder Inhalte aus Finanzberichten bezieht. Nur wenn keine relevante Information gefunden wird, nutze 'general_chat'.

# Verfügbare Tools: {tools}
# Tool-Namen: {tool_names}

# Verlauf der bisherigen Konversation (wichtig für Folgefragen wie 'und Google?'):
# {history}

# Frage: {input}

# Denke laut nach und folge diesem Format:
# Thought: <Dein Gedankengang>
# Action: <Toolname>
# Action Input: <Eingabe>
# Observation: <Ergebnis des Tools>
# ... (wiederhole Thought/Action/Observation bei Bedarf)
# Thought: Ich habe genug Informationen gesammelt.
# Final Answer: <deine finale Antwort>

# {agent_scratchpad}
# """)

#     agent_executor = AgentExecutor(
#         agent=create_react_agent(llm, tools, prompt),
#         tools=tools,
#         return_direct=True,  # ✅ gibt 'Final Answer' direkt aus
#         verbose=True,
#         handle_parsing_errors=True
#     )
#     agent_executor.name = "rag_agent"
#     return agent_executor

# # === 5. Optional: CLI-Test (nicht notwendig für Supervisor/Gradio) ===
# if __name__ == "__main__":
#     try:
#         vectorstore = load_existing_vectorstore()
#         print("✅ ChromaDB erfolgreich geladen")
#     except Exception as e:
#         print(f"⚠️ Fehler beim Laden von ChromaDB: {e}")
#         vectorstore = None

#     tools = setup_tools(vectorstore)
#     agent = create_agent(tools)

#     print("\n🧠 Agent ist bereit. Frage stellen (CTRL+C beendet)")
#     history = []

#     while True:
#         try:
#             query = input("\nFrage: ").strip()
#             if query.lower() in ["exit", "quit"]:
#                 break

#             history.append({"role": "user", "content": query})
#             response = agent.invoke({"input": query, "history": history})
#             print("\nAntwort:", response)
#             history.append({"role": "assistant", "content": response})

#         except KeyboardInterrupt:
#             break
#         except Exception as e:
#             print(f"❌ Fehler: {e}")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional

# === 1. Vektorstore laden ===
def load_existing_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    return Chroma(
        collection_name="example_collection",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db"
    )

# === 2. Tools vorbereiten ===
def setup_tools(vectorstore: Optional[Chroma] = None):
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

    tools = []

    if vectorstore:
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
            verbose=True
        )

        def debug_qa_chain(query):
            result = qa_chain.run(query)
            print("[DEBUG] RetrievalQA result:", result)
            return result

        tools.append(
            Tool(
                name="document_search",
                func=debug_qa_chain,
                description=(
                    "Suche nach konkreten Fakten, Zahlen oder Tabellen aus Finanzberichten. "
                    "Bevorzugt bei Umsatz-, Gewinn-, oder anderen dokumentenbasierten Fragen."
                )
            )
        )

    tools.append(
        Tool(
            name="general_chat",
            func=lambda q: llm.invoke(f"Antworte natürlich auf: {q}").content,
            description="Für Smalltalk oder Fragen ohne Dokumentenbezug."
        )
    )

    return tools

# === 3. ReAct-Agent mit erweitertem Prompt ===
def create_agent(tools: list):
    prompt = ChatPromptTemplate.from_template("""
Du bist ein ReAct-Agent für Unternehmensdaten. Befolge folgende Regeln strikt:

1. Nutze IMMER zuerst das Tool **document_search**, wenn die Frage sich auf:
   - Umsatz, Gewinn, Einnahmen
   - Jahre (z. B. 2021, 2022, 2023)
   - Inhalte aus Berichten, Tabellen oder Dokumenten
   bezieht.

2. Wenn das Jahr in der Frage **< aktuelles Jahr liegt**, gehe davon aus, dass die Daten veröffentlicht sind.
   Lass dich nicht mit 'nicht verfügbar' zufrieden geben.

3. Falls document_search keine gute Antwort bringt oder keine Zahl enthält,
   leite zur Websuche weiter (Tool: research_agent), sofern vorhanden.

4. Nutze general_chat **nur** für Smalltalk oder allgemeine Fragen.

Format:
Verfügbare Tools: {tools}
Tool-Namen: {tool_names}
Verlauf: {history}
Frage: {input}

Nutze folgenden Ablauf:
Thought: ...
Action: <Tool-Name oder Final Answer>
Action Input: <Text>
Observation: <Tool-Ergebnis>
...
Thought: Ich habe genug Information.
Final Answer: <Antwort>

{agent_scratchpad}
""")

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )
    executor.name = "rag_agent"
    return executor
