import logging
import requests
from datetime import datetime
from utils.helpers import (
    load_last_sent_id,
    save_last_sent_id,
    load_random_news_from_s3
)
from utils.send_news_to_tg import send_to_telegram
from utils.news_buffer import (
    add_news,
    get_latest_news
)
import os
from dotenv import load_dotenv

load_dotenv()
NEWS_API_URL = os.getenv("NEWS_API_URL")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


def parse_news_time(news):
    try:
        time_str = news.get("document", {}).get(
            "metadata", {}).get("publication_time")
        return datetime.strptime(time_str, "%d.%m.%Y %H:%M")
    except Exception as e:
        logger.warning(f"⚠️ Неможливо розпарсити час публікації: {e}")
        return None


def process_news_check():
    logger.info("🔍 Перевірка новин через API...")

    try:
        response = requests.get(f"{NEWS_API_URL}/latest")
        if response.status_code != 200:
            logger.warning(f"⚠️ API помилка: {response.status_code}")
            return

        news = response.json()
        news_id = news.get("document", {}).get("id")
        if not news_id:
            logger.warning("⚠️ Відсутній ID новини.")
            return

        last_sent_id = load_last_sent_id()
        if news_id == last_sent_id:
            logger.info("🟢 Нових новин немає. Отримуємо випадкову з архіву...")
            random_news = load_random_news_from_s3()
            if random_news:
                send_to_telegram(random_news)
                logger.info(f"📨 Рандомна новина надіслана з архіву.")
            else:
                logger.warning("📭 Архів порожній або помилка.")
            return

        # якщо нова — надсилаємо, додаємо в буфер і оновлюємо last_sent_id
        send_to_telegram(news)
        add_news(news)
        save_last_sent_id(news_id)
        logger.info(
            f"✅ Нова новина надіслана в Telegram та додана в буфер: {news_id}")

    except Exception as e:
        logger.error(f"❌ Помилка обробки новини: {e}")
