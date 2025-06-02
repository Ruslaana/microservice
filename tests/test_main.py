import pytest
from unittest.mock import patch, MagicMock
import main


@patch("main.send_to_telegram")
@patch("main.load_random_news_from_s3")
@patch("main.load_last_saved_id")
@patch("main.requests.get")
def test_check_news_no_new_news(
    mock_get, mock_load_last_id, mock_load_random_news, mock_send_telegram
):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "document": {"id": "123"}
    }

    mock_load_last_id.return_value = "123"
    mock_load_random_news.return_value = {
        "document": {"title": "random", "id": "999"}
    }

    main.check_news()

    mock_send_telegram.assert_called_once_with(
        mock_load_random_news.return_value)


@patch("main.send_to_telegram")
@patch("main.save_last_saved_id")
@patch("main.load_last_saved_id")
@patch("main.requests.get")
def test_check_news_new_news(
    mock_get, mock_load_last_id, mock_save_id, mock_send_telegram
):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "document": {"id": "456"}
    }

    mock_load_last_id.return_value = "123"

    main.check_news()

    mock_send_telegram.assert_called_once()
    mock_save_id.assert_called_once_with("456")


@patch("main.requests.get")
def test_check_news_api_failure(mock_get):
    mock_get.return_value.status_code = 500
    result = main.check_news()
    assert result is None


@patch("main.requests.get", side_effect=Exception("Connection error"))
def test_check_news_exception(mock_get):
    result = main.check_news()
    assert result is None
