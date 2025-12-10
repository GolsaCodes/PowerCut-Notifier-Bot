import requests
from bs4 import BeautifulSoup
import re
import json
import os
import jdatetime

def scrape_website():
    os.makedirs('cache', exist_ok=True)
    url = "https://qepd.co.ir/fa-IR/DouranPortal/6423/page/%D8%AE%D8%A7%D9%85%D9%88%D8%B4%DB%8C-%D9%87%D8%A7"
    response = requests.get(url)
    response.encoding = 'utf-8'  
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract all text content
    full_text = soup.get_text(separator='\n')
    lines = [line.strip() for line in full_text.split('\n') if line.strip()]

    # Extract Persian date
    date_match = next((line for line in lines if "برنامه مدیریت بار" in line), None)
    persian_date = ""
    if date_match:
       date_result = re.search(r'روز\s+(.+)', date_match)
       if date_result:
            persian_date = date_result.group(1).strip()
            print("persian date:", persian_date)

    # Extract time blocks and areas
    entries = []
    time_block = None
    areas = []

    for line in lines:
        if 'قطعی احتمالی برق در ساعت' in line:
            if time_block and areas:
                entries.append({"time": time_block, "areas": areas})
                areas = []
            time_block_match = re.search(r'ساعت\s+([\d تا]+)', line)
            if time_block_match:
                time_block = time_block_match.group(1)
        elif '🔻به آدرس های' in line or 'به آدرس های👇' in line:
            continue
        elif re.match(r'^[\u0600-\u06FF\s\d\-\(\)]+$', line) and time_block:
            areas.append(line)

    # Add the last block
    if time_block and areas:
        entries.append({"time": time_block, "areas": areas})

    # Save to JSON file
    output = {
        "date": persian_date,
        "entries": entries
    }

    today = jdatetime.date.today().isoformat()
    with open(f'cache/{today}.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return output