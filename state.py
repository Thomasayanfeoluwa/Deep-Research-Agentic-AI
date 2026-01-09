from typing import List, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

# Function to handle message accumulation
def add_messages(left: List[BaseMessage], right: List[BaseMessage]) -> List[BaseMessage]:
    """Add messages to the state."""
    if right is None:
        return left
    if left is None:
        return right
    return left + right

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query")
    query: str = Field(description="The search term to use for the web search.")

class WebSearchPlan(BaseModel):
    searches: List[WebSearchItem] = Field(description="A list of web searches to perform.")

class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report.")
    follow_up_questions: List[str] = Field(description="Suggested topics to research further.")

class ResearchState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    query: str
    search_plan: List[WebSearchItem]
    search_results: List[str]
    report: ReportData