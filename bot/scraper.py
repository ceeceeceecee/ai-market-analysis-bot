"""Market Scraper — RSS & Web Scraping

Extrahiert Artikel aus RSS-Feeds und Webseiten.
Respektiert robots.txt und implementiert Rate-Limiting.
"""

import time
import logging
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import feedparser
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class MarketScraper:
    """Scraped Artikel aus RSS-Feeds und Webseiten."""

    def __init__(
        self,
        user_agent: str = "MarketAnalysisBot/1.0 (+https://github.com/ceeceeceecee)",
        min_delay: float = 1.0,
        timeout: int = 15,
    ):
        """
        Args:
            user_agent: User-Agent String für HTTP-Anfragen
            min_delay: Minimale Verzögerung zwischen Anfragen (Sekunden)
            timeout: HTTP-Timeout in Sekunden
        """
        self.user_agent = user_agent
        self.min_delay = min_delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self._last_request_time = 0.0

    def _rate_limit(self):
        """Stellt sicher, dass Anfragen nicht zu schnell hintereinander erfolgen."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self._last_request_time = time.time()

    def _check_robots_txt(self, url: str) -> bool:
        """Prüft robots.txt, ob eine URL gescrapt werden darf.

        Args:
            url: Die zu prüfende URL

        Returns:
            True wenn Scraping erlaubt ist
        """
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            rp = RobotFileParser(robots_url)
            rp.read()
            return rp.can_fetch(self.user_agent, url)
        except Exception as e:
            logger.debug(f"robots.txt konnte nicht geprüft werden für {url}: {e}")
            return True  # Im Zweifel erlauben

    def fetch_rss(self, feed_url: str, max_articles: int = 20) -> list[dict]:
        """Ruft Artikel aus einem RSS-Feed ab.

        Args:
            feed_url: URL des RSS-Feeds
            max_articles: Maximale Anzahl an Artikeln

        Returns:
            Liste von Artikel-Dictionaries
        """
        self._rate_limit()
        logger.info(f"Rufe RSS-Feed ab: {feed_url}")

        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            logger.error(f"Fehler beim Parsen des RSS-Feeds {feed_url}: {e}")
            return []

        if feed.bozo and not feed.entries:
            logger.error(f"RSS-Feed Fehler ({feed_url}): {feed.bozo_exception}")
            return []

        articles = []
        for entry in feed.entries[:max_articles]:
            article = {
                "title": entry.get("title", "Ohne Titel"),
                "url": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "source": feed.feed.get("title", feed_url),
                "category": "rss",
            }

            # Datum parsen
            if entry.get("published_parsed"):
                try:
                    dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    article["published"] = dt.isoformat()
                except (TypeError, ValueError):
                    pass

            articles.append(article)

        logger.info(f"{len(articles)} Artikel aus {feed_url} geladen")
        return articles

    def scrape_page(self, url: str) -> dict:
        """Extrahiert den Inhalt einer Webseite.

        Args:
            url: URL der Webseite

        Returns:
            Artikel-Dictionary oder leeres Dict bei Fehler
        """
        # robots.txt prüfen
        if not self._check_robots_txt(url):
            logger.warning(f"Scraping blockiert durch robots.txt: {url}")
            return {}

        self._rate_limit()
        logger.info(f"Scrape Webseite: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Fehler beim Abrufen von {url}: {e}")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")

        # Titel extrahieren
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        else:
            h1 = soup.find("h1")
            title = h1.get_text(strip=True) if h1 else "Ohne Titel"

        # Hauptinhalt extrahieren (versuche common Article-Tags)
        content = ""
        for selector in ["article", "main", '[role="main"]', ".post-content", ".article-body"]:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(separator="\n", strip=True)
                break

        # Fallback: body-Text
        if not content:
            body = soup.find("body")
            if body:
                # Unnötige Elemente entfernen
                for tag in body.find_all(["script", "style", "nav", "footer", "header", "aside"]):
                    tag.decompose()
                content = body.get_text(separator="\n", strip=True)

        return {
            "title": title,
            "url": url,
            "published": "",
            "summary": content[:1000] if content else "",
            "full_text": content,
            "source": urlparse(url).netloc,
            "category": "web",
        }

    def get_articles(self, sources: list[dict], max_per_source: int = 10) -> list[dict]:
        """Sammelt Artikel aus allen konfigurierten Quellen.

        Args:
            sources: Liste von Quell-Konfigurationen (aus sources.yaml)
            max_per_source: Maximale Artikel pro Quelle

        Returns:
            Liste aller gesammelten Artikel
        """
        all_articles = []

        for source in sources:
            source_type = source.get("type", "rss")
            url = source.get("url", "")

            if not url:
                logger.warning(f"Quelle ohne URL übersprungen: {source}")
                continue

            try:
                if source_type == "rss":
                    articles = self.fetch_rss(url, max_per_source)
                elif source_type == "web":
                    article = self.scrape_page(url)
                    articles = [article] if article else []
                else:
                    logger.warning(f"Unbekannter Quelltyp: {source_type}")
                    continue

                # Kategorie aus Konfiguration übernehmen
                category = source.get("category", "allgemein")
                for article in articles:
                    article["category"] = category

                all_articles.extend(articles)

            except Exception as e:
                logger.error(f"Fehler bei Quelle {url}: {e}")
                continue

        logger.info(f"Insgesamt {len(all_articles)} Artikel gesammelt")
        return all_articles
