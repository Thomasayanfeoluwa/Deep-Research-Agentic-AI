from dotenv import load_dotenv
from langchain_tavily import TavilySearchResults
import os

load_dotenv()

print("--- Debugging Tavily Search ---")
print(f"API Key present: {bool(os.getenv('TAVILY_API_KEY'))}")

try:
    tool = TavilySearchResults(max_results=5)
    query = "most popular AI agent frameworks 2025"
    print(f"Running query: '{query}'...")
    
    results = tool.invoke(query)
    
    print("\n--- Raw Results ---")
    print(results)
    
    print("\n--- Analysis ---")
    for i, res in enumerate(results):
        print(f"[{i+1}] {res.get('url')}")
        print(f"     Content snippet: {res.get('content')[:200]}...")
        
except Exception as e:
    print(f"ERROR: {e}")
