from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from rag_agnet_ganzneu import create_agent, setup_tools, load_existing_vectorstore
from web_such_agent import research_agent, ask_question_and_save_answer
from qa_ethics_agent import qa_ethics_agent
from data_analysis_agent import agent as data_analysis_agent
import os
from dotenv import load_dotenv
import re
import time

# === ENV laden ===
load_dotenv()

# === LLM initialisieren ===
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# === RAG-Agent vorbereiten ===
vectorstore = load_existing_vectorstore()
tools = setup_tools(vectorstore)
rag_agent = create_agent(tools)

# === Supervisor erstellen ===
supervisor = create_supervisor(
    model=llm,
    agents=[rag_agent, research_agent, data_analysis_agent],
    prompt=(
        "You are a supervisor managing three agents:\n"
        "- 'rag_agent': Handles document-based and structured data questions.\n"
        "- 'research_agent': Handles real-time web search questions.\n"
        "- 'data_analysis_agent': Handles data analysis, statistics, CSV/Excel, plotting, and advanced comparisons.\n"
        "Always assign one task to one agent. Never do the work yourself.\n"
        "If the user asks for analysis, statistics, plotting, or comparison of data, use the data_analysis_agent.\n"
        "After each agent responds, hand back the results."
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile()

# === Smalltalk und Plausibilität ===
smalltalk_keywords = [
    "hallo", "hi", "wie geht", "guten morgen", "guten abend", "servus",
    "grüß dich", "moin", "hey", "was geht", "wie läufts", "alles klar",
    "was machst du", "wer bist du", "was kannst du"
]

def is_smalltalk(question: str) -> bool:
    return any(kw in question.lower() for kw in smalltalk_keywords)

def is_insufficient(answer: str, user_input: str = "") -> bool:
    if not answer or not isinstance(answer, str):
        return True
    if any(phrase in answer.lower() for phrase in [
        "keine daten", "nicht verfügbar", "unbekannt", "weiß ich nicht"
    ]):
        return True
    if any(kw in user_input.lower() for kw in ["wie viel", "umsatz", "gewinn", "aktuell", "zahlen", "betrag", "revenue"]):
        if not re.search(r"\d{4}|\d+[\.,]?\d*", answer):
            return True
    return len(answer.strip()) < 10

def adjust_temporal_phrasing(user_input: str) -> str:
    from datetime import datetime
    aktuelles_jahr = datetime.now().year
    import re
    match = re.search(r"(?:umsatz|gewinn|cash)[^0-9]*(\d{4})", user_input.lower())
    if match:
        jahr = int(match.group(1))
        if jahr < aktuelles_jahr:
            return f"{user_input} (Hinweis: Wir sind im Jahr {aktuelles_jahr}, die Zahlen für {jahr} sollten veröffentlicht sein.)"
    return user_input

def log_to_file(user_input, answer, source):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insuff_flag = "❗" if is_insufficient(answer, user_input) else "✅"
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n⏰ {timestamp}\n{insuff_flag} Frage: {user_input}\nAntwort: {answer}\nQuelle: {source}\n")
        f.write("-" * 60 + "\n")

# === Nur bei direktem Aufruf (nicht beim Import) ===
if __name__ == "__main__":
    print("\nSupervisor ist bereit. Gib eine Frage ein (oder 'exit' zum Beenden):")
    history = []

    while True:
        user_input = input("\nFrage: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break

        if is_smalltalk(user_input):
            general_chat_tool = tools[0]
            answer_text = general_chat_tool.run(user_input)
            source = "RAG-Agent (general_chat)"
        else:
            try:
                rag_result = rag_agent.invoke({"input": user_input, "history": history})
                answer_text = rag_result.get("output") if isinstance(rag_result, dict) else str(rag_result)
                source = "RAG-Agent"

                # NEU: Wenn Antwort leer, None oder zu kurz → Web-Agent nutzen
                if not answer_text or not isinstance(answer_text, str) or len(answer_text.strip()) < 5:
                    print("\n[Hinweis] RAG-Agent hat keine Antwort geliefert → Web-Agent wird verwendet...")
                    answer_text, source = ask_question_and_save_answer(user_input)
                elif is_insufficient(answer_text, user_input):
                    print("\n[Hinweis] RAG-Antwort unvollständig → Web-Agent wird verwendet...")
                    answer_text, source = ask_question_and_save_answer(user_input)

            except Exception as e:
                print("\n[Fehler] RAG-Agent fehlgeschlagen → Web-Agent wird verwendet...")
                answer_text, source = ask_question_and_save_answer(user_input)

        print("\nAntwort:")
        print(answer_text)
        print(f"Quelle: {source}")
        # Nach Ausgabe prüfen, ob eine Zahl in der finalen Antwort ist (egal ob von RAG oder Web-Agent)
        zahlen_keywords = ["wie viel", "umsatz", "gewinn", "aktuell", "zahlen", "betrag", "revenue"]
        if any(kw in user_input.lower() for kw in zahlen_keywords):
            if not re.search(r"\d{4}|\d+[\.,]?\d*", answer_text):
                print("\n⚠️ Es konnten keine aktuellen Umsatzzahlen gefunden werden. Bitte prüfe die offiziellen Finanzberichte oder die Investor Relations Seite des Unternehmens.")
        warnings = qa_ethics_agent.run(answer_text, [source])
        print("\n⚖️ QA/Ethik-Prüfung:")
        print(warnings)

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": answer_text})

# Export für Gradio-Zugriff 
__all__ = [
    "rag_agent", "tools", "ask_question_and_save_answer",
    "qa_ethics_agent", "is_smalltalk", "is_insufficient",
    "adjust_temporal_phrasing", "log_to_file"
]

