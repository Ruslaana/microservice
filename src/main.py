import time
import schedule
import logging
from utils.helpers import (
    fetch_latest_news,
    load_last_saved_id,
    save_last_saved_id,
    save_news_to_s3
)
from utils.send_news_to_telegram import send_to_telegram

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


def check_news():
    logger.info("🔍 Перевірка наявності нових новин...")
    all_news = fetch_latest_news()
    last_saved_id = load_last_saved_id()

    if not all_news:
        logger.warning("⚠️ Не вдалося отримати жодної новини.")
        return

    latest = all_news[0]

    if latest['id'] == last_saved_id:
        logger.info("🟢 Нових новин немає.")
        return

    logger.info(f"🆕 Нова новина: {latest['title']}")
    send_to_telegram(latest)
    save_news_to_s3(latest)
    save_last_saved_id(latest['id'])


schedule.every().day.at("09:00").do(check_news)
schedule.every().day.at("10:00").do(check_news)
schedule.every().day.at("11:00").do(check_news)
schedule.every().day.at("12:00").do(check_news)
schedule.every().day.at("20:00").do(check_news)

if __name__ == "__main__":
    logger.info("🟢 Сервіс запущено. Очікування за розкладом...")
    while True:
        schedule.run_pending()
        time.sleep(30)
