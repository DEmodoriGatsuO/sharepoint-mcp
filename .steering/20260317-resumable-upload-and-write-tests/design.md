# Design: Resumable Upload and Write Tool Tests

## Issue 1 — Resumable Upload Session

### Microsoft Graph API Upload Session Protocol

For files above 4 MB, the Graph API requires a two-phase upload:

1. **Create session** — POST to `…/createUploadSession` with an empty JSON body.
   The response contains an `uploadUrl` (a pre-authenticated Azure Blob URL, valid for a few days).

2. **Upload chunks** — PUT successive byte ranges to `uploadUrl`.
   Each request must include:
   ```
   Content-Range: bytes {start}-{end}/{total}
   Content-Length: {chunk_size}
   ```
   The server responds with `202 Accepted` for intermediate chunks and `200 OK` / `201 Created`
   for the final chunk, at which point the response body contains the created `driveItem`.

### Chunk Size Constraint

The Graph API requires that each chunk (except the last) be a multiple of 320 KB (327,680 bytes).
A chunk size of 5 MB (5,242,880 bytes = 16 × 320 KB) satisfies this constraint.

### Constants Added to `graph_client.py`

```python
LARGE_FILE_THRESHOLD = 4 * 1024 * 1024   # 4 MB — boundary between simple and resumable upload
UPLOAD_CHUNK_SIZE    = 5 * 1024 * 1024   # 5 MB — chunk size (multiple of 320 KB)
```

### New Method: `_upload_in_chunks()`

A private helper that accepts a pre-obtained `uploadUrl` and uploads the content in
`UPLOAD_CHUNK_SIZE`-sized pieces. It tracks `start`/`end` byte positions, sets the
`Content-Range` header on each PUT, and returns the final `driveItem` JSON.

### Updated Method: `upload_document()`

```
if len(file_content) < LARGE_FILE_THRESHOLD:
    → upload_file()          # simple PUT, unchanged
else:
    → POST createUploadSession
    → _upload_in_chunks()   # chunked PUT to uploadUrl
```

The `createUploadSession` endpoint is constructed by replacing `:/content` with
`:/createUploadSession` in the item path, e.g.:
```
sites/{id}/drives/{id}/root:/{path}/{name}:/createUploadSession
```

---

## Issue 2 — Write Tool Test Design

### Strategy

Tests are added to `tests/test_graph_client.py` using the same pattern established by the
existing tests: `@patch("requests.<verb>")` + `MagicMock` response objects.

### New Tests

| Test | Method under test | HTTP verb mocked |
|------|-------------------|-----------------|
| `test_upload_file` | `upload_file()` | `requests.put` |
| `test_upload_document_small` | `upload_document()` small path | `requests.put` |
| `test_upload_document_large` | `upload_document()` large path | `requests.post` + `requests.put` |
| `test_create_list_item` | `create_list_item()` | `requests.post` |
| `test_update_list_item` | `update_list_item()` | `requests.patch` |
| `test_create_site` | `create_site()` | `requests.post` |

### Large-File Test Strategy

`test_upload_document_large` uses `mock_put.side_effect` to return a 202 for the first chunk
and a 201 with a `driveItem` body for the second, verifying that:
- `createUploadSession` was called via POST
- Two PUT calls were made with correct `Content-Range` headers
- The final `driveItem` is returned as the result
