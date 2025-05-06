import requests
import xml.etree.ElementTree as ET
import json
import os
import logging
from datetime import datetime

NEWS_API_URL = "https://www.berlingske.dk/sitemap.xml/tag/1"
SEEN_FILE_PATH = "seen_ids.json"
NEWS_FILE_PATH = "news.json"

logger = logging.getLogger(__name__)


def fetch_latest_news():
    try:
        response = requests.get(NEWS_API_URL)
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


def is_new(news_item, seen_ids: set):
    return news_item['id'] not in seen_ids


def load_seen_ids() -> set:
    if os.path.exists(SEEN_FILE_PATH):
        try:
            with open(SEEN_FILE_PATH, 'r') as file:
                return set(json.load(file))

        except json.JSONDecodeError as e:
            logger.warning(f"Error decoding JSON from {SEEN_FILE_PATH}: {e}")
    return set()


def save_seen_ids(seen_ids: set):
    with open(SEEN_FILE_PATH, 'w') as file:
        json.dump(list(seen_ids), file)
        logger.info(f"Saved {len(seen_ids)} seen IDs to {SEEN_FILE_PATH}")


def load_news() -> list:
    if os.path.exists(NEWS_FILE_PATH):
        try:
            with open(NEWS_FILE_PATH, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logger.warning(f"Error decoding JSON from {NEWS_FILE_PATH}: {e}")
    return []


def save_news(news: list):
    with open(NEWS_FILE_PATH, 'w') as file:
        json.dump(news, file)
        logger.info(f"Saved {len(news)} news items to {NEWS_FILE_PATH}")
