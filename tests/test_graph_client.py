import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from auth.sharepoint_auth import SharePointContext
from utils.graph_client import GraphClient


@pytest.fixture
def mock_context():
    """Create a mock SharePoint context for testing."""
    return SharePointContext(
        access_token="test_token", token_expiry=datetime.now() + timedelta(hours=1)
    )


@pytest.fixture
def graph_client(mock_context):
    """Create a GraphClient instance with mock context."""
    return GraphClient(mock_context)


@patch("requests.get")
async def test_get(mock_get, graph_client):
    """Test the GET method of GraphClient."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"value": "test_data"}
    mock_get.return_value = mock_response

    # Test successful request
    result = await graph_client.get("endpoint/test")
    assert result == {"value": "test_data"}
    mock_get.assert_called_once_with(
        "https://graph.microsoft.com/v1.0/endpoint/test",
        headers=graph_client.context.headers,
    )

    # Test error response
    mock_get.reset_mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    with pytest.raises(Exception) as excinfo:
        await graph_client.get("endpoint/error")
    assert "Graph API error: 404" in str(excinfo.value)


@patch("requests.post")
async def test_post(mock_post, graph_client):
    """Test the POST method of GraphClient."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "new_item_id"}
    mock_post.return_value = mock_response

    # Test data
    test_data = {"name": "test_item"}

    # Test successful request
    result = await graph_client.post("endpoint/create", test_data)
    assert result == {"id": "new_item_id"}
    mock_post.assert_called_once_with(
        "https://graph.microsoft.com/v1.0/endpoint/create",
        headers=graph_client.context.headers,
        json=test_data,
    )

    # Test error response
    mock_post.reset_mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"

    with pytest.raises(Exception) as excinfo:
        await graph_client.post("endpoint/error", test_data)
    assert "Graph API error: 400" in str(excinfo.value)
