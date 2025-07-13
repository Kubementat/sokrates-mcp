# Architecture

## System Architecture
This project is a Python-based MCP server using the FastMCP framework. It's designed to be modular, with tools defined in `main.py` and configuration handled by `mcp_config.py`.

## Source Code Paths
- `main.py`: The main entry point of the server, where tools are registered.
- `mcp_config.py`: Handles server configuration.
- `workflow.py`: Contains the business logic for the tools.
- `src/knowledge_store.py`: Implements the in-memory knowledge base.

## Key Technical Decisions
- **FastMCP Framework**: Chosen for its simplicity and performance in building MCP servers.
- **Modular Design**: Tools are implemented as separate functions, making the codebase easy to maintain and extend.
- **In-Memory Knowledge Base**: A simple dictionary-based knowledge store is used for demonstration purposes.

## Design Patterns
- **Decorator Pattern**: Used by FastMCP to register tools (`@mcp.tool`).
- **Singleton Pattern**: The `knowledge_store` is a singleton instance, ensuring that all tools access the same data.

## Component Relationships
- `main.py` imports and uses `FastMCP`, `MCPConfig`, `Workflow`, and `knowledge_store`.
- `Workflow` uses `MCPConfig` to access configuration settings.
- The tools in `main.py` delegate their implementation to the `Workflow` class.