import os
import json
import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime

from scrapers.base import BaseSpider

# Disable SSL warnings for Nigerian Govt websites with expired/self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DAILY_LIMIT = 3
PTDF_NEWS_URL = "https://scholarship.ptdf.gov.ng/news/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

class PTDFSpider(BaseSpider):
    """
    Spider for the Nigerian PTDF Scholarship announcements.
    Monitors the official PTDF scholarship news portal for LSS (In-Country) and OSS (Overseas) application windows.
    """

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
        print(f"[*] Checking PTDF portal for upcoming 2027 scholarship announcements...")
        
        try:
            resp = requests.get(PTDF_NEWS_URL, headers=HEADERS, timeout=30, verify=False)
            if resp.status_code != 200:
                print(f"[-] Failed to retrieve PTDF webpage. Status code: {resp.status_code}")
                return []
            html = resp.text
        except Exception as e:
            print(f"[-] Error fetching PTDF page: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        history = self._load_history()
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        results = []
        
        # The new PTDF portal uses standard container divs for news items
        news_items = soup.find_all("div", class_="col-lg-4")
        if not news_items:
            news_items = soup.find_all("div", class_="card")
            
        for item in news_items:
            if len(results) >= DAILY_LIMIT:
                break
                
            title_tag = item.find("h4") or item.find("h3")
            if not title_tag:
                continue
                
            link_tag = item.find("a")
            if not link_tag:
                continue
                
            title_text = title_tag.get_text(strip=True)
            link_href = link_tag.get("href", "").strip()
            
            # Reconstruct URL if the portal uses relative paths
            if link_href.startswith("/"):
                link_href = "https://scholarship.ptdf.gov.ng" + link_href
                
            # Filter broadly to catch both Overseas (OSS) and In-Country (ISS) announcements
            title_lower = title_text.lower()
            keywords = ["scholarship", "award", "application", "oss", "iss", "overseas", "in-country"]
            if not any(word in title_lower for word in keywords):
                continue

            if link_href not in history:
                results.append({
                    "title": title_text,
                    "country": "Nigeria (In-Country) / Overseas (UK, France, Germany, Malaysia)",
                    "organization": "Petroleum Technology Development Fund (PTDF)",
                    "degree_level": "Undergraduate, Master's & PhD",
                    "funding_type": "Fully Funded (Tuition, Flight/Laptop, Stipend)",
                    "eligibility": "Nigerian Citizens, NYSC required for PG, 2:1 for MSc",
                    "deadline": "See portal for exact application window",
                    "link": link_href,
                    "requirements": "NIN, O'Level, Transcript, NYSC Cert, Local Govt ID",
                    "date_posted": today_str,
                    "source": "PTDF Official Portal"
                })

        if not results:
            print(f"[✓] No new PTDF scholarship announcements found. Window likely not open yet.")
            return []

        print(f"[+] PTDF Spider found {len(results)} new announcements!")
        return results

def get_spider():
    """Factory function used by main.py to load the spider."""
    return PTDFSpider()

