import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables first
load_dotenv()

# Get API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in .env file")

# Initialize LLM models with API key
model_mini = ChatGroq(
    model="openai/gpt-oss-20b", 
    temperature=0.3,
    groq_api_key=groq_api_key
)

model_large = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0.2,
    groq_api_key=groq_api_key
)

# Model names for reference
MODELS = {
    "mini": "openai/gpt-oss-20b",
    "large": "llama-3.3-70b-versatile"
}

print(f"✅ Models initialized: {MODELS['mini']} and {MODELS['large']}")