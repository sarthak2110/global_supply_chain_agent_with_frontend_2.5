"""
Central Orchestrator (The "Brain"):
Logic: Manages the "Dynamic Agent Selection" process. It identifies the user's intent, 
delegates tasks to the sub-agents, shares relevant context between them, 
and consolidates the final recommendation for the user.
"""



from google.adk.agents.llm_agent import Agent
from .sub_agents import supplier_negotiator_agent   #, inventory_analyst_agent, logistics_resolver_agent, 
from .prompt import client_preview_prompt           #central_orchestrator_agent_prompt


root_agent = Agent(
    model='gemini-2.5-pro',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=client_preview_prompt,
    sub_agents=[
        # inventory_analyst_agent,
        # logistics_resolver_agent,
        supplier_negotiator_agent
        ],
)












# """
# Central Orchestrator (The "Brain"):
# Logic: Manages the "Dynamic Agent Selection" process. It identifies the user's intent, 
# delegates tasks to the sub-agents, shares relevant context between them, 
# and consolidates the final recommendation for the user.
# """

# import logging
# from google.adk.agents.llm_agent import Agent
# from .sub_agents import inventory_analyst_agent, logistics_resolver_agent, supplier_negotiator_agent
# from .prompt import central_orchestrator_agent_prompt
# from .flag_config import get_saas_flag_value

# # 1. Set up the logger for this module
# logger = logging.getLogger(__name__)
# # Optional: Set level to INFO if it isn't configured globally
# logger.setLevel(logging.INFO) 

# def get_model():
#     default_model = 'gemini-2.5-flash'
#     try:
#         is_saas = get_saas_flag_value()
#         logger.info(f"SaaS flag evaluated to: {is_saas}")
        
#         if is_saas:
#             model_name = 'gemini-2.5-pro'
#         else:
#             model_name = 'gemini-2.5-flash'
            
#         logger.info(f"Model resolved to: {model_name}")
#         return model_name
#     except Exception as e:
#         logger.error(f"Error fetching SaaS flag: {e}. Defaulting to {default_model}")
#         return default_model

# # 2. DEFINE the callback function FIRST
# def pre_run_model_update(callback_context) -> None:
#     """
#     ADK Callback: Fires right before the Runner executes the agent logic.
#     """
#     logger.info("--- before_agent_callback triggered: Checking for model updates ---")
    
#     live_model = get_model()
    
#     # Log the transition (even if it's the same, it helps confirm the check happened)
#     logger.info(f"Updating root_agent model from '{root_agent.model}' to '{live_model}'")
    
#     root_agent.model = live_model
#     logger.info("--- Callback complete. Agent is resuming execution ---")
    
#     return None

# # 3. THEN initialize the agent and pass the defined function
# logger.info("Initializing root_agent on module load...")

# root_agent = Agent(
#     model=get_model(), 
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     instruction=central_orchestrator_agent_prompt,
#     sub_agents=[
#         inventory_analyst_agent,
#         logistics_resolver_agent,
#         supplier_negotiator_agent
#         ],
#     before_agent_callback=pre_run_model_update 
# )

# logger.info(f"root_agent initialized successfully with starting model: {root_agent.model}")






















# """
# Central Orchestrator (The "Brain"):
# Logic: Manages the "Dynamic Agent Selection" process. It identifies the user's intent, 
# delegates tasks to the sub-agents, shares relevant context between them, 
# and consolidates the final recommendation for the user.
# """

# from google.adk.agents.llm_agent import Agent
# from .sub_agents import inventory_analyst_agent, logistics_resolver_agent, supplier_negotiator_agent
# from .prompt import central_orchestrator_agent_prompt
# from .flag_config import get_saas_flag_value

# def get_model():
#     default_model = 'gemini-2.5-flash'
#     try:
#         is_saas = get_saas_flag_value()
#         if is_saas:
#             model_name = 'gemini-2.5-pro'
#         else:
#             model_name = 'gemini-2.5-flash'
            
#         print(f"\n\n\tMODEL USING : {model_name}\n\n")
#         return model_name
#     except:
#         return default_model

# # 1. DEFINE the callback function FIRST
# def pre_run_model_update(callback_context) -> None:
#     """
#     ADK Callback: Fires right before the Runner executes the agent logic.
#     """
#     live_model = get_model()
#     root_agent.model = live_model
#     return None

# # 2. THEN initialize the agent and pass the defined function
# root_agent = Agent(
#     model=get_model(), 
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     instruction=central_orchestrator_agent_prompt,
#     sub_agents=[
#         inventory_analyst_agent,
#         logistics_resolver_agent,
#         supplier_negotiator_agent
#         ],
#     before_agent_callback=pre_run_model_update # Now Python knows what this is!
# )