# Architecture

> This document describes the technology stack, development tools, technical constraints, and performance requirements for the SharePoint MCP Server.

---

## Technology Stack

### Runtime

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.10+ |
| MCP Framework | `mcp[cli]` (FastMCP) | >=0.1.0 |
| Authentication | `msal` (Microsoft Authentication Library) | >=1.20.0 |
| HTTP Client | `requests` | >=2.28.0 |
| Configuration | `python-dotenv` | >=0.21.0 |

### Document Processing (Optional)

| Library | Purpose |
|---------|---------|
| `pandas` | CSV / Excel parsing |
| `openpyxl` | Excel engine for pandas |
| `python-docx` | Word document parsing |
| `PyPDF2` | PDF text extraction |

### Development Tools

| Tool | Purpose | Config File |
|------|---------|-------------|
| `black` | Code formatter | `pyproject.toml` or defaults |
| `ruff` | Linter | `pyproject.toml` or defaults |
| `pytest` | Test runner | `pytest.ini` |
| `pytest-asyncio` | Async test support | `pytest.ini` (`asyncio_mode = auto`) |

---

## Development Environment

### Supported Environments

| Environment | Method |
|-------------|--------|
| Dev Container | `.devcontainer/` (VS Code / GitHub Codespaces) |
| Local venv | `python -m venv venv && pip install -r requirements.txt` |
| pip install | `pip install -e .` (editable install via `setup.py`) |

### Required Environment Variables

Defined in `.env` (see `.env.example`):

| Variable | Required | Description |
|----------|----------|-------------|
| `TENANT_ID` | Yes | Azure AD tenant ID |
| `CLIENT_ID` | Yes | Azure AD application (client) ID |
| `CLIENT_SECRET` | Yes | Azure AD client secret |
| `SITE_URL` | Yes | SharePoint site URL (`https://{tenant}.sharepoint.com/sites/{name}`) |
| `DEBUG` | No | Enable debug logging (`True` / `False`, default: `False`) |
| `USERNAME` | No | User email (for delegated auth, not used in current implementation) |
| `PASSWORD` | No | User password (for delegated auth, not used in current implementation) |

---

## Technical Constraints

| Constraint | Detail |
|-----------|--------|
| Auth method | Client credentials only (application permissions, no delegated user auth) |
| API surface | Microsoft Graph API v1.0 only |
| Token cache | File-based (`.token_cache`), single-process only |
| Document size | PDF extraction limited to first 10 pages; CSV/Excel preview to first 50 rows |
| Concurrency | Single-threaded async (FastMCP); no multi-process support |
| Transport | MCP stdio transport (default); HTTP transport available via `mcp dev` |

---

## Microsoft Graph API Permissions

The application requires the following **Application permissions** (admin consent required):

| Permission | Scope | Used For |
|-----------|-------|---------|
| `Sites.Read.All` | Read | Site info, document libraries, search |
| `Sites.ReadWrite.All` | Read/Write | List items, document upload |
| `Sites.Manage.All` | Full control | Site creation |
| `Files.Read.All` | Read | Document content retrieval |
| `Files.ReadWrite.All` | Read/Write | Document upload |
| `User.Read.All` | Read | User profile information |

> Any changes to required permissions must be documented in `docs/auth_guide.md`.

---

## Performance Requirements

| Metric | Target |
|--------|--------|
| Token acquisition (startup) | < 3 seconds |
| Tool response (simple read) | < 5 seconds |
| Document processing (< 1 MB) | < 10 seconds |
| Search results | < 10 seconds |

---

## Deployment

### Run as MCP Server (stdio)

```bash
python server.py
```

### Run in Development Mode (MCP Inspector)

```bash
mcp dev server.py
```

### Install in Claude Desktop

```bash
mcp install server.py --name "SharePoint Assistant"
```

### Claude Desktop Config (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "sharepoint": {
      "command": "python",
      "args": ["/path/to/sharepoint-mcp/server.py"],
      "env": {
        "TENANT_ID": "...",
        "CLIENT_ID": "...",
        "CLIENT_SECRET": "...",
        "SITE_URL": "..."
      }
    }
  }
}
```

---

## Logging

- Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Default level: `INFO`
- Debug level: `DEBUG` (set `DEBUG=True` in `.env`)
- Logger names: `sharepoint_mcp`, `sharepoint_tools`, `sharepoint_auth`, `graph_client`, `document_processor`
