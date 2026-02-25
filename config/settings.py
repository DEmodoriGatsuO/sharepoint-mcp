"""Configuration settings for the SharePoint MCP Server."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Basic settings
APP_NAME = "SharePoint MCP"
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# SharePoint connection settings
SHAREPOINT_CONFIG = {
    "tenant_id": os.getenv("TENANT_ID", ""),
    "client_id": os.getenv("CLIENT_ID", ""),
    "client_secret": os.getenv("CLIENT_SECRET", ""),
    "site_url": os.getenv("SITE_URL", ""),
    "username": os.getenv("USERNAME", ""),
    "password": os.getenv("PASSWORD", ""),
    "scope": [
        "https://graph.microsoft.com/.default",
        # The application must have these permissions:
        # - Sites.Read.All (for reading site content)
        # - Sites.ReadWrite.All (for modifying site content)
        # - Sites.Manage.All (for creating sites)
        # - Files.ReadWrite.All (for document operations)
    ],
}

# Microsoft Graph API settings
GRAPH_API_VERSION = "v1.0"
GRAPH_BASE_URL = f"https://graph.microsoft.com/{GRAPH_API_VERSION}"

# Token settings
TOKEN_CACHE_FILE = ".token_cache"

# Document processing settings
DOCUMENT_PROCESSING = {
    "max_text_preview_length": 5000,  # Maximum characters for text preview
    "max_rows_preview": 50,  # Maximum rows for CSV/Excel preview
    "supported_extensions": [
        "csv",
        "xlsx",
        "xls",
        "docx",
        "pdf",
        "txt",
        "md",
        "html",
        "htm",
    ],
}

# Content generation settings
CONTENT_GENERATION = {
    "default_audience": "general",
    "default_purpose": "general",
    "enable_rich_layout": True,
}
