from utils.stack import Stack

news_stack = Stack(max_size=2)


def add_news(news):
    news_stack.push(news)


def get_latest_news():
    return news_stack.peek()


def get_previous_news():
    if news_stack.size() >= 2:
        last = news_stack.pop()
        prev = news_stack.peek()
        news_stack.push(last)
        return prev
    return None


def buffer_size():
    return news_stack.size()
