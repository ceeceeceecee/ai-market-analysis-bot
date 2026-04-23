"""Market Analyzer — KI-gestützte Artikelanalyse

Zusammenfassung, Sentimentanalyse, Keyword-Extraktion und
Insight-Generierung mit Claude oder Gemini.
"""

import json
import logging
import os
import time
from typing import Optional

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """KI-gestützte Analyse von Marktartikeln."""

    MAX_RETRIES = 3
    RETRY_DELAY = 2

    def __init__(self, provider: str = "claude"):
        """
        Args:
            provider: 'claude' oder 'gemini'
        """
        self.provider = provider
        self._client = None

    def _get_client(self):
        """Initialisiert den KI-Client."""
        if self._client is not None:
            return self._client

        if self.provider == "claude":
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY nicht gesetzt.")
            self._client = anthropic.Anthropic(api_key=api_key)

        elif self.provider == "gemini":
            import google.generativeai as genai
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY nicht gesetzt.")
            genai.configure(api_key=api_key)
            self._client = genai.GenerativeModel("gemini-pro")

        else:
            raise ValueError(f"Unbekannter Anbieter: {self.provider}")

        return self._client

    def _call_ai(self, prompt: str, text: str) -> str:
        """Ruft die KI-API mit Retry-Logik auf."""
        client = self._get_client()

        last_error = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                if self.provider == "claude":
                    response = client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=1024,
                        messages=[
                            {"role": "user", "content": f"{prompt}\n\n---\n\n{text}"}
                        ],
                    )
                    return response.content[0].text

                elif self.provider == "gemini":
                    response = client.generate_content(f"{prompt}\n\n---\n\n{text}")
                    return response.text

            except Exception as e:
                last_error = e
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * attempt)
                    logger.warning(f"KI-Aufruf fehlgeschlagen (Versuch {attempt}/{self.MAX_RETRIES}): {e}")

        raise RuntimeError(f"KI-Analyse fehlgeschlagen nach {self.MAX_RETRIES} Versuchen: {last_error}")

    def summarize_article(self, title: str, text: str) -> str:
        """Fasst einen Artikel zusammen.

        Args:
            title: Artikel-Titel
            text: Artikel-Text

        Returns:
            Zusammenfassung auf Deutsch
        """
        prompt = f"""Du bist ein deutscher Marktanalyst. Fasse den folgenden Artikel in 2-3 Sätzen auf Deutsch zusammen.
Fokussiere auf die wichtigsten Aussagen und handlungsrelevante Informationen.

Titel: {title}

Zusammenfassung:"""

        return self._call_ai(prompt, text)

    def analyze_sentiment(self, title: str, text: str) -> dict:
        """Analysiert die Stimmung eines Artikels.

        Returns:
            Dictionary mit sentiment, score und begründung
        """
        prompt = """Analysiere die Stimmung (Sentiment) des folgenden Artikels.
Antworte AUSSCHLIESSLICH als JSON-Objekt mit folgenden Feldern:
- sentiment: "positiv", "negativ" oder "neutral"
- score: Zahl von -1.0 (sehr negativ) bis 1.0 (sehr positiv)
- begruendung: Ein Satz auf Deutsch der die Stimmung erklärt"""

        raw = self._call_ai(prompt, f"Titel: {title}\n\n{text}")
        try:
            json_match = raw[raw.find("{"):raw.rfind("}") + 1]
            return json.loads(json_match)
        except (json.JSONDecodeError, ValueError):
            return {"sentiment": "neutral", "score": 0.0, "begruendung": "Konnte nicht analysieren"}

    def extract_keywords(self, title: str, text: str) -> list[str]:
        """Extrahiert Schlüsselwörter aus einem Artikel.

        Returns:
            Liste von Schlüsselwörtern
        """
        prompt = """Extrahiere die 5 wichtigsten Schlüsselwörter aus dem folgenden Artikel.
Antworte AUSSCHLIESSLICH als JSON-Array von Strings.
Beispiel: ["KI", "Automobil", "Investition"]"""

        raw = self._call_ai(prompt, f"Titel: {title}\n\n{text}")
        try:
            json_match = raw[raw.find("["):raw.rfind("]") + 1]
            return json.loads(json_match)
        except (json.JSONDecodeError, ValueError):
            return []

    def generate_insights(self, articles: list[dict]) -> str:
        """Generiert eine übergeordnete Marktanalyse aus mehreren Artikeln.

        Args:
            articles: Liste von analysierten Artikeln

        Returns:
            Insights als Text auf Deutsch
        """
        articles_text = ""
        for i, article in enumerate(articles[:20], 1):
            articles_text += f"{i}. {article.get('title', 'Ohne Titel')} — {article.get('summary', '')[:200]}\n"

        prompt = """Du bist ein deutscher Marktanalyst. Basierend auf den folgenden Artikeln erstelle eine übergeordnete Marktanalyse (max 300 Wörter auf Deutsch):
- Wichtigste Trends (Top 3)
- Gemeinsame Themen
- Handlungsempfehlungen

Artikel:"""

        return self._call_ai(prompt, articles_text)

    def analyze_article(self, article: dict) -> dict:
        """Führt alle Analysen für einen Artikel durch.

        Args:
            article: Artikel-Dictionary

        Returns:
            Erweitertes Artikel-Dictionary mit Analysen
        """
        title = article.get("title", "")
        text = article.get("summary", "") or article.get("full_text", "")

        if not text.strip():
            article["ai_summary"] = "Kein Text zur Analyse verfügbar."
            article["sentiment"] = {"sentiment": "neutral", "score": 0.0, "begruendung": "Kein Text"}
            article["keywords"] = []
            return article

        try:
            article["ai_summary"] = self.summarize_article(title, text)
        except Exception as e:
            logger.error(f"Zusammenfassung fehlgeschlagen: {e}")
            article["ai_summary"] = "Zusammenfassung fehlgeschlagen."

        try:
            article["sentiment"] = self.analyze_sentiment(title, text)
        except Exception as e:
            logger.error(f"Sentimentanalyse fehlgeschlagen: {e}")
            article["sentiment"] = {"sentiment": "neutral", "score": 0.0, "begruendung": "Fehler"}

        try:
            article["keywords"] = self.extract_keywords(title, text)
        except Exception as e:
            logger.error(f"Keyword-Extraktion fehlgeschlagen: {e}")
            article["keywords"] = []

        return article
