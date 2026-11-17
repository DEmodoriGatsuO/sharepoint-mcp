"""Regression tests: an expired token must be refreshed, not rejected."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from auth.sharepoint_auth import SharePointContext, refresh_token_if_needed
from tools._tool_helpers import _check_auth


def _fresh_context() -> SharePointContext:
    return SharePointContext(
        access_token="new_token", token_expiry=datetime.now() + timedelta(hours=1)
    )


def test_check_auth_accepts_expired_token():
    """An expired token is handled by refresh_token_if_needed, not rejected."""
    expired = SharePointContext(
        access_token="old_token", token_expiry=datetime.now() - timedelta(minutes=5)
    )
    _check_auth(expired)  # must not raise


def test_check_auth_rejects_missing_context():
    with pytest.raises(Exception, match="SharePoint authentication failed"):
        _check_auth(None)


async def test_refresh_replaces_expired_token():
    expired = SharePointContext(
        access_token="old_token", token_expiry=datetime.now() - timedelta(minutes=5)
    )
    with patch(
        "auth.sharepoint_auth.get_auth_context",
        new=AsyncMock(return_value=_fresh_context()),
    ):
        await refresh_token_if_needed(expired)

    assert expired.access_token == "new_token"
    assert expired.is_token_valid()


async def test_refresh_recovers_from_startup_error_context():
    error_ctx = SharePointContext(
        access_token="error", token_expiry=datetime.now() + timedelta(seconds=10)
    )
    with patch(
        "auth.sharepoint_auth.get_auth_context",
        new=AsyncMock(return_value=_fresh_context()),
    ):
        await refresh_token_if_needed(error_ctx)

    assert error_ctx.access_token == "new_token"


async def test_refresh_keeps_valid_token():
    valid = _fresh_context()
    mock = AsyncMock()
    with patch("auth.sharepoint_auth.get_auth_context", new=mock):
        await refresh_token_if_needed(valid)

    mock.assert_not_called()
    assert valid.access_token == "new_token"
