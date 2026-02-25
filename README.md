[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/demodorigatsuo-sharepoint-mcp-badge.png)](https://mseep.ai/app/demodorigatsuo-sharepoint-mcp)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://docs.anthropic.com/claude/docs/model-context-protocol)
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-blueviolet.svg)](https://claude.ai/claude-code)

# SharePoint MCP Server

> **DISCLAIMER**: This project is not affiliated with, endorsed by, or related to Microsoft Corporation. SharePoint and Microsoft Graph API are trademarks of Microsoft Corporation. This is an independent, community-driven project.

SharePoint Model Context Protocol (MCP) server acts as a bridge that enables LLM applications (like Claude) to access content from your SharePoint site. With this project, you can use natural language to query documents, lists, and other content in your SharePoint site.

---

## Announcement — Active Development with Claude Code (February 25, 2026)

**We are excited to announce that active development of this project has resumed as of February 25, 2026, powered by [Claude Code](https://claude.ai/claude-code) — Anthropic's agentic coding tool.**

Starting today, all feature development, bug fixes, and improvements are driven by a structured, AI-assisted workflow:

- **Transparent planning** — every task begins with a documented design in `.steering/`
- **Consistent quality** — all changes pass `black`, `ruff`, and `pytest` before merge
- **Global collaboration** — contributions from developers worldwide are welcome

### What's coming

We are actively planning and will be delivering improvements across:

| Area | Planned Work |
|------|-------------|
| Tools | Expanded Graph API coverage (lists, pages, permissions) |
| Authentication | Certificate-based auth support |
| Performance | Pagination support for large libraries and lists |
| Testing | Broader test coverage for all tools |
| Documentation | Multilingual guides and usage examples |

**Want to follow along or contribute?** Watch this repository and check the [`.steering/`](.steering/) directory for the latest task plans.

---

## Features

- **Get Site Information**: Retrieve name, description, URL, and metadata of your SharePoint site
- **Browse Document Libraries**: List all document libraries (drives) in a site
- **Retrieve Document Content**: Read and parse DOCX, PDF, XLSX, CSV, and TXT files
- **SharePoint Search**: Full-text search across all content in your site
- **Create & Update List Items**: Add or modify records in SharePoint lists
- **Create Intelligent Lists**: Provision lists with AI-optimized schemas (projects, tasks, events, contacts)
- **Create Advanced Document Libraries**: Set up libraries with rich metadata for contracts, reports, and more
- **Upload Documents**: Push files directly into document libraries
- **Create Modern Pages**: Publish beautiful SharePoint pages with generated content
- **Create News Posts**: Publish news articles to your SharePoint site
- **Create Sites**: Provision new SharePoint team sites programmatically

## Prerequisites

- Python 3.10 or higher
- Access to a SharePoint site
- Microsoft Azure AD application registration (for authentication)

## Quickstart

Follow these steps to get the SharePoint MCP Server up and running quickly:

1. **Prerequisites**
   - Ensure you have Python 3.10+ installed
   - An Azure AD application with proper permissions (see docs/auth_guide.md)

2. **Installation**
   ```bash
   # Install from GitHub
   pip install git+https://github.com/DEmodoriGatsuO/sharepoint-mcp.git

   # Or install in development mode
   git clone https://github.com/DEmodoriGatsuO/sharepoint-mcp.git
   cd sharepoint-mcp
   pip install -e .
   ```

3. **Configuration**
   ```bash
   # Copy the example configuration
   cp .env.example .env
   
   # Edit the .env file with your details
   nano .env
   ```

4. **Run the Diagnostic Tools**
   ```bash
   # Check your configuration
   python config_checker.py
   
   # Test authentication
   python auth-diagnostic.py
   ```

5. **Start the Server**
   ```bash
   python server.py
   ```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/DEmodoriGatsuO/sharepoint-mcp.git
cd sharepoint-mcp
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit the .env file with your authentication details
```

## Configuration

1. Register an application in Azure AD and grant necessary permissions (see docs/auth_guide.md)
2. Configure your authentication information and SharePoint site URL in the `.env` file

## Usage

### Run in Development Mode

```bash
mcp dev server.py
```

### Install in Claude Desktop

```bash
mcp install server.py --name "SharePoint Assistant"
```

### Run Directly

```bash
python server.py
```

## Advanced Usage

### Handling Document Content

```python
# Example of retrieving document content
import requests

# Get document content
response = requests.get(
    "http://localhost:8080/sharepoint-mcp/document/Shared%20Documents/report.docx", 
    headers={"X-MCP-Auth": "your_auth_token"}
)

# Process content
if response.status_code == 200:
    document_content = response.json()
    print(f"Document name: {document_content['name']}")
    print(f"Size: {document_content['size']} bytes")
```

### Working with SharePoint Lists

```python
# Example of retrieving list data
import requests
import json

# Get list items
response = requests.get(
    "http://localhost:8080/sharepoint-mcp/list/Tasks", 
    headers={"X-MCP-Auth": "your_auth_token"}
)

# Create a new list item
new_item = {
    "Title": "Review quarterly report",
    "Status": "Not Started",
    "DueDate": "2025-05-01"
}

create_response = requests.post(
    "http://localhost:8080/sharepoint-mcp/list/Tasks", 
    headers={
        "X-MCP-Auth": "your_auth_token",
        "Content-Type": "application/json"
    },
    data=json.dumps(new_item)
)
```

## Integrating with Claude

See the documentation in [docs/usage.md](docs/usage.md) for detailed examples of how to use this server with Claude and other LLM applications.

## Monitoring and Troubleshooting

### Logs

The server logs to stdout by default. Set `DEBUG=True` in your `.env` file to enable verbose logging.

### Common Issues

- **Authentication Failures**: Run `python auth-diagnostic.py` to diagnose issues
- **Permission Errors**: Make sure your Azure AD app has the required permissions
- **Token Issues**: Use `python token-decoder.py` to analyze your token's claims

## License

This project is released under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome. Please open an issue first to discuss what you would like to change before making major modifications. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
