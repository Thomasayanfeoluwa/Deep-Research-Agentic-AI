from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from llm_models import model_large
from state import ReportData, ResearchState
import json

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
STRUCTURE:
1. Executive Summary (2-3 sentences)
2. Detailed Analysis with sections
3. Key Findings
4. Recommendations (if applicable)
5. Follow-up Questions (3-5 questions)

CRITERIA:
- Use markdown formatting
- Be thorough but concise
- Only use information from provided research
- Include specific details and examples
- Compare and contrast when possible

IMPORTANT: You MUST output a valid JSON object with these exact keys:
- "short_summary": string (2-3 sentence summary)
- "markdown_report": string (full markdown report)
- "follow_up_questions": array of strings (3-5 questions)"""

async def writer_node(state: ResearchState) -> dict:
    """WriterAgent: Synthesize the final report."""
    print("Thinking about the report...🤔")
    
    prompt = f"""ORIGINAL QUERY: {state['query']}

RESEARCH RESULTS:
{"="*50}
{chr(10).join(state['search_results'])}
{"="*50}

{WRITER_INSTRUCTIONS}

Return ONLY the JSON object with no additional text."""

    response = await model_large.ainvoke([
        SystemMessage(content="Return ONLY valid JSON, no function calls."),
        HumanMessage(content=prompt)
    ])
    
    # Clean and parse response
    content = response.content.strip()
    
    # Remove function call wrapper if present
    if content.startswith('<function=') and content.endswith('</function>'):
        start = content.find('{')
        end = content.rfind('}') + 1
        content = content[start:end]
    
    try:
        data = json.loads(content)
        report = ReportData(**data)
    except json.JSONDecodeError:
        # If JSON parsing fails, create ReportData directly
        report = ReportData(
            short_summary=f"Research on {state['query']}",
            markdown_report=content if len(content) > 100 else f"# Report\n\n{content}",
            follow_up_questions=["What are the implications?", "What needs verification?"]
        )
    
    print("Finished writing report")
    return {
        "report": report,
        "messages": [AIMessage(content="Final Report Generated.")]
    }