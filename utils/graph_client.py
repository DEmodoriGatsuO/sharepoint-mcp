"""Microsoft Graph API client for SharePoint MCP server."""

import logging

from auth.sharepoint_auth import SharePointContext
from utils._graph_constants import LARGE_FILE_THRESHOLD, UPLOAD_CHUNK_SIZE  # noqa: F401
from utils._graph_drive_ops import _GraphDriveOpsMixin
from utils._graph_http import _GraphHttpMixin
from utils._graph_list_ops import _GraphListOpsMixin
from utils._graph_page_ops import _GraphPageOpsMixin
from utils._graph_site_ops import _GraphSiteOpsMixin

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("graph_client")


class GraphClient(
    _GraphSiteOpsMixin,
    _GraphListOpsMixin,
    _GraphPageOpsMixin,
    _GraphDriveOpsMixin,
    _GraphHttpMixin,
):
    """Client for interacting with Microsoft Graph API."""

    def __init__(self, context: SharePointContext):
        """Initialize Graph client with SharePoint context."""
        self.context = context
        self.base_url = context.graph_url
        logger.debug(f"GraphClient initialized with base URL: {self.base_url}")
