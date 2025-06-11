from collections import deque

news_buffer = deque(maxlen=2)


def get_latest_news():
    return news_buffer[-1] if news_buffer else None


def get_previous_news():
    return news_buffer[-2] if len(news_buffer) >= 2 else None


def add_news(news):
    news_buffer.append(news)


def buffer_size():
    return len(news_buffer)
