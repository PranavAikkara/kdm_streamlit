# @title Payment Helper Agent
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

payment_helper_agent = LlmAgent(
    name="payment_helper",
    model=AGENT_MODEL, # LiteLlm configured Gemini 2.0 Flash model
    description="Specialized payment assistance agent that guides students through payment processes, troubleshoots payment issues, and provides information about payment methods and financial procedures.",
    instruction=load_prompt("payment_helper.md"),
    tools=[update_user_data, get_user_data, get_required_data_schema],
    include_contents='default'  # Include full conversation history for context sharing
) 