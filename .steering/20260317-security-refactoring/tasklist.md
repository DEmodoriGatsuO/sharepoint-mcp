# Task List: Security Fix and Resource Refactoring

## Tasks

### Issue 1 — Remove File-Based Token Cache

| # | Task | Status |
|---|------|--------|
| 1 | Remove `TOKEN_CACHE_FILE` constant from `config/settings.py` | ✅ Done |
| 2 | Remove `import os` and `TOKEN_CACHE_FILE` import from `auth/sharepoint_auth.py` | ✅ Done |
| 3 | Remove `msal.SerializableTokenCache()` instantiation and file load block | ✅ Done |
| 4 | Remove `token_cache=cache` parameter from `ConfidentialClientApplication` | ✅ Done |
| 5 | Remove `get_accounts()` / `acquire_token_silent()` attempt (cache always empty without file) | ✅ Done |
| 6 | Remove file write block after token acquisition | ✅ Done |

### Issue 2 — Refactor `resources/site.py`

| # | Task | Status |
|---|------|--------|
| 7 | Replace `import requests` with `from utils.graph_client import GraphClient` | ✅ Done |
| 8 | Replace raw `requests.get()` + manual header construction with `GraphClient.get()` | ✅ Done |
| 9 | Add missing root-site URL branch (`if site_name == "root" or not site_name`) | ✅ Done |
| 10 | Remove ~45 lines of commented-out placeholder code | ✅ Done |

### Verification

| # | Task | Status |
|---|------|--------|
| 11 | Run `black .` — no formatting issues | ✅ Done |
| 12 | Run `ruff check .` — no lint errors | ✅ Done |
| 13 | Run `pytest` — 9/9 tests pass | ✅ Done |

## Completion Criteria

- [x] No access token is written to disk in any form
- [x] `resources/site.py` uses `GraphClient` exclusively for Graph API calls
- [x] Root site URL construction is correct
- [x] No dead or commented-out code remains in `resources/site.py`
- [x] All quality checks pass
