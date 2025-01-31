import os

import pytest

from services.free_sms_alert.main import SMSAPI, SMSAPIError


@pytest.fixture
def real_sms_client():
    """Fixture to create an SMSAPI client with real credentials."""
    # Replace with your real credentials
    user = os.getenv("FREE_MOBILE_USER_ID")
    password = os.getenv("FREE_MOBILE_API_KEY")

    assert (
        user is not None
    ), "Missing environment variable: FREE_MOBILE_USER_ID"
    assert (
        password is not None
    ), "Missing environment variable: FREE_MOBILE_API_KEY"

    return SMSAPI(user=user, password=password)


def test_send_sms_real(real_sms_client):
    """Test that SMS is sent successfully with real credentials."""
    try:
        real_sms_client.send_sms("Integration test message")
        print("Integration test passed: SMS sent successfully.")
    except SMSAPIError as e:
        pytest.fail(f"Integration test failed: {e}")
