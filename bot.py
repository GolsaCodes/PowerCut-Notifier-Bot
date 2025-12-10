import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from scraper import scrape_website
from storage import load_subscriptions, save_subscription, remove_subscription
import json
import os
import jdatetime
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def check_cache():
    today = jdatetime.date.today().isoformat()
    cache_path = f'cache/{today}.json'
    if not os.path.exists(cache_path):
        print("Cache not found. Scraping data...")
        scrape_website()
    else:
        print("Cache found. Using cached data.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
   # check_cache()
    await update.message.reply_text(
        "به ربات اطلاع‌دهنده‌ی برنامه‌ی قطعی شهر قم خوش اومدین!\n"
        "دقت کنید که برای اطلاع‌رسانی دقیق، باید نام منطقه رو طبق چیزی که در وبسایت رسمی شرکت توزیع برق اومده وارد کنید.\n\n"
        "شما می‌تونید از دستورات زیر استفاده کنید:\n\n"
        "1) اضافه کردن منطقه‌ای که می‌خواهید در صورت قطعی برق، هرروز به صورت خودکار اطلاع‌رسانی بشه:\n"
        "/add نام منطقه\n"
        "مثال: /add صفاشهر\n\n"
        "2) حذف منطقه‌ای از لیست اطلاع‌رسانی:\n"
        "/remove نام منطقه\n"
        "مثال: /remove صفاشهر\n\n"
        "3) مشاهده‌ی لیست مناطق انتخاب‌شده‌ی شما:\n"
        "/list\n\n"
        "4) بررسی وضعیت قطعی برق در منطقه‌ای خاص برای امروز:\n"
        "/check نام منطقه\n"
        "مثال: /check نیروگاه"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    area_name = " ".join(context.args)
    if area_name:
        save_subscription(group_id, area_name)
        await update.message.reply_text(f"منطقه «{area_name}» با موفقیت به لیست اطلاع‌رسانی اضافه شد.")
    else:
        await update.message.reply_text("لطفاً نام یک منطقه را وارد کنید. مثال: /add صفاشهر")

async def list_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    subscriptions = load_subscriptions(group_id)
    if subscriptions:
        await update.message.reply_text("مناطق انتخاب‌ شده‌ی شما:\n" + "\n".join(subscriptions))
    else:
        await update.message.reply_text("هنوز هیچ منطقه‌ای برای اطلاع‌رسانی انتخاب نکرده‌اید.")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    area_name = " ".join(context.args)
    if area_name:
        if remove_subscription(group_id, area_name):
            await update.message.reply_text(f"منطقه «{area_name}» از لیست اطلاع‌رسانی حذف شد.")
        else:
            await update.message.reply_text(f"منطقه «{area_name}» در لیست شما یافت نشد.")
    else:
        await update.message.reply_text("لطفاً نام منطقه‌ای را که می‌خواهید حذف کنید وارد نمایید. مثال: /remove صفاشهر")

async def check_outage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    area_name = " ".join(context.args)

    if not area_name:
        await update.message.reply_text("لطفاً نام منطقه را وارد کنید.")
        return

    def normalize(text):
        return text.strip().replace('ي', 'ی').replace('ك', 'ک').replace('\u200c', '').replace('\u200f', '').lower()

    normalized_input = normalize(area_name)

    today = jdatetime.date.today().isoformat()
    cache_path = f'cache/{today}.json'
    today_display = jdatetime.date.today().strftime("%Y/%m/%d")

    if not os.path.exists(cache_path):
        await update.message.reply_text("داده‌ها در حال بارگذاری هستند. لطفاً کمی بعد دوباره تلاش کنید.")
        return

    with open(cache_path, 'r', encoding='utf-8') as f:
        outage_data = json.load(f)

    found = False
    for entry in outage_data.get("entries", []):
        for area in entry.get("areas", []):
            if normalize(area).find(normalized_input) != -1:
                time_range = entry['time']  # e.g., "8 تا 10"
                try:
                    parts = time_range.split("تا")
                    start = int(parts[0].strip())
                    end = int(parts[1].strip())

                    if start <= 12 and end <= 12:
                        time_label = "صبح"
                    elif start <= 18 and end <= 18:
                        time_label = "ظهر"
                    elif start <= 22 and end <= 22:
                        time_label = "شب"
                    else:
                        time_label = ""

                    message = f"قطعی برق در تاریخ «{today_display}» در منطقه «{area}» احتمالا در ساعت {time_range.strip()} {time_label} رخ می‌دهد."
                except Exception as e:
                    message = f"قطعی برق در تاریخ «{today_display}» در منطقه «{area}» احتمالا در ساعت {entry['time']} رخ می‌دهد."

                await update.message.reply_text(message)
                found = True
                break
        if found:
            break

    if not found:
        await update.message.reply_text(f"اطلاعاتی برای منطقه «{area_name}» یافت نشد.")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("list", list_subscriptions))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("check", check_outage))
    application.run_polling()

if __name__ == '__main__':

    main()
