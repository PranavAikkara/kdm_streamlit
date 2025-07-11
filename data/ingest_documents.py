"""
Document Ingestion Script for KDM Vector Database

This script reads the consolidated knowledge base with larger chunks,
parses the explicit metadata, and stores them in the Qdrant vector database for RAG functionality.
"""

import asyncio
import sys
import re
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from tools.vector import (
    initialize_collection, 
    add_document_chunk, 
    health_check,
    search_similar_chunks
)

class ConsolidatedKnowledgeBaseParser:
    """Handles parsing of the consolidated knowledge base file with larger chunks."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.chunks = []
        self.ingestion_stats = {
            "chunks_parsed": 0,
            "chunks_stored": 0,
            "total_characters": 0,
            "errors": []
        }
    
    def parse_knowledge_base(self) -> List[Dict[str, Any]]:
        """Parse the consolidated knowledge base file and extract chunks with metadata."""
        print(f"📖 Reading consolidated knowledge base from: {self.file_path}")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            print(f"❌ Error: Knowledge base file not found at {self.file_path}")
            return []
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return []
        
        # Split content by chunk markers
        chunk_pattern = r'===CHUNK_START===(.*?)===CHUNK_END==='
        chunk_matches = re.findall(chunk_pattern, content, re.DOTALL)
        
        for i, chunk_content in enumerate(chunk_matches, 1):
            try:
                chunk_data = self._parse_single_chunk(chunk_content.strip(), i)
                if chunk_data:
                    self.chunks.append(chunk_data)
                    self.ingestion_stats["chunks_parsed"] += 1
                    self.ingestion_stats["total_characters"] += len(chunk_data["content"])
                    
                    # Estimate tokens (roughly 1 token per 3-4 characters)
                    estimated_tokens = len(chunk_data["content"]) // 3.5
                    print(f"   📄 Parsed Chunk {i}: {chunk_data['course_name']} ({chunk_data['type']}) (~{estimated_tokens:.0f} tokens)")
                    
            except Exception as e:
                error_msg = f"Error parsing chunk {i}: {e}"
                self.ingestion_stats["errors"].append(error_msg)
                print(f"   ⚠️ {error_msg}")
        
        print(f"✅ Successfully parsed {len(self.chunks)} chunks from consolidated knowledge base")
        return self.chunks
    
    def _parse_single_chunk(self, chunk_content: str, chunk_number: int) -> Dict[str, Any]:
        """Parse a single chunk and extract metadata and content."""
        lines = chunk_content.strip().split('\n')
        
        metadata = {}
        content_lines = []
        parsing_metadata = True
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if parsing_metadata and ':' in line and not line.startswith('text:'):
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
            elif line.startswith('text:'):
                # Start of content
                parsing_metadata = False
                content_text = line[5:].strip()  # Remove 'text:' prefix
                if content_text:
                    content_lines.append(content_text)
            elif not parsing_metadata:
                content_lines.append(line)
        
        if not content_lines:
            return None
        
        content = ' '.join(content_lines)
        
        return {
            "chunk_number": chunk_number,
            "level": metadata.get("level", ""),
            "course_name": metadata.get("course_name", f"Chunk {chunk_number}"),
            "type": metadata.get("type", ""),
            "content": content,
            "chunk_id": f"chunk_{chunk_number}_{metadata.get('level', '')}_{metadata.get('type', '')}"
        }
    
    async def store_chunks_in_vector_db(self, chunks: List[Dict[str, Any]]) -> None:
        """Store all parsed chunks in the vector database."""
        print(f"\n💾 Storing {len(chunks)} consolidated chunks in vector database...")
        
        for chunk in chunks:
            try:
                # Prepare chunk text with title and content
                full_text = f"{chunk['course_name']} - {chunk['type'].title()}\n\n{chunk['content']}"
                
                success = await add_document_chunk(
                    text=full_text,
                    course_name=chunk['course_name'],
                    chunk_id=chunk['chunk_id'],
                    level=chunk['level'],
                    chunk_type=chunk['type']
                )
                
                if success:
                    self.ingestion_stats["chunks_stored"] += 1
                    estimated_tokens = len(full_text) // 3.5
                    print(f"   ✅ Stored Chunk {chunk['chunk_number']}: {chunk['course_name']} ({chunk['type']}) (~{estimated_tokens:.0f} tokens)")
                else:
                    error_msg = f"Failed to store Chunk {chunk['chunk_number']}: {chunk['course_name']} ({chunk['type']})"
                    self.ingestion_stats["errors"].append(error_msg)
                    print(f"   ❌ {error_msg}")
                    
            except Exception as e:
                error_msg = f"Exception storing Chunk {chunk['chunk_number']}: {e}"
                self.ingestion_stats["errors"].append(error_msg)
                print(f"   ⚠️ {error_msg}")
        
        print(f"\n✅ Vector database storage completed!")
    
    def print_ingestion_summary(self) -> None:
        """Print a comprehensive summary of the ingestion process."""
        print("\n" + "="*75)
        print("📊 KDM CONSOLIDATED KNOWLEDGE BASE INGESTION SUMMARY")
        print("="*75)
        print(f"Chunks Parsed: {self.ingestion_stats['chunks_parsed']}")
        print(f"Chunks Stored: {self.ingestion_stats['chunks_stored']}")
        print(f"Total Characters: {self.ingestion_stats['total_characters']:,}")
        
        if self.ingestion_stats["chunks_parsed"] > 0:
            avg_chunk_size = self.ingestion_stats["total_characters"] // self.ingestion_stats["chunks_parsed"]
            estimated_avg_tokens = avg_chunk_size // 3.5
            print(f"Average Chunk Size: {avg_chunk_size} characters")
            print(f"Estimated Avg Tokens: {estimated_avg_tokens:.0f} tokens per chunk")
            
            success_rate = (self.ingestion_stats["chunks_stored"] / self.ingestion_stats["chunks_parsed"]) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        if self.ingestion_stats["errors"]:
            print(f"\n⚠️ Errors encountered: {len(self.ingestion_stats['errors'])}")
            for error in self.ingestion_stats["errors"]:
                print(f"   • {error}")
        else:
            print("\n✅ No errors encountered - Perfect ingestion!")
        
        print(f"\n📋 Consolidated Chunk Categories:")
        chunk_types = {}
        for chunk in self.chunks:
            chunk_type = chunk.get('type', 'unknown')
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        for chunk_type, count in sorted(chunk_types.items()):
            print(f"   - {chunk_type.title()}: {count} chunks")
        
        print(f"\n⚡ Benefits of Consolidated Structure:")
        print(f"   - Larger chunks utilize token capacity efficiently")
        print(f"   - Comprehensive metadata for precise search")
        print(f"   - Consolidated information reduces fragmentation")
        print(f"   - Faster retrieval with fewer but richer chunks")
        print("="*75)

async def run_comprehensive_search_tests():
    """Run comprehensive search tests to verify the consolidated knowledge base."""
    print("\n🔍 Testing consolidated search functionality...")
    
    test_queries = [
        "What computer science programmes are available?",
        "Tell me about AI programme fees and scholarships",
        "MBA admission requirements and work experience",
        "Engineering programmes offered at KDM", 
        "International student visa requirements",
        "Campus facilities and accommodation",
        "Scholarship opportunities for Malaysian students",
        "Nursing programme course structure and duration",
        "What are the entry requirements for business programmes?",
        "Financial aid and payment options available"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔎 Test {i}: '{query}'")
        try:
            results = await search_similar_chunks(query, limit=3, score_threshold=0.6)
            if results:
                print(f"   ✅ Found {len(results)} relevant results")
                for j, result in enumerate(results, 1):
                    course_name = result.get('course_name', 'Unknown')
                    chunk_type = result.get('type', 'unknown')
                    level = result.get('level', 'general')
                    relevance = result.get('score', 0)
                    preview = result.get('text', '')[:80] + "..." if len(result.get('text', '')) > 80 else result.get('text', '')
                    
                    print(f"   {j}. {course_name} ({chunk_type}) [{level}] (relevance: {relevance:.3f})")
                    print(f"      Preview: {preview}")
            else:
                print(f"   ❌ No results found for query")
        except Exception as e:
            print(f"   ⚠️ Search error: {e}")

async def main():
    """Main ingestion process for the consolidated KDM knowledge base."""
    print("🏥 Checking system health...")
    health_status = await health_check()
    
    if not health_status.get("qdrant_connected", False):
        print("❌ Qdrant connection failed. Please check your configuration.")
        return
    
    if health_status.get("errors"):
        print("⚠️ Health check warnings:")
        for error in health_status["errors"]:
            print(f"   • {error}")
    else:
        print("✅ System health check passed!")
    
    print("🚀 Starting consolidated knowledge base ingestion process...")
    
    # Initialize vector database collection
    print("📦 Initializing vector database collection...")
    collection_created = await initialize_collection()
    if not collection_created:
        print("❌ Failed to initialize collection. Exiting.")
        return
    
    # Initialize parser and process knowledge base
    kb_file = Path(__file__).parent.parent / "knowledge_base_courses.txt"
    parser = ConsolidatedKnowledgeBaseParser(kb_file)
    
    # Parse the consolidated knowledge base
    chunks = parser.parse_knowledge_base()
    if not chunks:
        print("❌ No chunks parsed. Please check the knowledge base format.")
        return
    
    # Store chunks in vector database
    await parser.store_chunks_in_vector_db(chunks)
    
    # Print comprehensive summary
    parser.print_ingestion_summary()
    
    # Run search functionality tests
    await run_comprehensive_search_tests()
    
    print(f"\n🎉 KDM Consolidated Knowledge Base ingestion completed successfully!")
    print(f"🤖 Your chatbot is now ready with comprehensive, token-optimized course information!")

if __name__ == "__main__":
    asyncio.run(main()) 