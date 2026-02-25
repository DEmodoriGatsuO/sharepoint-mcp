# Product Requirements

> This document defines the product vision, target users, key features, and success criteria for the SharePoint MCP Server.

---

## Product Vision

SharePoint MCP Server is an open-source Model Context Protocol (MCP) server that acts as a bridge between LLM applications and Microsoft SharePoint. It enables users to interact with SharePoint content using natural language through LLM clients such as Claude Desktop.

---

## Target Users

| User Type | Description |
|-----------|-------------|
| Knowledge Workers | Users who work with SharePoint daily and want to access documents and lists via natural language |
| Developers | Engineers integrating SharePoint capabilities into LLM-based applications |
| IT Administrators | Admins who deploy and manage the MCP server within an organization |

---

## Key Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | Site Information | Retrieve basic information about a SharePoint site |
| 2 | Document Library Browsing | List all document libraries in a site |
| 3 | Document Content Retrieval | Fetch and process content from documents (DOCX, PDF, XLSX, CSV, TXT) |
| 4 | SharePoint Search | Full-text search across site content |
| 5 | List Item Management | Create and update items in SharePoint lists |
| 6 | Intelligent List Creation | Create lists with AI-optimized schemas based on purpose |
| 7 | Advanced Document Library | Create document libraries with rich metadata settings |
| 8 | Modern Page Creation | Create and publish SharePoint modern pages |
| 9 | News Post Creation | Create news posts in a SharePoint site |
| 10 | Site Creation | Create new SharePoint team sites |

---

## User Stories

### US-01: Retrieve Site Information
**As a** knowledge worker,
**I want to** ask the LLM "What is this SharePoint site about?",
**So that** I can quickly understand the site's purpose without navigating the SharePoint UI.

### US-02: Browse Document Libraries
**As a** knowledge worker,
**I want to** list available document libraries in my SharePoint site,
**So that** I can find the right library for my documents.

### US-03: Search Content
**As a** knowledge worker,
**I want to** search for documents or list items using natural language,
**So that** I can locate content without knowing exact file names or locations.

### US-04: Read Document Content
**As a** knowledge worker,
**I want to** read the content of a SharePoint document (PDF, DOCX, XLSX) via the LLM,
**So that** I can analyze or summarize it without downloading the file.

### US-05: Create List Items
**As a** knowledge worker,
**I want to** add new items to a SharePoint list via natural language,
**So that** I can update lists quickly without opening the SharePoint UI.

### US-06: Create SharePoint Assets
**As a** developer or admin,
**I want to** create sites, lists, document libraries, and pages through the LLM,
**So that** I can automate SharePoint provisioning tasks.

---

## Acceptance Criteria

| Feature | Criteria |
|---------|----------|
| Authentication | Server authenticates to Microsoft Graph API using client credentials (client secret or certificate) |
| Site Info | Returns site name, description, creation date, URL |
| Document Libraries | Returns a list of drives with name, type, and URL |
| Search | Returns matching items with title, URL, type, and summary |
| Document Content | Supports DOCX, PDF, XLSX, CSV, TXT; returns parsed content |
| List Item Create | Creates item with specified fields; returns created item ID |
| List Item Update | Updates specified fields; returns updated item |
| Error Handling | All tool errors surface as MCP tool errors with descriptive messages |
| Token Refresh | Access token is automatically refreshed before expiry |

---

## Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Security | Credentials stored in `.env` (never committed to version control) |
| Compatibility | Python 3.10+; MCP SDK compatible |
| Portability | Runnable in Docker, devcontainer, or local venv |
| Observability | Structured logging with configurable DEBUG mode |
| Maintainability | Code formatted with `black`, linted with `ruff`, tested with `pytest` |

---

## Business Requirements

- Must not be affiliated with or endorsed by Microsoft Corporation (see Disclaimer)
- Must comply with Microsoft Graph API terms of service
- All Microsoft Graph API permission changes must be documented in `docs/auth_guide.md`
- Project is open-source under MIT License
