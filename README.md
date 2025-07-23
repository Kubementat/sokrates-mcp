# sokrates-mcp

A MCP server offering tools for prompt refinement and execution workflows using the FastMCP framework.

## Features

- Model listing
- Prompt refinement with different types (code/default)
- External LLM processing
- Task breakdown into sub-tasks
- Modular configuration management

## Installation & Setup

### Prerequisites

Ensure you have:
* Python 3.8+
* uv (fast package installer)
* FastMCP development environment

### Local Configuration

1. Clone the repository if hosted:
```bash
git clone https://github.com/Kubementat/sokrates-mcp.git
cd sokrates-mcp
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

## Available Tools

### main.py

- **refine_prompt**: Refines a given prompt by enriching it with additional context.
  - Parameters:
    - `prompt` (str): The input prompt to be refined
    - `refinement_type` (str, optional): Type of refinement ('code' or 'default'). Default is 'default'
    - `model` (str, optional): Model name for refinement. Default is 'default'

- **refine_and_execute_external_prompt**: Refines a prompt and executes it with an external LLM.
  - Parameters:
    - `prompt` (str): The input prompt to be refined and executed
    - `refinement_model` (str, optional): Model for refinement. Default is 'default'
    - `execution_model` (str, optional): Model for execution. Default is 'default'
    - `refinement_type` (str, optional): Type of refinement ('code' or 'default'). Default is 'default'

- **handover_prompt**: Hands over a prompt to an external LLM for processing.
  - Parameters:
    - `prompt` (str): The prompt to be executed externally
    - `model` (str, optional): Model name for execution. Default is 'default'

- **breakdown_task**: Breaks down a task into sub-tasks with complexity ratings.
  - Parameters:
    - `task` (str): The full task description to break down
    - `model` (str, optional): Model name for processing. Default is 'default'

- **list_available_models**: Lists all available large language models accessible by the server.

### mcp_config.py

- **MCPConfig** class: Manages configuration settings for the MCP server.
  - Parameters:
    - `config_file_path` (str, optional): Path to YAML config file
    - `api_endpoint` (str, optional): API endpoint URL
    - `api_key` (str, optional): API key for authentication
    - `model` (str, optional): Model name

### workflow.py

- **Workflow** class: Implements the business logic for prompt refinement and execution.
  - Methods:
    - `refine_prompt`: Refines a given prompt
    - `refine_and_execute_external_prompt`: Refines and executes a prompt with an external LLM
    - `handover_prompt`: Hands over a prompt to an external LLM for processing
    - `breakdown_task`: Breaks down a task into sub-tasks
    - `list_available_models`: Lists all available models

## Project Structure

- `main.py`: Sets up the MCP server and registers tools
- `mcp_config.py`: Configuration management
- `workflow.py`: Business logic for prompt refinement and execution
- `pyproject.toml`: Dependency management

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

## Script List

### `main.py`
Sets up an MCP server using the FastMCP framework to provide tools for prompt refinement and execution workflows.
#### Usage
- `uv run python main.py` - Start the MCP server (default port: 8000)
- `uv run fastmcp dev main.py` - Run in development mode with auto-reload

### `mcp_config.py`
Provides configuration management for the MCP server. Loads configuration from a YAML file and sets default values if needed.
#### Usage
- Import and use in other scripts:
  ```python
  from mcp_config import MCPConfig
  config = MCPConfig(api_endpoint="https://api.example.com", model="my-model")
  ```

### `workflow.py`
Implements the business logic for prompt refinement and execution workflows. Contains methods to refine prompts, execute them with external LLMs, break down tasks, etc.
#### Usage
- Import and use in other scripts:
  ```python
  from workflow import Workflow
  from mcp_config import MCPConfig

  config = MCPConfig()
  workflow = Workflow(config)
  result = await workflow.refine_prompt("Write a Python function to sort a list", refinement_type="code")
  ```

### `src/mcp_client_example.py`
Demonstrates a basic Model Context Protocol (MCP) client using the fastmcp library. Defines a simple model and registers it with the client.
#### Usage
- Run as a standalone script:
  ```bash
  python src/mcp_client_example.py
  ```
- Or use with an ASGI server like Uvicorn:
  ```bash
  uvicorn src.mcp_client_example:main --factory
  ```

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

## Changelog

**0.1.5 (July 2025)**
- Updated README with comprehensive documentation
- Added tool descriptions and usage examples
- Improved project structure overview

**0.1.0 (March 7, 2025)**
- Initial release with refinement tools
- Basic FastMCP integration

Bug reports and feature requests: [GitHub Issues](https://github.com/Kubementat/sokrates-mcp/issues)
