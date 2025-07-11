"""
Vector Database Operations for KDM Document Search

This module provides async functions for interacting with Qdrant vector database,
including collection management, embedding generation, and similarity search.
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse

# Import configuration
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import qdrant_client, EMBEDDING_CONFIG

# Constants
COLLECTION_NAME = "kdmcollection"
DISTANCE_METRIC = Distance.COSINE


async def initialize_collection() -> bool:
    """
    Initialize the Qdrant collection for storing document embeddings.
    
    Returns:
        bool: True if collection was created or already exists, False on error
    """
    try:
        # Check if collection already exists
        collections = await qdrant_client.get_collections()
        existing_collections = [col.name for col in collections.collections]
        
        if COLLECTION_NAME in existing_collections:
            print(f"Collection '{COLLECTION_NAME}' already exists")
            return True
            
        # Create new collection
        await qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_CONFIG["dimensions"],
                distance=DISTANCE_METRIC
            )
        )
        
        print(f"Collection '{COLLECTION_NAME}' created successfully")
        return True
        
    except UnexpectedResponse as e:
        print(f"Error initializing collection: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error initializing collection: {e}")
        return False


async def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate embedding for the given text using DeepInfra BGE model.
    
    Args:
        text: Text to generate embedding for
        
    Returns:
        List[float]: Embedding vector or None on error
    """
    if not text.strip():
        print("Warning: Empty text provided for embedding")
        return None
    
    # Truncate text to fit model's 512 token limit (roughly 400 words or 2000 characters)
    max_chars = 2000  # Conservative estimate for 512 tokens
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(' ', 1)[0]  # Cut at word boundary
        print(f"Warning: Text truncated to {len(text)} characters to fit token limit")
        
    api_key = EMBEDDING_CONFIG["api_key"]
    if not api_key:
        print("Error: Embedding API key not found")
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Fixed payload format - DeepInfra expects "inputs" as an array
    payload = {
        "inputs": [text]
    }
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=EMBEDDING_CONFIG["timeout"])) as session:
            async with session.post(
                EMBEDDING_CONFIG["api_url"],
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Extract embedding from DeepInfra response format
                    if isinstance(result, list) and len(result) > 0:
                        # DeepInfra returns a list directly
                        embedding = result[0] if isinstance(result[0], list) else result
                        return embedding
                    elif "embeddings" in result and len(result["embeddings"]) > 0:
                        # Alternative format with embeddings key
                        embedding = result["embeddings"][0]
                        if isinstance(embedding, dict) and "embedding" in embedding:
                            return embedding["embedding"]
                        return embedding
                    else:
                        print(f"Unexpected response format: {result}")
                        return None
                else:
                    error_text = await response.text()
                    print(f"Embedding API error {response.status}: {error_text}")
                    return None
                    
    except asyncio.TimeoutError:
        print("Timeout error while generating embedding")
        return None
    except aiohttp.ClientError as e:
        print(f"HTTP client error while generating embedding: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error while generating embedding: {e}")
        return None


async def search_similar_chunks(query_text: str, limit: int = 5, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
    """
    Search for similar document chunks based on query text.
    
    Args:
        query_text: Text to search for
        limit: Maximum number of results to return
        score_threshold: Minimum similarity score
        
    Returns:
        List[Dict]: List of similar chunks with their metadata and scores
    """
    if not query_text.strip():
        print("Warning: Empty query text provided")
        return []
    
    try:
        # Generate embedding for query
        query_embedding = await generate_embedding(query_text)
        if not query_embedding:
            print("Failed to generate embedding for query")
            return []
        
        # Perform vector search
        search_results = await qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold
        )
        
        # Format results for LLM consumption with all available metadata
        formatted_results = []
        for result in search_results:
            formatted_result = {
                "text": result.payload.get("text", ""),
                "course_name": result.payload.get("course_name", ""),
                "level": result.payload.get("level", ""),
                "type": result.payload.get("type", ""),
                "chunk_id": result.payload.get("chunk_id", ""),
                "score": result.score,
                "id": result.id
            }
            formatted_results.append(formatted_result)
        
        print(f"Found {len(formatted_results)} similar chunks for query: '{query_text[:50]}...'")
        return formatted_results
        
    except UnexpectedResponse as e:
        print(f"Qdrant search error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error during search: {e}")
        return []


async def add_document_chunk(text: str, course_name: str, chunk_id: Optional[str] = None, level: str = "", chunk_type: str = "") -> bool:
    """
    Add a document chunk to the vector database.
    
    Args:
        text: Document text content
        course_name: Name of the course/program
        chunk_id: Optional custom ID for the chunk
        level: Course level (ug/pg/general)
        chunk_type: Type of content (overview/fees/requirements/etc.)
        
    Returns:
        bool: True if successfully added, False on error
    """
    if not text.strip():
        print("Warning: Empty text provided for document chunk")
        return False
    
    try:
        # Generate embedding for the text
        embedding = await generate_embedding(text)
        if not embedding:
            print("Failed to generate embedding for document chunk")
            return False
        
        # Create point for insertion - ensure ID is valid for Qdrant (integer or UUID)
        if chunk_id:
            # Convert string chunk_id to integer using hash for consistency
            point_id = abs(hash(chunk_id)) % (10**10)  # Ensure positive integer within reasonable range
        else:
            # Fallback to hashing text + course_name
            point_id = abs(hash(text + course_name)) % (10**10)
        
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "text": text,
                "course_name": course_name,
                "chunk_id": chunk_id,
                "level": level,
                "type": chunk_type
            }
        )
        
        # Insert into collection
        await qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[point]
        )
        
        print(f"Successfully added document chunk for course: {course_name}")
        return True
        
    except Exception as e:
        print(f"Error adding document chunk: {e}")
        return False


# Health check function
async def health_check() -> Dict[str, Any]:
    """
    Check the health of vector database connections and configuration.
    
    Returns:
        Dict: Health status information
    """
    status = {
        "qdrant_connected": False,
        "embedding_api_configured": False,
        "collection_exists": False,
        "errors": []
    }
    
    try:
        # Check Qdrant connection
        collections = await qdrant_client.get_collections()
        status["qdrant_connected"] = True
        
        # Check if collection exists
        existing_collections = [col.name for col in collections.collections]
        status["collection_exists"] = COLLECTION_NAME in existing_collections
        
    except Exception as e:
        status["errors"].append(f"Qdrant connection error: {e}")
    
    # Check embedding API configuration
    status["embedding_api_configured"] = bool(EMBEDDING_CONFIG["api_key"])
    
    if not status["embedding_api_configured"]:
        status["errors"].append("Embedding API key not configured")
    
    return status


# Initialize collection on module import
async def _initialize_on_startup():
    """Initialize collection when module is imported."""
    await initialize_collection()

# Note: In a real application, you'd call this during app startup
# For now, it's available to be called manually when needed 