"""
Tools package for KDM Student Onboarding System

This package contains various utility functions and tools used by the agents
for document processing, data extraction, and other specialized tasks.
"""

# Import user data management functions for easy access by agents
from .user_data_manager import (
    update_user_data,
    get_user_data, 
    get_required_data_schema
)

# Import RAG tools
from .rag_tool import (
    search_course_documents,
    search_eligibility_requirements
)

__all__ = [
    'update_user_data',
    'get_user_data',
    'get_required_data_schema',
    'search_course_documents', 
    'search_eligibility_requirements'
]

