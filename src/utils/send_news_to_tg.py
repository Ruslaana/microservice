import os
import requests
import logging
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NEWS_API_URL = os.getenv("NEWS_API_URL")
SUBSCRIBERS_URL = f"{NEWS_API_URL}/subscribers"

logger = logging.getLogger(__name__)


def format_telegram_text(news):
    doc = news.get("document", {})
    meta = doc.get("metadata", {})

    title = doc.get("title", "")
    content = doc.get("content", "")
    publication_time = meta.get(
        "publication_time") or datetime.now().strftime("%d.%m.%Y")
    author = meta.get("author") or meta.get("source", "berlingske.dk")
    source = meta.get("source", "")

    header = f"📰 *{title}*\n\n"
    footer = f"\n\n🕒 {publication_time}\n✍️ {author}\n🔗 [Читати новину]({source})"

    max_content_len = 1024 - len(header) - len(footer)
    short_content = content[:max_content_len].rstrip() + "..."
    return header + short_content + footer


def load_subscribers():
    try:
        response = requests.get(SUBSCRIBERS_URL)
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(
                f"⚠️ Не вдалося отримати підписників: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"❌ Помилка при отриманні підписників: {e}")
        return []


def send_to_telegram(news):
    chat_ids = load_subscribers()

    logger.info(json.dumps(news, indent=2, ensure_ascii=False))

    doc = news.get("document", {})
    meta = doc.get("metadata", {})
    image_url = meta.get("image_url")
    text = format_telegram_text(news)

    for chat_id in chat_ids:
        try:
            if image_url and image_url.startswith("http"):
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
                payload = {
                    "chat_id": chat_id,
                    "photo": image_url,
                    "caption": text,
                    "parse_mode": "Markdown"
                }
            else:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                }

            response = requests.post(url, json=payload)
            if response.status_code == 200:
                logger.info(f"📨 Успішно надіслано в Telegram: {chat_id}")
            else:
                logger.warning(
                    f"⚠️ Telegram помилка ({chat_id}): {response.text}")

        except Exception as e:
            logger.error(f"❌ Помилка надсилання в Telegram ({chat_id}): {e}")
