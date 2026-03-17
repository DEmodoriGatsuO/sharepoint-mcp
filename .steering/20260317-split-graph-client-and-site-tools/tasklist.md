# Task List: Split graph_client.py and site_tools.py

## Tasks

### Phase 1 — GraphClient Mixin Split

| # | Task | Status |
|---|------|--------|
| 1 | Create `utils/_graph_constants.py` with `LARGE_FILE_THRESHOLD` and `UPLOAD_CHUNK_SIZE` | ✅ Done |
| 2 | Create `utils/_graph_http.py` with `_GraphHttpMixin` (6 methods) | ✅ Done |
| 3 | Create `utils/_graph_site_ops.py` with `_GraphSiteOpsMixin` (3 methods) | ✅ Done |
| 4 | Create `utils/_graph_list_ops.py` with `_GraphListOpsMixin` (7 methods + schema data) | ✅ Done |
| 5 | Create `utils/_graph_page_ops.py` with `_GraphPageOpsMixin` (7 methods) | ✅ Done |
| 6 | Create `utils/_graph_drive_ops.py` with `_GraphDriveOpsMixin` (9 methods + metadata/folder data) | ✅ Done |
| 7 | Replace `utils/graph_client.py` with thin facade: `GraphClient(mixins)` + re-export constants | ✅ Done |

### Phase 2 — site_tools.py Domain Split

| # | Task | Status |
|---|------|--------|
| 8 | Create `tools/_tool_helpers.py` with `_check_auth` shared helper | ✅ Done |
| 9 | Create `tools/read_tools.py` with `register_read_tools` (7 tools) | ✅ Done |
| 10 | Create `tools/write_tools.py` with `register_write_tools` (3 tools) | ✅ Done |
| 11 | Create `tools/provisioning_tools.py` with `register_provisioning_tools` (5 tools) | ✅ Done |
| 12 | Replace `tools/site_tools.py` with 10-line delegator | ✅ Done |

### Phase 3 — Quality Checks

| # | Task | Status |
|---|------|--------|
| 13 | Run `black .` — no formatting issues | ✅ Done |
| 14 | Run `ruff check .` — no lint errors | ✅ Done |
| 15 | Run `pytest` — 15/15 tests pass | ✅ Done |
| 16 | Verify `server.py` unchanged | ✅ Done |
| 17 | Verify `tests/test_graph_client.py` unchanged | ✅ Done |

## Completion Criteria

- [x] `utils/graph_client.py` reduced from ~1,350 lines to ~30 lines
- [x] No single mixin file exceeds 300 lines
- [x] `tools/site_tools.py` reduced from 693 lines to ~10 lines
- [x] No single tool module exceeds 230 lines
- [x] `GraphClient`, `LARGE_FILE_THRESHOLD`, `UPLOAD_CHUNK_SIZE` importable from `utils.graph_client`
- [x] `register_site_tools` importable from `tools.site_tools`
- [x] No changes to `server.py`, `auth/`, `config/`, `resources/`, or `tests/`
- [x] All quality checks pass
