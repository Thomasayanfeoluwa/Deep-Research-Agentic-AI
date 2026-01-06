import json
import os

nb_path = r"c:\Users\ADEGOKE\Desktop\Deep Research Agentic AI\deepresearch1.ipynb"
print(f"Reading {nb_path}...")

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# 1. Update Imports
print("Scanning for imports...")
import_cell = None
for i, cell in enumerate(nb["cells"]):
    # print(f"Cell {i} type: {cell['cell_type']}")
    if cell["cell_type"] == "code":
        src_text = "".join(cell["source"])
        if "import os" in src_text:
            print(f"Found import cell at {i}")
            import_cell = cell
            # break - don't break, maybe multiple?

if import_cell:
    src = import_cell["source"]
    print("Updating imports...")
    if not any("ChatGroq" in line for line in src):
        src.insert(20, "from langchain_groq import ChatGroq\n")
        print("Added ChatGroq import")
    
    updated_tool_msg = False
    for j, line in enumerate(src):
        if "from langchain_core.messages" in line:
            if "ToolMessage" not in line:
                src[j] = "from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage\n"
                updated_tool_msg = True
                print("Updated ToolMessage import")
    if not updated_tool_msg:
        print("ToolMessage already present or line not found.")

# 2. Update Nodes Cell
print("Scanning for Nodes cell...")
node_cell = None
node_cell_index = -1
for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] == "code":
        src_text = "".join(cell["source"])
        if "class ResearchState" in src_text:
            print(f"Found Nodes cell at {i}")
            node_cell = cell
            node_cell_index = i
            break

if node_cell:
    print(f"Replacing contents of cell {node_cell_index}")
    new_source = [
        "#  STATE DEFINITION\n",
        "class ResearchState(TypedDict):\n",
        "    # messages tracks the conversation history\n",
        "    messages: Annotated[List[BaseMessage], add_messages]\n",
        "    # Specialized fields to hold intermediate data\n",
        "    query: str\n",
        "    search_plan: List[WebSearchItem]\n",
        "    search_results: List[str]\n",
        "    report: ReportData\n",
        "\n",
        "# NODE IMPLEMENTATIONS \n",
        "# Initialize models with Groq. Using qwen-2.5-32b as requested.\n",
        "model_mini = ChatGroq(model='qwen-2.5-32b', temperature=0)\n",
        "model_large = ChatGroq(model='qwen-2.5-32b', temperature=0)\n",
        "\n",
        "async def planner_node(state: ResearchState):\n",
        "    \"\"\"PlannerAgent: Logic to generate the search plan.\"\"\"\n",
        "    planner = model_mini.with_structured_output(WebSearchPlan)\n",
        "    # Re-instantiate planner for each call to be safe or keep global\n",
        "    response = await planner.ainvoke([\n",
        "        SystemMessage(content=PLANNER_INSTRUCTIONS),\n",
        "        HumanMessage(content=f\"Query: {state['query']}\")\n",
        "    ])\n",
        "    return {\n",
        "        \"search_plan\": response.searches,\n",
        "        \"messages\": [AIMessage(content=f\"Planned {len(response.searches)} searches.\")]\n",
        "    }\n",
        "\n",
        "async def search_node(state: ResearchState):\n",
        "    \"\"\"SearchAgent: Executes processes with autonomous tool loops.\"\"\"\n",
        "    search_agent = model_mini.bind_tools([web_search_tool])\n",
        "    \n",
        "    async def perform_single_search(item: WebSearchItem):\n",
        "        # Agent ReAct Loop\n",
        "        initial_msg = [\n",
        "            SystemMessage(content=SEARCH_INSTRUCTIONS),\n",
        "            HumanMessage(content=f\"Search term: {item.query}\\nReason: {item.reason}\")\n",
        "        ]\n",
        "        # 1. Ask model\n",
        "        res1 = await search_agent.ainvoke(initial_msg)\n",
        "        messages = list(initial_msg) + [res1]\n",
        "        \n",
        "        # 2. Check and Execute Tool\n",
        "        if res1.tool_calls:\n",
        "            for tc in res1.tool_calls:\n",
        "                # In this simulated environment, we invoke the tool directly\n",
        "                if tc['name'] == 'web_search_tool':\n",
        "                    out = web_search_tool.invoke(tc['args'])\n",
        "                    messages.append(ToolMessage(content=str(out), tool_call_id=tc['id']))\n",
        "            \n",
        "            # 3. Get Summary from Model\n",
        "            res2 = await search_agent.ainvoke(messages)\n",
        "            return f\"Summary for {item.query}: {res2.content}\"\n",
        "        \n",
        "        return f\"Summary for {item.query}: {res1.content}\"\n",
        "\n",
        "    # Run all search agents in parallel\n",
        "    results = await asyncio.gather(*[perform_single_search(i) for i in state[\"search_plan\"]])\n",
        "    \n",
        "    return {\n",
        "        \"search_results\": results,\n",
        "        \"messages\": [AIMessage(content=\"Web research completed.\")]\n",
        "    }\n",
        "\n",
        "async def writer_node(state: ResearchState):\n",
        "    \"\"\"WriterAgent: Synthesizes the final report.\"\"\"\n",
        "    # Groq supports structured output reasonably well\n",
        "    writer = model_large.with_structured_output(ReportData)\n",
        "    prompt = f\"Original query: {state['query']}\\n\\nResearch Results:\\n\" + \"\\n\".join(state[\"search_results\"])\n",
        "    \n",
        "    response = await writer.ainvoke([\n",
        "        SystemMessage(content=WRITER_INSTRUCTIONS),\n",
        "        HumanMessage(content=prompt)\n",
        "    ])\n",
        "    return {\n",
        "        \"report\": response,\n",
        "        \"messages\": [AIMessage(content=\"Final report generated.\")]\n",
        "    }\n",
        "\n",
        "async def push_node(state: ResearchState):\n",
        "    \"\"\"PushAgent: Autonomous push notification.\"\"\"\n",
        "    pusher = model_mini.bind_tools([push_notification_tool])\n",
        "    summary = state[\"report\"].short_summary\n",
        "    \n",
        "    messages = [\n",
        "        SystemMessage(content=PUSH_INSTRUCTIONS),\n",
        "        HumanMessage(content=summary)\n",
        "    ]\n",
        "    \n",
        "    res1 = await pusher.ainvoke(messages)\n",
        "    messages.append(res1)\n",
        "    \n",
        "    if res1.tool_calls:\n",
        "         for tc in res1.tool_calls:\n",
        "             if tc['name'] == 'push_notification_tool':\n",
        "                 out = push_notification_tool.invoke(tc['args'])\n",
        "                 messages.append(ToolMessage(content=str(out), tool_call_id=tc['id']))\n",
        "         \n",
        "         res2 = await pusher.ainvoke(messages)\n",
        "         return {\"messages\": [AIMessage(content=\"Notification pushed and confirmed.\")]}\n",
        "    \n",
        "    return {\"messages\": [AIMessage(content=\"Notification step completed (no call).\")]}\n"
    ]
    node_cell["source"] = new_source
else:
    print("Nodes cell not found!")

print("Writing file...")
with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)
print("Done.")
