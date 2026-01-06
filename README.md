# AGENTIC AI IN ACTION

<table style="margin: 0; text-align: left; width:100%">
    <tr>
        <td style="width: 150px; height: 150px; vertical-align: middle;">
            <img src="../assets/business.png" width="150" height="150" style="display: block;" />
        </td>
        <td>
            <h2 style="color:#00bfff;">Commercial implications</h2>
            <span style="color:#00bfff;">A Deep Research agent is broadly applicable to any business area, and to your own day-to-day activities. You can make use of this yourself!
            </span>
        </td>
    </tr>
</table>

## The Agentic AI focuses on Deep Research on any particular topic and then generate content based on the research.

## It makes use of 4 Agents:

1. Search Agent - searches online given a search term using an LangGraph and Groq hosted tool
2. Planner Agent - given a query from the user, come up with searches
3. Report Agent - make a report on results
4. Push Agent - send a notification to the user's phone with a summary

## The First Agent: Search Agent

Given a Search term, search for it on the internet and summarize results.
























does it follows this pattern 100% accurately just that in this case we ware using langgraph?
## We will be making 4 Agents:

1. Search Agent - searches online given a search term using an OpenAI hosted tool
2. Planner Agent - given a query from the user, come up with searches
3. Report Agent - make a report on results
4. Push Agent - send a notification to the user's phone with a summary


## Our First Agent: Search Agent

Given a Search term, search for it on the internet and summarize results.
INSTRUCTIONS = "You are a research assistant. Given a search term, you search the web for that term and \
produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 \
words. Capture the main points. Write succintly, no need to have complete sentences or good \
grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
essence and ignore any fluff. Do not include any additional commentary other than the summary itself."

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4.1-mini",
    model_settings=ModelSettings(tool_choice="required"),
)
message = "What are the most popular and successful AI Agent frameworks in May 2025"

with trace("Search"):
    result = await Runner.run(search_agent, message)

display(Markdown(result.final_output))


## Our Second Agent: Planner Agent

Given a query, come up with 5 ideas for web searches that could be run.

Use Structured Outputs as our way to ensure the Agent provides what we need.
# See note above about cost of WebSearchTool

HOW_MANY_SEARCHES = 5

INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."

# We use Pydantic objects to describe the Schema of the output

class WebSearchItem(BaseModel):
    reason: str
    "Your reasoning for why this search is important to the query."

    query: str
    "The search term to use for the web search."


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]
    """A list of web searches to perform to best answer the query."""

# We pass in the Pydantic object to ensure the output follows the schema

planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4.1-mini",
    output_type=WebSearchPlan,
)

message = "What are the most popular and successful AI Agent frameworks in May 2025"

with trace("Search"):
    result = await Runner.run(planner_agent, message)
    pprint(result.final_output)

## Our Third Agent: Writer Agent

Take the results of internet searches and make a report

INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words."
)


class ReportData(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary of the findings."""

    markdown_report: str
    """The final report"""

    follow_up_questions: list[str]
    """Suggested topics to research further"""


writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ReportData,
)

## Our Fourth Agent: push notification

Just to show how easy it is to make a tool!

I'm using a nifty product called PushOver - to set this up yourself, visit https://pushover.net

@function_tool
def push(message: str):
    """Send a push notification with this brief message"""
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)
    return {"status": "success"}
push
INSTRUCTIONS = """You are a member of a research team and will be provided with a short summary of a report.
When you receive the report summary, you send a push notification to the user using your tool, informing them that research is complete,
and including the report summary you receive"""


push_agent = Agent(
    name="Push agent",
    instructions=INSTRUCTIONS,
    tools=[push],
    model="gpt-4.1-mini",
    model_settings=ModelSettings(tool_choice="required")
)

### The next 3 functions will plan and execute the search, using planner_agent and search_agent

async def plan_searches(query: str):
    """ Use the planner_agent to plan which searches to run for the query """
    print("Planning searches...")
    result = await Runner.run(planner_agent, f"Query: {query}")
    print(f"Will perform {len(result.final_output.searches)} searches")
    return result.final_output

async def perform_searches(search_plan: WebSearchPlan):
    """ Call search() for each item in the search plan """
    print("Searching...")
    tasks = [asyncio.create_task(search(item)) for item in search_plan.searches]
    results = await asyncio.gather(*tasks)
    print("Finished searching")
    return results

async def search(item: WebSearchItem):
    """ Use the search agent to run a web search for each item in the search plan """
    input = f"Search term: {item.query}\nReason for searching: {item.reason}"
    result = await Runner.run(search_agent, input)
    return result.final_output

### The next 2 functions write a report and send a push notification

async def write_report(query: str, search_results: list[str]):
    """ Use the writer agent to write a report based on the search results"""
    print("Thinking about report...")
    input = f"Original query: {query}\nSummarized search results: {search_results}"
    result = await Runner.run(writer_agent, input)
    print("Finished writing report")
    return result.final_output

async def send_push(report: ReportData):
    """ Use the push agent to send a notification to the user """
    print("Pushing...")
    result = await Runner.run(push_agent, report.short_summary)
    print("Push sent")
    return report

### Showtime!

query ="What are the most popular and successful AI Agent frameworks in May 2025"

with trace("Research trace"):
    print("Starting research...")
    search_plan = await plan_searches(query)
    search_results = await perform_searches(search_plan)
    report = await write_report(query, search_results)
    await send_push(report)  
    print("Hooray!")
display(Markdown(report.markdown_report))