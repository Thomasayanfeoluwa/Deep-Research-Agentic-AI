import os
import requests
import logging
import streamlit as st
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from llm_models import model_mini
from state import ReportData, ResearchState

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
PUSHOVER_USER = st.secrets.get("PUSHOVER_USER")
PUSHOVER_TOKEN = st.secrets.get("PUSHOVER_TOKEN")

PUSH_INSTRUCTIONS = """You are a research assistant. When research is complete, send a notification.

IMPORTANT: Use the push_notification_tool to send the notification.
The tool requires a 'message' parameter.

Create a concise notification that includes:
1. Research completion announcement
2. Brief summary of findings
3. Indication that full report is ready

Keep the message under 500 characters."""

@tool
def push_notification_tool(message: str) -> str:
    """Send a push notification with this brief message."""
    if not PUSHOVER_USER or not PUSHOVER_TOKEN:
        return "Error: Pushover credentials not configured."
    
    payload = {
        "user": PUSHOVER_USER,
        "token": PUSHOVER_TOKEN,
        "message": message,
        "title": "Research Complete"
    }
    
    pushover_url = "https://api.pushover.net/1/messages.json"
    
    try:
        print(f"📤 Sending notification: {message[:100]}...")
        response = requests.post(pushover_url, data=payload, timeout=10)
        
        if response.status_code == 200:
            return "✅ Notification sent successfully!"
        else:
            return f"❌ Failed: {response.text}"
            
    except Exception as e:
        return f"❌ Error: {e}"

async def push_node(state: ResearchState) -> dict:
    """PushAgent: Send notification when research is complete."""
    print("🔔 Processing notification...")
    
    try:
        pusher = model_mini.bind_tools([push_notification_tool])
        
        # Extract summary from report - handle both dict and ReportData
        report = state.get("report")
        
        if report is None:
            summary = "Research completed. Full report available."
        elif isinstance(report, dict):
            # Handle dictionary report
            summary = report.get("short_summary", "Research completed. Check report.")
        elif hasattr(report, 'short_summary'):
            # Handle ReportData object
            summary = report.short_summary
        else:
            summary = "Research completed. See full report."
        
        print(f"📋 Summary for notification: {summary[:100]}...")
        
        # Create notification message
        notification_msg = f"""Research Complete!

Summary: {summary}

Full report is now available for review."""

        messages = [
            SystemMessage(content=PUSH_INSTRUCTIONS),
            HumanMessage(content=f"Please send this notification: {notification_msg}")
        ]

        res1 = await pusher.ainvoke(messages)
        logger.info(f"Push agent response: {res1}")
        
        messages.append(res1)

        # Handle tool calls
        if hasattr(res1, 'tool_calls') and res1.tool_calls:
            for tc in res1.tool_calls:
                if tc['name'] == 'push_notification_tool':
                    try:
                        # Get arguments
                        args = tc.get('args', {})
                        if not isinstance(args, dict):
                            args = {"message": str(args)}
                        
                        # Ensure message exists
                        if 'message' not in args:
                            args['message'] = notification_msg
                        
                        logger.info(f"Calling push_notification_tool with: {args}")
                        out = push_notification_tool.invoke(args['message'])
                        
                        messages.append(ToolMessage(
                            content=str(out),
                            tool_call_id=tc['id']
                        ))
                        
                        # Get confirmation
                        res2 = await pusher.ainvoke(messages)
                        print("✅ Push notification completed")
                        return {"messages": [AIMessage(content="Notification sent and confirmed.")]}
                        
                    except Exception as e:
                        logger.error(f"Error in push notification: {e}")
                        return {"messages": [AIMessage(content=f"Notification error: {e}")]}
        
        # If no tool was called
        print("⚠️ No notification sent (tool not called)")
        return {"messages": [AIMessage(content="Notification step completed (no call).")]}
        
    except Exception as e:
        error_msg = f"Error in push_node: {e}"
        print(f"❌ {error_msg}")
        return {"messages": [AIMessage(content=error_msg)]}
