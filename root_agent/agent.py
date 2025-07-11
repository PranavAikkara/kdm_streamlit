# @title Import necessary libraries
import os
import sys
import asyncio
from pathlib import Path
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
from subagents.eligibility_checker import eligibility_checker_agent
from subagents.document_digitiser import document_digitiser_agent
from subagents.programme_recommender import programme_recommender_agent
from subagents.fee_calculator import fee_calculator_agent
from subagents.registration_concierge import registration_concierge_agent
from subagents.smart_faq import smart_faq_agent
from subagents.payment_helper import payment_helper_agent

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import get_gemini_model

# Import user data management tools
from tools.user_data_manager import get_user_data, get_required_data_schema, update_user_data

# Function to load prompt from file
def load_prompt(prompt_file):
    prompt_path = Path(__file__).parent.parent / "prompts" / prompt_file
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

# Get configured Gemini 2.5 Flash model
AGENT_MODEL = get_gemini_model()

root_agent = LlmAgent(
    name="kdm_student_onboarding_orchestrator",
    model="gemini-2.5-flash", # LiteLlm configured Gemini 2.5 Flash model
    description="Intelligent assistant that guides prospective students through their entire KDM admission journey with user data management and intelligent routing between specialized agents.",
    instruction=load_prompt("orchestrator.txt"),
    tools=[get_user_data, get_required_data_schema, update_user_data],
    sub_agents=[eligibility_checker_agent, document_digitiser_agent, programme_recommender_agent, fee_calculator_agent, registration_concierge_agent, smart_faq_agent, payment_helper_agent],
    include_contents='default'  # Include full conversation history for context sharing
)

def create_chatbot_agent(user_id=None):
    """
    Create and return the KDM chatbot agent for use with Google ADK Runner.
    
    Args:
        user_id: Optional user ID (not used in current implementation but kept for compatibility)
        
    Returns:
        Agent: The configured KDM root agent
    """
    return root_agent

