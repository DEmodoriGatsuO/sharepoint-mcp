# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Resumable upload for large files** (`utils/graph_client.py`): Files ≥ 4 MB now use
  the Microsoft Graph API upload session protocol (POST `createUploadSession`, then PUT
  chunks of 5 MB with `Content-Range` headers) instead of falling back to a simple PUT
  that would fail silently. Added `LARGE_FILE_THRESHOLD` and `UPLOAD_CHUNK_SIZE` module
  constants and a new `_upload_in_chunks()` helper method.
- **Write tool test coverage** (`tests/test_graph_client.py`): Added six tests covering
  `upload_file`, `upload_document` (small and large paths), `create_list_item`,
  `update_list_item`, and `create_site`. Test count raised from 9 to 15.

---

## [0.1.0] - 2025-04-07

### Added
- Initial release
- SharePoint authentication using MSAL library
- Microsoft Graph API integration for SharePoint access
- MCP protocol implementation for LLM applications
- Site information and document library resources
- Basic SharePoint search functionality
- Authentication diagnostic tools
- Token analysis utilities