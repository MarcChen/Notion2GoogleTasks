from unittest.mock import MagicMock

import pytest

from services.free_sms_alert.main import SMSAPI, MissingParameter


@pytest.fixture
def sms_client():
    """Fixture to create an SMSAPI client."""
    return SMSAPI(user="test_user", password="test_password")


def test_send_sms_success(monkeypatch, sms_client):
    """Test that SMS is sent successfully when the API returns 200."""

    def mock_get(url):
        mock_response = MagicMock()
        mock_response.status_code = 200
        return mock_response

    monkeypatch.setattr("services.free_sms_alert.main.requests.get", mock_get)

    sms_client.send_sms("Hello, this is a test message!")
    # No exceptions mean success.


def test_send_sms_error_400(monkeypatch, sms_client):
    """Test that a MissingParameter exception is raised for HTTP 400."""

    def mock_get(url):
        mock_response = MagicMock()
        mock_response.status_code = 400
        return mock_response

    monkeypatch.setattr("services.free_sms_alert.main.requests.get", mock_get)

    with pytest.raises(MissingParameter):
        sms_client.send_sms("Test message")
