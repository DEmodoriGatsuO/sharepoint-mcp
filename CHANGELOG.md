# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security

- **Remove plaintext token cache** (`auth/sharepoint_auth.py`): The MSAL token cache is now
  kept in memory only. The `.token_cache` file — which previously stored a live Microsoft Graph
  API access token in plaintext — is no longer written to disk. The `TOKEN_CACHE_FILE` constant
  has been removed from `config/settings.py`.

### Fixed

- **Root site URL bug** (`resources/site.py`): Requests to root SharePoint sites (URLs without
  a `/sites/{name}` path segment) were constructing a malformed Graph API endpoint. The URL
  branching logic now matches `auth/sharepoint_auth.py` and handles both root and named sites
  correctly.

### Refactored

- **`resources/site.py` uses `GraphClient`**: Replaced the direct `requests.get()` call with
  `GraphClient.get()`, aligning the resource handler with the rest of the codebase. Removed
  ~45 lines of commented-out placeholder code.

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