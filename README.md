# AI Market Analysis Bot

> Automatische Marktberichte mit KI — RSS/Web-Quellen überwachen, analysieren und als HTML/PDF-Report generieren
> Python bot that monitors RSS feeds & websites, analyzes with AI, generates structured HTML/PDF reports

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg) ![Python](https://img.shields.io/badge/Python-3.11+-green.svg) ![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

## Features

- **RSS-Feed Überwachung** — Konfigurierbare RSS-Quellen (heise.de, t3n.de, etc.)
- **Web-Scraping** — Artikel von Webseiten mit BeautifulSoup extrahieren
- **KI-Zusammenfassung** — Claude oder Gemini fasst Artikel zusammen
- **Sentimentanalyse** — Stimmung der Artikel automatisch bewerten
- **HTML-Report** — Professioneller, responsiver, druckfreundlicher Report
- **Cron / n8n** — Automatische Ausführung über Cron oder n8n Workflow
- **Konfigurierbare Quellen** — Eigene Quellen über YAML hinzufügen
- **Rate-Limiting** — Respektiert robots.txt und Quellen-Ratenlimits

## Schnellstart

```bash
git clone https://github.com/ceeceeceecee/ai-market-analysis-bot.git
cd ai-market-analysis-bot

# Abhängigkeiten installieren
pip install -r requirements.txt

# Konfiguration anpassen
cp config/sources.example.yaml config/sources.yaml
cp config/settings.example.yaml config/settings.yaml

# Bot ausführen
python main.py --config config/settings.yaml --output output/report.html

# Oder mit Docker
docker-compose up
```

## Projektstruktur

```
ai-market-analysis-bot/
  main.py                     # Orchestrierung & CLI
  bot/
    scraper.py                # RSS/Web Scraper
    analyzer.py               # KI-Analyse (Claude/Gemini)
    report_generator.py       # HTML-Report Generator
  config/
    sources.example.yaml      # Nachrichtenquellen
    settings.example.yaml     # Bot-Konfiguration
  templates/
    report.html.j2            # Jinja2 HTML-Template
  docs/
    setup-guide.md            # Einrichtungsanleitung
```

## Lizenz

MIT — siehe [LICENSE](LICENSE)
