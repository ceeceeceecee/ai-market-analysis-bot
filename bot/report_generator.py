"""Report Generator — HTML-Marktberichte

Erstellt professionelle HTML-Reports mit Jinja2-Templates.
Unterstützt Sentiment-Farbcodierung und Kategorie-Gruppierung.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generiert HTML-Marktberichte aus analysierten Artikeln."""

    def __init__(self, template_dir: Optional[str] = None):
        """
        Args:
            template_dir: Pfad zum Template-Verzeichnis
        """
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
        )

    def _sentiment_color(self, sentiment: str) -> str:
        """Gibt eine CSS-Farbe für das Sentiment zurück."""
        colors = {
            "positiv": "#22c55e",
            "negativ": "#ef4444",
            "neutral": "#94a3b8",
        }
        return colors.get(sentiment.lower(), "#94a3b8")

    def _sentiment_emoji(self, sentiment: str) -> str:
        """Gibt ein Emoji für das Sentiment zurück."""
        emojis = {
            "positiv": "📈",
            "negativ": "📉",
            "neutral": "➡️",
        }
        return emojis.get(sentiment.lower(), "➡️")

    def _group_by_category(self, articles: list[dict]) -> dict[str, list[dict]]:
        """Gruppiert Artikel nach Kategorie."""
        groups = {}
        for article in articles:
            cat = article.get("category", "Allgemein")
            if cat not in groups:
                groups[cat] = []
            groups[cat].append(article)
        return groups

    def create_html_report(
        self,
        articles: list[dict],
        insights: str = "",
        title: str = "Marktanalyse Report",
    ) -> str:
        """Erstellt einen HTML-Report.

        Args:
            articles: Liste der analysierten Artikel
            insights: Übergeordnete Markt-Insights
            title: Report-Titel

        Returns:
            HTML-String

        Raises:
            TemplateNotFound: Wenn das Template nicht gefunden wird
        """
        try:
            template = self.env.get_template("report.html.j2")
        except TemplateNotFound:
            logger.warning("Template nicht gefunden, verwende integriertes Template")
            return self._create_fallback_report(articles, insights, title)

        # Artikel nach Kategorie gruppieren
        categories = self._group_by_category(articles)

        # Statistiken
        total = len(articles)
        sentiments = {"positiv": 0, "negativ": 0, "neutral": 0}
        for article in articles:
            sent = article.get("sentiment", {}).get("sentiment", "neutral").lower()
            sentiments[sent] = sentiments.get(sent, 0) + 1

        # Alle Keywords sammeln
        all_keywords = []
        for article in articles:
            all_keywords.extend(article.get("keywords", []))

        # Template rendern
        html = template.render(
            title=title,
            date=datetime.now().strftime("%d.%m.%Y %H:%M"),
            articles=articles,
            categories=categories,
            insights=insights,
            total=total,
            sentiments=sentiments,
            keywords=all_keywords[:20],
            sentiment_color=self._sentiment_color,
            sentiment_emoji=self._sentiment_emoji,
        )

        return html

    def save_report(self, html: str, output_path: str) -> str:
        """Speichert den Report als HTML-Datei.

        Args:
            html: HTML-Content
            output_path: Ausgabedatei-Pfad

        Returns:
            Absoluter Pfad zur gespeicherten Datei
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        logger.info(f"Report gespeichert: {path.absolute()}")
        return str(path.absolute())

    def _create_fallback_report(self, articles: list[dict], insights: str, title: str) -> str:
        """Integriertes Fallback-Template wenn Jinja2-Template fehlt."""
        rows = ""
        for article in articles:
            sent = article.get("sentiment", {})
            color = self._sentiment_color(sent.get("sentiment", "neutral"))
            rows += f"""
            <tr>
                <td>{article.get('title', 'Ohne Titel')}</td>
                <td>{article.get('source', '')}</td>
                <td>{article.get('category', '')}</td>
                <td style="color:{color}">{sent.get('sentiment', 'neutral')}</td>
                <td>{article.get('ai_summary', '')[:200]}</td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><title>{title}</title>
<style>body{{font-family:sans-serif;margin:40px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px;text-align:left}}th{{background:#1e293b;color:white}}</style>
</head><body>
<h1>{title}</h1><p>Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
<table><tr><th>Titel</th><th>Quelle</th><th>Kategorie</th><th>Sentiment</th><th>Zusammenfassung</th></tr>{rows}</table>
{f'<h2>Insights</h2><p>{insights}</p>' if insights else ''}
</body></html>"""
