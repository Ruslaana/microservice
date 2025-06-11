import os
import json
import logging
from dotenv import load_dotenv
import boto3
import random

load_dotenv()

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
aws_bucket_name = os.getenv("AWS_BUCKET_NAME")

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

last_sent_id_key = "meta/last_sent_id.txt"
logger = logging.getLogger(__name__)


def load_last_sent_id():
    try:
        response = s3_client.get_object(
            Bucket=aws_bucket_name, Key=last_sent_id_key)
        return response['Body'].read().decode('utf-8')
    except s3_client.exceptions.NoSuchKey:
        logger.info("🆕 Перший запуск — last_sent_id ще не існує.")
        return None
    except Exception as e:
        logger.warning(f"❌ Помилка при читанні last_sent_id: {e}")
        return None


def save_last_sent_id(news_id):
    try:
        s3_client.put_object(
            Bucket=aws_bucket_name,
            Key=last_sent_id_key,
            Body=str(news_id).encode('utf-8'),
            ContentType='text/plain'
        )
        logger.info(f"💾 Збережено last_sent_id: {news_id}")
    except Exception as e:
        logger.error(f"❌ Помилка при збереженні last_sent_id: {e}")


def load_random_news_from_s3():
    try:
        response = s3_client.list_objects_v2(
            Bucket=aws_bucket_name, Prefix="news/")
        objects = response.get("Contents", [])

        if not objects:
            logger.debug("📭 Архів порожній.")
            return None

        json_keys = [obj["Key"]
                     for obj in objects if obj["Key"].endswith(".json")]
        random_key = random.choice(json_keys)
        response = s3_client.get_object(Bucket=aws_bucket_name, Key=random_key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)

    except Exception as e:
        logger.error(f"❌ Помилка при витягуванні новини з S3: {e}")
        return None
