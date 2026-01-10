# from typing import List
# from pydantic import Field
# from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
# from llm_models import model_mini
# from state import WebSearchItem, WebSearchPlan, ResearchState

# HOW_MANY_SEARCHES = 3

# PLANNER_INSTRUCTIONS = """You are a helpful research assistant.
# Given a query, come up with a set of web searches to perform to best answer the query.
# Output exactly {HOW_MANY_SEARCHES} terms to query for. Focus on recent and distinct queries.
# For each search, provide:
# 1. A clear reason why this search is important
# 2. A specific, actionable search query

# Make sure the searches are comprehensive and cover different aspects of the topic.""".format(HOW_MANY_SEARCHES=HOW_MANY_SEARCHES)

# async def planner_node(state: ResearchState) -> dict:
#     """PlannerAgent: Logic to generate the search plan."""
#     print("Planning the searches...🤔")
    
#     # Create the planner with structured output
#     # planner = model_mini.with_structured_output(WebSearchPlan)
#     planner = model_mini 
#     response = await planner.ainvoke([...])
#     plan = WebSearchPlan.model_validate(json.loads(response.content))
    
#     response = await planner.ainvoke([
#         SystemMessage(content=PLANNER_INSTRUCTIONS),
#         HumanMessage(content=f"Query: {state['query']}")
#     ])
    
#     print(f"Will search {len(response.searches)} searches 🔎")
#     return {
#         "search_plan": response.searches,
#         "messages": [AIMessage(content=f"Planned {len(response.searches)} searches.")]
#     }
















import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from llm_models import model_mini
from state import WebSearchItem, WebSearchPlan, ResearchState

HOW_MANY_SEARCHES = 3

PLANNER_INSTRUCTIONS = f"""
You are a helpful research assistant.
Given a query, come up with exactly {HOW_MANY_SEARCHES} web searches to answer the query comprehensively.
Output a JSON object with the following structure:

{{
  "searches": [
    {{
      "query": "<specific search term>",
      "reason": "<reason why this search is important>"
    }}
  ]
}}

Ensure the searches are recent, distinct, and cover different aspects of the topic.
Only output JSON — no extra text or markdown.
"""

async def planner_node(state: ResearchState) -> dict:
    """PlannerAgent: Logic to generate the search plan."""
    print("Planning the searches...🤔")
    
    planner = model_mini

    # Call the model
    response: AIMessage = await planner.ainvoke([
        SystemMessage(content=PLANNER_INSTRUCTIONS),
        HumanMessage(content=f"Query: {state['query']}")
    ])

    # Parse JSON safely
    try:
        plan_data = json.loads(response.content)
        plan = WebSearchPlan.model_validate(plan_data)
        print(f"Will search {len(plan.searches)} searches 🔎")
        return {
            "search_plan": plan.searches,
            "messages": [AIMessage(content=f"Planned {len(plan.searches)} searches.")]
        }
    except (json.JSONDecodeError, ValueError) as e:
        print(f"⚠️ Failed to parse planner output: {e}")
        return {
            "search_plan": [],
            "messages": [AIMessage(content="Planner failed to generate a valid search plan.")]
        }
