"""
FastAPI Routes for RegPilot RAG Pipeline

Provides REST API endpoints for the RAG system.
Integrates with FastAPI backend.
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from rag.retriever import RAGInterface

# Create router
router = APIRouter(prefix="/api/rag", tags=["rag"])

# Initialize RAG interface
rag = RAGInterface()


# Response models
class CircularResult(BaseModel):
    """Search result for a circular."""
    id: str
    title: str
    score: float
    deadline: Optional[str] = None
    applicability: List[str] = []
    tags: List[str] = []
    severity: str
    status: str
    ai_summary: str


class SearchResponse(BaseModel):
    """Response from search endpoint."""
    query: str
    count: int
    results: List[CircularResult]


class CircularResponse(BaseModel):
    """Response for a single circular."""
    id: str
    title: str
    deadline: Optional[str] = None
    applicability: List[str] = []
    tags: List[str] = []
    severity: str
    status: str
    ai_summary: str


class StatusResponse(BaseModel):
    """Response from status endpoint."""
    total_circulars: int
    ready: bool
    embedding_model: str


class RefreshResponse(BaseModel):
    """Response from refresh endpoint."""
    status: str
    message: str
    count: int


# Routes
@router.get("/search", response_model=SearchResponse)
async def search_circulars(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(5, ge=1, le=50, description="Number of results"),
    severity: Optional[str] = Query(None, description="Filter by severity (high/medium/low)"),
):
    """
    Search for RBI circulars.
    
    Parameters:
    - q: Search query (required)
    - top_k: Number of results (1-50, default 5)
    - severity: Optional filter by severity level
    
    Returns:
    - List of matching circulars with relevance scores
    
    Example:
    GET /api/rag/search?q=KYC+compliance&top_k=5
    """
    try:
        results = rag.search_circulars(q, top_k, severity)
        
        return SearchResponse(
            query=q,
            count=len(results),
            results=[CircularResult(**r) for r in results]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/circular/{circular_id}", response_model=CircularResponse)
async def get_circular(circular_id: str):
    """
    Get a specific circular by ID.
    
    Parameters:
    - circular_id: Circular ID (e.g., RBI/2024/001)
    
    Returns:
    - Full circular details
    
    Example:
    GET /api/rag/circular/RBI%2F2024%2F001
    """
    try:
        circular = rag.get_circular(circular_id)
        
        if not circular:
            raise HTTPException(status_code=404, detail=f"Circular {circular_id} not found")
        
        return CircularResponse(**circular)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get RAG system status.
    
    Returns:
    - System statistics and readiness status
    
    Example:
    GET /api/rag/status
    """
    try:
        status = rag.get_status()
        return StatusResponse(**status)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_index():
    """
    Refresh the vector store from processed circulars.
    
    Returns:
    - Refresh operation status
    
    Example:
    POST /api/rag/refresh
    """
    try:
        result = rag.refresh()
        return RefreshResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # For testing the routes
    print("RegPilot RAG Routes initialized")
    print("\nAvailable endpoints:")
    print("  GET  /api/rag/search?q=...&top_k=5")
    print("  GET  /api/rag/circular/{id}")
    print("  GET  /api/rag/status")
    print("  POST /api/rag/refresh")
