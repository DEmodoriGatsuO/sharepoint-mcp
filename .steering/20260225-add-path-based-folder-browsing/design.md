# Design — Add Path-Based Folder Browsing and Document Access

## Implementation Approach

Apply the same path-based Graph API pattern already used by `upload_document` to read operations.
No new files will be created; changes are limited to appending methods and tools to the existing
`utils/graph_client.py` and `tools/site_tools.py`.

---

## Components to Change

| File | Change |
|------|--------|
| `utils/graph_client.py` | Add 3 new methods |
| `tools/site_tools.py` | Add 3 new `@mcp.tool()` definitions inside `register_site_tools()` |
| `docs/functional-design.md` | Add 3 rows to the tool table |

---

## Graph API Endpoints

| Tool | Method | Endpoint |
|------|--------|----------|
| `list_folder_contents` | GET | `sites/{site_id}/drives/{drive_id}/root/children` (root) |
| | GET | `sites/{site_id}/drives/{drive_id}/root:/{folder_path}:/children` (subfolder) |
| `get_document_by_path` | GET | `sites/{site_id}/drives/{drive_id}/root:/{file_path}:/content` |
| `get_item_metadata` | GET | `sites/{site_id}/drives/{drive_id}/root:/{item_path}` |

---

## GraphClient Methods (utils/graph_client.py)

### `list_folder_contents(site_id, drive_id, folder_path)`

```python
async def list_folder_contents(
    self, site_id: str, drive_id: str, folder_path: str = ""
) -> Dict[str, Any]:
```

- If `folder_path` is empty or `"/"`: use `root/children`
- Otherwise: use `root:/{folder_path}:/children`
- Sends a `GET` request and returns the raw JSON response

### `get_document_content_by_path(site_id, drive_id, file_path)`

```python
async def get_document_content_by_path(
    self, site_id: str, drive_id: str, file_path: str
) -> bytes:
```

- Endpoint: `sites/{site_id}/drives/{drive_id}/root:/{file_path}:/content`
- Strips `Content-Type` header before request (same pattern as `get_document_content`)
- Returns raw response bytes

### `get_item_metadata_by_path(site_id, drive_id, item_path)`

```python
async def get_item_metadata_by_path(
    self, site_id: str, drive_id: str, item_path: str
) -> Dict[str, Any]:
```

- Endpoint: `sites/{site_id}/drives/{drive_id}/root:/{item_path}`
- Sends a `GET` request and returns the raw JSON response

---

## MCP Tools (tools/site_tools.py)

### `list_folder_contents`

```
Parameters:
  site_id: str     — Site ID
  drive_id: str    — Drive (document library) ID
  folder_path: str — Folder path (e.g. "General", "Docs/2026"); omit for root

Returns: JSON array of items with name, type, size, id, web_url, last_modified
```

### `get_document_by_path`

```
Parameters:
  site_id: str   — Site ID
  drive_id: str  — Drive ID
  file_path: str — File path (e.g. "General/report.docx")
  filename: str  — File name used by DocumentProcessor for extension detection

Returns: JSON — result of DocumentProcessor.process_document()
```

### `get_item_metadata`

```
Parameters:
  site_id: str   — Site ID
  drive_id: str  — Drive ID
  item_path: str — Item path, file or folder (e.g. "General/report.docx")

Returns: JSON with id, name, size, web_url, created_by, created_datetime,
         last_modified_datetime, folder (if directory), file (if file)
```

---

## Data Structure Changes

None. No changes to `SharePointContext` or the existing `GraphClient` structure are required.

---

## Impact Analysis

| Scope | Detail |
|-------|--------|
| `utils/graph_client.py` | 3 methods appended at the end; no changes to existing methods |
| `tools/site_tools.py` | 3 tools added inside `register_site_tools()`; no changes to existing tools |
| `server.py` | No changes required |
| `tests/` | 3 new test cases added to `tests/test_graph_client.py` |
| Existing functionality | No impact |
