# Dummy-Basisklasse, damit der Import funktioniert
class Agent:
    def __init__(self, name=None, instructions=None):
        self.name = name
        self.instructions = instructions

def check_facts_and_ethics(answer, sources):
    # Dummy-Checks: Du kannst hier GPT, OpenAI Moderation API oder eigene Regeln nutzen
    warnings = []
    if not answer or not isinstance(answer, str) or len(answer) == 0:
        warnings.append("⚠️ Keine Antwort erhalten.")
        return warnings
    if not sources or len(sources) == 0:
        warnings.append("⚠️ Keine Quellenangabe gefunden.")
    if "kann ich nicht" in answer.lower() or "unbekannt" in answer.lower():
        warnings.append("⚠️ Antwort ist unvollständig oder unsicher.")
    # Beispiel für Bias-Check (sehr einfach)
    if "immer" in answer.lower() or "nie" in answer.lower():
        warnings.append("⚠️ Möglicher Bias in der Formulierung erkannt.")
    # Hier könntest du weitere Checks einbauen (z.B. OpenAI Moderation API, Fact-Checking, etc.)
    return warnings

class QA_EthicsAgent(Agent):
    def __init__(self):
        super().__init__(
            name="QA & Ethics Reviewer",
            instructions="Prüft Antworten auf Fakten, Quellen, Bias und Ethik."
        )
    def run(self, answer, sources):
        warnings = check_facts_and_ethics(answer, sources)
        if warnings:
            return "\n".join(warnings)
        return "✅ Antwort besteht die QA/Ethik-Prüfung."

qa_ethics_agent = QA_EthicsAgent()