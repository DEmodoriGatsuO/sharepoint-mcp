"""Authentication package for SharePoint MCP server."""

from .sharepoint_auth import (
    SharePointContext,
    get_auth_context,
    refresh_token_if_needed,
)

__all__ = ["SharePointContext", "get_auth_context", "refresh_token_if_needed"]
