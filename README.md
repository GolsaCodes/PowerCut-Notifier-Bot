# Telegram Power Outage Notifier Bot

A Telegram bot that automatically notifies users about scheduled power outages in **Qom, Iran**.

The bot retrieves power outage schedules from the official electricity distribution website, allowing users to subscribe to specific regions and receive updates about planned power cuts.

## Features

- **Region Subscription:** Add specific regions to receive power outage notifications.
- **Automatic Updates:** Retrieve daily outage schedules from the official website.
- **Personalized Notifications:** Save user subscriptions and notify users about their selected regions.
- **Region Management:** Add, remove, and view subscribed regions.
- **Outage Checking:** Check the scheduled power outage time for a specific region.
- **Data Caching:** Store scraped data in daily JSON files to reduce unnecessary website requests.
- **Persian Date Support:** Use the Jalali calendar for date handling and displaying outage schedules.
- **Multiple Users:** Support subscriptions from multiple Telegram users.

## Telegram Bot Commands

| Command | Description | Example |
|---|---|---|
| `/start` | Start the bot and display instructions | `/start` |
| `/add` | Subscribe to a region | `/add صفاشهر` |
| `/remove` | Unsubscribe from a region | `/remove صفاشهر` |
| `/list` | Display subscribed regions | `/list` |
| `/check` | Check today's outage schedule for a region | `/check نیروگاه` |

## Project Structure

```text
PowerCut-Notifier-Bot/
│
├── bot.py              # Main Telegram bot and command handlers
├── scraper.py          # Scrapes outage schedules from the website
├── scheduler.py        # Handles scheduled tasks
├── storage.py          # Manages user subscriptions
├── setup_db.py         # Database initialization
├── utils.py            # Utility functions
├── requirements.txt   
├── .gitignore         
└── README.md               
```

## Technologies Used

- **Python** – Core programming language
- **python-telegram-bot** – Telegram Bot API integration
- **BeautifulSoup / Web Scraping** – Extracting outage schedules
- **JSON** – Storing cached outage data
- **SQLite / Database** – Subscription storage
- **jdatetime** – Persian (Jalali) date handling
- **python-dotenv** – Managing environment variables

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/GolsaCodes/PowerCut-Notifier-Bot.git
cd PowerCut-Notifier-Bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
BOT_TOKEN=your_telegram_bot_token
```

Replace `your_telegram_bot_token` with your Telegram bot token.

### 4. Run the bot

```bash
python bot.py
```

## How It Works

1. Users start the bot using `/start`.
2. Users subscribe to their preferred regions using `/add`.
3. The bot retrieves the latest power outage schedule from the official electricity distribution website.
4. Retrieved data is cached in daily JSON files.
5. Every night at a scheduled time, the bot automatically sends notifications to subscribed users, informing them of the expected power outage times for the following day in their selected regions.
6. Users can check the outage schedule for any region using `/check`.
7. Users can manage their subscriptions using `/add`, `/remove`, and `/list`.

## Notes

- This project was developed to provide easier access to scheduled power outage information in Qom, Iran.
- For accurate results, users should enter region names exactly as listed on the official electricity distribution website.
- Notifications depend on the availability and accuracy of the published outage schedules.
