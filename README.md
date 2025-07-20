# splunk-mcp-server

A lightweight, extensible **Model Context Protocol (MCP)** server for **Splunk Enterprise**, designed to integrate with **Claude Desktop** or any MCP-compatible agent. Enables secure, async, chat-based interaction with your Splunk data using **FastAPI**.

---

## 🔧 Supported Tools

- `get_knowledge_objects`
- `search_splunk`
- `get_splunk_indexes`
- `get_log_stats`
- `get_all_users`
- `get_user_info`
- `search_errors`

---

## ⚡ Features

- ⚡ **Async HTTP client** via [`httpx`](https://www.python-httpx.org/)
- 🧩 **Simple plugin-style architecture** for adding tools
- 💻 Designed for **local development** or integration with Claude Desktop
- 🚀 Built with **FastAPI** and **Python 3.13**


## 🛠 Installation Guide

### 1. Install Claude Desktop
Download and install from [Anthropic Claude Desktop](https://www.anthropic.com/index/claude-desktop) (macOS only for now).

### 2. Install `uv` (Python package manager by Astral)

 sudo curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/opt" sh

### 3. Clone the repository

git clone https://github.com/balajifunny/splunk-mcp-server.git
cd splunk-mcp-server

### 4. Set your Splunk Configurations

Update the Splunk configuration section in main.py 

## 

SPLUNK_HOST=127.0.0.1
SPLUNK_PORT=8089
SPLUNK_USERNAME=<your_splunk_username>
SPLUNK_PASSWORD=<your_splunk_password>
SPLUNK_SCHEME=https

### 5. Update Claude Desktop configuration

~/Library/Application Support/Claude/claude_desktop_config.json

## 

{
  "mcpServers": {
    "splunk-mcp-demo": {
      "command": "/opt/uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/Users/<your_user_name>/splunk-mcp-server/main.py"
      ]
    }
  }
}
