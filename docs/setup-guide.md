# Einrichtungsanleitung — AI Market Analysis Bot

## Voraussetzungen

- Python 3.11 oder neuer
- pip
- Git

## Lokale Installation

### 1. Repository klonen

```bash
git clone https://github.com/ceeceeceecee/ai-market-analysis-bot.git
cd ai-market-analysis-bot
```

### 2. Virtuelle Umgebung erstellen

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 4. Konfigurieren

```bash
cp config/sources.example.yaml config/sources.yaml
cp config/settings.example.yaml config/settings.yaml
cp .env.example .env
```

**Quellen anpassen:** `config/sources.yaml` bearbeiten und gewünschte RSS/Web-Quellen eintragen.

**API-Keys eintragen:** `.env` bearbeiten und Claude oder Gemini API-Key eintragen.

### 5. Bot ausführen

```bash
python main.py --config config/settings.yaml --output output/report.html
```

## Docker-Installation

```bash
cp .env.example .env
# API-Keys eintragen
docker-compose up -d
```

## Automatisierung

### Mit Cron

```bash
# Wochentags um 08:00 Uhr
0 8 * * 1-5 cd /pfad/zum/bot && python main.py --output /pfad/zum/output/report.html
```

### Mit n8n

1. Cron-Node → Schedule: Wochentags 08:00
2. Execute Command Node: `python /pfad/zum/bot/main.py`
3. Optional: E-Mail Node zum Versenden des Reports

## Eigene Quellen hinzufügen

In `config/sources.yaml` neue Einträge hinzufügen:

```yaml
sources:
  - type: rss
    url: "https://deine-quelle.de/rss"
    category: "DeineKategorie"
    name: "Quellenname"

  - type: web
    url: "https://beispiel.de/artikel"
    category: "News"
    name: "Beispielartikel"
```

## Troubleshooting

### "Keine Artikel gefunden"
- Prüfe die RSS-URLs in `sources.yaml`
- Teste Feed im Browser: URL direkt öffnen

### "ANTHROPIC_API_KEY nicht gesetzt"
`.env` Datei erstellen und API-Key eintragen.

### "weasyprint ImportError"
Für PDF-Export: `pip install weasyprint`
Benötigt System-Bibliotheken (siehe Dockerfile).

### Rate-Limiting
Wenn Quellen 429-Fehler zurückgeben, erhöhe `min_delay` im Scraper oder reduziere `max_articles_per_source`.
