from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from llm_models import model_large
from state import ReportData, ResearchState
import json
import re

WRITER_INSTRUCTIONS = """You are a senior researcher writing a comprehensive, in-depth professional report.

CRITICAL REQUIREMENTS:
1. LENGTH: Your report MUST be between 1500-2000 words. This is not optional.
2. DEPTH: Provide extensive detail, multiple examples, comparisons, and analysis for each topic.
3. STRUCTURE: Use clear markdown sections with proper headings (##, ###).
4. ACCURACY: ONLY use information from the provided search results. Do NOT invent frameworks or data.
5. SPECIFICITY: Include specific names, versions, dates, market data, and technical details found in search results.
6. COMPARISONS: Provide detailed comparisons between frameworks, highlighting strengths/weaknesses.
7. EXAMPLES: Include concrete use cases and implementation examples where available.

If search data is missing on a topic, explicitly state: 'I could not find information on [topic]'.
DO NOT mention 'TensorFlow Agents' or 'PyTorch Agents' unless they appear in the actual search results.

Remember: The report must be COMPREHENSIVE (1500-2000 words) with substantial depth and detail.

Format your report as:
## Executive Summary
[2-3 sentence summary]

## Detailed Analysis
[In-depth analysis with multiple sections]

## Key Findings
[Bulleted or numbered list]

## Recommendations
[If applicable]

## Follow-up Questions
[3-5 questions for further research]

IMPORTANT: Return a valid JSON object with these exact keys:
- "short_summary": string
- "markdown_report": string  
- "follow_up_questions": array of strings

Return ONLY the JSON object, no other text."""

async def writer_node(state: ResearchState) -> dict:
    """WriterAgent: Synthesize the final report."""
    print("Thinking about the report...🤔")
    
    # Create prompt
    prompt = f"""ORIGINAL QUERY: {state['query']}

RESEARCH RESULTS:
{"="*50}
{chr(10).join(state['search_results'])}
{"="*50}

{WRITER_INSTRUCTIONS}

Return ONLY the JSON object with no additional text."""

    # Get raw response (NO with_structured_output)
    response = await model_large.ainvoke([
        SystemMessage(content="You are a research writer. Return JSON only."),
        HumanMessage(content=prompt)
    ])
    
    # Extract and clean JSON
    content = response.content.strip()
    
    # Remove function call wrapper if present
    if content.startswith('<function='):
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != 0:
            content = content[start:end]
    
    # Remove markdown code blocks
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    
    # Parse JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Extract JSON with regex
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except:
                data = {
                    "short_summary": f"Research on {state['query']}",
                    "markdown_report": content,
                    "follow_up_questions": ["What are the key findings?", "What needs more research?"]
                }
        else:
            data = {
                "short_summary": "Report generation issue",
                "markdown_report": content,
                "follow_up_questions": ["Fix report formatting", "Debug JSON parsing"]
            }
    
    # Create ReportData object
    report = ReportData(
        short_summary=data.get("short_summary", "No summary"),
        markdown_report=data.get("markdown_report", "# No report"),
        follow_up_questions=data.get("follow_up_questions", ["Question 1", "Question 2"])
    )
    
    print("Finished writing report")
    return {
        "report": report,
        "messages": [AIMessage(content="Final Report Generated.")]
    }