import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# Get API key
groq_api_key = st.secrets.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in .env file")

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

MODELS = {
    "mini": "openai/gpt-oss-20b",
    "large": "llama-3.3-70b-versatile"
}

print(f"✅ Models initialized: {MODELS['mini']} and {MODELS['large']}")
