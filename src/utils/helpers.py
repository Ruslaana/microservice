import json
import os
import logging
from dotenv import load_dotenv
import boto3
import uuid
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

last_saved_id_key = "meta/last_saved_id.txt"

logger = logging.getLogger(__name__)


def load_last_saved_id():
    try:
        response = s3_client.get_object(
            Bucket=aws_bucket_name, Key=last_saved_id_key)
        return response['Body'].read().decode('utf-8')
    except s3_client.exceptions.NoSuchKey:
        logger.info("🔰 Перший запуск — last_saved_id ще не існує.")
        return None
    except Exception as e:
        logger.warning(f"Помилка при читанні last_saved_id: {e}")
        return None


def save_last_saved_id(news_id):
    try:
        s3_client.put_object(
            Bucket=aws_bucket_name,
            Key=last_saved_id_key,
            Body=str(news_id).encode('utf-8'),
            ContentType='text/plain'
        )
        logger.info(f"💾 Збережено last_saved_id: {news_id}")
    except Exception as e:
        logger.error(f"❌ Помилка при збереженні last_saved_id: {e}")


def save_news_to_s3(news_item):
    try:
        filename = f"news/{uuid.uuid4()}.json"
        s3_client.put_object(
            Bucket=aws_bucket_name,
            Key=filename,
            Body=json.dumps(news_item, ensure_ascii=False),
            ContentType='application/json'
        )
        logger.info(f"☁️ Новина збережена в S3: {filename}")
    except Exception as e:
        logger.error(f"❌ Помилка при збереженні новини в S3: {e}")


def load_random_news_from_s3():
    try:
        response = s3_client.list_objects_v2(
            Bucket=aws_bucket_name, Prefix="news/")
        objects = response.get("Contents", [])

        if not objects:
            logger.warning("⚠️ Архів порожній.")
            return None

        random_key = random.choice(objects)["Key"]

        response = s3_client.get_object(Bucket=aws_bucket_name, Key=random_key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)

    except Exception as e:
        logger.error(f"❌ Помилка при витягуванні випадкової новини з S3: {e}")
        return None
