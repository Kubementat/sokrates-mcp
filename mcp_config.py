# MCP Configuration Module
#
# This module provides configuration management for the MCP server.
# It loads configuration from a YAML file and sets default values if needed.
#
# Parameters:
# - config_file_path: Path to the YAML configuration file (default: ~/.sokrates-mcp/config.yml)
# - api_endpoint: API endpoint URL (default: http://localhost:1234/v1)
# - api_key: API key for authentication (default: mykey)
# - model: Model name to use (default: qwen/qwen3-8b)
#
# Usage example:
#   config = MCPConfig(api_endpoint="https://api.example.com", model="my-model")
import os
import yaml
import logging
from sokrates import Config

DEFAULT_API_ENDPOINT = "http://localhost:1234/v1"
DEFAULT_API_KEY = "mykey"
DEFAULT_MODEL = "qwen/qwen3-8b"

class MCPConfig:
    """Configuration management class for MCP server.

    This class handles loading configuration from a YAML file and provides
    default values for various parameters.

    Attributes:
        CONFIG_FILE_PATH (str): Default path to the configuration file
        DEFAULT_PROMPTS_DIRECTORY (str): Default directory for prompts
        DEFAULT_REFINEMENT_PROMPT_FILENAME (str): Default refinement prompt filename
        DEFAULT_REFINEMENT_CODING_PROMPT_FILENAME (str): Default refinement coding prompt filename

    Methods:
        __init__: Initialize the configuration with optional parameters
        _load_config_from_file: Load configuration from file
    """
    CONFIG_FILE_PATH = os.path.expanduser("~/.sokrates-mcp/config.yml")
    DEFAULT_PROMPTS_DIRECTORY = Config.DEFAULT_PROMPTS_DIRECTORY
    DEFAULT_REFINEMENT_PROMPT_FILENAME = "refine-prompt.md"
    DEFAULT_REFINEMENT_CODING_PROMPT_FILENAME = "refine-coding-v3.md"
    
    def __init__(self, config_file_path=CONFIG_FILE_PATH, api_endpoint = DEFAULT_API_ENDPOINT, api_key = DEFAULT_API_KEY, model= DEFAULT_MODEL, verbose=False):
        """Initialize MCP configuration.

        Args:
            config_file_path (str): Path to the YAML configuration file.
                                   Defaults to CONFIG_FILE_PATH.
            api_endpoint (str): API endpoint URL. Defaults to DEFAULT_API_ENDPOINT.
            api_key (str): API key for authentication. Defaults to DEFAULT_API_KEY.
            model (str): Model name to use. Defaults to DEFAULT_MODEL.
            verbose (bool): Enable verbose logging. Defaults to False.

        Returns:
            None

        Side Effects:
            Initializes instance attributes with values from config file or defaults
            Sets up logging based on verbose parameter
        """
        self.logger = logging.getLogger(__name__)
        self.config_file_path = config_file_path
        config_data = self._load_config_from_file(self.config_file_path)

        self.api_endpoint = config_data.get("api_endpoint", api_endpoint)
        self.api_key = config_data.get("api_key", api_key)
        self.model = config_data.get("model", model)
        self.prompts_directory = config_data.get("prompts_directory", self.DEFAULT_PROMPTS_DIRECTORY)
        self.refinement_prompt_filename = config_data.get("refinement_prompt_filename", self.DEFAULT_REFINEMENT_PROMPT_FILENAME)
        self.refinement_coding_prompt_filename = config_data.get("refinement_coding_prompt_filename", self.DEFAULT_REFINEMENT_CODING_PROMPT_FILENAME)
        
        self.logger.info(f"Configuration loaded from {self.config_file_path}:")
        self.logger.info(f"  API Endpoint: {self.api_endpoint}")
        self.logger.info(f"  Model: {self.model}")
        self.logger.info(f"  Prompts Directory: {self.prompts_directory}")
        self.logger.info(f"  Refinement Prompt Filename: {self.refinement_prompt_filename}")
        self.logger.info(f"  Refinement Coding Prompt Filename: {self.refinement_coding_prompt_filename}")

    def _load_config_from_file(self, config_file_path):
        """Load configuration data from a YAML file.

        Args:
            config_file_path (str): Path to the YAML configuration file

        Returns:
            dict: Parsed configuration data or empty dict if file doesn't exist
                  or cannot be parsed

        Side Effects:
            Prints error messages to stdout if file reading or parsing fails
        """
        if os.path.exists(config_file_path):
            try:
                with open(config_file_path, 'r') as f:
                    return yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML config file {config_file_path}: {e}")
            except Exception as e:
                print(f"Error reading config file {config_file_path}: {e}")
        return {}