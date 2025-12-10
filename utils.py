import asyncio
import json
import os
import jdatetime
from telegram import Bot
from storage import load_all_subscriptions
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

async def send_outage_notifications():
    today = jdatetime.date.today().isoformat()
    try:
        with open(f'cache/{today}.json', 'r', encoding='utf-8') as f:
            outage_info = json.load(f)
    except FileNotFoundError:
        print("No outage data found for today.")
        return

    data = load_all_subscriptions()
    if not data:
        print("No subscriptions found.")
        return

    persian_date = outage_info.get("date", "امروز")

    for group_id, subscriptions in data.items():
        for area in subscriptions:
            outage_time = None
            for entry in outage_info.get("entries", []):
                if any(area in a for a in entry.get("areas", [])):
                    outage_time = entry["time"]
                    break

            if outage_time:
                message = f"📢 اطلاعیه قطعی برق {persian_date}:\nمنطقه: {area}\nزمان احتمالی: {outage_time}"
            else:
                message = f"ℹ️ برای منطقه «{area}» در تاریخ {persian_date} برنامه‌ی قطعی یافت نشد."

            try:
                await bot.send_message(chat_id=group_id, text=message)
                print(f"✅ Sent to {group_id}: {area}")
            except Exception as e:

                print(f"❌ Failed to send to {group_id}: {e}")
