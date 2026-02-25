from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from auth.sharepoint_auth import SharePointContext


def test_sharepoint_context_headers():
    """Test that headers are correctly generated from context."""
    context = SharePointContext(
        access_token="test_token", token_expiry=datetime.now() + timedelta(hours=1)
    )

    headers = context.headers
    assert headers["Authorization"] == "Bearer test_token"
    assert headers["Content-Type"] == "application/json"


def test_token_expiry():
    """Test token expiry checking."""
    # Token is valid
    context = SharePointContext(
        access_token="test_token", token_expiry=datetime.now() + timedelta(hours=1)
    )
    assert context.is_token_valid()

    # Token is expired
    context = SharePointContext(
        access_token="test_token", token_expiry=datetime.now() - timedelta(hours=1)
    )
    assert not context.is_token_valid()

    # Null expiry
    context = SharePointContext(access_token="test_token", token_expiry=None)
    assert not context.is_token_valid()


@patch("requests.get")
def test_test_connection(mock_get):
    """Test the connection test method."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # Create context
    context = SharePointContext(
        access_token="test_token", token_expiry=datetime.now() + timedelta(hours=1)
    )

    # Test with environment variables
    with patch.dict(
        "os.environ", {"SITE_URL": "https://contoso.sharepoint.com/sites/test"}
    ):
        assert context.test_connection()

    # Test failure case
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    with patch.dict(
        "os.environ", {"SITE_URL": "https://contoso.sharepoint.com/sites/test"}
    ):
        assert not context.test_connection()
