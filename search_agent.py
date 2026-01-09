"""
Search agent for executing web searches and summarizing results.
"""
import asyncio
from typing import List
import logging
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from llm_models import model_mini
from state import WebSearchItem, ResearchState

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEARCH_INSTRUCTIONS = """You are a research assistant. Your task is to use the web_search_tool to search for information.

IMPORTANT: When using the web_search_tool, you MUST provide a 'query' parameter with the search term.

Search the web for the given term and produce a concise summary of the results. 
The summary must be 2-3 paragraphs and less than 300 words. 
Capture the main points. Write succinctly.

Focus on:
1. Key facts and data
2. Important dates and versions
3. Main features and capabilities
4. Comparisons and differentiations
5. Recent developments"""

@tool
def web_search_tool(query: str) -> str:
    """Search the web for the given term. Use this for research.
    
    Args:
        query: The search term to look up.
    """
    try:
        print(f"🔍 Searching for: {query}")
        search = TavilySearchResults(max_results=3)
        result = search.invoke({"query": query})  # Pass as dictionary
        return str(result)
    except Exception as e:
        error_msg = f"Error performing search for '{query}': {e}"
        print(f"❌ {error_msg}")
        return error_msg

async def search_node(state: ResearchState) -> dict:
    """SearchAgent: Executes web searches and summarizes results."""
    print(f"🔍 Executing {len(state['search_plan'])} searches...")
    
    try:
        # Bind the tool to the model
        search_agent = model_mini.bind_tools([web_search_tool])
        
        async def perform_single_search(item: WebSearchItem) -> str:
            try:
                print(f"  Starting search: '{item.query}'")
                
                # Create initial message
                initial_msg = [
                    SystemMessage(content=SEARCH_INSTRUCTIONS),
                    HumanMessage(content=f"Please search for information about: {item.query}\nReason for this search: {item.reason}")
                ]
                
                # Get initial response
                res1 = await search_agent.ainvoke(initial_msg)
                logger.info(f"Initial response: {res1}")
                
                messages = list(initial_msg) + [res1]
                summary = ""

                # Handle tool calls
                if hasattr(res1, 'tool_calls') and res1.tool_calls:
                    print(f"  Tool calls detected: {res1.tool_calls}")
                    
                    for tc in res1.tool_calls:
                        if tc['name'] == 'web_search_tool':
                            try:
                                # Ensure query parameter exists
                                args = tc.get('args', {})
                                if not isinstance(args, dict):
                                    args = {"query": str(args)}
                                
                                # Add query if missing
                                if 'query' not in args:
                                    args['query'] = item.query
                                
                                logger.info(f"Calling web_search_tool with args: {args}")
                                out = web_search_tool.invoke(args)
                                
                                messages.append(ToolMessage(
                                    content=str(out),
                                    tool_call_id=tc['id']
                                ))
                                
                                # Get summary from model
                                res2 = await search_agent.ainvoke(messages)
                                summary = res2.content
                                
                            except Exception as e:
                                logger.error(f"Error in tool execution: {e}")
                                summary = f"Error searching for {item.query}: {e}"
                else:
                    # If no tool calls, use the initial response
                    summary = res1.content
                
                # Format the result
                result = f"""SEARCH: {item.query}
REASON: {item.reason}
SUMMARY: {summary if summary else 'No summary generated'}
{'='*60}"""
                
                print(f"  ✓ Completed search: '{item.query}'")
                return result
                
            except Exception as e:
                error_msg = f"Error in search for '{item.query}': {e}"
                print(f"  ❌ {error_msg}")
                return error_msg
        
        # Execute searches in parallel
        results = await asyncio.gather(
            *[perform_single_search(item) for item in state["search_plan"]],
            return_exceptions=True
        )
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_msg = f"Search {i+1} failed: {result}"
                processed_results.append(error_msg)
                print(f"❌ {error_msg}")
            else:
                processed_results.append(result)
        
        print("✅ Web research completed.")
        return {
            "search_results": processed_results,
            "messages": [AIMessage(content="Web research completed.")]
        }
        
    except Exception as e:
        error_msg = f"Error in search_node: {e}"
        print(f"❌ {error_msg}")
        return {
            "search_results": [f"Search error: {e}"],
            "messages": [AIMessage(content="Error in search phase.")]
        }