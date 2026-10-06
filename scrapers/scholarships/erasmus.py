import os
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scrapers.base import BaseSpider

DAILY_LIMIT = 5
BASE_URL = "https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

class ErasmusSpider(BaseSpider):

    def _get_history_path(self):
        """Locates history.json in root regardless of execution context."""
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        return os.path.join(root_dir, "history.json")

    def _load_history(self):
        """Reads previously dispatched URLs from the central history.json."""
        history_path = self._get_history_path()
        if not os.path.exists(history_path):
            return set()

        try:
            with open(history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
                elif isinstance(data, dict):
                    if "links" in data and isinstance(data["links"], list):
                        return set(data["links"])
                    return set(data.keys())
        except Exception as e:
            print(f"[!] Warning reading history.json: {e}")
            return set()
        return set()

    def scrape(self):
        print(f"[*] Crawling live EU portal for up to {DAILY_LIMIT} unposted programmes...")
        history = self._load_history()
        today_str = datetime.now().strftime("%Y-%m-%d")

        results = []
        seen_in_run = set()

        # Catalogue spans pages 0 to 11 (20 programmes per page)
        for page in range(12):
            if len(results) >= DAILY_LIMIT:
                break

            url = f"{BASE_URL}?page={page}"
            html = None

            # BaseSpider fetch fallback
            if hasattr(self, "fetch_html"):
                try:
                    html = self.fetch_html(url)
                except Exception:
                    html = None

            if not html:
                try:
                    resp = requests.get(url, headers=HEADERS, timeout=20)
                    if resp.status_code == 200:
                        html = resp.text
                except Exception as e:
                    print(f"[-] Error fetching page {page}: {e}")
                    continue

            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            tags = soup.find_all("a")

            for tag in tags:
                href = tag.get("href", "").strip()
                title = tag.text.strip().replace("\n", " ")

                # Match external consortium URLs, skip internal EU navigation
                if href.startswith("http") and "europa.eu" not in href and len(title) > 10:
                    if href not in history and href not in seen_in_run:
                        seen_in_run.add(href)

                        # Enforce the 10-field contract
                        results.append({
                            "title": title,
                            "country": "European Union (Multi-Country)",
                            "organization": "European Commission / Partner Universities",
                            "degree_level": "Masters (Joint Degree)",
                            "funding_type": "Fully Funded (Tuition + €1,400/month + Travel)",
                            "eligibility": "Graduates & Final-Year Students Worldwide",
                            "deadline": "Opens Oct - Jan (Varies per program)",
                            "link": href,
                            "requirements": "Transcripts, CV, Motivation Letter, 2 References",
                            "date_posted": today_str,
                            "source": "Erasmus Mundus"
                        })

                        if len(results) == DAILY_LIMIT:
                            break

            time.sleep(1)  # Polite crawling delay between pages

        if not results:
            print(f"[✓] All available programmes on the EU portal are already logged in history.json ({len(history)} total).")
            print("[✓] Zero new programmes found. Waiting for official catalogue updates.")
            return []

        print(f"[+] Erasmus Spider selected {len(results)} unposted programmes for dispatch.")
        return results

def get_spider():
    return ErasmusSpider()
