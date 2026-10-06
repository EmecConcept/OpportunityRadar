import json
import os
import time

from scrapers.scholarships.erasmus import get_spider as get_erasmus
from scrapers.scholarships.commonwealth import get_spider as get_commonwealth
from scrapers.scholarships.ptdf import get_spider as get_ptdf
from scrapers.jobs.micro1 import get_spider as get_micro1
from scrapers.jobs.mercor import get_spider as get_mercor
from scrapers.jobs.jobicy import get_spider as get_jobicy
from utils.formatter import format_telegram_message, format_job_bundle
from utils.dispatcher import send_telegram_message
from config import HISTORY_FILE

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def main():
    print("=======================================")
    print("🚀 EMEC OPPORTUNITY BOT INITIALIZING...")
    print("=======================================")
    
    history = load_history()
    
    # Active spiders registry (Pure Hourly Contracts & Scholarships)
    spiders = [
        get_erasmus(),
        get_commonwealth(),
        get_micro1(),
        get_jobicy(),
        get_ptdf(),
        get_mercor()
    ]
    
    new_opportunities = []
    
    for spider in spiders:
        results = spider.scrape()
        for item in results:
            if item['link'] not in history:
                new_opportunities.append(item)
                history.append(item['link'])
                
    save_history(history)
    
    print(f"\n📊 SUMMARY: Found {len(new_opportunities)} NEW opportunities!\n")
    
    # 1. Separate items by type
    scholarships = [opp for opp in new_opportunities if opp.get('degree_level') != "Job"]
    jobs = [opp for opp in new_opportunities if opp.get('degree_level') == "Job"]
    
    # 2. Dispatch Scholarships (Individually)
    for opp in scholarships:
        msg = format_telegram_message(opp)
        print("-" * 40)
        print(msg)
        send_telegram_message(msg)
        time.sleep(1)  
        
    # 3. Dispatch Jobs (As a single compiled list)
    if jobs:
        bundle_msg = format_job_bundle(jobs)
        print("-" * 40)
        print(bundle_msg)
        send_telegram_message(bundle_msg)

if __name__ == "__main__":
    main()
