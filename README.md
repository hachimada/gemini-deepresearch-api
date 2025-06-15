# Gemini Deep Research API

This project provides a FastAPI-powered deep research service using LangGraph and Google's Gemini models. The API performs comprehensive research on user queries by dynamically generating search terms, querying the web using Google Search, reflecting on results to identify knowledge gaps, and iteratively refining searches until it can provide well-supported answers with citations.

## Features

- 🧠 Powered by a LangGraph agent for advanced research capabilities
- 🔍 Dynamic search query generation using Google Gemini models
- 🌐 Integrated web research via Google Search API
- 🤔 Reflective reasoning to identify knowledge gaps and refine searches
- 📄 Generates answers with citations from gathered sources
- 🚀 FastAPI REST API for easy integration

## Project Structure

The project contains:

-   `src/agent/`: Contains the LangGraph/FastAPI application with the research agent logic

## Getting Started

Follow these steps to get the API server running locally.

**1. Prerequisites:**

-   Python 3.11+
-   **`GEMINI_API_KEY`**: The API requires a Google Gemini API key.
    1.  Create a file named `.env` by copying the `.env.example` file.
    2.  Open the `.env` file and add your Gemini API key: `GEMINI_API_KEY="YOUR_ACTUAL_API_KEY"

**2. Install Dependencies:**

```bash
uv sync
```

**3. Run API Server:**

```bash
uv run python -m uvicorn src.agent.app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

**4. API Usage:**

Send POST requests to `/api/research` endpoint:

```bash
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "量子コンピューティングの現状",
    "initial_search_query_count": 3,
    "max_research_loops": 2
  }'
```

## API Endpoint

### POST /api/research

**Request Body:**
```json
{
  "query": "Research topic or question (required)",
  "initial_search_query_count": 3,
  "max_research_loops": 2,
  "query_generator_model": "gemini-2.0-flash",
  "reflection_model": "gemini-2.5-flash-preview-04-17",
  "answer_model": "gemini-2.5-pro-preview-05-06"
}
```

All fields except `query` are optional. Default values:
- `initial_search_query_count`: 3 (maps internally to `number_of_initial_queries`)
- `max_research_loops`: 2
- Models: Use latest Gemini versions as defined in configuration

**Response:**
```json
{
  "answer": "Comprehensive research answer with citations",
  "sources": [
    {
      "label": "Source title",
      "short_url": "Short URL for display", 
      "value": "Full URL"
    }
  ],
  "research_loop_count": 2,
  "queries_executed": ["executed query 1", "executed query 2"]
}
```

## How the Research Agent Works

The core research engine is a LangGraph agent in `src/agent/graph.py` with these steps:

1.  **Generate Initial Queries:** Creates multiple search queries from user input using Gemini 2.0 Flash
2.  **Web Research:** Executes parallel searches using Google Search API + Gemini
3.  **Reflection & Knowledge Gap Analysis:** Analyzes results for completeness using Gemini 2.5 Flash
4.  **Iterative Refinement:** Generates follow-up queries if gaps found (up to max loops)
5.  **Finalize Answer:** Synthesizes comprehensive answer with citations using Gemini 2.5 Pro

## Production Deployment

For production deployment, you can run the API server directly:

```bash
uv run python -m uvicorn src.agent.app:app --host 0.0.0.0 --port 8000
```

Make sure to set the `GEMINI_API_KEY` environment variable in your production environment.

## Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/) - For the REST API server
- [LangGraph](https://github.com/langchain-ai/langgraph) - For building the research agent workflow
- [Google Gemini](https://ai.google.dev/models/gemini) - LLM for query generation, reflection, and answer synthesis
- [Google Search API](https://developers.google.com/custom-search) - For web search capabilities
- [Pydantic](https://pydantic.dev/) - For data validation and serialization

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details. 