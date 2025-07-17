[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/demodorigatsuo-sharepoint-mcp-badge.png)](https://mseep.ai/app/demodorigatsuo-sharepoint-mcp)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://docs.anthropic.com/claude/docs/model-context-protocol)
# SharePoint MCP Server

> **DISCLAIMER**: This project is not affiliated with, endorsed by, or related to Microsoft Corporation. SharePoint and Microsoft Graph API are trademarks of Microsoft Corporation. This is an independent, community-driven project.

SharePoint Model Context Protocol (MCP) server acts as a bridge that enables LLM applications (like Claude) to access content from your SharePoint site. With this project, you can use natural language to query documents, lists, and other content in your SharePoint site.

## Features

- **Browse Document Libraries**: View contents of SharePoint document libraries
- **Access List Data**: Retrieve and manipulate SharePoint list data
- **Retrieve Document Content**: Access content from specific documents
- **SharePoint Search**: Search across your entire site
- **Create List Items**: Add new items to SharePoint lists

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
