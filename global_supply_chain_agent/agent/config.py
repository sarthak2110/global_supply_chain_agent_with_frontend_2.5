import os
import logging

# GEMINI MODELS - https://ai.google.dev/gemini-api/docs/models

logger = logging.getLogger(__name__)



INVENTORY_AGENT_LLM_MODEL_NAME =    os.getenv("INVENTORY_AGENT_LLM_MODEL_NAME", 'gemini-2.5-pro')
LOGISTICS_AGENT_LLM_MODEL_NAME=     os.getenv("LOGISTICS_AGENT_LLM_MODEL_NAME", 'gemini-2.5-pro')
SUPPLIER_AGENT_LLM_MODEL_NAME=      os.getenv("SUPPLIER_AGENT_LLM_MODEL_NAME", 'gemini-2.5-pro')
 

PROJECT_ID= os.getenv("PROJECT_ID",'saas-poc-env')
LOCATION=os.getenv("LOCATION",'us-central1')


BQ_TABLE_NAME = os.getenv("BQ_TABLE_NAME", 'inventory_data')
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", 'mcp')
BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID", 'saas-poc-env')

# MODEL_ARMOR_TEMPLATE_ID = os.getenv("MODEL_ARMOR_TEMPLATE_ID",'TravelApp_Armor')
# BIGQUERY_PROJECT_ID=os.getenv("BIGQUERY_PROJECT_ID",'saas-poc-env')