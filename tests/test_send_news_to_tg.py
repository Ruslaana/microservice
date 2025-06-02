import pytest
from unittest.mock import patch, MagicMock
from src.utils import send_news_to_tg as tg


@pytest.fixture
def sample_news():
    return {
        "document": {
            "title": "Тестова новина",
            "content": "Контент новини." * 50,
            "metadata": {
                "publication_time": "2024-01-01",
                "author": "Автор",
                "source": "https://example.com/news",
                "image_url": "https://example.com/image.jpg"
            }
        }
    }


def test_format_telegram_text_truncates_long_content(sample_news):
    result = tg.format_telegram_text(sample_news)
    assert result.startswith("📰 *Тестова новина*")
    assert "...🕒" not in result
    assert "Читати новину" in result


@patch("src.utils.send_news_to_tg.requests.get")
def test_load_subscribers_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [123, 456]
    assert tg.load_subscribers() == [123, 456]


@patch("src.utils.send_news_to_tg.requests.get")
def test_load_subscribers_failure(mock_get):
    mock_get.return_value.status_code = 500
    assert tg.load_subscribers() == []


@patch("src.utils.send_news_to_tg.requests.get", side_effect=Exception("Network error"))
def test_load_subscribers_exception(mock_get):
    assert tg.load_subscribers() == []


@patch("src.utils.send_news_to_tg.requests.post")
@patch("src.utils.send_news_to_tg.load_subscribers", return_value=[123])
def test_send_to_telegram_with_image(mock_subs, mock_post, sample_news):
    mock_post.return_value.status_code = 200
    tg.send_to_telegram(sample_news)
    mock_post.assert_called_once()


@patch("src.utils.send_news_to_tg.requests.post")
@patch("src.utils.send_news_to_tg.load_subscribers", return_value=[123])
def test_send_to_telegram_without_image(mock_subs, mock_post, sample_news):
    sample_news["document"]["metadata"]["image_url"] = None
    mock_post.return_value.status_code = 200
    tg.send_to_telegram(sample_news)
    mock_post.assert_called_once()
