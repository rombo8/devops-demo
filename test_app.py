from unittest.mock import MagicMock, patch

from app import app


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.data == b"OK"


@patch("app.redis_client")
@patch("app.get_db_connection")
def test_homepage_from_postgresql(mock_db_connection, mock_redis):
    mock_redis.get.return_value = None

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (42,)

    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    mock_db_connection.return_value = mock_connection

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"visitor #42" in response.data
    assert b"PostgreSQL" in response.data

    mock_redis.get.assert_called_once_with("visits_count")
    mock_redis.set.assert_called_once_with("visits_count", 42)


@patch("app.redis_client")
def test_homepage_from_redis(mock_redis):
    mock_redis.get.return_value = "99"

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"visitor #99" in response.data
    assert b"Redis cache" in response.data