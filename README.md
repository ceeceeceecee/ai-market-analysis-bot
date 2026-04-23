# AI Market Analysis Bot

[![Python](https://img.shields.io/badge/python-3.11+-green?logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker)](https://www.docker.com)
[![Claude](https://img.shields.io/badge/Claude-supported-9945FF?logo=anthropic)](https://anthropic.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

> RSS/Web-Quellen überwachen, mit KI analysieren und als professioneller HTML/PDF-Report generieren.

Monitor RSS feeds & websites, analyze with AI, generate professional HTML/PDF reports.

---

## Screenshot

![Sample Report](screenshots/sample-report.png)
*Automatisch generierter Wochenbericht: Artikel, Sentiment-Analyse, Keywords & KI-Trend-Empfehlungen.*

---

## Features

| Feature | Beschreibung |
|---------|-------------|
| RSS-Feed Überwachung | Konfigurierbare Quellen (heise, t3n, etc.) |
| Web-Scraping | Artikel mit BeautifulSoup extrahieren |
| KI-Zusammenfassung | Claude oder Gemini fasst Artikel zusammen |
| Sentimentanalyse | Stimmung automatisch bewerten (Positiv/Neutral/Negativ) |
| HTML-Report | Professionell, responsiv, druckfreundlich |
| Cron / n8n | Automatische Ausführung |
| Konfigurierbare Quellen | Eigene Quellen über YAML hinzufügen |
| Rate-Limiting | Respektiert robots.txt & Quellen-Limits |

---

## Quick Start

```bash
git clone https://github.com/ceeceeceecee/ai-market-analysis-bot.git
cd ai-market-analysis-bot

# Abhängigkeiten
pip install -r requirements.txt

# Konfiguration
cp config/sources.example.yaml config/sources.yaml
cp config/settings.example.yaml config/settings.yaml

# Bot ausführen
python main.py --config config/settings.yaml --output output/report.html

# Oder mit Docker
docker compose up
```

### Voraussetzungen

- Python 3.11+
- Claude oder Gemini API Key
- (Optional) n8n für Automatisierung

---

## Projektstruktur

```
ai-market-analysis-bot/
├── main.py                     # Orchestrierung & CLI
├── bot/
│   ├── scraper.py              # RSS/Web Scraper
│   ├── analyzer.py             # KI-Analyse (Claude/Gemini)
│   └── report_generator.py     # HTML-Report Generator
├── config/
│   ├── sources.example.yaml    # Nachrichtenquellen
│   └── settings.example.yaml   # Bot-Konfiguration
├── templates/
│   └── report.html.j2          # Jinja2 HTML-Template
├── docker-compose.yml
└── docs/
    └── setup-guide.md          # Einrichtungsanleitung
```

---

## Use Cases

| Zielgruppe | Szenario |
|------------|----------|
| KMU | Wettbewerbs- & Markttrends verfolgen |
| Agenturen | Kunden-Reports automatisiert erstellen |
| Freelancer | Branchen-News auf dem Laufenden halten |
| Investoren | Sentiment-Analyse für Entscheidungen |

---

## Tech Stack

- **Python** — Core-Logic
- **BeautifulSoup** — Web-Scraping
- **feedparser** — RSS-Feed Parsing
- **Claude / Gemini** — KI-Analyse & Zusammenfassung
- **Jinja2** — HTML-Template-Engine
- **Docker** — Container-Deployment

---

## Roadmap

- [ ] PDF-Export
- [ ] Multi-Sprachen (EN/FR)
- [ ] Telegram/Discord Bot Integration
- [ ] Dashboard mit Historie

---

## Contributing

1. Fork → Feature-Branch → Commit → Push → Pull Request

---

## Lizenz

[MIT](LICENSE) — frei nutzbar.

## Author

[ceeceeceecee](https://github.com/ceeceeceecee)

## Weitere Projekte

- [AI Document Analyzer](https://github.com/ceeceeceecee/ai-document-analyzer) — Dokumentenanalyse
- [n8n Business Automation](https://github.com/ceeceeceecee/n8n-business-automation) — n8n Integration
