# main.py - MCP Server for sokrates library

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
#
# # Refine and execute a prompt with an external LLM
# await refine_and_execute_external_prompt(
#     "Generate a summary of the following text: ...",
#     refinement_model="model1",
#     execution_model="model2"
# )
#
# # Hand over a prompt to an external LLM
# await handover_prompt("Translate this text to French: ...")
#
# # Break down a task into sub-tasks
# await breakdown_task("Implement user authentication system")
#
# # List available models
# await list_available_models()
# ```
#

from typing import Annotated, Optional
from pydantic import Field
from sokrates import RefinementWorkflow, FileHelper, LLMApi, PromptRefiner
from mcp_config import MCPConfig
from workflow import Workflow
from fastmcp import FastMCP, Context
import logging
import os

config = MCPConfig()
workflow = Workflow(config)

# Configure logging for better visibility of fastmcp operations
log_file_path = os.path.expanduser("~/.sokrates-mcp/server.log")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the MCP Server
mcp = FastMCP(
    name="sokrates-mcp",
    instructions="A MCP server for using sokrates python library's tools: prompt refinement and improvement workflows.",
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
    Refines a given prompt by enriching the input prompt with additional context and improving clarity
    for further processing by large language models.

    Args:
        prompt (str): The input prompt to be refined.
        ctx (Context): The MCP context object.
        refinement_type (str, optional): Type of refinement ('code' or 'default'). Default is 'default'.
        model (str, optional): Model name for refinement. Default is 'default'.

    Returns:
        str: The refined prompt.

    This function delegates the actual refinement work to the workflow.refine_prompt method.
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
    """
    Refines a given prompt and executes it with an external LLM.

    Args:
        prompt (str): The input prompt to be refined and executed.
        ctx (Context): The MCP context object.
        refinement_model (str, optional): Model for refinement. Default is 'default'.
        execution_model (str, optional): Model for execution. Default is 'default'.
        refinement_type (str, optional): Type of refinement ('code' or 'default'). Default is 'default'.

    Returns:
        str: The execution result of the refined prompt from the external LLM.

    This function first refines the prompt and then executes it with an external LLM.
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
    temperature: Annotated[float, Field(description="[Optional] The temperature of the llm to use for generating the ideas. The default value is 0.7 .", default=0.7)],
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the external prompt processing. The default model name is 'default', which will pick the server's default model.", default='default')],
    ) -> str:
    """
    Hands over a prompt to an external LLM for processing.

    Args:
        prompt (str): The prompt to be executed externally.
        ctx (Context): The MCP context object.
        model (str, optional): Model name for execution. Default is 'default'.
        temperature (float, optional): the temperature to use for the external execution

    Returns:
        str: The processed result from the external LLM.

    This function delegates the prompt execution to an external LLM and returns the result.
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
    Breaks down a task into sub-tasks and returns a JSON list of sub-tasks with complexity ratings.

    Args:
        task (str): The full task description to break down.
        ctx (Context): The MCP context object.
        model (str, optional): Model name for processing. Default is 'default'.

    Returns:
        str: A JSON string containing the list of sub-tasks with complexity ratings.

    This function uses an LLM to analyze the task and break it down into manageable sub-tasks.
    """
    return await workflow.breakdown_task(task=task, ctx=ctx, model=model)

@mcp.tool(
    name="generate_random_ideas",
    description="Invents and generates a random topic an generates the provided count of ideas on the topic.",
    tags={"idea", "generator", "idea generation", "invention", "random"}
)
async def generate_random_ideas(ctx: Context,
    idea_count: Annotated[int, Field(description="[Optional] The number of ideas to generate. The default value is 1.", default=1)],
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the generation. The default model name is 'default', which will pick the server's default model.", default='default')],
    temperature: Annotated[float, Field(description="[Optional] The temperature of the llm to use for generating the ideas. The default value is 0.7 .", default=0.7)]
    ) -> str:
    return await workflow.generate_random_ideas(ctx=ctx, model=model, idea_count=idea_count, temperature=temperature)

@mcp.tool(
    name="generate_ideas_on_topic",
    description="Generates the provided count of ideas on the provided topic.",
    tags={"idea", "generator", "idea generation", "invention"}
)
async def generate_ideas_on_topic(
    ctx: Context,
    topic: Annotated[str, Field(description="The topic to generate ideas for.")],
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the generation. The default model name is 'default', which will pick the server's default model.", default='default')],
    idea_count: Annotated[int, Field(description="[Optional] The number of ideas to generate. The default value is 1.", default=1)],
    temperature: Annotated[float, Field(description="The temperature of the llm to use for generating the ideas. The default value is 0.7 .", default=0.7)]
    ) -> str:
    return await workflow.generate_ideas_on_topic(ctx=ctx, model=model, topic=topic, idea_count=idea_count, temperature=temperature)

@mcp.tool(
    name="list_available_models",
    description="Lists all available large language models accessible by the sokrates-mcp server.",
    tags={"refinement", "llm", "models", "list"}
)
async def list_available_models(ctx: Context) -> str:
    """
    Returns a list of all available large language models.

    Args:
        ctx (Context): The MCP context object.

    Returns:
        str: A string containing the list of available models.

    This function queries the workflow to get a list of all models accessible by the server.
    """
    return await workflow.list_available_models(ctx=ctx)

if __name__ == "__main__":
    mcp.run()
    # mcp.run(transport="streamable-http")