"""AI Market Analysis Bot — Hauptmodul

Orchestriert das Sammeln, Analysieren und Berichten von Marktartikeln.
"""

import argparse
import logging
import sys
from pathlib import Path

import yaml

from bot.scraper import MarketScraper
from bot.analyzer import MarketAnalyzer
from bot.report_generator import ReportGenerator


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Konfiguriert das Logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


def load_yaml(path: str) -> dict:
    """Lädt eine YAML-Datei."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logging.error(f"Konfigurationsdatei nicht gefunden: {path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.error(f"Fehler beim Parsen der YAML-Datei {path}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="AI Market Analysis Bot — Automatische Marktberichte mit KI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Report generieren (Standard)
  python main.py --config config/settings.yaml

  # Eigenen Ausgabepfad
  python main.py --output /pfad/zum/report.html

  # Nur Artikel sammeln (ohne KI-Analyse)
  python main.py --scrape-only

  # Verbose-Modus
  python main.py -v --config config/settings.yaml
        """,
    )

    parser.add_argument("--config", "-c", type=str, default="config/settings.yaml", help="Pfad zur Konfigurationsdatei")
    parser.add_argument("--output", "-o", type=str, default="output/report.html", help="Ausgabedatei für den Report")
    parser.add_argument("--format", "-f", type=str, choices=["html", "pdf"], default="html", help="Ausgabeformat")
    parser.add_argument("--scrape-only", action="store_true", help="Nur Artikel sammeln, keine KI-Analyse")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose-Logging")

    args = parser.parse_args()
    logger = setup_logging(args.verbose)

    # Konfiguration laden
    settings = load_yaml(args.config)
    sources_file = settings.get("sources_file", "config/sources.yaml")
    sources = load_yaml(sources_file).get("sources", [])

    if not sources:
        logger.warning("Keine Quellen konfiguriert. Verwende Beispielquellen.")
        sources = [
            {"type": "rss", "url": "https://www.heise.de/rss/heise-atom.xml", "category": "Tech"},
            {"type": "rss", "url": "https://t3n.de/rss", "category": "KI"},
        ]

    logger.info(f"Starte Market Analysis Bot mit {len(sources)} Quellen...")

    # Schritt 1: Artikel sammeln
    logger.info("Schritt 1/3: Artikel sammeln...")
    scraper = MarketScraper()
    articles = scraper.get_articles(sources, max_per_source=settings.get("max_articles_per_source", 10))

    if not articles:
        logger.error("Keine Artikel gefunden. Prüfe die Quellenkonfiguration.")
        sys.exit(1)

    logger.info(f"{len(articles)} Artikel gesammelt.")

    if args.scrape_only:
        logger.info("Scrape-Only Modus — keine KI-Analyse. Artikel auf stdout:")
        for i, article in enumerate(articles, 1):
            logger.info(f"  {i}. [{article.get('category', '?')}] {article.get('title', 'Ohne Titel')}")
        sys.exit(0)

    # Schritt 2: KI-Analyse
    logger.info("Schritt 2/3: KI-Analyse...")
    provider = settings.get("ai_provider", "claude")
    analyzer = MarketAnalyzer(provider=provider)

    analyzed_articles = []
    for i, article in enumerate(articles, 1):
        logger.info(f"Analysiere Artikel {i}/{len(articles)}: {article.get('title', '?')[:50]}...")
        try:
            analyzed = analyzer.analyze_article(article)
            analyzed_articles.append(analyzed)
        except Exception as e:
            logger.error(f"Analyse fehlgeschlagen für Artikel {i}: {e}")
            article["ai_summary"] = f"Analyse fehlgeschlagen: {e}"
            article["sentiment"] = {"sentiment": "neutral", "score": 0.0, "begruendung": "Fehler"}
            article["keywords"] = []
            analyzed_articles.append(article)

    # Schritt 3: Insights generieren
    logger.info("Schritt 3/3: Insights generieren...")
    insights = ""
    try:
        insights = analyzer.generate_insights(analyzed_articles)
    except Exception as e:
        logger.error(f"Insight-Generierung fehlgeschlagen: {e}")

    # Report erstellen
    logger.info("Erstelle Report...")
    generator = ReportGenerator()
    html = generator.create_html_report(
        articles=analyzed_articles,
        insights=insights,
        title=settings.get("report_title", "Marktanalyse Report"),
    )

    # Speichern
    output_path = generator.save_report(html, args.output)
    logger.info(f"Report gespeichert: {output_path}")

    # Optional: PDF erstellen
    if args.format == "pdf":
        try:
            from weasyprint import HTML
            pdf_path = output_path.replace(".html", ".pdf")
            HTML(string=html).write_pdf(pdf_path)
            logger.info(f"PDF gespeichert: {pdf_path}")
        except ImportError:
            logger.error("weasyprint nicht installiert. PDF-Erstellung übersprungen. Installieren mit: pip install weasyprint")
        except Exception as e:
            logger.error(f"PDF-Erstellung fehlgeschlagen: {e}")

    logger.info("Fertig!")


if __name__ == "__main__":
    main()
