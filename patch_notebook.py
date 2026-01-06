import json
import os
import sys

print("Starting patch script...")

file_path = r"c:\Users\ADEGOKE\Desktop\Deep Research Agentic AI\deepresearch1.ipynb"

if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
    sys.exit(1)

print(f"Reading {file_path}...")
try:
    with open(file_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)

print("File read successfully. Modifying...")

try:
    # --- Update Instructions (Cell Index 1) ---
    cell_instr = nb["cells"][1]
    # Verify
    if "PLANNER_INSTRUCTIONS" not in "".join(cell_instr.get("source", [])):
        print("Finding instr cell...")
        for cell in nb["cells"]:
            if "PLANNER_INSTRUCTIONS" in "".join(cell.get("source", [])):
                cell_instr = cell
                break
    
    cell_instr["source"] = [
        "# --- 1. CONFIGURATION & INSTRUCTIONS ---\n",
        "# We preserve your exact instructions as constants for the nodes\n",
        "PLANNER_INSTRUCTIONS = \"You are a helpful research assistant. Given a query, come up with a set of web searches to perform to best answer the query. Output 5 specific terms to query for. Focus on recent and distinct queries.\"\n",
        "\n",
        "SEARCH_INSTRUCTIONS = \"You are a research assistant. Given a search term, you search the web for that term and produce a concise, factual summary of the results. The summary must be 2-3 paragraphs. Capture the main points, especially specific entity names, dates, and version numbers. Write clearly. Do not include any additional commentary other than the summary itself.\"\n",
        "\n",
        "WRITER_INSTRUCTIONS = (\n",
        "    \"You are a senior researcher tasked with writing a cohesive report for a research query. \"\n",
        "    \"You will be provided with the original query, and some initial research done by a research assistant.\\n\"\n",
        "    \"You should first come up with an outline for the report that describes the structure and \"\n",
        "    \"flow of the report. Then, generate the report and return that as your final output.\\n\"\n",
        "    \"The final output should be in markdown format, detailed, and accurate. Focus on modern info. \"\n",
        "    \"If the research is missing, state that. Do not hallucinate.\"\n",
        ")\n",
        "\n",
        "PUSH_INSTRUCTIONS = \"\"\"You are a member of a research team and will be provided with a short summary of a report.\n",
        "When you receive the report summary, you send a push notification to the user using your tool, informing them that research is complete,\n",
        "and including the report summary you receive\"\"\""
    ]
    
    # --- Update Nodes (Cell Index 5) ---
    cell_nodes = nb["cells"][5]
    # Verify
    if "async def search_node" not in "".join(cell_nodes.get("source", [])):
        print("Finding nodes cell...")
        for cell in nb["cells"]:
            if "async def search_node" in "".join(cell.get("source", [])):
                cell_nodes = cell
                break
    
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
        "# Initialize models with Groq\n",
        "# Reverting to llama-3.3-70b-versatile for better structured output reliability\n",
        "model_mini = ChatGroq(model=\"llama-3.3-70b-versatile\")\n",
        "model_large = ChatGroq(model=\"llama-3.3-70b-versatile\")\n",
        "\n",
        "async def planner_node(state: ResearchState):\n",
        "    \"\"\"PlannerAgent: Logic to generate the search plan.\"\"\"\n",
        "    print(\"--- AGENT: Planning the searches ---\")\n",
        "    planner = model_mini.with_structured_output(WebSearchPlan)\n",
        "    response = await planner.ainvoke([\n",
        "        SystemMessage(content=PLANNER_INSTRUCTIONS),\n",
        "        HumanMessage(content=f\"Query: {state['query']}\")\n",
        "    ])\n",
        "    print(f\"--- AGENT: Will search {len(response.searches)} searches ---\")\n",
        "    return {\n",
        "        \"search_plan\": response.searches,\n",
        "        \"messages\": [AIMessage(content=f\"Planned {len(response.searches)} searches.\")]\n",
        "    }\n",
        "\n",
        "async def search_node(state: ResearchState):\n",
        "    \"\"\"SearchAgent: Executes processes with autonomous tool loops.\"\"\"\n",
        "    search_agent = model_mini.bind_tools([web_search_tool])\n",
        "    \n",
        "    print(f\"--- AGENT: Executing {len(state['search_plan'])} parallel searches... ---\")\n",
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
        "    # Parallel execution\n",
        "    results = await asyncio.gather(*[perform_single_search(i) for i in state[\"search_plan\"]])\n",
        "    print(\"--- AGENT: Web research completed. ---\")\n",
        "    \n",
        "    return {\n",
        "        \"search_results\": results,\n",
        "        \"messages\": [AIMessage(content=\"Web research completed.\")]\n",
        "    }\n",
        "\n",
        "async def writer_node(state: ResearchState):\n",
        "    \"\"\"WriterAgent: Synthesizes the final report.\"\"\"\n",
        "    print(\"--- AGENT: Thinking about the report... ---\")\n",
        "    writer = model_large.with_structured_output(ReportData)\n",
        "    prompt = f\"Original query: {state['query']}\\n\\nResearch Results:\\n\" + \"\\n\".join(state[\"search_results\"])\n",
        "    \n",
        "    response = await writer.ainvoke([\n",
        "        SystemMessage(content=WRITER_INSTRUCTIONS),\n",
        "        HumanMessage(content=prompt)\n",
        "    ])\n",
        "    print(\"--- AGENT: Finished writing report ---\")\n",
        "    return {\n",
        "        \"report\": response,\n",
        "        \"messages\": [AIMessage(content=\"Final report generated.\")]\n",
        "    }\n",
        "\n",
        "async def push_node(state: ResearchState):\n",
        "    \"\"\"PushAgent: Autonomous push notification.\"\"\"\n",
        "    print(\"--- AGENT: Pushing notification ---\")\n",
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
        "         print(\"--- AGENT: Push sent and work perfected ---\")\n",
        "         return {\"messages\": [AIMessage(content=\"Notification pushed and confirmed.\")]}\n",
        "    \n",
        "    return {\"messages\": [AIMessage(content=\"Notification step completed (no call).\")]}\n"
    ]
    
    cell_nodes["source"] = new_source
    
    print("Writing back to file...")
    # Write
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=4)
    print("Patch Complete!")

except Exception as e:
    print(f"Error during patch: {e}")
    import traceback
    traceback.print_exc()
