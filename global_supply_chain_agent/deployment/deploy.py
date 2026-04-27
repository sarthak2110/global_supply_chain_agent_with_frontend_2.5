import os

os.environ.setdefault("PROJECT", "<>")
os.environ.setdefault("LOCATION", "us-central1")
os.environ.setdefault("STAGING_BUCKET", "<>")

# --- Imports ---

from agent.agent import root_agent
from vertexai.preview import reasoning_engines
from vertexai import agent_engines
import vertexai

# --- User Variables ---
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

# --- Initialize Vertex AI ---
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

print(f"Current Directory: {os.getcwd()}")

# --- Deploy to Google Cloud ---
try:
    remote_agent = agent_engines.AgentEngine.create(
        agent_engine=root_agent,                              
        requirements="./requirements.txt",
        extra_packages=["./agent"],
        display_name="global supply chain agent",
        description="deployed by agent_engine_deploy.py",
        env_vars={
            "GOOGLE_GENAI_USE_VERTEXAI": "TRUE",
            "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "TRUE",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "TRUE",
            "MAPS_GCS_BUCKET": "<>",
            "GOOGLE_MAPS_API_KEY":"<>",
            "PROJECT_ID": '<>',
            "LOCATION": '<>',
            "BQ_TABLE_NAME":'<>',
            "BQ_DATASET_ID":'<>',
            "BQ_PROJECT_ID":'<>'
        }
    )
    print("✅ Deployment successful!")
    print(f"Agent Resource Name: {remote_agent.resource_name}")
except Exception as e:
    print(f"❌ Deployment failed: {e}")

