import json
import re
from datetime import datetime, timedelta, timezone
from curl_cffi import requests as cffi_requests
from scrapers.base import BaseSpider

class MercorSpider(BaseSpider):
    """
    Mercor Spider targeting high-paying, 100% Worldwide remote AI expert contracts.
    Enforces strict geo-filtering and a 24-hour posting cutoff.
    """

    def scrape(self):
        print("[*] Scraping Mercor (Filtering for Worldwide & Last 24 Hours)...")
        results = []
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=24)
        today_str = now.strftime("%Y-%m-%d")

        url = "https://work.mercor.com/explore"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        try:
            resp = cffi_requests.get(url, headers=headers, impersonate="chrome120", timeout=25)
            if resp.status_code != 200:
                print(f"[!] Mercor returned HTTP {resp.status_code}")
                return results

            html = resp.text.replace('\\"', '"')
            chunks = re.split(r'"listingId"\s*:\s*"', html)
            seen_ids = set()

            for chunk in chunks[1:]:
                listing_id = chunk.split('"', 1)[0]
                if not listing_id.startswith("list_") or listing_id in seen_ids:
                    continue
                seen_ids.add(listing_id)

                # ----------------------------------------------------
                # 1. 24-Hour Date Filter
                # ----------------------------------------------------
                date_match = re.search(r'"createdAt"\s*:\s*"(.*?)"', chunk)
                if not date_match:
                    date_match = re.search(r'"postedAt"\s*:\s*"(.*?)"', chunk)

                date_posted_str = today_str
                if date_match:
                    try:
                        raw_date = date_match.group(1)
                        posted_dt = datetime.strptime(raw_date[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                        if posted_dt < cutoff_time:
                            continue  # Older than 24 hours
                        date_posted_str = posted_dt.strftime("%Y-%m-%d")
                    except Exception:
                        pass

                # ----------------------------------------------------
                # 2. Strict Worldwide Geo-Filter
                # ----------------------------------------------------
                # Extract eligibleLocation (e.g., ["USA"], [], or null)
                elig_loc_match = re.search(r'"eligibleLocation"\s*:\s*(\[[^\]]*\]|null)', chunk)
                elig_res_match = re.search(r'"eligibleResidenceLocation"\s*:\s*(\[[^\]]*\]|null)', chunk)
                inelig_res_match = re.search(r'"ineligibleResidenceLocation"\s*:\s*(\[[^\]]*\]|null)', chunk)

                # Rule A: Must not have restricted country lists (Must be [] or null)
                if elig_loc_match:
                    raw_val = elig_loc_match.group(1)
                    if raw_val != "null" and raw_val != "[]":
                        continue  # Geo-restricted to specific countries (e.g. USA, GBR)

                # Rule B: Must not restrict residence
                if elig_res_match:
                    raw_val = elig_res_match.group(1)
                    if raw_val != "null" and raw_val != "[]":
                        continue  # Residence restricted (e.g. CAN, USA)

                # Rule C: Must not blacklist Nigeria or African jurisdictions
                if inelig_res_match:
                    raw_val = inelig_res_match.group(1)
                    if '"NGA"' in raw_val:
                        continue

                # ----------------------------------------------------
                # 3. Pay Rate Extraction
                # ----------------------------------------------------
                rate_min = re.search(r'"rateMin"\s*:\s*([\d\.]+)', chunk)
                rate_max = re.search(r'"rateMax"\s*:\s*([\d\.]+)', chunk)
                freq_match = re.search(r'"payRateFrequency"\s*:\s*"(.*?)"', chunk)

                if rate_min and rate_max:
                    rmin = int(float(rate_min.group(1)))
                    rmax = int(float(rate_max.group(1)))
                    freq = freq_match.group(1).lower() if freq_match else "hourly"

                    if "task" in freq:
                        unit = "/task"
                    elif "one-time" in freq:
                        unit = " (one-time)"
                    elif "year" in freq or "annual" in freq:
                        unit = "/yr"
                    else:
                        unit = "/hr"

                    pay = f"${rmin} - ${rmax}{unit}" if rmin != rmax else f"${rmin}{unit}"
                else:
                    pay = "Hourly Contract"

                # ----------------------------------------------------
                # 4. Title & Apply Link Re-construction
                # ----------------------------------------------------
                title_match = re.search(r'"title"\s*:\s*"(.*?)"', chunk)
                slug_match = re.search(r'"slug"\s*:\s*"(.*?)"', chunk)

                title = title_match.group(1) if title_match else "Remote AI Expert"
                slug = slug_match.group(1) if slug_match else "job"
                link = f"https://work.mercor.com/jobs/{listing_id}/{slug}"

                # ----------------------------------------------------
                # 5. Adhere to strict 10-field BaseSpider Contract
                # ----------------------------------------------------
                results.append({
                    "title": title,
                    "country": "Remote (Worldwide)",
                    "organization": "Mercor",
                    "degree_level": "Job",
                    "funding_type": pay,
                    "eligibility": "Domain Expert",
                    "deadline": "Rolling",
                    "link": link,
                    "requirements": "See link for required skills",
                    "date_posted": date_posted_str,
                    "source": "Mercor"
                })

            print(f"[+] Found {len(results)} Worldwide Mercor roles posted in the last 24 hours.")

        except Exception as e:
            print(f"[-] Mercor scrape error: {e}")

        return results

def get_spider():
    return MercorSpider()
