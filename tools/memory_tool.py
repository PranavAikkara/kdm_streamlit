"""
Memory Search Tool for KDM Student Onboarding System

This tool allows agents to search conversation history and previous interactions
to maintain context across agent transfers and sessions.
"""

import asyncio
from typing import Dict, Any, Optional
import json

# Global reference to the runner for memory access
_runner = None

def set_runner(runner):
    """Set the global runner reference for memory access."""
    global _runner
    _runner = runner

async def search_conversation_memory_async(query: str, user_id: str = "user123", app_name: str = "KDM_Student_Onboarding") -> Dict[str, Any]:
    """
    Search conversation memory for relevant context.
    
    Args:
        query: Search query to find relevant conversation history
        user_id: User ID to search within
        app_name: Application name
        
    Returns:
        Dictionary containing relevant memories and context
    """
    if not _runner or not _runner.memory_service:
        return {
            "success": False,
            "error": "Memory service not available",
            "memories": []
        }
    
    try:
        # Search memory for relevant context
        search_response = await _runner.memory_service.search_memory(
            app_name=app_name,
            user_id=user_id,
            query=query
        )
        
        memories = []
        for memory in search_response.memories:
            memory_text = ""
            if memory.content and memory.content.parts:
                memory_text = " ".join([part.text for part in memory.content.parts if part.text])
            
            memories.append({
                "author": memory.author,
                "timestamp": memory.timestamp,
                "content": memory_text
            })
        
        return {
            "success": True,
            "memories": memories,
            "total_found": len(memories)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "memories": []
        }

def search_conversation_memory(query: str, user_id: str = "user123", app_name: str = "KDM_Student_Onboarding") -> str:
    """
    Search conversation memory for relevant context (synchronous wrapper).
    
    This tool helps agents find relevant information from previous conversations,
    including phone numbers, extracted document data, and user preferences.
    
    Args:
        query: Search query (e.g., "phone number", "academic qualification", "12th grade")
        user_id: User ID to search within (default: "user123")
        app_name: Application name (default: "KDM_Student_Onboarding")
        
    Returns:
        JSON string with search results including relevant conversation history
        
    Examples:
        - search_conversation_memory("phone number") - Find user's phone number
        - search_conversation_memory("academic qualification") - Find education details
        - search_conversation_memory("document upload") - Find uploaded document info
    """
    # Run the async function in an event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(
        search_conversation_memory_async(query, user_id, app_name)
    )
    
    return json.dumps(result, indent=2)

def get_conversation_context(context_type: str = "recent") -> str:
    """
    Get conversation context for better agent coordination.
    
    Args:
        context_type: Type of context to retrieve ("recent", "user_profile", "documents")
        
    Returns:
        JSON string with relevant context information
    """
    if context_type == "recent":
        query = "recent conversation user message"
    elif context_type == "user_profile":
        query = "phone number personal information name"
    elif context_type == "documents":
        query = "document upload extract academic qualification"
    else:
        query = context_type
    
    return search_conversation_memory(query) 