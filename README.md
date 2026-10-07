 # OpportunityRadar
 
 OpportunityRadar is an automated Python pipeline that discovers new scholarships and remote job opportunities, then posts them to Telegram.
 
 ## What it does
 
 - Scrapes multiple scholarship and job sources
 - Standardizes opportunity data into a shared structure
 - Prevents duplicate alerts using `history.json`
 - Sends formatted updates to a Telegram channel
 - Runs daily through GitHub Actions
 
 ## Project structure
 
 - `main.py` — orchestrates scraping, deduplication, and dispatching
 - `scrapers/` — source-specific spiders for scholarships and jobs
 - `utils/formatter.py` — message formatting for Telegram posts
 - `utils/dispatcher.py` — Telegram message delivery with chunking/fallback
 - `.github/workflows/daily_scrape.yml` — scheduled automation workflow
 
 ## Setup
 
 1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
 2. Create a `.env` file in the project root:
    ```env
    TELEGRAM_BOT_TOKEN=your_bot_token
    TELEGRAM_CHAT_ID=your_chat_id
    ```
 
 ## Run locally
 
 ```bash
 python main.py
 ```
 
 ## Automation
 
 The workflow in `.github/workflows/daily_scrape.yml` runs daily at **05:00 UTC** and can also be triggered manually from GitHub Actions.