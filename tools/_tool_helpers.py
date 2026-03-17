"""Shared helpers for MCP tool modules."""


def _check_auth(sp_ctx) -> None:
    """Check if authentication context is valid, raise exception if not."""
    if not sp_ctx or sp_ctx.access_token == "error" or not sp_ctx.is_token_valid():
        raise Exception(
            "SharePoint authentication failed. Please check your configuration "
            "(CLIENT_ID, CLIENT_SECRET, TENANT_ID, SITE_URL)."
        )
