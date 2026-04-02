"""
Logistics Resolver Agent:
Logic: Calls external shipping and weather APIs to identify delays (e.g., port congestion). It autonomously reroutes shipments to maintain connectivity and minimize downtime.
Tools: Interacts with third-party logistics (3PL) tracking systems and mapping services.
"""

from __future__ import annotations

from google.adk.agents import Agent
from datetime import date
import os
import asyncio

from .prompt import build_logistics_resolver_prompt
from .tools import land_route_map 
from .tools.load_excel_data_tool import load_data_from_excel, to_json_blobs
from agent.config import LOGISTICS_AGENT_LLM_MODEL_NAME
def create_agent() -> Agent:
    """
    ADK calls this function dynamically.
    """
    # 1. Load data
    suppliers_list, quotes_list, finance_policy = load_data_from_excel()

    # ---> THE FIX: Remove the problematic PO format string <---
    if "po_number_format" in finance_policy:
        del finance_policy["po_number_format"]

    # 2. Extract ONLY the city from the ship_to address 
    ship_to_full = finance_policy.get("po_defaults", {}).get("ship_to", "")
    destination_city = ship_to_full.split(",")[-1].strip() if ship_to_full else "Unknown City"

    # 3. Convert to JSON blobs
    suppliers_json, quotes_json, finance_policy_json = to_json_blobs(
        suppliers_list, quotes_list, finance_policy
    )

    # 4. Build instruction with the extracted city
    instruction = build_logistics_resolver_prompt(
        suppliers_json=suppliers_json,
        quotes_json=quotes_json,
        finance_policy_json=finance_policy_json,
        destination_city=destination_city,
        today_iso=date.today().isoformat(),
    )

    return Agent(
        model=LOGISTICS_AGENT_LLM_MODEL_NAME,
        name="logistics_resolver_agent",
        description=(
            "Simulates weather delays and uses the Google Maps MCP tool to autonomously "
            "calculate alternative land routes between cities, ensuring compliance with financial limits."
        ),
        instruction=instruction,
        tools=[land_route_map], 
    )

# Export for ADK Web
# logistics_resolver_agent = create_agent()

# Export for ADK Web
logistics_resolver_agent = create_agent()


# from .tools import land_route_map   #, flying_tracks_map

# logistics_resolver_agent = Agent(
#     model="gemini-2.0-flash",
#     name="logistics_resolver_agent",
#     description=(
#         "An agent that generates interactive route maps for land routes using Google Directions, "
#         # "and visualizes recent observed flight tracks using OpenSky."
#     ),
#     instruction=route_planner_prompt,
#     tools=[land_route_map], #flying_tracks_map
# )






# gcloud beta services enable mapstools.googleapis.com --project=saas-poc-env
# gcloud beta services mcp enable mapstools.googleapis.com --project=saas-poc-env