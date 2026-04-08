from __future__ import annotations

import os
import re
import json
import httpx
import logging
import base64
from datetime import timedelta

import chainlit as cl
from google.cloud import storage
import google.auth
import google.auth.transport.requests

# ----------------------------
# Config
# ----------------------------
PROJECT_ID = "saas-poc-env"
LOCATION = "us-central1"
ENGINE_ID = "8954972452421632"
# https://us-central1-aiplatform.googleapis.com/v1/projects/736134210043/locations/us-central1/reasoningEngines/8954972452421632:query
# AGENT_ENGINE_QUERY_URL = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{ENGINE_ID}:query"
# AGENT_ENGINE_STREAM_URL = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{ENGINE_ID}:streamQuery?alt=sse"

AGENT_ENGINE_QUERY_URL = os.environ.get(
    "AGENT_ENGINE_QUERY_URL",
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{ENGINE_ID}:query"
)
AGENT_ENGINE_STREAM_URL = os.environ.get(
    "AGENT_ENGINE_STREAM_URL",
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{ENGINE_ID}:streamQuery?alt=sse"
)


GCS_BUCKET = os.environ.get("GCS_BUCKET", "sarthak-test")
GCS_OBJECT = os.environ.get("GCS_OBJECT", "maps/route_map.html")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chainlit-frontend")

# ----------------------------
# Logic Humanizer Map
# ----------------------------
TOOL_DESCRIPTIONS = {
    "ask_data_insights": "Analyzing supply chain data for specific inventory patterns...",
    "land_route_map": "Calculating the most efficient driving route and preparing geographic data...",
    "transfer_to_agent": "Routing the request to a specialized regional specialist...",
    "query_inventory": "Checking real-time stock levels across global warehouse locations...",
    "get_weather": "Assessing environmental factors that may impact logistics timelines..."
}

# ----------------------------
# Helpers
# ----------------------------
def wants_map(text: str) -> bool:
    t = text.lower()
    return "map" in t or "route" in t or "direction" in t

def generate_signed_map_url(bucket: str, object_name: str, ttl_min: int = 30) -> str:
    # FIX 2: Workstation 400 Impersonation Fix & Base64 Fallback
    try:
        credentials, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        
        client = storage.Client(project=project, credentials=credentials)
        blob = client.bucket(bucket).blob(object_name)
        
        kwargs = {
            "version": "v4",
            "method": "GET",
            "expiration": timedelta(minutes=ttl_min),
            "response_disposition": "inline",
        }
        
        sa_email = getattr(credentials, "service_account_email", None)
        
        if sa_email == "default":
            try:
                resp = httpx.get(
                    "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email",
                    headers={"Metadata-Flavor": "Google"},
                    timeout=2.0
                )
                if resp.status_code == 200:
                    sa_email = resp.text.strip()
            except Exception:
                pass

        if sa_email and sa_email != "default":
            kwargs["service_account_email"] = sa_email
            if hasattr(credentials, "token") and credentials.token:
                kwargs["access_token"] = credentials.token

        return blob.generate_signed_url(**kwargs)
        
    except Exception as e:
        logger.warning(f"Signing failed ({e}). Falling back to direct Data URI render!")
        html_content = blob.download_as_text()
        b64_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
        return f"data:text/html;base64,{b64_html}"

async def render_map(map_url: str):
    map_el = cl.CustomElement(name="RouteMap", props={"src": map_url, "height": 420}, display="inline")
    await cl.Message(content="✅ **Route Map Generated:**", elements=[map_el]).send()

def get_bearer_token() -> str:
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    return creds.token

