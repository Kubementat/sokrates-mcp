from fastmcp import Context
from .mcp_config import MCPConfig
from sokrates import FileHelper, RefinementWorkflow, LLMApi, PromptRefiner, IdeaGenerationWorkflow
from sokrates.coding.code_review_workflow import run_code_review
from pathlib import Path
from typing import List
class Workflow:
  
  WORKFLOW_COMPLETION_MESSAGE = "Workflow completed."
  
  def __init__(self, config: MCPConfig):
    self.config = config
    default_provider = self.config.get_default_provider()
    self.default_model = default_provider['default_model']
    self.default_api_endpoint = default_provider['api_endpoint']
    self.default_api_key = default_provider['api_key']

    self.prompt_refiner = PromptRefiner()
    
  def _get_model(self, provider, model=''):
    if not model or model == 'default':
      return provider['default_model']
    return model
  
  def _get_provider(self, provider_name: str = ''):
    if not provider_name or provider_name == 'default':
      return self.config.get_default_provider()
    return self.config.get_provider_by_name(provider_name)
  
  def _initialize_refinement_workflow(self, provider_name: str = '', model: str = ''):
    provider = self._get_provider(provider_name)
    model = self._get_model(provider=provider, model=model)
    self.refinement_workflow = RefinementWorkflow(api_endpoint=provider['api_endpoint'], api_key=provider['api_key'], model=model)
    return {
      'provider': provider['name'],
      'model': model
    }
    
  def load_refinement_prompt(self, refinement_type : str = 'default'):
    path=self.config.prompts_directory
    
    if refinement_type == 'code' or refinement_type == 'coding':
      refinement_prompt_file = str(Path(f"{path}/{self.config.refinement_coding_prompt_filename}").resolve())
    else:
      refinement_prompt_file = str(Path(f"{path}/{self.config.refinement_prompt_filename}").resolve())

    return FileHelper.read_file(refinement_prompt_file, verbose=False)
    
  async def refine_prompt(self, prompt: str, ctx: Context, provider: str, model: str, refinement_type: str = 'default') -> str:
    refinement_prompt = self.load_refinement_prompt(refinement_type)
    ret = self._initialize_refinement_workflow(provider_name=provider, model=model)
    
    await ctx.info(f"Prompt refinement and execution workflow started with refinement model: {ret['model']} . Waiting for the response from the LLM...")
    refined = self.refinement_workflow.refine_prompt(input_prompt=prompt, refinement_prompt=refinement_prompt)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return refined
  
  async def refine_and_execute_external_prompt(self, prompt: str, ctx: Context, provider: str, refinement_model: str, execution_model: str, refinement_type: str = 'default') -> str:
    refinement_prompt = self.load_refinement_prompt(refinement_type)

    prov = self._get_provider(provider)
    refinement_model = self._get_model(provider=prov, model=refinement_model)
    execution_model = self._get_model(provider=prov, model=execution_model)

    ret = self._initialize_refinement_workflow(provider_name=provider, model=execution_model)
    await ctx.info(f"Prompt refinement and execution workflow started with refinement model: {refinement_model} and execution model {execution_model} . Waiting for the responses from the LLMs...")
    result = self.refinement_workflow.refine_and_send_prompt(input_prompt=prompt, refinement_prompt=refinement_prompt, refinement_model=refinement_model, execution_model=execution_model)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result
  
  async def handover_prompt(self, prompt: str, ctx: Context, provider: str, model: str, temperature=0.7) -> str:
    
    refiner = PromptRefiner()
    
    prov = self._get_provider(provider)
    model = self._get_model(provider=prov, model=model)
    llm_api = LLMApi(api_endpoint=prov['api_endpoint'], api_key=prov['api_key'])

    result = llm_api.send(prompt,model=model, temperature=temperature)
    result = refiner.clean_response(result)
    
    await ctx.info(f"External Prompt execution workflow started with model: {model} . Waiting for the responses from the LLM...")
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result
  
  async def breakdown_task(self, task: str, ctx: Context, provider: str, model: str) -> str:
    ret = self._initialize_refinement_workflow(provider_name=provider, model=model)
    await ctx.info(f"Task break-down started with model: {ret['model']} . Waiting for the response from the LLM...")
    result = self.refinement_workflow.breakdown_task(task=task)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result
  
  async def generate_random_ideas(self, ctx: Context, provider: str, idea_count: int = 1, temperature: float = 0.7, model: str = None) -> str:
    prov = self._get_provider(provider)
    model = self._get_model(provider=prov, model=model)
    await ctx.info(f"Task `generate random ideas` started at provider: {prov['name']} with model: {model} , idea_count: {idea_count} and temperature: {temperature}. Waiting for the response from the LLM...")

    idea_generation_workflow = IdeaGenerationWorkflow(api_endpoint=prov['api_endpoint'], 
      api_key=prov['api_key'], 
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
  
  async def generate_ideas_on_topic(self, ctx: Context, topic: str, provider: str, model: str, idea_count: int = 1, temperature: float = 0.7) -> str:
    prov = self._get_provider(provider)
    model = self._get_model(provider=prov, model=model)

    await ctx.info(f"Task `generate ideas on topic` started with topic: '{topic}' , model: {model} , idea_count: {idea_count} and temperature: {temperature}. Waiting for the response from the LLM...")
    idea_generation_workflow = IdeaGenerationWorkflow(api_endpoint=prov['api_endpoint'], 
      api_key=prov['api_key'], 
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
  
  async def generate_code_review(self, ctx: Context, source_file_paths: List[str], target_directory: str, provider: str, model:str, review_type:str):
    prov = self._get_provider(provider)
    model = self._get_model(provider=prov, model=model)

    await ctx.info(f"Generating code review of type: {review_type} - using model: {model} - for source files: {source_file_paths} ...")
    run_code_review(file_paths=source_file_paths,
                    directory_path=None,
                    output_dir=target_directory,
                    review_type=review_type, 
                    api_endpoint=prov['api_endpoint'],
                    api_key=prov['api_key'],
                    model=model)
    # TODO: also include some basic info of the review results (e.g. the complete review file list)
    # so that the caller gains more information about the result and file locations
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return f"Successfully generated review files in {target_directory} ."
    
    
  async def list_available_providers(self, ctx: Context) -> str:
    providers = self.config.available_providers()
    result = "# Configured providers"
    for prov in providers:
      prov_string = f"-{prov['name']} : type: {prov['type']} - api_endpoint: {prov['api_endpoint']}"
      result = f"{result}\n{prov_string}"
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result

  async def list_available_models_for_provider(self, ctx: Context, provider_name: str = "") -> str:
    await ctx.info(f"Retrieving endpoint information and list of available models for configured provider {provider_name} ...")
    if not provider_name:
      provider = self.config.get_default_provider()
    else:
      provider = self.config.get_provider_by_name(provider_name)
    
    llm_api = LLMApi(api_endpoint=provider['api_endpoint'], api_key=provider['api_key'])
    models = llm_api.list_models()
    if not models:
      return "# No models available"

    api_headline = f"# Target API Endpoint\n{provider['api_endpoint']}\n"

    model_list = "\n".join([f"- {model}" for model in models])
    result = f"{api_headline}\n# List of available models\n{model_list}"
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result