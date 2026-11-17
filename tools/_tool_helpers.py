"""Shared helpers for MCP tool modules."""


def _check_auth(sp_ctx) -> None:
    """Check that an authentication context exists.

    An expired token or the startup error context is not a failure here:
    ``refresh_token_if_needed`` runs right after this check and re-authenticates
    in both cases. Raising on expiry would make every call fail once the first
    token (valid for about an hour) has expired.
    """
    if not sp_ctx:
        raise Exception(
            "SharePoint authentication failed. Please check your configuration "
            "(CLIENT_ID, CLIENT_SECRET, TENANT_ID, SITE_URL)."
        )
