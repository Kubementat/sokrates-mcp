from fastmcp import Context
from mcp_config import MCPConfig
from sokrates import FileHelper, RefinementWorkflow, LLMApi, PromptRefiner, IdeaGenerationWorkflow
from pathlib import Path
class Workflow:
  
  WORKFLOW_COMPLETION_MESSAGE = "Workflow completed."
  
  def __init__(self, config: MCPConfig):
    self.config = config
    self.llm_api = LLMApi()
    self.prompt_refiner = PromptRefiner()
    self.refinement_workflow = RefinementWorkflow(api_endpoint=config.api_endpoint, api_key=config.api_key, model=config.model)
    
  def get_model(self, model=None):
    if model == 'None' or model == 'default' or model is None:
      return self.config.model
    return model
  
  def initialize_refinement_workflow(self, api_endpoint: str = None, api_key: str = None, model: str = None):
    model = self.get_model(model)
    if api_endpoint is None:
      api_endpoint = self.config.api_endpoint
    if api_key is None:
      api_key = self.config.api_key
    self.refinement_workflow = RefinementWorkflow(api_endpoint=api_endpoint, api_key=api_key, model=model)
    
  def load_refinement_prompt(self, refinement_type : str = 'default'):
    path=self.config.prompts_directory
    
    if refinement_type == 'code' or refinement_type == 'coding':
      refinement_prompt_file = str(Path(f"{path}/{self.config.refinement_coding_prompt_filename}").resolve())
    else:
      refinement_prompt_file = str(Path(f"{path}/{self.config.refinement_prompt_filename}").resolve())

    return FileHelper.read_file(refinement_prompt_file, verbose=False)
    
  async def refine_prompt(self, prompt: str, ctx: Context, model: str, refinement_type: str = 'default') -> str:
    refinement_prompt = self.load_refinement_prompt(refinement_type)
    self.initialize_refinement_workflow(model=model)
    model = self.get_model(model)
    
    await ctx.info(f"Prompt refinement and execution workflow started with refinement model: {model} . Waiting for the response from the LLM...")
    refined = self.refinement_workflow.refine_prompt(input_prompt=prompt, refinement_prompt=refinement_prompt)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return refined
  
  async def refine_and_execute_external_prompt(self, prompt: str, ctx: Context, refinement_model: str, execution_model: str, refinement_type: str = 'default') -> str:
    refinement_prompt = self.load_refinement_prompt(refinement_type)
    
    refinement_model = self.get_model(refinement_model)
    execution_model = self.get_model(execution_model)
    
    await ctx.info(f"Prompt refinement and execution workflow started with refinement model: {refinement_model} and execution model {execution_model} . Waiting for the responses from the LLMs...")
    result = self.refinement_workflow.refine_and_send_prompt(input_prompt=prompt, refinement_prompt=refinement_prompt, refinement_model=refinement_model, execution_model=execution_model)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result
  
  async def handover_prompt(self, prompt: str, ctx: Context, model: str, temperature=0.7) -> str:
    llm_api = LLMApi(api_endpoint=self.config.api_endpoint, api_key=self.config.api_key)
    refiner = PromptRefiner()
    
    model = self.get_model(model)
    
    result = llm_api.send(prompt,model=model, temperature=temperature)
    result = refiner.clean_response(result)
    
    await ctx.info(f"External Prompt execution workflow started with model: {model} . Waiting for the responses from the LLM...")
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result
  
  async def breakdown_task(self, task: str, ctx: Context, model: str) -> str:
    model = self.get_model(model)
    await ctx.info(f"Task break-down started with model: {model} . Waiting for the response from the LLM...")
    result = self.refinement_workflow.breakdown_task(task=task, model=model)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result
  
  async def generate_random_ideas(self, ctx: Context, idea_count: int = 1, temperature: float = 0.7, model: str = None) -> str:
    await ctx.info(f"Task `generate random ideas` started with model: {model} , idea_count: {idea_count} and temperature: {temperature}. Waiting for the response from the LLM...")
    if model == 'default':
      model = None
    idea_generation_workflow = IdeaGenerationWorkflow(api_endpoint=self.config.api_endpoint, 
      api_key=self.config.api_key, 
      idea_count=idea_count, 
      temperature=temperature,
      generator_llm_model=model,
      refinement_llm_model=model,
      execution_llm_model=model,
      topic_generation_llm_model=model
    )
    results = idea_generation_workflow.run()
    result_text = f"\n---\n".join(results)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result_text
  
  async def generate_ideas_on_topic(self, ctx: Context, topic: str, idea_count: int = 1, temperature: float = 0.7, model: str = None) -> str:
    await ctx.info(f"Task `generate ideas on topic` started with topic: '{topic}' , model: {model} , idea_count: {idea_count} and temperature: {temperature}. Waiting for the response from the LLM...")
    if model == 'default':
      model = None
    idea_generation_workflow = IdeaGenerationWorkflow(api_endpoint=self.config.api_endpoint, 
      api_key=self.config.api_key, 
      topic=topic,
      idea_count=idea_count, 
      temperature=temperature,
      generator_llm_model=model,
      refinement_llm_model=model,
      execution_llm_model=model,
      topic_generation_llm_model=model
    )
    results = idea_generation_workflow.run()
    result_text = f"\n---\n".join(results)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result_text

  async def list_available_models(self, ctx: Context) -> str:
    await ctx.info("Retrieving list of available models...")
    models = self.llm_api.list_models()
    if not models:
      return "# No models available"

    model_list = "\n".join([f"- {model}" for model in models])
    result = f"# List of available models\n{model_list}"
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result