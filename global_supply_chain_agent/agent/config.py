import os
import logging

# GEMINI MODELS - https://ai.google.dev/gemini-api/docs/models

logger = logging.getLogger(__name__)



INVENTORY_AGENT_LLM_MODEL_NAME = os.getenv("INVENTORY_AGENT_LLM_MODEL_NAME", 'gemini-2.5-pro')

 

PROJECT_ID= os.getenv("PROJECT_ID",'saas-poc-env')
LOCATION=os.getenv("LOCATION",'us-central1')

# MODEL_ARMOR_TEMPLATE_ID = os.getenv("MODEL_ARMOR_TEMPLATE_ID",'TravelApp_Armor')
# BIGQUERY_PROJECT_ID=os.getenv("BIGQUERY_PROJECT_ID",'saas-poc-env')