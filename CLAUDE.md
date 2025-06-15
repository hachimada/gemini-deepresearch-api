# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Project Setup
```bash
# Install backend dependencies
cd backend && pip install .

# Install frontend dependencies  
cd frontend && npm install

# Set up environment variables
cp backend/.env.example backend/.env
# Add GEMINI_API_KEY to backend/.env
```

### Development Servers
```bash
# Start both frontend and backend servers
make dev

# Start frontend only (Vite dev server on port 5173)
make dev-frontend

# Start backend only (LangGraph dev server on port 2024)
make dev-backend
```

### Backend Development
```bash
cd backend

# Run tests
make test

# Run specific test file
make test TEST_FILE=tests/unit_tests/test_specific.py

# Run tests in watch mode
make test_watch

# Run extended tests
make extended_tests

# Format code
make format

# Lint code (includes ruff, mypy, import sorting)
make lint

# Start LangGraph dev server directly
langgraph dev
```

### Frontend Development
```bash
cd frontend

# Start dev server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

### Production Deployment
```bash
# Build Docker image
docker build -t gemini-fullstack-langgraph -f Dockerfile .

# Run with docker-compose (requires GEMINI_API_KEY and LANGSMITH_API_KEY)
GEMINI_API_KEY=<key> LANGSMITH_API_KEY=<key> docker-compose up
```

## Architecture Overview

### LangGraph Agent Flow
The core backend is a LangGraph agent (`backend/src/agent/graph.py`) that implements a research workflow:

1. **Query Generation** (`generate_query`): Generates multiple search queries from user input using Gemini 2.0 Flash
2. **Parallel Web Research** (`web_research`): Executes searches in parallel using Google Search API + Gemini
3. **Reflection** (`reflection`): Analyzes results for knowledge gaps using reasoning model (Gemini 2.5 Flash)
4. **Research Evaluation** (`evaluate_research`): Decides whether to continue research or finalize answer
5. **Answer Finalization** (`finalize_answer`): Synthesizes final response with citations

### State Management
- **OverallState**: Main state containing messages, search queries, results, and configuration
- **ReflectionState**: Tracks research sufficiency and follow-up queries
- **QueryGenerationState**: Manages generated search queries
- **WebSearchState**: Individual search execution state

### Configuration System
Agent behavior is controlled via `Configuration` class in `backend/src/agent/configuration.py`:
- Model selection (query_generator_model, reflection_model, answer_model)
- Research parameters (number_of_initial_queries, max_research_loops)
- Runtime configuration via environment variables or RunnableConfig

### Frontend Architecture
React app (`frontend/src/App.tsx`) uses LangGraph SDK for real-time streaming:
- **Real-time Events**: Processes agent execution events (generate_query, web_research, reflection, finalize_answer)
- **Activity Timeline**: Shows research progress in real-time
- **Message Streaming**: Displays conversation with AI responses
- **Research Effort Levels**: Maps to different agent configurations (low/medium/high effort)

### API Integration
- **Development**: Frontend connects to `localhost:2024` (LangGraph dev server)
- **Production**: Frontend served by FastAPI at `/app`, API at same host
- **Environment Detection**: Uses `import.meta.env.DEV` for API URL switching

### Key Files
- `backend/src/agent/graph.py`: Main agent workflow
- `backend/src/agent/state.py`: Type definitions for agent state
- `backend/src/agent/configuration.py`: Agent configuration schema
- `backend/src/agent/app.py`: FastAPI application with frontend serving
- `backend/langgraph.json`: LangGraph deployment configuration
- `frontend/src/App.tsx`: Main React application with streaming logic

### Environment Variables
- `GEMINI_API_KEY`: Required for Google Gemini API access
- `LANGSMITH_API_KEY`: Optional, for LangSmith tracing in production
- Frontend API URL automatically switches based on environment