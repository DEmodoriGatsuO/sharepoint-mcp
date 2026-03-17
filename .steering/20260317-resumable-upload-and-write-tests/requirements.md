# Requirements: Resumable Upload and Write Tool Tests

## Background

A code review identified two medium-priority improvements after the initial security fixes were merged.

---

## Issue 1 — Large File Upload Falls Back to Simple PUT

### Problem

`upload_document` in `utils/graph_client.py` logged a warning and fell back to a simple PUT request for files larger than 4 MB. Simple PUT uploads are not supported by the Microsoft Graph API for files above this threshold, so any upload of a large document would silently fail.

### Acceptance Criteria

- Files ≥ 4 MB must use a Microsoft Graph API resumable upload session.
- The implementation must follow the Graph API upload session protocol:
  - POST to `createUploadSession` to obtain an upload URL.
  - PUT file content to the upload URL in chunks of 5 MB (a multiple of 320 KB).
  - Each chunk carries a `Content-Range` header.
- Files < 4 MB must continue to use the existing simple PUT path.
- All existing tests must continue to pass.
- New tests must cover both the small-file and large-file upload paths.

---

## Issue 2 — No Tests for Write Tools

### Problem

The test suite covered only read-oriented `GraphClient` methods. The following write/mutation methods had zero test coverage:

- `upload_file`
- `upload_document` (both small and large paths)
- `create_list_item`
- `update_list_item`
- `create_site`

### Acceptance Criteria

- Each write method listed above must have at least one test covering the happy path.
- Error cases must be tested where the method raises on a non-success HTTP status.
- Tests must use `unittest.mock.patch` on the relevant `requests.*` function.
