import requests
from fake_useragent import UserAgent
from abc import ABC, abstractmethod

class BaseSpider(ABC):
    """
    Standard Base Spider for the Emec Opportunity Pipeline.
    Enforces a strict 10-field dictionary return format.
    """

    def __init__(self):
        try:
            ua = UserAgent()
            agent = ua.random
        except Exception:
            agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

        self.headers = {
            'User-Agent': agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    @abstractmethod
    def scrape(self):
        """
        Must return a list of dicts with all 10 standardized keys:
        {
            "title": str,
            "country": str,
            "organization": str,
            "degree_level": str,
            "funding_type": str,
            "eligibility": str,
            "deadline": str,
            "link": str,
            "requirements": str,
            "date_posted": str
        }
        """
        pass

    def fetch_html(self, url):
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[!] Network error fetching {url}: {e}")
            return None

    def fetch_json(self, url):
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[!] Network error fetching API {url}: {e}")
            return None
