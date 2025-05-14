import json
import os
import logging
import uuid
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

NEWS_FILE = "news.json"
LAST_SAVED_ID_KEY = "meta/last_saved_id.txt"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


def upload_news_to_s3(news_list):
    for item in reversed(news_list):
        filename = f"news/{uuid.uuid4()}.json"
        try:
            s3_client.put_object(
                Bucket=AWS_BUCKET_NAME,
                Key=filename,
                Body=json.dumps(item),
                ContentType='application/json'
            )
            logger.info(f"Uploaded: {item['id']}")
        except ClientError as e:
            logger.error(f"Failed to upload {item['id']}: {e}")


def save_last_saved_id(news_id):
    try:
        s3_client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=LAST_SAVED_ID_KEY,
            Body=news_id.encode('utf-8'),
            ContentType='text/plain'
        )
        logger.info(f"Saved last_saved_id: {news_id}")
    except ClientError as e:
        logger.error(f"Failed to save last_saved_id: {e}")


def migrate():
    if not os.path.exists(NEWS_FILE):
        logger.error(f"File {NEWS_FILE} not found.")
        return

    with open(NEWS_FILE, "r", encoding="utf-8") as file:
        try:
            news_list = json.load(file)
        except json.JSONDecodeError as e:
            logger.error(f"Error reading JSON: {e}")
            return

    if not news_list:
        logger.warning("news.json is empty.")
        return

    logger.info(f"Found {len(news_list)} news items to upload.")
    upload_news_to_s3(news_list)
    save_last_saved_id(news_list[-1]["id"])


if __name__ == "__main__":
    migrate()
