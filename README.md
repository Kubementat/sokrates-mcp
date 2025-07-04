# My MCP Server

A Model Context Protocol (MCP) server implementation providing tools for code refinement and system interaction.

## Installation & Setup

### Prerequisites
Ensure you have:
* Python 3.8+
* uv (fast package installer)
* FastMCP development environment

### Local Configuration
1. Clone the repository if hosted:
```bash
git clone https://github.com/Kubementat/llm-tools-mcp-server.git
cd llm-tools-mcp-server
```

2. Install dependencies using pyproject.toml:
```bash
uv pip install .
```

3. Verify installation:
```bash
python -c "import fastmcp; print(fastmcp.__version__)"
```

## Usage Examples

### Starting the Server
```bash
uv run python main.py
# Default port: 8000 (check console output for exact address)
```

### Development Mode
```bash
uv run fastmcp dev main.py
# Auto-reloads on code changes with detailed logs
```

## Architecture & Technical Details

The server follows a modular design pattern:
1. Tools are registered in `main.py` using FastMCP decorators
2. Dependency management via pyproject.toml
3. Configuration files stored in `.my_mcp_server/` directory

![Architecture Diagram](https://via.placeholder.com/600x400?text=MCP+Server+Architecture)

## Contributing Guidelines

1. Fork the repository and create feature branches
2. Follow PEP8 style guide with 4-space indentation
3. Submit pull requests with:
   - Clear description of changes
   - Updated tests (see Testing section)
   - Documentation updates

Join our [Slack community](https://example.com/slack) for collaboration.

## Testing & Validation

We use `pytest` for testing:
```bash
uv run pytest tests/
```

## Dependencies & Licenses

| Package | Version | License |
|---------|---------|---------|
| fastmcp | 0.1.2   | MIT     |
| uv      | 0.3.4   | Apache-2|

Full license text in `LICENSE.md`

## Roadmap & Future Work

Q2 2025:
- Add authentication middleware
- Implement tool versioning

Challenges:
- Cross-platform compatibility testing
- Large file handling optimizations

## FAQ & Troubleshooting

**Q:** How to change the server port?  
**A:** Set `FASTMCP_PORT` environment variable before starting:

```bash
export FASTMCP_PORT=8080
uv run python main.py
```

**Common Error:**
If you see "ModuleNotFoundError: fastmcp", ensure:
1. Dependencies are installed (`uv pip install .`)
2. Python virtual environment is activated

## Additional Resources

- [MCP Specification Documentation](https://mcp-spec.readthedocs.io)
- Related project: [llm-tools-mcp-client](https://github.com/Kubementat/llm-tools-mcp-server)


## Changelog

**0.1.0 (March 7, 2025)**
- Initial release with refinement tools
- Basic FastMCP integration

Bug reports and feature requests: [GitHub Issues](https://github.com/Kubementat/llm-tools-mcp-server/issues)
