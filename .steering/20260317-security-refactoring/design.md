# Design: Security Fix and Resource Refactoring

## Issue 1 — Remove File-Based Token Cache

### Root Cause Analysis

`get_auth_context()` in `auth/sharepoint_auth.py` used `msal.SerializableTokenCache` to persist the MSAL token cache across process restarts. On each invocation it:

1. Loaded `.token_cache` from disk and deserialized it into the cache object.
2. Passed the cache to `msal.ConfidentialClientApplication`.
3. Attempted `acquire_token_silent()` using accounts found in the cache.
4. Fell back to `acquire_token_for_client()` if silent acquisition failed.
5. Re-serialized the cache and wrote it back to `.token_cache`.

For the **client credentials flow** (`acquire_token_for_client`), the cache stores the access token itself — not a refresh token — so the file directly contained a live bearer token.

### Design Decision

Remove file-based persistence entirely. Rationale:

- The server calls `get_auth_context()` once at startup (via FastMCP lifespan), and `refresh_token_if_needed()` on subsequent calls within the same process. Persistence across restarts provides minimal benefit.
- `acquire_token_for_client()` is fast (single HTTPS POST to Azure AD). The overhead of re-acquiring on restart is negligible.
- Keeping tokens in memory only is the safest default for a server-side application.

### Changes

| File | Change |
|------|--------|
| `auth/sharepoint_auth.py` | Remove `import os`, remove `TOKEN_CACHE_FILE` import, replace `msal.SerializableTokenCache()` with no cache argument, remove file load/save blocks, remove `get_accounts()` / `acquire_token_silent()` attempt |
| `config/settings.py` | Remove `TOKEN_CACHE_FILE = ".token_cache"` constant |

### Flow After Change

```
get_auth_context()
  └─ ConfidentialClientApplication (in-memory cache only)
       └─ acquire_token_for_client()  ← always called; fast HTTPS roundtrip
            └─ return SharePointContext(access_token, token_expiry)
```

---

## Issue 2 — Refactor `resources/site.py` to Use GraphClient

### Root Cause Analysis

`resources/site.py` imported `requests` directly and built the URL, headers, and error handling manually. The `GraphClient` abstraction in `utils/graph_client.py` was created precisely to centralise this logic, but `resources/site.py` was never updated to use it.

The root site URL bug originated from a copy-paste omission: the branch `if site_name == "root" or not site_name` that exists in `auth/sharepoint_auth.py` was missing here, so the URL was always constructed as `sites/{domain}:/sites/{site_name}` regardless of whether the site was a root site.

### Design Decision

Replace the raw `requests.get()` call with `GraphClient.get()`, aligning `resources/site.py` with every other file that accesses the Graph API. Remove all dead (commented-out) code.

### Changes

| File | Change |
|------|--------|
| `resources/site.py` | Remove `import requests`, add `from utils.graph_client import GraphClient`, replace raw HTTP call with `await GraphClient(sp_ctx).get(endpoint)`, add root-site URL branch, remove ~45 lines of commented-out placeholder code |

### URL Construction Logic (aligned with `auth/sharepoint_auth.py`)

```python
if site_name == "root" or not site_name:
    endpoint = f"sites/{domain}:"          # root site
else:
    endpoint = f"sites/{domain}:/sites/{site_name}"  # named site
```

### Error Handling

`GraphClient.get()` raises an `Exception` on non-200 responses. The existing `try/except Exception` block in the handler catches this and returns a descriptive error string, which is the expected MCP resource error pattern.