# ----------------------------
# Chainlit Events
# ----------------------------
@cl.on_chat_start
async def start():
    cl.user_session.set("initialized", True)
    user = cl.user_session.get("user")
    user_id = user.identifier if user else "logistics-manager"
    cl.user_session.set("user_id", user_id)

    welcome_html = (
        '<style>.MuiAvatar-root { display: none !important; }</style>'
        '<div class="scmgpt-container">'
        '<div class="header-profile"><span class="model-info">Model: SupplyChain-v2.5-pro</span></div>'
        '<div class="welcome-area">'
        '<h1>Hello, <span class="highlight">Logistics Manager</span></h1>'
        '<p class="sub-headline">Where should we start?</p>'
        "</div>"
        "</div>"
    )
    await cl.Message(content=welcome_html).send()
    
    payload = {"class_method": "async_create_session", "input": {"user_id": user_id}}
    headers = {"Authorization": f"Bearer {get_bearer_token()}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(AGENT_ENGINE_QUERY_URL, json=payload, headers=headers)
            data = resp.json()
            cl.user_session.set("session_id", data.get("output", {}).get("id"))
    except Exception as e:
        logger.error(f"Init Error: {e}")
        await cl.Message(content=f"❌ **Connection Error:** Could not reach the backend. {e}").send()

@cl.on_message
async def main(message: cl.Message):
    user_text = message.content
    user_id = cl.user_session.get("user_id")
    session_id = cl.user_session.get("session_id")
    
    # 1. Decode Mode Tag
    mode = "fast"
    if user_text.endswith('\u200D'): mode = "pro"
    elif user_text.endswith('\u200C'): mode = "thinking"
    elif user_text.endswith('\u200B'): mode = "fast"
    
    user_text = user_text.strip()
    message.content = user_text
    await message.update()

    current_agent = "Central Orchestrator"
    msg = cl.Message(content="")
    message_started = False

    # 2. Init Thought Step
    thought_step = None
    if mode in ["thinking", "pro"]:
        thought_step = cl.Step(name="Thought process", type="run")
        await thought_step.send()

    payload = {"class_method": "async_stream_query", "input": {"user_id": user_id, "session_id": session_id, "message": user_text}}
    headers = {"Authorization": f"Bearer {get_bearer_token()}", "Content-Type": "application/json", "Accept": "text/event-stream"}

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", AGENT_ENGINE_STREAM_URL, json=payload, headers=headers) as response:
                
                if response.status_code != 200:
                    error_data = await response.aread()
                    msg.content = f"❌ **API Error {response.status_code}:**\n{error_data.decode()}"
                    await msg.send()
                    return

                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line or line == "data: [DONE]": continue
                    data_str = line[5:].strip() if line.startswith("data:") else line
                    
                    try:
                        chunk = json.loads(data_str)
                        
                        # --- A. AGENT LABELING ---
                        author = chunk.get("author", "")
                        if author and author.lower() not in ["", "user", "model", "system"]:
                            current_agent = author.replace("_", " ").title()
                            if thought_step:
                                thought_step.name = f"Agent: {current_agent} | Thought process"
                                await thought_step.update()

                        # --- B. CONTENT STREAMING ---
                        content = chunk.get("content", {})
                        if isinstance(content, str) and content.strip():
                            if not message_started: await msg.send(); message_started = True
                            await msg.stream_token(re.sub(r'^Agent:.*?\n+', '', content))

                        parts = content.get("parts", []) if isinstance(content, dict) else []
                        for part in parts:
                            if "text" in part and part["text"].strip():
                                if not message_started: await msg.send(); message_started = True
                                await msg.stream_token(re.sub(r'^Agent:.*?\n+', '', part["text"]))

                            # --- C. DEEP HUMANIZED THINKING ---
                            if thought_step:
                                if "function_call" in part:
                                    fn_name = part["function_call"].get("name", "")
                                    human_step = TOOL_DESCRIPTIONS.get(fn_name, f"Processing data via {fn_name.replace('_', ' ')}...")
                                    await thought_step.stream_token(f"📍 **{human_step}**\n\n")

                                if "function_response" in part:
                                    inner = part["function_response"].get("response", {}).get("response", [])
                                    if isinstance(inner, list):
                                        for item in inner:
                                            if "Answer" in item:
                                                ans = re.sub(r'([a-z])([A-Z])', r'\1 \2', item["Answer"])
                                                await thought_step.stream_token(f"{ans}\n\n")
                                            elif "SQL Generated" in item:
                                                await thought_step.stream_token(f"📊 **Database Insights:**\n```sql\n{item['SQL Generated']}\n```\n\n")
                                
                                if "thought" in part:
                                    await thought_step.stream_token(f"{part['thought']}\n\n")

                    except json.JSONDecodeError: continue
    except Exception as e:
        logger.error(f"Stream Error: {e}")
        if not message_started:
            msg.content = f"❌ **Client Error:** {str(e)}"
            await msg.send()
        else:
            msg.content += f"\n\n⚠️ **Client Error:** {str(e)}"
    finally:
        if thought_step: await thought_step.update()
        if message_started: await msg.update()
        else: await cl.Message(content="✅ *Action completed.*").send()

    # FIX 3: SMART MAP TRIGGER
    user_intent_map = wants_map(user_text)
    agent_mentions_map = "route_map.html" in msg.content.lower()
    is_error = "technical issue" in msg.content.lower() or "cannot calculate" in msg.content.lower()
    
    if (user_intent_map or agent_mentions_map) and not is_error:
        await cl.Message(content="🗺️ Fetching latest map from GCS…").send()
        try:
            url = generate_signed_map_url(GCS_BUCKET, GCS_OBJECT)
            await render_map(url)
        except Exception as e:
            await cl.Message(content=f"❌ Failed to render map: {e}").send()