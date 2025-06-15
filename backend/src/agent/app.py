# mypy: disable - error - code = "no-untyped-def,misc"
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent.graph import graph

# Define the FastAPI app
app = FastAPI()


# Request/Response schemas
class ResearchRequest(BaseModel):
    query: str
    initial_search_query_count: Optional[int] = None
    max_research_loops: Optional[int] = None
    query_generator_model: Optional[str] = None
    reflection_model: Optional[str] = None
    answer_model: Optional[str] = None


class Source(BaseModel):
    label: str
    short_url: str
    value: str


class ResearchResponse(BaseModel):
    answer: str
    sources: List[Source]
    research_loop_count: int
    queries_executed: List[str]


@app.post("/api/research", response_model=ResearchResponse)
async def deep_research(request: ResearchRequest):
    """Execute deep research on a given query.
    
    Args:
        request: Research request containing the query and optional configuration
        
    Returns:
        Research response with answer, sources, and metadata
    """
    try:
        # Prepare configuration
        config_dict = {}
        if request.initial_search_query_count is not None:
            config_dict["number_of_initial_queries"] = request.initial_search_query_count
        if request.max_research_loops is not None:
            config_dict["max_research_loops"] = request.max_research_loops
        if request.query_generator_model is not None:
            config_dict["query_generator_model"] = request.query_generator_model
        if request.reflection_model is not None:
            config_dict["reflection_model"] = request.reflection_model
        if request.answer_model is not None:
            config_dict["answer_model"] = request.answer_model
        
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=request.query)]
        }
        
        # Execute the research graph
        config = {"configurable": config_dict} if config_dict else None
        result = graph.invoke(initial_state, config=config)
        
        # Extract response data
        answer = result["messages"][-1].content if result["messages"] else "No answer generated"
        sources = [
            Source(
                label=source["label"],
                short_url=source["short_url"],
                value=source["value"]
            )
            for source in result.get("sources_gathered", [])
        ]
        research_loop_count = result.get("research_loop_count", 0)
        queries_executed = result.get("search_query", [])
        
        return ResearchResponse(
            answer=answer,
            sources=sources,
            research_loop_count=research_loop_count,
            queries_executed=queries_executed
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research execution failed: {str(e)}")
