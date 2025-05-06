import time
import schedule
import logging
from utils.helpers import fetch_latest_news, is_new, load_seen_ids, save_seen_ids, load_news, save_news

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

seen_ids = load_seen_ids()
all_news = load_news()


def check_news():
    logger.info("Checking for new news...")
    news_item = fetch_latest_news()
    updated_news = False
    for item in news_item:
        if is_new(item, seen_ids):
            logger.info(f"New news found: {item['title']}")
            seen_ids.add(item['id'])
            all_news.append(item)
            updated_news = True
    if updated_news:
        save_seen_ids(seen_ids)
        save_news(all_news)


schedule.every(1).hours.do(check_news)

if __name__ == "__main__":
    check_news()
    while True:
        schedule.run_pending()
        time.sleep(1)
