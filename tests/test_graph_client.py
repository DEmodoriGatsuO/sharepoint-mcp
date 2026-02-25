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


@patch("requests.get")
async def test_list_folder_contents_root(mock_get, graph_client):
    """Test list_folder_contents with an empty path (root listing)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "value": [{"name": "General", "folder": {}, "id": "abc123"}]
    }
    mock_get.return_value = mock_response

    result = await graph_client.list_folder_contents("site1", "drive1", "")
    assert result["value"][0]["name"] == "General"
    call_url = mock_get.call_args[0][0]
    assert "root/children" in call_url
    assert "root:/" not in call_url


@patch("requests.get")
async def test_list_folder_contents_subfolder(mock_get, graph_client):
    """Test list_folder_contents with a subfolder path."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "value": [{"name": "report.docx", "file": {}, "id": "def456"}]
    }
    mock_get.return_value = mock_response

    result = await graph_client.list_folder_contents("site1", "drive1", "General")
    assert result["value"][0]["name"] == "report.docx"
    call_url = mock_get.call_args[0][0]
    assert "root:/General:/children" in call_url


@patch("requests.get")
async def test_get_document_content_by_path(mock_get, graph_client):
    """Test get_document_content_by_path returns bytes content."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"file content bytes"
    mock_get.return_value = mock_response

    result = await graph_client.get_document_content_by_path(
        "site1", "drive1", "General/report.docx"
    )
    assert result == b"file content bytes"
    call_url = mock_get.call_args[0][0]
    assert "root:/General/report.docx:/content" in call_url


@patch("requests.get")
async def test_get_item_metadata_by_path(mock_get, graph_client):
    """Test get_item_metadata_by_path returns item metadata dict."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "abc123",
        "name": "report.docx",
        "size": 4096,
        "webUrl": "https://contoso.sharepoint.com/sites/test/report.docx",
    }
    mock_get.return_value = mock_response

    result = await graph_client.get_item_metadata_by_path(
        "site1", "drive1", "General/report.docx"
    )
    assert result["id"] == "abc123"
    assert result["name"] == "report.docx"
    call_url = mock_get.call_args[0][0]
    assert "root:/General/report.docx" in call_url
