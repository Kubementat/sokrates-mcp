# main.py - MCP Server for LLM Tools

# This script sets up an MCP server using the FastMCP framework to provide tools for prompt refinement and execution workflows.
# It includes several tools that can be used to refine prompts, execute them with external LLMs, break down tasks,
# and list available models.
# 
# Main Purpose
# The primary purpose of this script is to create a robust MCP server that facilitates interaction with large language models
# through various prompt engineering workflows. It provides APIs for refining prompts, executing them externally,
# breaking down complex tasks, and listing available models.
# 
# Parameters
# - `refine_prompt`: Refines a given prompt by enriching it with additional context.
#   - `prompt` (str): The input prompt to be refined.
#   - `refinement_type` (str, optional): Type of refinement ('code' or 'default'). Default is 'default'.
#   - `model` (str, optional): Model name for refinement. Default is 'default'.
# 
# - `refine_and_execute_external_prompt`: Refines a prompt and executes it with an external LLM.
#   - `prompt` (str): The input prompt to be refined and executed.
#   - `refinement_model` (str, optional): Model for refinement. Default is 'default'.
#   - `execution_model` (str, optional): Model for execution. Default is 'default'.
#   - `refinement_type` (str, optional): Type of refinement ('code' or 'default'). Default is 'default'.
# 
# - `handover_prompt`: Hands over a prompt to an external LLM for processing.
#   - `prompt` (str): The prompt to be executed externally.
#   - `model` (str, optional): Model name for execution. Default is 'default'.
# 
# - `breakdown_task`: Breaks down a task into sub-tasks with complexity ratings.
#   - `task` (str): The full task description to break down.
#   - `model` (str, optional): Model name for processing. Default is 'default'.
# 
# - `list_available_models`: Lists all available large language models accessible by the server.
# 
# Usage Examples
# ```python
# Refine a prompt
# await refine_prompt("Write a Python function to sort a list", refinement_type="code")

# # Refine and execute a prompt with an external LLM
# await refine_and_execute_external_prompt(
#     "Generate a summary of the following text: ...",
#     refinement_model="model1",
#     execution_model="model2"
# )

# # Hand over a prompt to an external LLM
# await handover_prompt("Translate this text to French: ...")

# # Break down a task into sub-tasks
# await breakdown_task("Implement user authentication system")

# # List available models
# await list_available_models()
# ```

from typing import Annotated, Optional
from pydantic import Field
from llm_tools import RefinementWorkflow, FileHelper, LLMApi, PromptRefiner
from mcp_config import MCPConfig
from workflow import Workflow
from fastmcp import FastMCP, Context
import logging
import os

config = MCPConfig()
workflow = Workflow(config)

# Configure logging for better visibility of fastmcp operations
log_file_path = os.path.expanduser("~/.llm-tools-mcp/server.log")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the MCP Server
mcp = FastMCP(
    name="llm-tools-mcp",
    instructions="A MCP server for using the llm tools: prompt refinement and improvement workflows.",
    version="0.1.0"
)

# -------------------------------------------------------------------------

@mcp.tool(
    name="refine_prompt",
    description="Refines a given prompt by enriching the prompt with additional context and improving clarity for further processing by large language models. A prompt received like this can be sent further directly after receiving the response. The refinement_type can be used to improve the results: e.g. for a coding task this should be set to the code type.",
    tags={"prompting", "refinement"}
)
async def refine_prompt(prompt: Annotated[str, Field(description="Input prompt that should be refined")],
    ctx: Context,
    refinement_type: Annotated[str, Field(description="The type of the refinement. This could be 'code' (for refining coding tasks) or 'default' . The default type is: default", default="default")],
    model: Annotated[str, Field(description="The name of the model that should be used for the prompt refinement process. The default model name is 'default', which will pick the server's default model.", default='default')],
    ) -> str:
    """
    Refines a given prompt by enriching the input prompt with additional context and improving clarity for further processing by large language models.
    """    
    return await workflow.refine_prompt(prompt=prompt, ctx=ctx, model=model, refinement_type=refinement_type)

# -------------------------------------------------------------------------

@mcp.tool(
    name="refine_and_execute_external_prompt",
    description="Refines a given prompt by enriching the input prompt with additional context and then executes the prompt with an external llm. It delivers back the exection result of the refined prompt on the external llm. The refinement_type can be used to improve the results: e.g. for a coding task this should be set to the code type.",
    tags={"prompting", "refinement" , "external_processing"}
)
async def refine_and_execute_external_prompt(prompt: Annotated[str, Field(description="Input prompt that should be refined and then processed.")], 
    ctx: Context,
    refinement_model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the prompt refinement process. The default refinement model name is 'default', which will pick the server's default model.", default='default')],
    execution_model: Annotated[str, Field(description="[Optional] The name of the external model that should be used for the execution of the refined prompt. The default execution model name is 'default', which will pick the server's default model.", default='default')],
    refinement_type: Annotated[str, Field(description="The type of the refinement. This could be 'code' (for refining coding tasks) or 'default' for any general refinement tasks. The default type is: default", default="default")],
    ) -> str:
    """Refines a given prompt and sends it to the LLM for further processing.
    """
    return await workflow.refine_and_execute_external_prompt(prompt=prompt, ctx=ctx, refinement_model=refinement_model, execution_model=execution_model, refinement_type=refinement_type)

# -------------------------------------------------------------------------

@mcp.tool(
    name="handover_prompt",
    description="Hands over a prompt to an external llm for processing and delivers back the processed result.",
    tags={"prompting", "refinement"}
)
async def handover_prompt(prompt: Annotated[str, Field(description="Prompt that should be executed externally.")], 
    ctx: Context,
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the external prompt processing. The default model name is 'default', which will pick the server's default model.", default='default')],
    ) -> str:
    """Hands over a prompt to an external llm for processing and delivers back the processed result.
    """
    return await workflow.handover_prompt(prompt=prompt, ctx=ctx, model=model)

# -------------------------------------------------------------------------

@mcp.tool(
    name="breakdown_task",
    description="Breaks down a task into sub-tasks back a json list of sub-tasks with complexity ratings.",
    tags={"prompting", "task", "breakdown"}
)
async def breakdown_task(task: Annotated[str, Field(description="The full task description to break down further.")], 
    ctx: Context,
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the external prompt processing. The default model name is 'default', which will pick the server's default model.", default='default')],
    ) -> str:
    """
    Breaks down a task into sub-tasks back a json list of sub-tasks with complexity ratings.
    """
    return await workflow.breakdown_task(task=task, ctx=ctx, model=model)

@mcp.tool(
    name="list_available_models",
    description="Lists all available large language models accessible by the llm-tools-mcp server.",
    tags={"refinement", "llm", "models", "list"}
)
async def list_available_models(ctx: Context) -> str:
    """
    Returns a list of all available models.
    """
    return await workflow.list_available_models(ctx=ctx)

if __name__ == "__main__":
    mcp.run()