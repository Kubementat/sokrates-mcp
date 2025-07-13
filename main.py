from fastmcp import FastMCP, Context
from typing import Annotated, Optional
from pydantic import Field
from llm_tools import RefinementWorkflow, FileHelper, LLMApi, PromptRefiner
from mcp_config import MCPConfig
from workflow import Workflow

config = MCPConfig()
workflow = Workflow(config)

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
    return await workflow.refine_prompt(prompt=prompt, ctx=ctx, model=model)

# -------------------------------------------------------------------------

@mcp.tool(
    name="refine_and_execute_external_prompt",
    description="Refines a given prompt by enriching the input prompt with additional context and then executes the prompt with an external llm. It delivers back the exection result of the refined prompt on the external llm.",
    tags={"prompting", "refinement" , "external_processing"}
)
async def refine_and_execute_external_prompt(prompt: Annotated[str, Field(description="Input prompt that should be refined and then processed.")], 
    ctx: Context,
    refinement_model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the prompt refinement process. The default refinement model name is: qwen/qwen3-8b", default="qwen/qwen3-8b")],
    execution_model: Annotated[str, Field(description="[Optional] The name of the external model that should be used for the execution of the refined prompt. The default execution model name is: qwen/qwen3-8b", default="qwen/qwen3-8b")],
    ) -> str:
    """Refines a given prompt and sends it to the LLM for further processing.
    """
    return await workflow.refine_and_execute_external_prompt(prompt=prompt, ctx=ctx, refinement_model=refinement_model, execution_model=execution_model)

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
    return await workflow.handover_prompt(prompt=prompt, ctx=ctx, model=model)

# -------------------------------------------------------------------------

@mcp.tool(
    name="breakdown_task",
    description="Breaks down a task into sub-tasks back a json list of sub-tasks with complexity ratings.",
    tags={"prompting", "task", "breakdown"}
)
async def breakdown_task(task: Annotated[str, Field(description="The full task description to break down further.")], 
    ctx: Context,
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the external prompt processing. The default model name is: qwen/qwen3-8b", default="qwen/qwen3-8b")],
    ) -> str:
    """
    Breaks down a task into sub-tasks back a json list of sub-tasks with complexity ratings.
    """
    return await workflow.breakdown_task(task=task, ctx=ctx, model=model)

if __name__ == "__main__":
    mcp.run()