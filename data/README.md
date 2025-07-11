# KDM Data Ingestion

This directory contains sample course data and ingestion scripts for populating the vector database.

## Files

### `sample_courses.py`
Contains comprehensive course information for 4 KDM programs:
- **Data Science Masters** (24-month graduate program)
- **MBA Business Administration** (20-month executive program) 
- **Computer Science Bachelor** (4-year undergraduate program)
- **Digital Marketing Certificate** (6-month professional certificate)

Each course includes detailed sections:
- Program overview and objectives
- Eligibility requirements and prerequisites
- Program structure and curriculum details
- Fees, scholarships, and financial information
- Career outcomes and employment statistics

### `ingest_documents.py`
Intelligent document chunking and ingestion script that:
- ✂️ **Semantic Chunking**: Splits documents by logical sections
- 🧹 **Content Cleaning**: Normalizes whitespace and formatting
- 📦 **Vector Storage**: Stores chunks in Qdrant with embeddings
- 🔍 **Search Testing**: Validates functionality with sample queries
- 📊 **Progress Tracking**: Provides detailed ingestion statistics

## Quick Start

### 1. Prerequisites
Ensure you have set environment variables:
```bash
export EMBEDDING_MODEL_API=your_deepinfra_api_key
export QDRANT_API_KEY=your_qdrant_api_key
```

### 2. Install Dependencies
```bash
pip install -r ../requirements.txt
```

### 3. Run Ingestion
From the project root directory:
```bash
python data/ingest_documents.py
```

### 4. Expected Output
```
🏥 Checking system health...
✅ System health check passed!
🚀 Starting document ingestion process...
📦 Initializing vector database collection...

📚 Processing course: Data Science Masters
   ✂️  Created 5 chunks
   ✅ Stored chunk 1/5: overview
   ✅ Stored chunk 2/5: eligibility_requirements
   ✅ Stored chunk 3/5: program_details
   ✅ Stored chunk 4/5: fees_and_scholarships
   ✅ Stored chunk 5/5: career_outcomes

📚 Processing course: MBA Business Administration
   ✂️  Created 5 chunks
   ✅ Stored chunk 1/5: overview
   ...

🔍 Testing search functionality...
🔎 Testing query: 'Data Science eligibility requirements'
   ✅ Found 3 results
   1. Data Science Masters (score: 0.856)
      ELIGIBILITY REQUIREMENTS FOR DATA SCIENCE MASTERS: Academic Requirements: - Bachelor's degree...

📊 INGESTION SUMMARY
============================================================
Courses Processed: 4
Chunks Created: 20
Chunks Stored: 20
Success Rate: 100.0%

✅ No errors encountered!
🎉 Document ingestion completed successfully!
```

## Chunking Strategy

### Semantic Sections
Documents are chunked by logical sections:
- **Overview** - Program description and objectives
- **Eligibility Requirements** - Academic and experience requirements
- **Program Details** - Curriculum, duration, format
- **Fees and Scholarships** - Financial information
- **Career Outcomes** - Employment and salary statistics

### Smart Splitting
Long sections (>2000 characters) are intelligently split:
- Maintains paragraph boundaries
- Preserves semantic meaning
- Optimal chunk size for embeddings (1500 characters)
- Prevents information fragmentation

## Sample Data Overview

| Course | Level | Duration | Field | Target Audience |
|--------|-------|----------|-------|-----------------|
| **Data Science Masters** | Graduate | 24 months | Technology/STEM | STEM graduates, working professionals |
| **MBA Business Administration** | Graduate | 20 months | Business | Experienced professionals, managers |
| **Computer Science Bachelor** | Undergraduate | 4 years | Technology/STEM | High school graduates |
| **Digital Marketing Certificate** | Certificate | 6 months | Marketing/Business | Working professionals, career changers |

## Vector Database Structure

Each chunk is stored with:
```python
{
    "text": "Program content...",
    "course_name": "Data Science Masters"
}
```

## Testing RAG Functionality

After ingestion, test your RAG tools:

```python
from tools.rag_tool import search_course_documents

# Test search
result = await search_course_documents(
    query="What are the requirements for Data Science Masters?",
    limit=5
)

print(result["documents"])
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   ❌ Embedding API not configured. Please check your API key.
   ```
   **Solution**: Set `EMBEDDING_MODEL_API` environment variable

2. **Qdrant Connection Failed**
   ```
   ❌ Qdrant not connected. Please check your configuration.
   ```
   **Solution**: Verify `QDRANT_API_KEY` and URL in `config.py`

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'tools.vector'
   ```
   **Solution**: Run script from project root: `python data/ingest_documents.py`

### Health Check
Run system diagnostics:
```python
from tools.vector import health_check
import asyncio

status = asyncio.run(health_check())
print(status)
```

## Next Steps

1. **Add Real Data**: Replace sample courses with actual KDM course documents
2. **Advanced Metadata**: Add filtering by program level, field, duration
3. **Document Updates**: Implement versioning and incremental updates
4. **Monitoring**: Add ingestion logs and performance metrics

## Data Statistics

- **Total Documents**: 4 courses
- **Average Chunks per Course**: ~5-6
- **Estimated Vector Storage**: ~20-25 document chunks
- **Search Coverage**: All major program types and levels 