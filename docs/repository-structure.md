# Repository Structure

> This document defines the folder and file layout, directory roles, and file placement rules for the SharePoint MCP Server.

---

## Directory Tree

```
sharepoint-mcp/
├── server.py                    # MCP server entry point
├── setup.py                     # Package installation config
├── requirements.txt             # Runtime + dev dependencies
├── pytest.ini                   # pytest configuration
├── .env.example                 # Environment variable template
├── .gitignore
│
├── auth/                        # Authentication modules
│   ├── __init__.py
│   └── sharepoint_auth.py       # SharePointContext, get_auth_context, refresh_token_if_needed
│
├── config/                      # Configuration
│   ├── __init__.py
│   ├── settings.py              # Loads .env, exposes SHAREPOINT_CONFIG, APP_NAME, DEBUG
│   └── credentials.py.template  # Template for manual credential setup
│
├── tools/                       # MCP tool definitions
│   ├── __init__.py
│   └── site_tools.py            # register_site_tools() — all @mcp.tool() definitions
│
├── resources/                   # MCP resource definitions
│   ├── __init__.py
│   └── site.py                  # register_site_resources() — sharepoint://site-info
│
├── utils/                       # Shared utilities
│   ├── __init__.py
│   ├── graph_client.py          # GraphClient — HTTP wrapper for Microsoft Graph API
│   ├── document_processor.py    # DocumentProcessor — parses DOCX, PDF, XLSX, CSV, TXT
│   └── content_generator.py     # ContentGenerator — generates page titles and content
│
├── tests/                       # pytest test suite
│   ├── tests-init.py            # Test package init (non-standard name, see note)
│   ├── test_auth.py             # Tests for auth/sharepoint_auth.py
│   └── test_graph_client.py     # Tests for utils/graph_client.py
│
├── docs/                        # Persistent project documents
│   ├── product-requirements.md  # Product vision, user stories, acceptance criteria
│   ├── functional-design.md     # Per-feature architecture, data models, diagrams
│   ├── architecture.md          # Tech stack, constraints, deployment
│   ├── repository-structure.md  # This file
│   ├── development-guidelines.md # Coding conventions, testing standards, Git rules
│   ├── glossary.md              # Domain and code terminology
│   ├── auth_guide.md            # Azure AD setup and Graph API permissions
│   └── usage.md                 # Usage examples for LLM clients
│
├── .steering/                   # Task-scoped documents (one dir per task)
│   └── YYYYMMDD-task-title/
│       ├── requirements.md
│       ├── design.md
│       └── tasklist.md
│
├── .github/                     # GitHub configuration
│   ├── workflows/               # CI/CD (GitHub Actions)
│   ├── ISSUE_TEMPLATE/          # Bug report / feature request templates
│   └── PULL_REQUEST_TEMPLATE.md
│
└── auth-diagnostic.py           # Standalone auth diagnostic script
    config_checker.py            # Standalone config validation script
    token-decoder.py             # Standalone JWT token decoder script
```

---

## Directory Roles

| Directory | Role |
|-----------|------|
| `auth/` | All authentication logic. Only `sharepoint_auth.py` should interact with MSAL. |
| `config/` | Environment loading and configuration constants. No business logic. |
| `tools/` | MCP tool registrations. Each file registers a group of related tools via a `register_*_tools()` function. |
| `resources/` | MCP resource registrations. Each file registers resources via a `register_*_resources()` function. |
| `utils/` | Reusable utilities with no MCP or auth dependencies (except `GraphClient` which accepts `SharePointContext`). |
| `tests/` | All pytest tests. File names must match `test_*.py`. |
| `docs/` | Persistent design documents. Updated only when fundamental design changes. |
| `.steering/` | Task-scoped documents. One directory per development task, named `YYYYMMDD-task-title`. |

---

## File Placement Rules

| Type of File | Where to Place |
|-------------|---------------|
| New MCP tool | Add to `tools/site_tools.py`, or create `tools/{feature}_tools.py` and register in `server.py` |
| New MCP resource | Add to `resources/site.py`, or create `resources/{feature}.py` and register in `server.py` |
| New Graph API method | Add to `utils/graph_client.py` |
| New document type support | Add to `utils/document_processor.py` |
| New test file | Place in `tests/`, name as `test_{module}.py` |
| New persistent doc | Place in `docs/` with kebab-case filename |
| New task steering doc | Create `.steering/YYYYMMDD-{task-title}/` and add `requirements.md`, `design.md`, `tasklist.md` |
| Environment variables | Declare in `.env.example`; load in `config/settings.py` |
| Secrets / credentials | `.env` only — never commit; already in `.gitignore` |

---

## Naming Conventions (Files)

| Convention | Example |
|-----------|---------|
| Python modules | `snake_case.py` |
| Test files | `test_{module_name}.py` |
| Markdown docs | `kebab-case.md` |
| Steering directories | `YYYYMMDD-kebab-case-title/` |

---

## Notes

- `tests/tests-init.py` uses a non-standard name (hyphen instead of `__init__.py`) due to the original project setup. New test files should follow the `test_*.py` pattern.
- `auth-diagnostic.py`, `config_checker.py`, and `token-decoder.py` are standalone scripts in the root for operational use; they are not part of the importable package.
- `config/credentials.py.template` is a template file for manual credential setup and should never contain real secrets.
