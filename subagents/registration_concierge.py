# @title Registration Concierge Agent
import os
import sys
import asyncio
from pathlib import Path
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import get_gemini_model

# Import RAG tools and user data management
from tools.rag_tool import search_course_documents
from tools.user_data_manager import update_user_data, get_user_data, get_required_data_schema

# Function to load prompt from file
def load_prompt(prompt_file):
    prompt_path = Path(__file__).parent.parent / "prompts" / prompt_file
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

# Get configured Gemini 2.0 Flash model
AGENT_MODEL = get_gemini_model()

registration_concierge_agent = LlmAgent(
    name="registration_concierge",
    model="gemini-2.5-flash", # LiteLlm configured Gemini 2.0 Flash model
    description="Comprehensive registration support agent that guides students through enrollment procedures, document submission, and pre-arrival preparation with personalized assistance and institutional knowledge.",
    instruction=load_prompt("registration_concierge.md"),
    tools=[search_course_documents, update_user_data, get_user_data, get_required_data_schema],
    include_contents='default'  # Include full conversation history for context sharing
) 