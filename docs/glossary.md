# Glossary

> This document defines domain terminology, business terms, and naming conventions used in the SharePoint MCP Server codebase and documentation.

---

## Domain Terminology

### Microsoft / SharePoint

| Term | Definition |
|------|-----------|
| **SharePoint** | Microsoft's web-based collaboration platform for document management and team sites |
| **SharePoint Online** | The cloud-hosted version of SharePoint, part of Microsoft 365 |
| **Microsoft Graph API** | Unified REST API for accessing Microsoft 365 services including SharePoint, Teams, and OneDrive |
| **Microsoft Entra ID** | Microsoft's cloud identity service (formerly Azure Active Directory / Azure AD) |
| **Azure AD** | Abbreviation still used in code and config; refers to Microsoft Entra ID |
| **Tenant** | An organization's instance of Microsoft 365 / Entra ID (identified by `TENANT_ID`) |
| **Site** | A SharePoint site collection (e.g., `https://{tenant}.sharepoint.com/sites/{name}`) |
| **Drive** | A SharePoint document library, accessed via Microsoft Graph as a Drive resource |
| **Document Library** | A SharePoint container for storing files; represented as a Drive in Graph API |
| **List** | A SharePoint structured data container (similar to a database table or spreadsheet) |
| **List Item** | A single row/record in a SharePoint List |
| **Modern Page** | A SharePoint page built with the modern experience framework (as opposed to classic pages) |
| **News Post** | A type of Modern Page with a news template; appears in the site's news feed |
| **Site Column** | A reusable metadata column defined at site level and available across lists/libraries |
| **Content Type** | A named collection of site columns defining a document or item schema in SharePoint |

### Authentication

| Term | Definition |
|------|-----------|
| **MSAL** | Microsoft Authentication Library — Python library for acquiring tokens from Entra ID |
| **Client Credentials Flow** | OAuth 2.0 flow for application-to-application auth (no user interaction); used in this project |
| **Access Token** | Short-lived JWT bearer token used to authenticate Graph API requests |
| **Token Expiry** | UTC datetime after which the access token is invalid and must be refreshed |
| **Client Secret** | A password-equivalent credential for a registered Entra ID application |
| **Application Permission** | A Graph API permission granted to an application (not a user); requires admin consent |
| **Admin Consent** | An Entra ID admin's approval for an application to use Application permissions |
| **Scope** | The set of Graph API permissions requested in a token; e.g., `https://graph.microsoft.com/.default` |

---

## MCP Terminology

| Term | Definition |
|------|-----------|
| **MCP** | Model Context Protocol — an open protocol for connecting LLM applications to external data sources and tools |
| **MCP Server** | A process that exposes tools and resources to an LLM client via MCP |
| **MCP Client** | An LLM application (e.g., Claude Desktop) that consumes MCP servers |
| **Tool** | An MCP-exposed function the LLM can invoke (e.g., `get_site_info`, `search_sharepoint`) |
| **Resource** | An MCP-exposed data source the LLM can read (e.g., `sharepoint://site-info`) |
| **FastMCP** | The high-level Python MCP framework used in this project (`mcp.server.fastmcp.FastMCP`) |
| **Lifespan** | An async context manager in FastMCP that manages server startup/shutdown and shared state |
| **Context** | The MCP request context passed to every tool/resource handler, providing access to lifespan state |

---

## Code Terminology

| Term / Symbol | Definition |
|--------------|-----------|
| `SharePointContext` | Dataclass holding the access token, expiry, and Graph base URL; passed through the MCP lifespan |
| `GraphClient` | Utility class wrapping HTTP calls to Microsoft Graph API |
| `DocumentProcessor` | Utility class for parsing document content (DOCX, PDF, XLSX, CSV, TXT) |
| `ContentGenerator` | Utility class generating SharePoint page titles and content based on purpose and audience |
| `SHAREPOINT_CONFIG` | Dict loaded from environment variables; contains tenant_id, client_id, client_secret, site_url |
| `_check_auth()` | Internal helper that raises if the `SharePointContext` token is missing or invalid |
| `refresh_token_if_needed()` | Async function that refreshes the access token if it is expired or near expiry |
| `register_site_tools()` | Function that registers all MCP tools with the `FastMCP` instance |
| `register_site_resources()` | Function that registers all MCP resources with the `FastMCP` instance |
| `HAS_DOCUMENT_LIBRARIES` | Boolean flag set at import time; `True` if all document-processing libraries are available |

---

## Naming Conventions in Code

| Pattern | Convention | Example |
|---------|-----------|---------|
| MCP tool functions | `snake_case`, imperative verb + noun | `get_site_info`, `create_list_item` |
| Graph API wrappers | `snake_case`, mirrors tool naming | `get_site_info()`, `create_list_item()` |
| Config constants | `UPPER_SNAKE_CASE` | `APP_NAME`, `GRAPH_BASE_URL` |
| Private helpers | Leading underscore | `_check_auth()`, `_process_csv()` |
| Test fixtures | Descriptive noun | `mock_context`, `graph_client` |

---

## Abbreviations

| Abbreviation | Full Form |
|-------------|-----------|
| MCP | Model Context Protocol |
| LLM | Large Language Model |
| AAD | Azure Active Directory (now Microsoft Entra ID) |
| SP | SharePoint |
| API | Application Programming Interface |
| JWT | JSON Web Token |
| MSAL | Microsoft Authentication Library |
| REST | Representational State Transfer |
| CRUD | Create, Read, Update, Delete |
| CI | Continuous Integration |
| PR | Pull Request |
