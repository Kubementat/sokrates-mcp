from llm_tools import Config

DEFAULT_API_ENDPOINT = "http://localhost:1234/v1"
# TODO: make this configurable via startup parameters of the server or an optional config file
# DEFAULT_API_ENDPOINT = "http://192.168.178.57:1234/v1"
DEFAULT_API_KEY = "mykey"
DEFAULT_MODEL = "qwen/qwen3-14b"

class MCPConfig:
    WORKFLOW_COMPLETION_MESSAGE = "Workflow completed."
    DEFAULT_PROMPTS_DIRECTORY = "/Users/dude/dev/os_projects/llm_tools/src/llm_tools/prompts"
    # DEFAULT_PROMPTS_DIRECTORY = Config.DEFAULT_PROMPTS_DIRECTORY
    DEFAULT_REFINEMENT_PROMPT_FILENAME = "refine-prompt.md"

    def __init__(self, api_endpoint = DEFAULT_API_ENDPOINT, api_key = DEFAULT_API_KEY, model= DEFAULT_MODEL):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.model = model