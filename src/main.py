import time
import schedule
import logging
import os
import requests
from dotenv import load_dotenv
from utils.helpers import (
    load_last_saved_id,
    save_last_saved_id,
    load_random_news_from_s3
)
from utils.send_news_to_tg import send_to_telegram

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

NEWS_API_URL = os.getenv("NEWS_API_URL")


def check_news():
    logger.info("🔍 Перевірка новин через API...")

    try:
        response = requests.get(f"{NEWS_API_URL}/latest")
        if response.status_code != 200:
            logger.warning(f"⚠️ API помилка: {response.status_code}")
            return

        news = response.json()
        doc = news.get("document", {})
        news_id = doc.get("id")
        if not news_id:
            logger.warning("⚠️ Відсутній ID новини.")
            return

        last_saved_id = load_last_saved_id()
        if news_id == last_saved_id:
            logger.info(
                "🟢 Нових новин немає. Спроба надіслати випадкову з архіву.")
            archived_news = load_random_news_from_s3()
            if archived_news:
                send_to_telegram(archived_news)
            else:
                logger.debug(
                    "📭 Архів порожній або не вдалося завантажити новину.")
            return

        send_to_telegram(news)
        save_last_saved_id(news_id)

    except Exception as e:
        logger.error(f"❌ {e}")


schedule.every().hour.do(check_news)

if __name__ == "__main__":
    check_news()
    logger.info("🟢 Сервіс запущено. Очікування за розкладом...")
    while True:
        schedule.run_pending()
        time.sleep(30)
