import json
from datetime import datetime, timedelta
from curl_cffi import requests
from scrapers.base import BaseSpider

class Micro1Spider(BaseSpider):
    
    def scrape(self):
        print("[*] Scraping Micro1 Public Opportunities Board...")
        results = []
        now = datetime.utcnow()
        cutoff_time = now - timedelta(hours=24)
        today_str = now.strftime("%Y-%m-%d")
        
        api_url = "https://prod-api.micro1.ai/api/v1/job/portal?page=1&limit=50&keyword="
        
         headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://www.micro1.ai",
            "Referer": "https://www.micro1.ai/",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }

        payload = {
            "action": "get_all_jobs"
        }

        try:
            resp = requests.post(api_url, headers=headers, json=payload, impersonate="chrome120", timeout=15)

            
            if resp.status_code == 200:
                data = resp.json()
                jobs_list = data.get("data", [])
                
                if isinstance(jobs_list, dict):
                    jobs_list = jobs_list.get("jobs", jobs_list.get("data", []))
                
                print(f"[+] Retrieved {len(jobs_list)} total jobs. Filtering for last 24 hours...")
                
                for item in jobs_list:
                    # 1. Parse and evaluate date_posted (24-hour cutoff)
                    date_str = item.get("date_posted")
                    if date_str:
                        try:
                            # Standardize format: "YYYY-MM-DD HH:MM:SS"
                            posted_dt = datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
                            if posted_dt < cutoff_time:
                                continue  # Skip jobs older than 24 hours
                        except Exception:
                            pass
                    
                    # 2. Extract hourly pay rate
                    rate_dict = item.get("ideal_hourly_rate") or {}
                    if isinstance(rate_dict, dict) and rate_dict.get("min") and rate_dict.get("max"):
                        pay = f"${rate_dict['min']} - ${rate_dict['max']}/hr"
                    else:
                        # Skip if there is no hourly rate specified
                        continue
                    
                    title = item.get("job_name", "Remote AI Expert")
                    
                    job_link = item.get("apply_url")
                    if not job_link:
                        job_id = item.get("job_id", "")
                        job_link = f"https://jobs.micro1.ai/post/{job_id}" if job_id else "https://www.micro1.ai/experts/opportunities"
                    
                    skills = item.get("skills", [])
                    reqs = ", ".join(skills) if isinstance(skills, list) and skills else "See link for required skills"
                    
                    results.append({
                        "title": title,
                        "country": "Remote",
                        "organization": item.get("company_name", "Micro1 AI"),
                        "degree_level": "Job",
                        "funding_type": pay,
                        "eligibility": "Domain Expert",
                        "deadline": "Rolling",
                        "link": job_link,
                        "requirements": reqs,
                        "date_posted": date_str or today_str,
                        "source": "Micro1"
                    })
                
                print(f"[+] Found {len(results)} jobs posted within the last 24 hours.")
                return results
            else:
                print(f"[!] Endpoint Error. Status: {resp.status_code}")
                
        except Exception as e:
            print(f"[-] Scrape failed: {e}")

        return results

def get_spider():
    return Micro1Spider()
