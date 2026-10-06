import time
from datetime import datetime, timedelta
import requests  # Using standard requests to prevent Termux ISP blocks
from scrapers.base import BaseSpider

class JobicySpider(BaseSpider):
    
    def scrape(self):
        print("[*] Scraping Jobicy (Africa & Globally Eligible Hourly Contracts)...")
        results = []
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        cutoff_time = datetime.now() - timedelta(hours=24)
        api_url = "https://jobicy.com/api/v2/remote-jobs"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            # impersonate tag removed for standard requests
            resp = requests.get(api_url, headers=headers, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                jobs_list = data.get("jobs", [])
                
                for item in jobs_list:
                    # 1. Enforce 24-Hour Rule
                    pub_date_str = item.get("pubDate", "")
                    if pub_date_str:
                        try:
                            clean_date = pub_date_str.replace("T", " ").replace("Z", "")[:19]
                            posted_dt = datetime.strptime(clean_date, "%Y-%m-%d %H:%M:%S")
                            if posted_dt < cutoff_time:
                                continue
                        except Exception:
                            pass
                            
                    # 2. Enforce Hourly/Contract Only
                    job_types = item.get("jobType", [])
                    job_types_str = " ".join(job_types).lower() if isinstance(job_types, list) else str(job_types).lower()
                    
                    if "contract" not in job_types_str and "freelance" not in job_types_str:
                        continue
                        
                    # 3. ELIGIBILITY FILTER: Global or open to Africa/EMEA
                    geo_raw = item.get("jobGeo", "")
                    geo = geo_raw.lower()
                    allowed_regions = ["anywhere", "worldwide", "global", "emea", "africa", "nigeria"]
                    
                    if not any(region in geo for region in allowed_regions):
                        continue
                        
                    title = item.get("jobTitle", "Remote Role")
                    company = item.get("companyName", "Unknown Company")
                    industries = item.get("jobIndustry", [])
                    industry_tag = industries[0] if industries else "Diverse"
                    
                    sal_min = item.get("salaryMin")
                    sal_max = item.get("salaryMax")
                    sal_currency = item.get("salaryCurrency", "$")
                    
                    if sal_min and sal_max and str(sal_min).isdigit():
                        pay = f"{sal_currency}{sal_min} - {sal_currency}{sal_max}/hr"
                    else:
                        pay = "Hourly / Contract"
                    
                    results.append({
                        "title": title,
                        "country": geo_raw if geo_raw else "Global Remote",
                        "organization": company,
                        "degree_level": "Job", 
                        "funding_type": pay,
                        "eligibility": "Global / EMEA Contractor",
                        "deadline": "Rolling",
                        "link": item.get("url", ""),
                        "requirements": f"Industry: {industry_tag}",
                        "date_posted": today_str,
                        "source": "Jobicy"
                    })
                    
                print(f"[+] Found {len(results)} fresh African-eligible hourly/contract jobs from Jobicy.")
                return results
            else:
                print(f"[!] Jobicy API Error. Status: {resp.status_code}")
                
        except Exception as e:
            print(f"[-] Scrape failed: {e}")

        return results

def get_spider():
    return JobicySpider()
