# # import os
# # import re
# # from datetime import datetime
# # from dotenv import load_dotenv
# # from langchain_google_genai import ChatGoogleGenerativeAI
# # from rag_agnet_ganzneu import create_agent, setup_tools, load_existing_vectorstore
# # from web_such_agent import research_agent, ask_question_and_save_answer
# # from qa_ethics_agent import qa_ethics_agent
# # from langgraph_supervisor import create_supervisor
# # from data_analysis_agent import agent as data_analysis_agent

# # # === ENV laden ===
# # load_dotenv()

# # # === LLM initialisieren ===
# # llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# # # === RAG-Agent vorbereiten ===
# # vectorstore = load_existing_vectorstore()
# # tools = setup_tools(vectorstore)
# # rag_agent = create_agent(tools)

# # # === Supervisor ===
# # supervisor = create_supervisor(
# #     model=llm,
# #     agents=[rag_agent, research_agent],
# #     prompt=(
# #         "You are a supervisor managing two agents:\n"
# #         "- 'rag_agent': Handles document-based and structured data questions.\n"
# #         "- 'research_agent': Handles real-time web search questions.\n"
# #         "Always assign one task to one agent. Never do the work yourself.\n"
# #         "If an agent provides incomplete answers (no numbers or vague), assign to the other agent.\n"
# #     ),
# #     add_handoff_back_messages=True,
# #     output_mode="full_history",
# # ).compile()

# # # === Smalltalk ===
# # smalltalk_keywords = ["hallo", "hi", "wie geht", "servus", "wer bist", "was kannst"]
# # def is_smalltalk(question: str) -> bool:
# #     return any(kw in question.lower() for kw in smalltalk_keywords)

# # # === Intelligente Antwortprüfung ===
# # def is_insufficient(answer: str, user_input: str = "") -> bool:
# #     if not answer or not isinstance(answer, str) or len(answer.strip()) < 10:
# #         return True
# #     ausweich = [
# #         "keine daten", "nicht verfügbar", "weiß ich nicht", "unbekannt",
# #         "nicht gefunden", "nicht bekannt", "keine information", 
# #         "ich konnte keine information", "nicht enthalten", "nicht zugänglich",
# #         "werden voraussichtlich", "werden später veröffentlicht",
# #         "noch nicht veröffentlicht", "noch nicht bekannt", 
# #         "ich kann keine auskunft geben", "keine aktuellen zahlen"
# #     ]
# #     if any(phrase in answer.lower() for phrase in ausweich):
# #         return True
# #     if any(kw in user_input.lower() for kw in ["wie viel", "umsatz", "gewinn", "einnahmen", "zahlen", "betrag", "revenue", "cash"]):
# #         if not re.search(r"\d{4}|\d+[\.,]?\d*", answer):
# #             return True
# #     return False

# # # === Zeitliche Logik bei Jahrfragen ===
# # def adjust_temporal_phrasing(user_input: str) -> str:
# #     aktuelles_jahr = datetime.now().year
# #     match = re.search(r"(?:umsatz|gewinn|cash)[^0-9]*(\d{4})", user_input.lower())
# #     if match:
# #         jahr = int(match.group(1))
# #         if jahr < aktuelles_jahr:
# #             return f"{user_input} (Hinweis: Wir sind im Jahr {aktuelles_jahr}, die Zahlen für {jahr} sollten veröffentlicht sein.)"
# #     return user_input

# # # === Logging mit Markierung ===
# # def log_to_file(user_input, answer, source):
# #     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #     insuff_flag = "❗" if is_insufficient(answer, user_input) else "✅"
# #     with open("chat_log.txt", "a", encoding="utf-8") as f:
# #         f.write(f"\n⏰ {timestamp}\n{insuff_flag} Frage: {user_input}\nAntwort: {answer}\nQuelle: {source}\n")
# #         f.write("-" * 60 + "\n")

# # # === CLI-Loop ===
# # if __name__ == "__main__":
# #     print("📊 Intelligenter Supervisor aktiv. Gib eine Frage ein (oder 'exit'):")
# #     history = []

# #     while True:
# #         user_input = input("\nFrage: ").strip()
# #         if user_input.lower() in ["exit", "quit"]:
# #             break

# #         adjusted_input = adjust_temporal_phrasing(user_input)

# #         if is_smalltalk(user_input):
# #             general_chat_tool = tools[0]
# #             answer = general_chat_tool.run(user_input)
# #             source = "RAG-Agent (general_chat)"
# #         else:
# #             try:
# #                 rag_result = rag_agent.invoke({"input": adjusted_input, "history": history})
# #                 answer = rag_result.get("output") if isinstance(rag_result, dict) else str(rag_result)
# #                 source = "RAG-Agent"

# #                 if is_insufficient(answer, adjusted_input):
# #                     print("[⚠️] RAG-Antwort unzureichend → Web-Agent wird verwendet...")
# #                     answer, source = ask_question_and_save_answer(user_input)

# #             except Exception:
# #                 print("[❌] RAG-Agent fehlgeschlagen → Web-Agent wird verwendet...")
# #                 answer, source = ask_question_and_save_answer(user_input)

# #         qa_result = qa_ethics_agent.run(answer, [source])
# #         print(f"\n✅ Antwort:\n{answer}\n📚 Quelle: {source}\n⚖️ QA/Ethikprüfung: {qa_result}")

# #         history.append({"role": "user", "content": user_input})
# #         history.append({"role": "assistant", "content": answer})

# #         log_to_file(user_input, answer, source)
# import gradio as gr
# from supervisor_main import (
#     rag_agent, tools, ask_question_and_save_answer,
#     qa_ethics_agent, is_smalltalk, is_insufficient,
#     adjust_temporal_phrasing, log_to_file
# )
# from data_analysis_agent import agent as data_analysis_agent

