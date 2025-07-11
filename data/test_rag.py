"""
Test Script for RAG Functionality

This script tests the RAG tools and vector search after document ingestion.
Run this after successfully ingesting documents to verify everything works.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from tools.rag_tool import search_course_documents, search_eligibility_requirements
from tools.vector import health_check, search_similar_chunks


async def test_basic_search():
    """Test basic vector search functionality."""
    print("🔍 Testing Basic Vector Search")
    print("-" * 40)
    
    test_queries = [
        "What are the requirements for Data Science Masters?",
        "MBA program fees and costs",
        "Computer Science bachelor career prospects",
        "Digital Marketing certificate duration and schedule",
        "international student IELTS requirements"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        
        try:
            results = await search_similar_chunks(query, limit=2, score_threshold=0.6)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"   {i}. {result['course_name']} (score: {result['score']:.3f})")
                    print(f"      {result['text'][:120]}...")
            else:
                print("   ⚠️  No results found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def test_rag_tools():
    """Test the RAG tool functions."""
    print("\n\n🛠️  Testing RAG Tools")
    print("-" * 40)
    
    # Test general search tool
    print("\n1. Testing search_course_documents:")
    try:
        result = await search_course_documents(
            query="What programming languages are taught in Computer Science?",
            limit=3
        )
        
        print(f"   Status: {result['status']}")
        print(f"   Documents found: {result['total_found']}")
        
        if result['documents']:
            for doc in result['documents'][:2]:  # Show first 2
                print(f"   - {doc['course_name']} (relevance: {doc['relevance_score']})")
                print(f"     {doc['content'][:100]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test specialized eligibility search
    print("\n2. Testing search_eligibility_requirements:")
    try:
        result = await search_eligibility_requirements(
            student_background="Bachelor in Psychology with 3.2 GPA",
            program_name="Data Science Masters"
        )
        
        print(f"   Status: {result['status']}")
        print(f"   Requirements found: {len(result.get('requirements_found', []))}")
        print(f"   Policies found: {len(result.get('policies_found', []))}")
        
        if result.get('requirements_found'):
            req = result['requirements_found'][0]
            print(f"   Sample requirement: {req['content'][:100]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def test_eligibility_scenarios():
    """Test specific eligibility scenarios."""
    print("\n\n👨‍🎓 Testing Eligibility Scenarios")
    print("-" * 40)
    
    scenarios = [
        {
            "background": "Bachelor in Computer Science with 3.5 GPA",
            "program": "Data Science Masters",
            "expected": "Should be eligible"
        },
        {
            "background": "High school graduate with 90% average",
            "program": "Computer Science Bachelor", 
            "expected": "Should be eligible"
        },
        {
            "background": "5 years marketing experience",
            "program": "Digital Marketing Certificate",
            "expected": "Should be eligible"
        },
        {
            "background": "2 years work experience, no bachelor degree",
            "program": "MBA Business Administration",
            "expected": "Should NOT be eligible"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Background: {scenario['background']}")
        print(f"   Program: {scenario['program']}")
        print(f"   Expected: {scenario['expected']}")
        
        try:
            result = await search_eligibility_requirements(
                student_background=scenario['background'],
                program_name=scenario['program']
            )
            
            if result['status'] == 'success':
                total_docs = result.get('total_documents', 0)
                req_docs = len(result.get('requirements_found', []))
                print(f"   ✅ Found {total_docs} total docs, {req_docs} requirement docs")
            else:
                print(f"   ❌ Search failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def test_cross_program_search():
    """Test searching across multiple programs."""
    print("\n\n🔄 Testing Cross-Program Search")
    print("-" * 40)
    
    cross_queries = [
        "programs that require IELTS for international students",
        "courses with internship opportunities", 
        "programs under $50,000 tuition fees",
        "technology related degree programs",
        "part-time study options available"
    ]
    
    for query in cross_queries:
        print(f"\n📝 Query: {query}")
        
        try:
            result = await search_course_documents(query, limit=4)
            
            if result['status'] == 'success':
                courses_found = set()
                for doc in result['documents']:
                    courses_found.add(doc['course_name'])
                
                print(f"   ✅ Found info from {len(courses_found)} programs:")
                for course in sorted(courses_found):
                    print(f"      - {course}")
            else:
                print(f"   ⚠️  {result.get('message', 'No results')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def main():
    """Main test function."""
    print("🧪 KDM RAG System Test Suite")
    print("=" * 50)
    
    # Health check first
    print("🏥 Checking system health...")
    try:
        health = await health_check()
        
        if not health['qdrant_connected']:
            print("❌ Qdrant not connected!")
            return
            
        if not health['embedding_api_configured']:
            print("❌ Embedding API not configured!")
            return
            
        if not health['collection_exists']:
            print("❌ Collection doesn't exist! Run ingestion first:")
            print("   python data/ingest_documents.py")
            return
            
        print("✅ All systems operational!")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Run all tests
    try:
        await test_basic_search()
        await test_rag_tools()
        await test_eligibility_scenarios()
        await test_cross_program_search()
        
        print("\n\n🎉 All tests completed!")
        print("✅ RAG system is working correctly")
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 