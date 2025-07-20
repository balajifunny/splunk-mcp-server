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
