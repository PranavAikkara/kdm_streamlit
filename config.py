"""
Configuration file for KDM Student Onboarding System

This file contains model configurations, API settings, and other constants
used throughout the application.
"""

import os
from google.adk.models.lite_llm import LiteLlm
from typing import Optional
from qdrant_client import AsyncQdrantClient

# Model Configuration
MODEL_GEMINI_2_5_FLASH = "gemini-2.5-flash"
DEFAULT_MODEL = MODEL_GEMINI_2_5_FLASH

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# Vector Database Configuration
EMBEDDING_CONFIG = {
    "api_key": os.getenv("EMBEDDING_MODEL_API"),
    "api_url": "https://api.deepinfra.com/v1/inference/BAAI/bge-large-en-v1.5",
    "timeout": 30,
    "dimensions": 1024  # BGE Large model dimensions
}

# Debug: Check if embedding API key is loaded
embedding_api_key = EMBEDDING_CONFIG["api_key"]


# Qdrant Configuration
qdrant_api_key = os.getenv("QDRANT_API_KEY")


qdrant_client = AsyncQdrantClient(
    url="https://8889bc57-c76e-4707-aca1-dda9416115d6.eu-west-2-0.aws.cloud.qdrant.io",
    api_key=qdrant_api_key,
    timeout=20
)

# LiteLLM Model Configuration
def get_gemini_model(api_key: Optional[str] = None) -> LiteLlm:
    """
    Create and configure Gemini 2.0 Flash model using LiteLLM.
    
    Args:
        api_key: Google API key. If None, reads from environment.
        
    Returns:
        Configured LiteLlm model instance for Gemini 2.0 Flash
        
    Raises:
        ValueError: If API key is not found
    """
    if api_key is None:
        api_key = GOOGLE_API_KEY
        
    if not api_key:
        raise ValueError(
            "Google API key not found. Set GOOGLE_API_KEY environment variable "
            "or pass api_key parameter."
        )
    
    # Configure LiteLLM for Gemini 2.0 Flash using Google AI Studio
    model = LiteLlm(
        model=f"gemini/{MODEL_GEMINI_2_5_FLASH}",  # Prefix with 'gemini/' for Google AI Studio
        api_key=api_key,
        # Optional: Add additional configuration
        temperature=0.7,
        max_tokens=8192,
        top_p=0.95,
    )
    
    return model

# Agent Configuration
AGENT_CONFIG = {
    "name": "kdm_student_onboarding_orchestrator",
    "description": "Intelligent assistant that guides prospective students through their entire KDM admission journey, from initial inquiry to successful enrollment.",
    "model": MODEL_GEMINI_2_5_FLASH,
    "temperature": 0.7,
    "max_tokens": 8192,
}

# Onboarding Stages
ONBOARDING_STAGES = [
    "greeting",
    "profile_collection", 
    "document_upload",
    "eligibility_check",
    "program_recommendation",
    "fee_calculation", 
    "registration",
    "completion"
]

# Student Data Fields
REQUIRED_STUDENT_FIELDS = [
    "name",
    "email", 
    "phone",
    "academic_background",
    "preferred_programs"
]

OPTIONAL_STUDENT_FIELDS = [
    "address",
    "emergency_contact",
    "special_requirements",
    "scholarship_interest"
] 