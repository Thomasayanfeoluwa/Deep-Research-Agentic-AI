# CORRECTED STATE DEFINITION
# Replace cell 4 (lines 147-152) with this corrected version

class ResearchState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    query: str
    search_plan: List[WebSearchItem]
    search_results: List[str]
    report: ReportData
