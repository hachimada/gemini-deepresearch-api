# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Project Setup
```bash
# Install backend dependencies
cd backend && pip install .

# Set up environment variables
cp backend/.env.example backend/.env
# Add GEMINI_API_KEY to backend/.env
```

### API Development
```bash
cd backend

# Start API server for development
uv run python -m uvicorn src.agent.app:app --host 0.0.0.0 --port 8000 --reload

# Test API endpoint
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{"query": "量子コンピューティングの現状", "initial_search_query_count": 3, "max_research_loops": 2}'
```

### Production Deployment
```bash
# Start API server for production
cd backend
uv run python -m uvicorn src.agent.app:app --host 0.0.0.0 --port 8000
```

## Architecture Overview

### Deep Research API
FastAPI-based REST API that executes comprehensive research using LangGraph agent workflow.

### LangGraph Agent Flow
The core research engine is a LangGraph agent (`backend/src/agent/graph.py`) with sequential workflow:

1. **Query Generation** (`generate_query`): Creates multiple search queries from user input using Gemini 2.0 Flash
2. **Parallel Web Research** (`web_research`): Executes searches in parallel using Google Search API + Gemini
3. **Reflection** (`reflection`): Analyzes results for knowledge gaps using Gemini 2.5 Flash
4. **Research Evaluation** (`evaluate_research`): Decides whether to continue research or finalize answer
5. **Answer Finalization** (`finalize_answer`): Synthesizes comprehensive answer with citations using Gemini 2.5 Pro

### API Endpoint
**POST /api/research**

Request Schema:
```python
class ResearchRequest(BaseModel):
    query: str                                    # Required research query
    initial_search_query_count: Optional[int]     # Maps to number_of_initial_queries
    max_research_loops: Optional[int]             # Maximum research iterations
    query_generator_model: Optional[str]          # Gemini model for query generation
    reflection_model: Optional[str]               # Gemini model for reflection
    answer_model: Optional[str]                   # Gemini model for final answer
```

Response Schema:
```python
class ResearchResponse(BaseModel):
    answer: str                    # Final research answer with citations
    sources: List[Source]          # Web sources with URLs and labels
    research_loop_count: int       # Number of research loops executed
    queries_executed: List[str]    # All search queries executed
```

### Configuration System
Agent behavior controlled via `Configuration` class:
- **Default Models**: Gemini 2.0 Flash, 2.5 Flash, 2.5 Pro
- **Default Parameters**: 3 initial queries, 2 max research loops
- **Runtime Override**: Via API request parameters

### Key Files
- `backend/src/agent/app.py`: FastAPI application with /api/research endpoint
- `backend/src/agent/graph.py`: LangGraph agent workflow implementation
- `backend/src/agent/state.py`: Type definitions for agent state management
- `backend/src/agent/configuration.py`: Agent configuration schema
- `backend/src/agent/tools_and_schemas.py`: Pydantic models for structured output

### Environment Variables
- `GEMINI_API_KEY`: Required for Google Gemini API access