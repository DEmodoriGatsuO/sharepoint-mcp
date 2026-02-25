# Requirements — Add Path-Based Folder Browsing and Document Access

## Background

Ref: https://github.com/DEmodoriGatsuO/sharepoint-mcp/issues/6

Currently, `get_document_content` requires an `item_id` that cannot be discovered
through existing tools. `list_document_libraries` only shows top-level drives.
Users have no way to browse folder structures or retrieve documents by path,
making the server difficult to use in practice.

`upload_document` already uses the path-based Graph API pattern
(`root:/{folder_path}/{file_name}:/content`), so the same approach should be
applied consistently to read operations.

## User Stories

### US-F01: Browse Folder Contents
**As a** knowledge worker,
**I want to** list files and subfolders inside a specific folder in a document library,
**So that** I can discover documents without needing to know item IDs in advance.

### US-F02: Retrieve Document Content by Path
**As a** knowledge worker,
**I want to** read a document by specifying its folder path and file name,
**So that** I can access content directly without first running a search or metadata lookup.

### US-F03: Get Item Metadata by Path
**As a** knowledge worker,
**I want to** get the metadata (name, size, modified date, item_id) of a file or folder by path,
**So that** I can inspect an item and obtain its `item_id` for use with other tools.

## Acceptance Criteria

- [ ] `list_folder_contents(site_id, drive_id, folder_path)` returns a list of items in the given folder; `folder_path=""` or `"/"` returns the root of the drive
- [ ] `get_document_by_path(site_id, drive_id, file_path, filename)` returns parsed document content (delegates to `DocumentProcessor`)
- [ ] `get_item_metadata(site_id, drive_id, item_path)` returns name, size, item_id, web_url, created/modified datetimes
- [ ] All three tools handle authentication, token refresh, and Graph API errors consistently with existing tools
- [ ] All three tools are registered in `register_site_tools()`
- [ ] Corresponding `GraphClient` methods are added to `utils/graph_client.py`
- [ ] `black` + `ruff` + `pytest` all pass

## Constraints

- Use Microsoft Graph API v1.0 only
- Path-based endpoints: `sites/{site_id}/drives/{drive_id}/root:/{path}:/children`, `root:/{path}`, `root:/{path}:/content`
- For root-level listing, use `sites/{site_id}/drives/{drive_id}/root/children`
- Consistent with existing tool patterns (`_check_auth`, `refresh_token_if_needed`, `GraphClient`)
