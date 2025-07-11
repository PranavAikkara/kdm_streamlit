# @title Document Digitizer Agent
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

# Import user data management tools
from tools.user_data_manager import update_user_data, get_user_data, get_required_data_schema

# Function to load prompt from file
def load_prompt(prompt_file):
    prompt_path = Path(__file__).parent.parent / "prompts" / prompt_file
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

# Get configured Gemini 2.0 Flash model
AGENT_MODEL = get_gemini_model()

document_digitiser_agent = LlmAgent(
    name="document_digitiser",
    model="gemini-2.5-flash", # LiteLlm configured Gemini 2.0 Flash model
    description="Expert document processing agent that extracts and validates student information from academic transcripts, certificates, and identification documents with intelligent data validation and user profile management.",
    instruction=load_prompt("document_digitiser.md"),
    tools=[update_user_data, get_user_data, get_required_data_schema],
    include_contents='default'  # Include full conversation history for context sharing
) 