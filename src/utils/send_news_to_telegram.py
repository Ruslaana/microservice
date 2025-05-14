import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logger = logging.getLogger(__name__)


def send_to_telegram(news_item):
    message = f"📰 Новина:\n{news_item['title']}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info(f"📨 Надіслано в Telegram: {news_item['id']}")
        else:
            logger.warning(
                f"⚠️ Помилка при відправленні в Telegram: {response.text}")
    except Exception as e:
        logger.error(f"❌ Telegram send error: {e}")
