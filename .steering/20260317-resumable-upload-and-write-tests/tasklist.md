# Task List: Resumable Upload and Write Tool Tests

## Tasks

### Issue 1 — Resumable Upload

| # | Task | Status |
|---|------|--------|
| 1 | Add `LARGE_FILE_THRESHOLD` and `UPLOAD_CHUNK_SIZE` constants to `graph_client.py` | ✅ Done |
| 2 | Add `_upload_in_chunks()` private method to `GraphClient` | ✅ Done |
| 3 | Update `upload_document()` to use upload session for files ≥ `LARGE_FILE_THRESHOLD` | ✅ Done |

### Issue 2 — Write Tool Tests

| # | Task | Status |
|---|------|--------|
| 4 | Add `test_upload_file` — happy path + error case | ✅ Done |
| 5 | Add `test_upload_document_small` — verifies simple PUT path | ✅ Done |
| 6 | Add `test_upload_document_large` — verifies session creation + two-chunk upload | ✅ Done |
| 7 | Add `test_create_list_item` — happy path with body verification | ✅ Done |
| 8 | Add `test_update_list_item` — happy path + error case | ✅ Done |
| 9 | Add `test_create_site` — happy path with body verification | ✅ Done |

### Verification

| # | Task | Status |
|---|------|--------|
| 10 | Run `black .` — no formatting issues | ✅ Done |
| 11 | Run `ruff check .` — no lint errors | ✅ Done |
| 12 | Run `pytest` — 15/15 tests pass (9 existing + 6 new) | ✅ Done |

## Completion Criteria

- [x] Files ≥ 4 MB use a resumable upload session (no more silent fallback)
- [x] `LARGE_FILE_THRESHOLD` and `UPLOAD_CHUNK_SIZE` are exported constants (testable)
- [x] All five previously untested write methods now have test coverage
- [x] All quality checks pass
