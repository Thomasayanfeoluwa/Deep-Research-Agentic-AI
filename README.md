# AGENTIC AI IN ACTION

<table style="margin: 0; text-align: left; width:100%">
    <tr>
        <td style="width: 150px; height: 150px; vertical-align: middle;">
            <img src="agenticAI.png" alt="Agentic AI" width="150" height="150" style="display: block;" />
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

## The First Agent: Planner Agent
In any given query the Planner Agent comes up with the set of web search tools to best answer the query. 

## The Second Agent: Search Agent
Given a Search term, the Search Agent searches for it on the internet and summarize results.

## The Third Agent: Writer Agent
This agent writes a comprehensive professional report from the searches performed.

## The Fourth Agent: Push Agent
The Agent gets the summary of all the searches and push the notification to the user. Here I used PushOver.



# 🔧 Technology Stack

Component	                        Technology	            Purpose
Frontend	                        Streamlit	            Interactive chat interface
Backend	Python 3.10+	                                    Application logic
AI/LLM	Groq API (Llama 3.3 70B % openai/gpt-oss-20b)	    Natural language order processing
Notifications	                    PushOver                For recieving the alert of the Research Summary 

# 🛠️ Installation & Setup
Prerequisites
Python 3.13 
Groq API account (free tier available)
LangChain API key (for Tracing the tools used and the Graphs)
PushOver account (for notification)
Tavily (test mode available)

# Step 1: Clone and Setup
bash
# Clone the repository
git clone <repository-url>
cd Deep_Research_Agentic_AI

# Create virtual environment
uv venv python=3.13

# Activate virtual environment
# On Windows:
Deep_Research_Agentic_AI\Scripts\activate
# On macOS/Linux:
source Deep_Research_Agentic_AI/bin/activate

# Install dependencies
uv add -r requirements.txt
Step 2: Environment Configuration
Create a .env file in the root directory:

bash
# Groq and LangChain API Configuration
GROQ_API_KEY=your_groq_api_key_here
LANGCHAIN_API_KEY="**********************"

# PushOver and Tavily Configuration
PUSHOVER_USER="*************************"
PUSHOVER_TOKEN="************************"
TAVILY_API_KEY="**********************"

# Step 3: Obtain API Keys

# Groq API Key
Visit Groq Cloud
Sign up for free account
Generate API key from dashboard
Add to .env file

# LangChain API
Sign up at LangChain
Get Account API key

# PushOver Credentials For Notification
Download the PushOver App on Android or iOS 
Get the Token and the User Keys 

# Tavily
Create a Tavily Account
Login to the account and get the API Key.

# Step 4: Run the Application

bash
# Start the application
streamlit run dashboard.py

# The app will be available at: [http://localhost:8000](https://deep-research-agentic-ai-j9bxhyedfcfqde9m72j9he.streamlit.app/)
📋 Core Components Documentation
🎯 dashboard.py
Purpose: Orchestrates the entir research processing workflow


Issues: Create a GitHub issue for bugs
Discussions: Use GitHub discussions for questions
Email: Contact ayanfeoluwadegoke@gmail.com



![WhatsApp Image 2026-01-10 at 14 51 01_42ab3294](https://github.com/user-attachments/assets/dad3f1d3-b141-47b6-b085-186b6acaea4a)


