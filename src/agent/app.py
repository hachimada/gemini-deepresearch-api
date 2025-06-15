"""Deep Research API using LangGraph and Google Gemini."""
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field, validator

from agent.graph import graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting Deep Research API")
    yield
    logger.info("Shutting down Deep Research API")


# Define the FastAPI app with enhanced configuration
app = FastAPI(
    title="Deep Research API",
    description="Comprehensive research API powered by LangGraph and Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with structured error response."""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error",
                "timestamp": time.time(),
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions with structured error response."""
    logger.exception(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error occurred",
                "type": "internal_error",
                "timestamp": time.time(),
            }
        },
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {process_time:.3f}s"
    )
    return response


# Request/Response schemas
class ResearchRequest(BaseModel):
    """Request model for research endpoint."""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The research query to investigate",
        example="量子コンピューティングの現状と将来性について"
    )
    initial_search_query_count: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Number of initial search queries to generate (1-10)",
        example=3
    )
    max_research_loops: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Maximum number of research loops (1-5)",
        example=2
    )
    query_generator_model: Optional[str] = Field(
        None,
        description="Gemini model for query generation",
        example="gemini-2.0-flash-exp"
    )
    reflection_model: Optional[str] = Field(
        None,
        description="Gemini model for reflection",
        example="gemini-2.5-flash"
    )
    answer_model: Optional[str] = Field(
        None,
        description="Gemini model for final answer generation",
        example="gemini-2.5-pro"
    )
    
    @validator("query")
    def validate_query(cls, v: str) -> str:
        """Validate and clean query string."""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class Source(BaseModel):
    """Source information model."""
    
    label: str = Field(
        description="Human-readable label for the source",
        example="Wikipedia - Quantum Computing"
    )
    short_url: str = Field(
        description="Shortened URL of the source",
        example="https://en.wikipedia.org/wiki/Quantum_computing"
    )
    value: str = Field(
        description="Content or summary from the source",
        example="Quantum computing is a type of computation..."
    )


class ResearchMetadata(BaseModel):
    """Metadata about the research process."""
    
    research_loop_count: int = Field(
        description="Number of research loops executed",
        example=2
    )
    queries_executed: List[str] = Field(
        description="List of all search queries that were executed",
        example=["quantum computing current state", "quantum computing applications 2024"]
    )
    processing_time_seconds: float = Field(
        description="Total processing time in seconds",
        example=12.5
    )
    timestamp: float = Field(
        description="Unix timestamp when research was completed",
        example=1699123456.789
    )


class ResearchResponse(BaseModel):
    """Response model for research endpoint."""
    
    answer: str = Field(
        description="Comprehensive research answer with citations",
        example="Based on current research, quantum computing has made significant progress..."
    )
    sources: List[Source] = Field(
        description="List of sources used in the research",
        example=[]
    )
    metadata: ResearchMetadata = Field(
        description="Metadata about the research process"
    )
    success: bool = Field(
        default=True,
        description="Whether the research was successful"
    )


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(
        description="Service status",
        example="healthy"
    )
    timestamp: float = Field(
        description="Current timestamp",
        example=1699123456.789
    )
    version: str = Field(
        description="API version",
        example="1.0.0"
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint.
    
    Returns:
        Health status information
    """
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version="1.0.0"
    )


@app.post(
    "/api/research",
    response_model=ResearchResponse,
    status_code=status.HTTP_200_OK,
    tags=["Research"],
    summary="Execute deep research",
    description="Perform comprehensive research on a given query using LangGraph and Google Gemini"
)
async def deep_research(request: ResearchRequest) -> ResearchResponse:
    """Execute deep research on a given query.
    
    This endpoint performs multi-step research using:
    1. Query generation and expansion
    2. Parallel web searches
    3. Content analysis and reflection
    4. Comprehensive answer synthesis
    
    Args:
        request: Research request containing the query and optional configuration
        
    Returns:
        Comprehensive research response with answer, sources, and metadata
        
    Raises:
        HTTPException: If research execution fails
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting research for query: {request.query}")
        
        # Prepare configuration
        config_dict: Dict[str, Any] = {}
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
        logger.info(f"Executing research graph with config: {config_dict}")
        
        result = graph.invoke(initial_state, config=config)
        
        # Extract and validate response data
        if not result or "messages" not in result or not result["messages"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No research results generated"
            )
        
        answer = result["messages"][-1].content
        if not answer or not answer.strip():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Empty research answer generated"
            )
        
        # Process sources with validation
        sources = []
        for source_data in result.get("sources_gathered", []):
            try:
                source = Source(
                    label=source_data.get("label", "Unknown Source"),
                    short_url=source_data.get("short_url", ""),
                    value=source_data.get("value", "")
                )
                sources.append(source)
            except Exception as e:
                logger.warning(f"Failed to process source: {e}")
                continue
        
        research_loop_count = result.get("research_loop_count", 0)
        queries_executed = result.get("search_query", [])
        
        # Ensure queries_executed is a list
        if not isinstance(queries_executed, list):
            queries_executed = [str(queries_executed)] if queries_executed else []
        
        processing_time = time.time() - start_time
        logger.info(f"Research completed in {processing_time:.2f}s with {len(sources)} sources")
        
        return ResearchResponse(
            answer=answer.strip(),
            sources=sources,
            metadata=ResearchMetadata(
                research_loop_count=research_loop_count,
                queries_executed=queries_executed,
                processing_time_seconds=round(processing_time, 3),
                timestamp=time.time()
            ),
            success=True
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.exception(f"Research failed after {processing_time:.2f}s: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Research execution failed",
                "error_type": type(e).__name__,
                "processing_time": round(processing_time, 3)
            }
        )
