# Usage Guide

> **DISCLAIMER**: This is an unofficial, community-developed project that is not affiliated with, endorsed by, or related to Microsoft Corporation.

This guide explains how to use the SharePoint MCP Server with Claude and other LLM applications.

---

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials:
   - `TENANT_ID` — from the Azure Portal
   - `CLIENT_ID` / `CLIENT_SECRET` — from your Azure AD application registration
   - `SITE_URL` — your SharePoint site URL

2. Start the server:

   ```bash
   # stdio — for Claude Desktop / MCP Inspector
   python server.py

   # HTTP — for web services and Copilot agents
   python server.py --transport streamable-http --port 8000
   ```

3. For development and testing, use MCP Inspector:

   ```bash
   mcp dev server.py
   ```

4. To install in Claude Desktop:

   ```bash
   mcp install server.py --name "SharePoint Assistant"
   ```

---

## Available Tools

### Read Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_site_info` | — | Get site name, description, URL, and metadata |
| `list_document_libraries` | — | List all document libraries in the site |
| `list_folder_contents` | `site_id`, `drive_id`, `folder_path` | Browse files and subfolders by path |
| `get_document_content` | `site_id`, `drive_id`, `item_id`, `filename` | Parse and return content of DOCX, PDF, XLSX, CSV, or TXT |
| `get_document_by_path` | `site_id`, `drive_id`, `file_path`, `filename` | Retrieve document content by file path |
| `get_item_metadata` | `site_id`, `drive_id`, `item_path` | Get metadata for a file or folder |
| `search_sharepoint` | `query` | Full-text search across all site content |

### Write Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `upload_document` | `site_id`, `drive_id`, `folder_path`, `filename`, `content` | Upload a file to a document library |
| `create_list_item` | `site_id`, `list_id`, `fields` | Create a new item in a list |
| `update_list_item` | `site_id`, `list_id`, `item_id`, `fields` | Update an existing list item |

### Provisioning Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `create_sharepoint_site` | `display_name`, `alias`, `description` | Create a new SharePoint team site |
| `create_intelligent_list` | `site_id`, `purpose`, `display_name` | Create a list with an AI-optimized schema (`projects`, `tasks`, `events`, `contacts`, `documents`) |
| `create_advanced_document_library` | `site_id`, `display_name`, `doc_type` | Create a library with rich metadata (`general`, `contracts`, `marketing`, `reports`, `projects`) |
| `create_modern_page` | `site_id`, `name`, `purpose`, `audience` | Publish a modern SharePoint page |
| `create_news_post` | `site_id`, `title`, `description`, `content` | Publish a news article to the site |

---

## Example Prompts

### Browse and Search

```
What document libraries are available on my SharePoint site?
```

```
Search my SharePoint site for documents related to "quarterly revenue".
```

```
Show me all files in the "Reports/2026" folder of the "Shared Documents" library.
```

### Document Access

```
Can you read the contents of "sales_data.xlsx" from my Reports library?
```

```
Analyze the "project_plan.docx" file and summarize the key milestones.
```

### List Management

```
Show me all items in the "Tasks" list on my SharePoint site.
```

```
Create a new task in the "Tasks" list with the title "Prepare monthly report" and status "Not Started".
```

```
Update item 42 in the "Projects" list and set the status to "Completed".
```

### Provisioning

```
Create a new SharePoint site for our Marketing team with the alias "marketing".
```

```
Create a "Projects" list called "Marketing Projects" with fields for status, priority, and due dates.
```

```
Create a document library called "Legal Documents" for contracts with appropriate metadata fields.
```

```
Create a welcome page called "home" for our team site.
```

### Multi-step Workflow

```
Set up a new project area in SharePoint:
1. Create a site called "Product Launch" with alias "productlaunch"
2. Add a tasks list with status, priority, and due date fields
3. Create a document library for project documents
4. Create a welcome page introducing the project
```

---

## Using Site IDs

Many tools require a `site_id`. Obtain it first with `get_site_info`, then pass it to subsequent calls:

```
First get information about my SharePoint site, then use the site ID to create a new tasks list.
```

---

## Document Processing Capabilities

| Format | Extracted Content |
|--------|------------------|
| XLSX / CSV | Data preview, column names, basic statistics (first 50 rows) |
| DOCX | Full text, tables, document structure, metadata |
| PDF | Text, metadata, form fields (first 10 pages) |
| TXT / MD / HTML | Full text content |

---

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| Authentication error | Run `python auth-diagnostic.py` |
| Permission denied | Check Azure AD app permissions in the portal |
| Token invalid | Run `python token-decoder.py` to inspect claims |
| Site not found | Verify `SITE_URL` in `.env` matches your actual site URL |
