"""
RAG Tool for KDM Document Search

This module provides RAG (Retrieval-Augmented Generation) functionality as a tool
for Google ADK agents to search and retrieve relevant course documents.
"""

import asyncio
from typing import Dict, List, Any
from google.adk.tools import ToolContext

# Import vector database functions
from .vector import search_similar_chunks, initialize_collection


async def search_course_documents_async(
    query: str, 
    program_filter: str = "", 
    limit: int = 5,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Search course documents and requirements using vector similarity.
    
    Use this tool to find relevant information about course requirements, 
    eligibility criteria, program details, and academic policies from the 
    institutional knowledge base.
    
    Args:
        query: The search query describing what information is needed
        program_filter: Optional filter to search within specific program/course (default: "")
        limit: Maximum number of relevant documents to return (default: 5)
        tool_context: ADK tool context (automatically provided, can be None)
        
    Returns:
        Dict containing search results with documents, metadata, and status
        
    Example:
        {"status": "success", "documents": [...], "total_found": 3}
    """
    try:
        # Ensure collection is initialized
        await initialize_collection()
        
        # Enhance query with program filter if provided
        enhanced_query = f"{query} {program_filter}".strip() if program_filter and program_filter.strip() else query
        
        # Search for similar document chunks
        results = await search_similar_chunks(
            query_text=enhanced_query,
            limit=limit,
            score_threshold=0.6  # Lower threshold for more results
        )
        
        if not results:
            return {
                "status": "no_results",
                "message": f"No relevant documents found for query: '{query}'",
                "documents": [],
                "total_found": 0,
                "query_used": enhanced_query
            }
        
        # Format results for LLM consumption
        formatted_documents = []
        for result in results:
            doc = {
                "content": result["text"],
                "course_name": result["course_name"],
                "relevance_score": round(result["score"], 3),
                "source_id": str(result["id"])
            }
            formatted_documents.append(doc)
        
        return {
            "status": "success",
            "message": f"Found {len(results)} relevant documents",
            "documents": formatted_documents,
            "total_found": len(results),
            "query_used": enhanced_query
        }
        
    except Exception as e:
        error_msg = f"Error searching course documents: {str(e)}"
        print(error_msg)
        
        return {
            "status": "error",
            "message": error_msg,
            "documents": [],
            "total_found": 0,
            "query_used": query
        }


async def search_eligibility_requirements_async(
    student_background: str,
    program_name: str,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Search for specific eligibility requirements based on student background and target program.
    
    This specialized function helps determine if a student meets the requirements for a specific program
    by searching relevant course documents and eligibility criteria.
    
    Args:
        student_background: Student's academic background, qualifications, GPA, etc.
        program_name: Name of the program/course the student is interested in
        tool_context: ADK tool context (automatically provided)
        
    Returns:
        Dict containing eligibility information and requirements
    """
    try:
        # Create targeted query for eligibility checking
        eligibility_query = f"eligibility requirements admission criteria {program_name} {student_background}"
        
        # Search for relevant documents
        search_result = await search_course_documents_async(
            query=eligibility_query,
            program_filter=program_name,
            limit=7,  # Get more results for comprehensive eligibility check
            tool_context=tool_context
        )
        
        if search_result["status"] != "success":
            return search_result
        
        # Extract eligibility-specific information
        requirements = []
        policies = []
        
        for doc in search_result["documents"]:
            content = doc["content"].lower()
            if any(keyword in content for keyword in ["requirement", "prerequisite", "minimum", "must have"]):
                requirements.append(doc)
            elif any(keyword in content for keyword in ["policy", "admission", "criteria"]):
                policies.append(doc)
        
        return {
            "status": "success",
            "program_name": program_name,
            "student_background": student_background,
            "requirements_found": requirements,
            "policies_found": policies,
            "all_documents": search_result["documents"],
            "total_documents": search_result["total_found"],
            "search_query": eligibility_query
        }
        
    except Exception as e:
        error_msg = f"Error checking eligibility requirements: {str(e)}"
        print(error_msg)
        
        return {
            "status": "error",
            "message": error_msg,
            "program_name": program_name,
            "student_background": student_background
        }


# Synchronous wrapper functions for ADK agents
def search_course_documents_sync(query: str, program_filter: str = "", limit: int = 5) -> str:
    """
    Search course documents and requirements using vector similarity.
    
    This tool helps agents find relevant information about course requirements, 
    eligibility criteria, program details, and academic policies from the 
    institutional knowledge base.
    
    Args:
        query: The search query describing what information is needed
        program_filter: Optional filter to search within specific program/course (default: "")
        limit: Maximum number of relevant documents to return (default: 5)
        
    Returns:
        JSON string containing search results with documents, metadata, and status
        
    Examples:
        - search_course_documents_sync("MBA programs")
        - search_course_documents_sync("admission requirements", "MBA", 3)
        - search_course_documents_sync("fee structure")
    """
    try:
        # Use existing event loop if available, otherwise create new one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, 
                        search_course_documents_async(query, program_filter, limit, None)
                    )
                    result = future.result()
            else:
                result = loop.run_until_complete(search_course_documents_async(query, program_filter, limit, None))
        except RuntimeError:
            # No event loop, create a new one
            result = asyncio.run(search_course_documents_async(query, program_filter, limit, None))
        
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        import json
        error_result = {
            "status": "error",
            "message": f"Search error: {str(e)}",
            "documents": [],
            "total_found": 0,
            "query_used": query
        }
        return json.dumps(error_result, indent=2)


def search_eligibility_requirements_sync(student_background: str, program_name: str) -> str:
    """
    Search for specific eligibility requirements based on student background and target program.
    
    This specialized function helps determine if a student meets the requirements for a specific program
    by searching relevant course documents and eligibility criteria.
    
    Args:
        student_background: Student's academic background, qualifications, GPA, etc.
        program_name: Name of the program/course the student is interested in
        
    Returns:
        JSON string containing eligibility information and requirements
        
    Examples:
        - search_eligibility_requirements_sync("12th grade Science", "MBA")
        - search_eligibility_requirements_sync("Bachelor Computer Science 3.5 GPA", "Master Data Science")
    """
    try:
        # Use existing event loop if available, otherwise create new one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, 
                        search_eligibility_requirements_async(student_background, program_name, None)
                    )
                    result = future.result()
            else:
                result = loop.run_until_complete(search_eligibility_requirements_async(student_background, program_name, None))
        except RuntimeError:
            # No event loop, create a new one
            result = asyncio.run(search_eligibility_requirements_async(student_background, program_name, None))
        
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        import json
        error_result = {
            "status": "error",
            "message": f"Eligibility search error: {str(e)}",
            "program_name": program_name,
            "student_background": student_background
        }
        return json.dumps(error_result, indent=2)


# Export the synchronous functions for agent use
search_course_documents = search_course_documents_sync
search_eligibility_requirements = search_eligibility_requirements_sync 