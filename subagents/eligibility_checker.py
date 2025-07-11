# @title Eligibility Checker Agent
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

# Import RAG tools, user data management, and memory search
from tools.rag_tool import search_course_documents, search_eligibility_requirements
from tools.user_data_manager import update_user_data, get_user_data, get_required_data_schema
from tools.memory_tool import search_conversation_memory, get_conversation_context

# Function to load prompt from file
def load_prompt(prompt_file):
    prompt_path = Path(__file__).parent.parent / "prompts" / prompt_file
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

# Get configured Gemini 2.0 Flash model
AGENT_MODEL = get_gemini_model()

eligibility_checker_agent = LlmAgent(
    name="eligibility_checker",
    model="gemini-2.5-flash", # LiteLlm configured Gemini 2.0 Flash model
    description="Student eligibility verification agent that determines program eligibility using rule-driven and AI-based assessment of academic qualifications with access to institutional course documents and user data management.",
    instruction=load_prompt("eligibility_checker.md"),
    tools=[search_course_documents, search_eligibility_requirements, update_user_data, get_user_data, get_required_data_schema],
    include_contents='default'  # Include full conversation history for context sharing
) 