import time
import schedule
import logging
from utils.news_service import process_news_check

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

schedule.every().hour.do(process_news_check)

if __name__ == "__main__":
    process_news_check()
    while True:
        schedule.run_pending()
        time.sleep(30)
