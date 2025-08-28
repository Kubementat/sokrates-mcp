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
from urllib.parse import urlparse
from pathlib import Path
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
        _validate_url: Validate URL format
        _validate_api_key: Validate API key format
        _validate_model_name: Validate model name format
        _ensure_directory_exists: Ensure directory exists and is valid
    """
    CONFIG_FILE_PATH = os.path.expanduser("~/.sokrates-mcp/config.yml")
    DEFAULT_PROMPTS_DIRECTORY = Config().prompts_directory
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

        # Validate and set configuration values (ensure all are strings)
        self.api_endpoint = str(config_data.get("api_endpoint", api_endpoint))
        if not self._validate_url(self.api_endpoint):
            raise ValueError(f"Invalid API endpoint URL: {self.api_endpoint}")

        self.api_key = str(config_data.get("api_key", api_key))
        if not self._validate_api_key(self.api_key):
            raise ValueError(f"Invalid API key format: {self.api_key}")

        self.model = str(config_data.get("model", model))
        if not self._validate_model_name(self.model):
            raise ValueError(f"Invalid model name: {self.model}")

        prompts_directory = config_data.get("prompts_directory", self.DEFAULT_PROMPTS_DIRECTORY)
        if not self._ensure_directory_exists(prompts_directory):
            raise ValueError(f"Invalid prompts directory: {prompts_directory}")
        self.prompts_directory = prompts_directory

        refinement_prompt_filename = config_data.get("refinement_prompt_filename", self.DEFAULT_REFINEMENT_PROMPT_FILENAME)
        if not os.path.exists(os.path.join(prompts_directory, refinement_prompt_filename)):
            raise FileNotFoundError(f"Refinement prompt file not found: {refinement_prompt_filename}")
        self.refinement_prompt_filename = refinement_prompt_filename

        refinement_coding_prompt_filename = config_data.get("refinement_coding_prompt_filename", self.DEFAULT_REFINEMENT_CODING_PROMPT_FILENAME)
        if not os.path.exists(os.path.join(prompts_directory, refinement_coding_prompt_filename)):
            raise FileNotFoundError(f"Refinement coding prompt file not found: {refinement_coding_prompt_filename}")
        self.refinement_coding_prompt_filename = refinement_coding_prompt_filename
        
        self.logger.info(f"Configuration loaded from {self.config_file_path}:")
        self.logger.info(f"  API Endpoint: {self.api_endpoint}")
        self.logger.info(f"  Model: {self.model}")
        self.logger.info(f"  Prompts Directory: {self.prompts_directory}")
        self.logger.info(f"  Refinement Prompt Filename: {self.refinement_prompt_filename}")
        self.logger.info(f"  Refinement Coding Prompt Filename: {self.refinement_coding_prompt_filename}")

    def _validate_url(self, url):
        """Validate URL format.

        Args:
            url (str): URL to validate

        Returns:
            bool: True if valid URL, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False

    def _validate_api_key(self, api_key):
        """Validate API key format.

        Args:
            api_key (str): API key to validate

        Returns:
            bool: True if valid API key, False otherwise
        """
        # For testing purposes, allow shorter keys but still enforce alphanumeric + special chars
        return all(c.isalnum() or c in '-_=+.' for c in api_key)

    def _validate_model_name(self, model):
        """Validate model name format.

        Args:
            model (str): Model name to validate

        Returns:
            bool: True if valid model name, False otherwise
        """
        return bool(model) and all(c.isalnum() or c in '/-_.@' for c in model)

    def _ensure_directory_exists(self, directory_path):
        """Ensure directory exists and is valid.

        Args:
            directory_path (str): Directory path to check/validate

        Returns:
            bool: True if directory exists or was created successfully, False otherwise
        """
        try:
            path = Path(directory_path)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            return path.is_dir()
        except Exception as e:
            self.logger.error(f"Error ensuring directory exists: {e}")
            return False

    def _load_config_from_file(self, config_file_path):
        """Load configuration data from a YAML file.

        Args:
            config_file_path (str): Path to the YAML configuration file

        Returns:
            dict: Parsed configuration data or empty dict if file doesn't exist
                  or cannot be parsed

        Side Effects:
            Logs error messages if file reading or parsing fails
        """
        try:
            # Ensure config directory exists
            Path(config_file_path).parent.mkdir(parents=True, exist_ok=True)

            if os.path.exists(config_file_path):
                with open(config_file_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            else:
                self.logger.warning(f"Config file not found at {config_file_path}. Using defaults.")
                # Create empty config file
                with open(config_file_path, 'w') as f:
                    yaml.dump({}, f)
                return {}
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML config file {config_file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Error reading config file {config_file_path}: {e}")
        return {}