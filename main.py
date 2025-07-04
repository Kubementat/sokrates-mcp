from fastmcp import FastMCP, Context
from typing import Annotated, Optional
from pydantic import Field
from llm_tools import RefinementWorkflow, FileHelper, LLMApi, PromptRefiner

# DEFAULT_API_ENDPOINT = "http://localhost:1234/v1"
# TODO: make this configurable via startup parameters of the server or an optional config file
DEFAULT_API_ENDPOINT = "http://192.168.178.57:1234/v1"
DEFAULT_API_KEY = "mykey"
DEFAULT_MODEL = "gemma-3n-e4b-it-text"

class MCPConfig:
    WORKFLOW_COMPLETION_MESSAGE = "Workflow completed."
    DEFAULT_PROMPTS_DIRECTORY = "/Users/dude/dev/os_projects/llm_tools/src/llm_tools/cli/prompts"
    DEFAULT_REFINEMENT_PROMPT_FILENAME = "refine-prompt.md"

    def __init__(self, api_endpoint = DEFAULT_API_ENDPOINT, api_key = DEFAULT_API_KEY, model= DEFAULT_MODEL):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.model = model
    
config = MCPConfig()

# Initialize the MCP Server
mcp = FastMCP(
    name="llm-tools-mcp-server",
    instructions="A MCP server for using the llm tools: prompt refinement and improvement workflows.",
    version="0.1.0"
)

# -------------------------------------------------------------------------

@mcp.tool(
    name="refine_prompt",
    description="Refines a given prompt by enriching the prompt with additional context and improving clarity for further processing by large language models. A prompt received like this can be sent further directly after receiving the response.",
    tags={"prompting", "refinement"}
)
async def refine_prompt(prompt: Annotated[str, Field(description="Input prompt that should be refined")], 
    ctx: Context,
    model: Annotated[str, Field(description="The name of the model that should be used for the prompt refinement process. The default model name is: qwen/qwen3-8b", default="qwen/qwen3-8b")],
    ) -> str:
    """
    Refines a given prompt by enriching the input prompt with additional context and improving clarity for further processing by large language models.
    """    
    refinement_prompt_file = f"{MCPConfig.DEFAULT_PROMPTS_DIRECTORY}/{MCPConfig.DEFAULT_REFINEMENT_PROMPT_FILENAME}"
    refinement_prompt = FileHelper.read_file(refinement_prompt_file, verbose=False)
    await ctx.info(f"Read refinement prompt from: {refinement_prompt_file}")
    
    refinement_workflow = RefinementWorkflow(api_endpoint=config.api_endpoint, api_key=config.api_key, model=model)
    await ctx.info(f"Prompt refinement and execution workflow started with refinement model: {model} . Waiting for the response from the LLM...")
    refined = refinement_workflow.refine_prompt(prompt, refinement_prompt)
    await ctx.info(MCPConfig.WORKFLOW_COMPLETION_MESSAGE)
    return refined

# -------------------------------------------------------------------------

@mcp.tool(
    name="refine_and_process_prompt",
    description="Refines a given prompt by enriching the input prompt with additional context and then processes the prompt with an external llm. It delivers back the exection result of the refined prompt.",
    tags={"prompting", "refinement"}
)
async def refine_and_process_prompt(prompt: Annotated[str, Field(description="Input prompt that should be refined and then processed.")], 
    ctx: Context,
    refinement_model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the prompt refinement process. The default refinement model name is: qwen/qwen3-8b", default="qwen/qwen3-8b")],
    execution_model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the execution of the refined prompt. The default execution model name is: qwen/qwen3-8b", default="qwen/qwen3-8b")],
    ) -> str:
    """Refines a given prompt and sends it to the LLM for further processing.
    """
    refinement_prompt_file = f"{MCPConfig.DEFAULT_PROMPTS_DIRECTORY}/{MCPConfig.DEFAULT_REFINEMENT_PROMPT_FILENAME}"
    refinement_prompt = FileHelper.read_file(refinement_prompt_file, verbose=False)
    await ctx.info(f"Read refinement prompt from: {refinement_prompt_file}")
    
    refinement_workflow = RefinementWorkflow(api_endpoint=config.api_endpoint, api_key=config.api_key, model=refinement_model)
    await ctx.info(f"Prompt refinement and execution workflow started with refinement model: {refinement_model} and execution model {execution_model} . Waiting for the responses from the LLMs...")
    result = refinement_workflow.refine_and_send_prompt(input_prompt=prompt, refinement_prompt=refinement_prompt, refinement_model=refinement_model, execution_model=execution_model)
    await ctx.info(MCPConfig.WORKFLOW_COMPLETION_MESSAGE)
    return result

# -------------------------------------------------------------------------

@mcp.tool(
    name="handover_prompt",
    description="Hands over a prompt to an external llm for processing and delivers back the processed result.",
    tags={"prompting", "refinement"}
)
async def handover_prompt(prompt: Annotated[str, Field(description="Prompt that should be executed externally.")], 
    ctx: Context,
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the external prompt processing. The default model name is: qwen/qwen3-8b", default="qwen/qwen3-8b")],
    ) -> str:
    """Hands over a prompt to an external llm for processing and delivers back the processed result.
    """
    llm_api = LLMApi()
    refiner = PromptRefiner()
    result = llm_api.send(prompt,model=model)
    result = refiner.clean_response(result)
    
    await ctx.info(f"External Prompt execution workflow started with model: {model} . Waiting for the responses from the LLM...")
    await ctx.info(MCPConfig.WORKFLOW_COMPLETION_MESSAGE)
    return result

if __name__ == "__main__":
    mcp.run()