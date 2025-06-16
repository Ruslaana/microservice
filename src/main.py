import time
import schedule
import logging
from utils.news_service import process_news_check

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

schedule.every().day.at("09:00").do(process_news_check)
schedule.every().day.at("10:00").do(process_news_check)
schedule.every().day.at("11:00").do(process_news_check)
schedule.every().day.at("12:00").do(process_news_check)
schedule.every().day.at("20:00").do(process_news_check)

process_news_check()

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(30)
