import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from scrapers.base import BaseSpider

DAILY_LIMIT = 5
DIRECT_URL = "https://cscuk.fcdo.gov.uk/commonwealth-shared-scholarships-eligible-courses/"
PORTAL_URL = "https://cscuk.fcdo.gov.uk/scholarships/commonwealth-shared-scholarships-applications/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

class CommonwealthSpider(BaseSpider):
    """
    Spider for the UK Commonwealth Shared Scholarships.
    Monitors the FCDO portal for the 2027/2028 academic cycle update.
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

    def _fetch_html(self):
        """Fetches the eligible courses table directly over HTTPS."""
        if hasattr(self, "fetch_html"):
            try:
                html = self.fetch_html(DIRECT_URL)
                if html: 
                    return html
            except Exception:
                pass

        try:
            resp = requests.get(DIRECT_URL, headers=HEADERS, timeout=25)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            print(f"[-] Error fetching Commonwealth page: {e}")
            
        return None

    def scrape(self):
        print(f"[*] Checking Commonwealth Shared portal for up to {DAILY_LIMIT} unposted programmes...")
        html = self._fetch_html()
        
        if not html:
            print("[-] Failed to retrieve eligible courses webpage.")
            return []

        soup = BeautifulSoup(html, "html.parser")
        
        # =====================================================================
        # GATEKEEPER CHECK: Wait for the 2027/2028 cycle to go live
        # =====================================================================
        page_title = soup.find("title").get_text(strip=True) if soup.find("title") else ""
        if "2027" not in page_title and "2028" not in page_title:
            print(f"[✓] Portal still showing old cycle: '{page_title}'.")
            print("[✓] Sleeping until the 2027/2028 update goes live in November. Zero items extracted.")
            return []

        history = self._load_history()
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        content_blocks = soup.find_all("div", class_="scholarshipContent")
        results = []
        seen_in_run = set()

        for block in content_blocks:
            if len(results) >= DAILY_LIMIT:
                break

            h1 = block.find("h1")
            theme = h1.get_text(strip=True).replace("\xa0", " ") if h1 else "General Development"

            table = block.find("table")
            if not table:
                continue

            for row in table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 2:
                    university = cols[0].get_text(separator=" ", strip=True).replace("\xa0", " ").strip()
                    course_name = cols[1].get_text(separator=" ", strip=True).replace("\xa0", " ").strip()

                    if len(university) < 3 or len(course_name) < 3:
                        continue

                    # Create a unique, deterministic slug for history.json and clickability
                    slug_base = f"{university.lower().replace(' ', '-')}-{course_name.lower().replace(' ', '-')}-2027"
                    clean_slug = "".join(e for e in slug_base if e.isalnum() or e == '-')
                    canonical_link = f"{DIRECT_URL}#{clean_slug}"

                    if canonical_link not in history and canonical_link not in seen_in_run:
                        seen_in_run.add(canonical_link)

                        results.append({
                            "title": f"{course_name} (Shared Award)",
                            "country": "United Kingdom",
                            "organization": university,
                            "degree_level": "Master's",
                            "funding_type": "Fully Funded (£1,452-£1,781/mo + Tuition + Flights)",
                            "eligibility": "Commonwealth Citizen (Nigeria), First Class / 2:1 Honours or Pending",
                            "deadline": "Mid-December 2026 (Annual Window)",
                            "link": canonical_link,
                            "requirements": f"Theme: {theme}. Requires direct university admission + CSC nomination.",
                            "date_posted": today_str,
                            "source": "Commonwealth Shared Scholarships"
                        })

                        if len(results) == DAILY_LIMIT:
                            break

        if not results:
            print(f"[✓] All available 2027 programmes are already logged in history.json ({len(history)} total).")
            return []

        print(f"[+] Commonwealth Spider selected {len(results)} unposted programmes for dispatch.")
        return results

def get_spider():
    """Factory function used by main.py to load the spider."""
    return CommonwealthSpider()
