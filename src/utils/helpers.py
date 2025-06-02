import os
import json
import logging
from dotenv import load_dotenv
import boto3
import random
from botocore.exceptions import ClientError


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
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            logger.info("🔰 Перший запуск — last_saved_id ще не існує.")
            return None
        raise
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


def load_random_news_from_s3():
    try:
        response = s3_client.list_objects_v2(
            Bucket=aws_bucket_name, Prefix="news/")
        objects = response.get("Contents", [])

        if not objects:
            logger.debug("📭 Архів порожній.")
            return None

        random_key = random.choice(objects)["Key"]
        response = s3_client.get_object(Bucket=aws_bucket_name, Key=random_key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)

    except Exception as e:
        logger.error(f"❌ Помилка при витягуванні новини з S3: {e}")
        return None
