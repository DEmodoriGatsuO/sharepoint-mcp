# Task List — Add Path-Based Folder Browsing and Document Access

## Completion Criteria

- `list_folder_contents`, `get_document_by_path`, and `get_item_metadata` tools are
  functional and registered in `register_site_tools()`
- Corresponding `GraphClient` methods exist in `utils/graph_client.py`
- New tests added to `tests/test_graph_client.py`
- `black`, `ruff`, and `pytest` all pass with zero errors
- PR references `Closes #6`

---

## Tasks

### Phase 1: Branch Setup

- [x] Create branch `fix/issue-6-path-based-folder-browsing`

### Phase 2: GraphClient Methods (utils/graph_client.py)

- [ ] Add `list_folder_contents(site_id, drive_id, folder_path)` method
  - Empty / `"/"` path → `root/children`
  - Non-empty path → `root:/{folder_path}:/children`
- [ ] Add `get_document_content_by_path(site_id, drive_id, file_path)` method
  - Endpoint: `root:/{file_path}:/content`
  - Return raw bytes (same pattern as `get_document_content`)
- [ ] Add `get_item_metadata_by_path(site_id, drive_id, item_path)` method
  - Endpoint: `root:/{item_path}`
  - Return JSON dict

### Phase 3: MCP Tools (tools/site_tools.py)

- [ ] Add `list_folder_contents` tool
  - Parameters: `site_id`, `drive_id`, `folder_path` (default `""`)
  - Format response: list of items with `name`, `type`, `size`, `id`, `web_url`, `last_modified`
- [ ] Add `get_document_by_path` tool
  - Parameters: `site_id`, `drive_id`, `file_path`, `filename`
  - Delegate to `DocumentProcessor.process_document()`
- [ ] Add `get_item_metadata` tool
  - Parameters: `site_id`, `drive_id`, `item_path`
  - Format response: `id`, `name`, `size`, `web_url`, `created_datetime`, `last_modified_datetime`, `folder` / `file` fields

### Phase 4: Tests (tests/test_graph_client.py)

- [ ] Add test for `list_folder_contents` (root path)
- [ ] Add test for `list_folder_contents` (subfolder path)
- [ ] Add test for `get_document_content_by_path`
- [ ] Add test for `get_item_metadata_by_path`

### Phase 5: Documentation

- [ ] Update `docs/functional-design.md` — add 3 rows to the tool table

### Phase 6: Quality Checks

- [ ] `black .` — zero reformats
- [ ] `ruff check .` — zero errors
- [ ] `pytest` — all tests pass

### Phase 7: Commit & PR

- [ ] Commit with message `fix: #6 - add path-based folder browsing and document access tools`
- [ ] Push branch and create PR referencing `Closes #6`
