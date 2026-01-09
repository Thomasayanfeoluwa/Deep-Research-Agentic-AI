import asyncio
import traceback
from typing import Generator
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Import modules
from llm_models import model_mini, model_large
from state import ResearchState, ReportData
from planner_agent import planner_node
from search_agent import search_node
from writer_agent import writer_node
from notification_agent import push_node

class ResearchManager:
    """Manages the research workflow."""
    
    def __init__(self):
        """Initialize the research workflow graph."""
        print("🚀 Initializing Research Manager...")
        
        try:
            # Build the StateGraph
            self.builder = StateGraph(ResearchState)
            
            # Add nodes
            self.builder.add_node("planner", planner_node)
            self.builder.add_node("researcher", search_node)
            self.builder.add_node("writer", writer_node)
            self.builder.add_node("notifier", push_node)
            
            # Add edges
            self.builder.add_edge(START, "planner")
            self.builder.add_edge("planner", "researcher")
            self.builder.add_edge("researcher", "writer")
            self.builder.add_edge("writer", "notifier")
            self.builder.add_edge("notifier", END)
            
            # Compile graph
            memory = MemorySaver()
            self.graph = self.builder.compile(checkpointer=memory)
            
            print("✅ Research Manager initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing Research Manager: {e}")
            traceback.print_exc()
            raise
    
    async def run(self, user_query: str) -> Generator[str, None, None]:
        """Run the research workflow with clean output."""
        print(f"\n{'='*60}")
        print(f"📋 STARTING RESEARCH: {user_query}")
        print(f"{'='*60}\n")
        
        inputs = {
            "query": user_query,
            "messages": [HumanMessage(content=user_query)]
        }
        config = {"configurable": {"thread_id": f"user_{hash(user_query) % 10000}"}}
        
        try:
            # Track node execution
            completed_nodes = set()
            
            # Stream execution - using events instead of values to get node names
            async for event in self.graph.astream(inputs, config=config, stream_mode="events"):
                # Filter for node completion events only
                if event.__class__.__name__ == "NodeFinish":
                    node_name = event.node
                    if node_name not in completed_nodes:
                        completed_nodes.add(node_name)
                        
                        # Emojis for each node
                        emoji = {
                            "planner": "📋",
                            "researcher": "🔍",
                            "writer": "📝",
                            "notifier": "🔔"
                        }.get(node_name, "⚙️")
                        
                        status_msg = f"{emoji} {node_name.upper()} COMPLETE"
                        print(status_msg)
                        
                        # Yield only once per node
                        if node_name != "__end__":
                            yield f"**{status_msg}**\n\n"
            
            # Get final state
            final_state = await self.graph.aget_state(config)
            
            # Extract report
            if "report" in final_state.values:
                report = final_state.values["report"]
                
                # Ensure report is ReportData object, not dict/JSON
                if isinstance(report, dict):
                    try:
                        report = ReportData(**report)
                    except:
                        report = ReportData(
                            short_summary="Report format error",
                            markdown_report="# Format Error\n\nCould not parse report.",
                            follow_up_questions=["Fix report formatting", "Debug parser"]
                        )
                
                print(f"\n{'='*60}")
                print("✅ RESEARCH COMPLETED SUCCESSFULLY")
                print(f"{'='*60}")
                print(f"📄 Report length: {len(report.markdown_report)} characters")
                print(f"❓ Follow-up questions: {len(report.follow_up_questions)}")
                print(f"{'='*60}\n")
                
                # Yield final report - ONLY markdown, no JSON
                yield f"## 📋 Final Research Report\n\n"
                yield str(report.markdown_report) + "\n\n"
                yield "## ❓ Follow-up Questions\n\n"
                for q in report.follow_up_questions:
                    yield f"- {q}\n"
                
                yield f"\n\n---\n**✅ Research completed successfully!**\n"
                yield f"**Query:** {user_query}\n"
                yield f"**Summary:** {report.short_summary[:150]}...\n"
                
            else:
                error_msg = "❌ Error: Report not generated in final state"
                print(error_msg)
                yield error_msg
                
        except Exception as e:
            error_msg = f"❌ ERROR in research workflow: {str(e)}"
            print(f"\n{'='*60}")
            print("❌ WORKFLOW FAILED")
            print(f"{'='*60}")
            print(f"Error: {e}")
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            yield f"## ❌ Research Failed\n\n"
            yield f"**Error:** {str(e)[:200]}\n\n"
            yield "Please check your API keys and try again."

# For direct testing
if __name__ == "__main__":
    async def test():
        manager = ResearchManager()
        query = "What are the latest AI developments?"
        async for chunk in manager.run(query):
            print(chunk, end="")
    
    asyncio.run(test())