# history = []

# def chat_supervisor(message, chat_history):
#     global history
#     user_input = message.strip()
#     adjusted_input = adjust_temporal_phrasing(user_input)
#     history.append({"role": "user", "content": user_input})

#     # Routing für Data-Analysis-Agent
#     analysis_keywords = [
#         "analysiere", "analyse", "plot", "diagramm", "visualisiere", "statistik", "vergleich", "vergleiche", "csv", "datenanalyse", "korrelation", "trend", "zeitreihe", "daten", "tabelle"
#     ]
#     if any(kw in user_input.lower() for kw in analysis_keywords):
#         try:
#             answer = data_analysis_agent.run(user_input)
#             source = "Data-Analysis-Agent"
#         except Exception as e:
#             answer = f"Fehler beim Data-Analysis-Agent: {e}"
#             source = "Data-Analysis-Agent"
#     elif is_smalltalk(user_input):
#         general_chat_tool = tools[0]
#         answer = general_chat_tool.run(user_input)
#         source = "RAG-Agent (general_chat)"
#     else:
#         try:
#             result = rag_agent.invoke({"input": adjusted_input, "history": history})
#             answer = result.get("output") if isinstance(result, dict) else str(result)
#             source = "RAG-Agent"

#             if is_insufficient(answer, adjusted_input):
#                 answer, source = ask_question_and_save_answer(user_input)

#         except Exception:
#             answer, source = ask_question_and_save_answer(user_input)

#     history.append({"role": "assistant", "content": answer})
#     qa = qa_ethics_agent.run(answer, [source])

#     annotated = f"{answer}\n\n📚 Quelle: {source}\n⚖️ QA/Ethikprüfung: {qa}"
#     log_to_file(user_input, answer, source)
#     return annotated

# demo = gr.ChatInterface(
#     fn=chat_supervisor,
#     title="📊 Supervisor Multi-Agent",
#     description="Frage mich zu Umsatz, Firmen, Echtzeit & Ethik – kombiniert RAG + Web + QA.",
#     chatbot=gr.Chatbot(height=500),
#     textbox=gr.Textbox(placeholder="Deine Frage...", label="Frage"),
# )

# if __name__ == "__main__":
#     demo.launch()
import gradio as gr
import os
import re
from pathlib import Path
from datetime import datetime

from supervisor_main import (
    rag_agent, tools, ask_question_and_save_answer,
    qa_ethics_agent, is_smalltalk, is_insufficient,
    adjust_temporal_phrasing, log_to_file
)
from data_analysis_agent import agent as data_analysis_agent


history = []

# === Funktion: Erkenne Analyseaufträge ===
def is_data_analysis_request(user_input: str) -> bool:
    chart_keywords = [
        "analysiere", "analyse", "plot", "diagramm", "visualisiere",
        "statistik", "vergleich", "vergleiche", "csv", "datenanalyse",
        "korrelation", "trend", "zeitreihe", "daten", "tabelle"
    ]
    finance_keywords = [
        "umsatz", "gewinn", "einnahmen", "ausgaben", "cash", "kapital",
        "verbindlichkeit", "kosten", "aktien", "bilanz", "umsätze"
    ]
    return any(a in user_input.lower() for a in chart_keywords) and any(f in user_input.lower() for f in finance_keywords)


# === Neu: Suche nach neuestem Diagramm im Ordner ===
def get_latest_figure():
    figures_path = Path("figures")
    if not figures_path.exists():
        return None
    figures = list(figures_path.glob("*.png"))
    return str(max(figures, key=os.path.getctime)) if figures else None


# === Hauptlogik ===
def chat_supervisor(message, chat_history):
    global history
    user_input = message.strip()
    adjusted_input = adjust_temporal_phrasing(user_input)
    history.append({"role": "user", "content": user_input})

    image_path = None

    if is_data_analysis_request(user_input):
        try:
            answer = data_analysis_agent.run(user_input)
            source = "Data-Analysis-Agent"
            image_path = get_latest_figure()
        except Exception as e:
            answer = f"Fehler beim Data-Analysis-Agent: {e}"
            source = "Data-Analysis-Agent"

    elif is_smalltalk(user_input):
        general_chat_tool = tools[0]
        answer = general_chat_tool.run(user_input)
        source = "RAG-Agent (general_chat)"

    else:
        try:
            result = rag_agent.invoke({"input": adjusted_input, "history": history})
            answer = result.get("output") if isinstance(result, dict) else str(result)
            source = "RAG-Agent"

            if is_insufficient(answer, adjusted_input):
                answer, source = ask_question_and_save_answer(user_input)

        except Exception:
            answer, source = ask_question_and_save_answer(user_input)

    history.append({"role": "assistant", "content": answer})
    qa = qa_ethics_agent.run(answer, [source])
    annotated = f"{answer}\n\n📚 Quelle: {source}\n⚖️ QA/Ethikprüfung: {qa}"
    log_to_file(user_input, answer, source)

    return (annotated, image_path)


# === Gradio UI ===
demo = gr.ChatInterface(
    fn=chat_supervisor,
    title="📊 Supervisor Multi-Agent Chat",
    description="Kombinierte KI mit RAG + Websuche + Statistik + QA. Stelle Fragen zu Umsatz, Firmen, Trends & mehr.",
    chatbot=gr.Chatbot(height=500),
    textbox=gr.Textbox(placeholder="Frage z.B. 'Zeige Apple Umsatz als Diagramm'", label="Frage"),
    additional_outputs=[gr.Image(label="📈 Diagramm", visible=True)]
)


if __name__ == "__main__":
    demo.launch()

