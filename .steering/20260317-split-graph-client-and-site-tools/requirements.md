# Requirements: Split graph_client.py and site_tools.py

## Background

A code review identified two large files that were growing difficult to navigate:

- `utils/graph_client.py` — ~1,350 lines, a single `GraphClient` class with 32 methods spanning HTTP transport, site operations, list CRUD, page management, and drive/file operations.
- `tools/site_tools.py` — 693 lines, a single `register_site_tools()` function registering 15 MCP tools of three distinct responsibilities: read-only access, write mutations, and provisioning.

Neither file violated correctness, but the size made it hard to locate code by domain and increased the cognitive overhead of every code review.

---

## Issue 1 — `utils/graph_client.py` Too Large

### Problem

All 32 methods coexist in one class. A developer fixing a list-schema bug must scroll past HTTP transport boilerplate, page layout logic, and folder-structure generators to reach the relevant code. Method interdependencies (e.g. `create_advanced_document_library` calls `self.add_column_to_list()` and `self.create_folder_in_library()`) prevent a naive class-per-domain split because all `self.*` calls must resolve to the same instance.

### Acceptance Criteria

- Methods are split into logical domain groups, each in its own file.
- `GraphClient` continues to be importable from `utils.graph_client` with no change to its public API.
- `LARGE_FILE_THRESHOLD` and `UPLOAD_CHUNK_SIZE` continue to be importable from `utils.graph_client`.
- No changes to any file that imports `GraphClient`.
- All existing tests pass unchanged.

---

## Issue 2 — `tools/site_tools.py` Too Large

### Problem

All 15 MCP tools are registered by a single `register_site_tools()` function. The file mixes read-only tools (no side effects) with write tools (CRUD mutations) and provisioning tools (create top-level SharePoint structures). This makes the file hard to scan and means every contributor edits the same file regardless of which category they are working on.

### Acceptance Criteria

- Tools are split into files by responsibility: read, write, and provisioning.
- The `_check_auth` helper used by all 15 tools is not duplicated.
- `register_site_tools()` continues to be importable from `tools.site_tools` with the same signature.
- `server.py` requires no changes.
- All existing tests pass unchanged.
