from __future__ import annotations

import os
import re
import json
import httpx
import logging
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
ENGINE_ID = "8388183554151940096"

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
# This translates technical tool calls into Gemini-style "Thinking" steps
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
    credentials, project = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    client = storage.Client(project=project, credentials=credentials)
    blob = client.bucket(bucket).blob(object_name)
    return blob.generate_signed_url(version="v4", method="GET", expiration=timedelta(minutes=ttl_min), response_disposition="inline")

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
        '<div class="header-profile"><span class="model-info">Model: SupplyChain-v4.2</span></div>'
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
                                # 1. Handle Technical Tool Calls -> Transform to Human Steps
                                if "function_call" in part:
                                    fn_name = part["function_call"].get("name", "")
                                    human_step = TOOL_DESCRIPTIONS.get(fn_name, f"Processing data via {fn_name.replace('_', ' ')}...")
                                    await thought_step.stream_token(f"📍 **{human_step}**\n\n")

                                # 2. Handle Rationale/Answers from the Engine
                                if "function_response" in part:
                                    inner = part["function_response"].get("response", {}).get("response", [])
                                    if isinstance(inner, list):
                                        for item in inner:
                                            if "Answer" in item:
                                                ans = re.sub(r'([a-z])([A-Z])', r'\1 \2', item["Answer"])
                                                await thought_step.stream_token(f"{ans}\n\n")
                                            elif "SQL Generated" in item:
                                                await thought_step.stream_token(f"📊 **Database Insights:**\n```sql\n{item['SQL Generated']}\n```\n\n")
                                
                                # 3. Handle Gemini's Native 'Thought' Block (Gemini 2.5 feature)
                                if "thought" in part:
                                    await thought_step.stream_token(f"{part['thought']}\n\n")

                    except json.JSONDecodeError: continue
    except Exception as e:
        logger.error(f"Stream Error: {e}")
    finally:
        if thought_step: await thought_step.update()
        if message_started: await msg.update()
        else: await cl.Message(content="✅ *Action completed.*").send()

    if wants_map(user_text):
        await render_map(generate_signed_map_url(GCS_BUCKET, GCS_OBJECT))