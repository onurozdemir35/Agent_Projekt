# 📦 Notwendige Bibliotheken importieren
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from smolagents import InferenceClientModel, CodeAgent
from huggingface_hub import login

# 🔑 HuggingFace-Token laden und anmelden
login(os.getenv("HF_TOKEN"))

# 🧠 LLM-Modell mit Inference API initialisieren
model = InferenceClientModel("meta-llama/Llama-3.1-70B-Instruct")

# 🤖 Agent definieren mit erlaubten Bibliotheken
agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=[
        "numpy",
        "pandas",
        "matplotlib.pyplot",
        "seaborn"
    ]
)

# 📁 Sicherstellen, dass der Ausgabeordner existiert
os.makedirs("figures", exist_ok=True)

# 📓 Zusätzliche Notizen (z.B. Beschreibung der Spalten)
additional_notes = """
### Variablenbeschreibung:
- 'company': Name des Unternehmens
- 'concept': Finanzkennzahl (z.B. Umsatz, Ausgaben, Eigenkapital)
- Spalten im Format '2024-03-31': stellen Quartalsdaten dar
- Diese Datei enthält Finanzergebnisse verschiedener Unternehmen über mehrere Quartale hinweg.
"""

# 📣 Benutzerinteraktion – Eingabeaufforderung
print("🔍 Bitte gib deinen Analyseauftrag ein (z.B. 'Vergleiche die Verbindlichkeiten von Apple und Microsoft im Jahr 2024.'):\n")
user_prompt = input("> ")

# 🏃 Agent ausführen mit Analyseauftrag
antwort = agent.run(
    user_prompt,
    additional_args={
        "source_file": "all_company_financials.csv",
        "additional_notes": additional_notes
    }
)

# 🖨 Ergebnis anzeigen
print("\n📊 Analyseergebnis:\n")
print(antwort)