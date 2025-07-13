from fastmcp import Context
from mcp_config import MCPConfig
from llm_tools import FileHelper, RefinementWorkflow, LLMApi, PromptRefiner

class Workflow:
  
  def __init__(self, config: MCPConfig):
    self.config = config
    self.llm_api = LLMApi()
    self.prompt_refiner = PromptRefiner()
    self.refinement_workflow = RefinementWorkflow(api_endpoint=config.api_endpoint, api_key=config.api_key, model=config.model)
    
  async def refine_prompt(self, prompt: str, ctx: Context, model: str) -> str:
    refinement_prompt_file = f"{MCPConfig.DEFAULT_PROMPTS_DIRECTORY}/{MCPConfig.DEFAULT_REFINEMENT_PROMPT_FILENAME}"
    refinement_prompt = FileHelper.read_file(refinement_prompt_file, verbose=False)
    
    await ctx.info(f"Prompt refinement and execution workflow started with refinement model: {model} . Waiting for the response from the LLM...")
    refined = self.refinement_workflow.refine_prompt(prompt, refinement_prompt)
    await ctx.info(MCPConfig.WORKFLOW_COMPLETION_MESSAGE)
    return refined
  
  async def refine_and_execute_external_prompt(self, prompt: str, ctx: Context, refinement_model: str, execution_model: str) -> str:
    refinement_prompt_file = f"{MCPConfig.DEFAULT_PROMPTS_DIRECTORY}/{MCPConfig.DEFAULT_REFINEMENT_PROMPT_FILENAME}"
    refinement_prompt = FileHelper.read_file(refinement_prompt_file, verbose=False)
    
    await ctx.info(f"Prompt refinement and execution workflow started with refinement model: {refinement_model} and execution model {execution_model} . Waiting for the responses from the LLMs...")
    result = self.refinement_workflow.refine_and_send_prompt(input_prompt=prompt, refinement_prompt=refinement_prompt, refinement_model=refinement_model, execution_model=execution_model)
    await ctx.info(MCPConfig.WORKFLOW_COMPLETION_MESSAGE)
    return result
  
  async def handover_prompt(self, prompt: str, ctx: Context, model: str) -> str:
    llm_api = LLMApi(api_endpoint=self.config.api_endpoint, api_key=self.config.api_key)
    refiner = PromptRefiner()
    result = llm_api.send(prompt,model=model)
    result = refiner.clean_response(result)
    
    await ctx.info(f"External Prompt execution workflow started with model: {model} . Waiting for the responses from the LLM...")
    await ctx.info(MCPConfig.WORKFLOW_COMPLETION_MESSAGE)
    return result
  
  async def breakdown_task(self, task: str, ctx: Context, model: str) -> str:
    breakdown_instructions_filepath = f"{MCPConfig.DEFAULT_PROMPTS_DIRECTORY}/breakdown-v1.md"
    breakdown_instructions = FileHelper.read_file(breakdown_instructions_filepath, verbose=False)

    await ctx.info(f"Task break-down started with model: {model} . Waiting for the response from the LLM...")
    result = self.refinement_workflow.breakdown_task(task=task, breakdown_instructions=breakdown_instructions, model=model)
    await ctx.info(MCPConfig.WORKFLOW_COMPLETION_MESSAGE)
    return result