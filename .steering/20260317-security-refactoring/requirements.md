# Requirements: Security Fix and Resource Refactoring

## Background

A code review identified two high-priority issues that needed to be addressed before continuing with further feature development.

---

## Issue 1 — Plaintext Token Cache on Disk

### Problem

`auth/sharepoint_auth.py` was persisting the MSAL token cache to a local file (`.token_cache`) in plaintext JSON. This file contains a valid Microsoft Graph API access token, which grants full SharePoint access for up to one hour.

**Risk**: Any process or user with read access to the working directory can steal an active access token.

### Acceptance Criteria

- Access tokens must not be written to disk in any form.
- Token acquisition must still succeed for the client credentials flow.
- All existing tests must continue to pass.

---

## Issue 2 — Inconsistent HTTP Access in `resources/site.py`

### Problem

`resources/site.py` used `import requests` to make raw HTTP calls directly, bypassing the `GraphClient` abstraction used everywhere else. This caused two problems:

1. **Inconsistency**: Error handling, logging, and auth header management were duplicated outside of `GraphClient`.
2. **Bug**: The root SharePoint site URL was constructed incorrectly — the `else` branch for root sites (`sites/{domain}:`) was missing, meaning root-site deployments would always produce a malformed URL.

Additionally, the file contained ~45 lines of commented-out placeholder code in Japanese, increasing maintenance noise.

### Acceptance Criteria

- `resources/site.py` must use `GraphClient` for all Graph API calls.
- Root site and named site URL construction must match the logic in `auth/sharepoint_auth.py`.
- All commented-out dead code must be removed.
- All existing tests must continue to pass.
