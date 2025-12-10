import schedule
import time
from scraper import scrape_website
from utils import send_outage_notifications
import json
import os
import jdatetime

def job():
    load_or_scrape_data()
    import asyncio
    asyncio.run(send_outage_notifications())

def load_or_scrape_data():
    today = jdatetime.date.today().isoformat()
    cache_path = f'cache/{today}.json'

    if os.path.exists(cache_path):
        print("✅ Cache found. Loading from cache.")
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print("⏳ Cache not found. Scraping...")
        return scrape_website()
# Schedule job at 10:00 PM everyday
schedule.every().day.at("22:00").do(job)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
