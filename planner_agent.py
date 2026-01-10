from typing import List
from pydantic import Field
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from llm_models import model_mini
from state import WebSearchItem, WebSearchPlan, ResearchState

HOW_MANY_SEARCHES = 3

PLANNER_INSTRUCTIONS = """You are a helpful research assistant.
Given a query, come up with a set of web searches to perform to best answer the query.
Output exactly {HOW_MANY_SEARCHES} terms to query for. Focus on recent and distinct queries.
For each search, provide:
1. A clear reason why this search is important
2. A specific, actionable search query

Make sure the searches are comprehensive and cover different aspects of the topic.""".format(HOW_MANY_SEARCHES=HOW_MANY_SEARCHES)

async def planner_node(state: ResearchState) -> dict:
    """PlannerAgent: Logic to generate the search plan."""
    print("Planning the searches...🤔")
    
    # Create the planner with structured output
    planner = model_mini.with_structured_output(WebSearchPlan)
    response = await planner.ainvoke([
        SystemMessage(content=PLANNER_INSTRUCTIONS),
        HumanMessage(content=f"Query: {state['query']}")
    ])
    
    print(f"Will search {len(response.searches)} searches 🔎")
    return {
        "search_plan": response.searches,
        "messages": [AIMessage(content=f"Planned {len(response.searches)} searches.")]
    }






