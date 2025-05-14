import requests
import xml.etree.ElementTree as ET
import json
import os
import logging
from dotenv import load_dotenv
import boto3
import uuid

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

sitemap_url = "https://www.berlingske.dk/sitemap.xml/tag/1"
last_saved_id_key = "meta/last_saved_id.txt"

logger = logging.getLogger(__name__)


def fetch_latest_news():
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        news_items = []

        for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
            loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if loc is not None:
                news_items.append({"id": loc.text, "title": loc.text})
        return news_items
    except Exception as e:
        logger.error(f"Error fetching or parsing news: {e}")
        return []


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
            Body=news_id.encode('utf-8'),
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
            Body=json.dumps(news_item),
            ContentType='application/json'
        )
        logger.info(f"☁️ Новина збережена в S3: {filename}")
    except Exception as e:
        logger.error(f"❌ Помилка при збереженні новини в S3: {e}")
