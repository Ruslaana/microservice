import json
import pytest
from unittest.mock import patch, MagicMock
from src.utils import helpers
from botocore.exceptions import ClientError


@patch("src.utils.helpers.s3_client")
def test_load_last_saved_id_success(mock_s3):
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=lambda: b"123")
    }

    result = helpers.load_last_saved_id()
    assert result == "123"


@patch("src.utils.helpers.s3_client")
def test_load_last_saved_id_no_key(mock_s3):
    mock_s3.get_object.side_effect = ClientError(
        {"Error": {"Code": "NoSuchKey"}}, "GetObject"
    )
    result = helpers.load_last_saved_id()
    assert result is None


@patch("src.utils.helpers.s3_client")
def test_save_last_saved_id(mock_s3):
    helpers.save_last_saved_id("456")
    mock_s3.put_object.assert_called_once()
    args, kwargs = mock_s3.put_object.call_args
    assert kwargs["Key"] == "meta/last_saved_id.txt"
    assert kwargs["Body"] == b"456"


@patch("src.utils.helpers.s3_client")
def test_load_random_news_from_s3(mock_s3):
    mock_s3.list_objects_v2.return_value = {
        "Contents": [{"Key": "news/1.json"}, {"Key": "news/2.json"}]
    }
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=lambda: json.dumps({"title": "Random"}).encode("utf-8"))
    }

    result = helpers.load_random_news_from_s3()
    assert result["title"] == "Random"
