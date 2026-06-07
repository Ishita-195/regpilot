"""
RAG Interface for RegPilot

High-level search API for querying RBI circulars.
Provides semantic search with metadata filtering.
"""

import logging
from typing import List, Dict, Optional
from rag.vector_store import CircularVectorStore

logger = logging.getLogger(__name__)


class RAGInterface:
    """High-level interface for RAG searches."""
    
    def __init__(self, index_path: str = "./rag/faiss_index.bin", metadata_path: str = "./rag/faiss_metadata.json"):
        """Initialize RAG interface."""
        self.vector_store = CircularVectorStore(index_path, metadata_path)
    
    def search_circulars(self, query: str, top_k: int = 5, severity: Optional[str] = None) -> List[Dict]:
        """
        Search for circulars by query.
        
        Args:
            query: Search query text
            top_k: Number of results
            severity: Optional filter (high, medium, low)
        
        Returns:
            List of matching circulars with scores
        """
        results = self.vector_store.search(query, top_k)
        
        # Apply severity filter if provided
        if severity:
            results = [r for r in results if r.get("severity") == severity]
        
        return results
    
    def get_circular(self, circular_id: str) -> Optional[Dict]:
        """Get a specific circular by ID."""
        return self.vector_store.get_circular(circular_id)
    
    def get_status(self) -> Dict:
        """Get RAG system status."""
        stats = self.vector_store.get_stats()
        return {
            "total_circulars": stats["total_circulars"],
            "ready": stats["ready"],
            "embedding_model": "Hash-based (demo) / sentence-transformers (production)",
        }
    
    def refresh(self) -> Dict:
        """Refresh the vector store from processed circulars."""
        from data.processor import DataProcessor
        
        processor = DataProcessor()
        count = processor.load_processed_circulars()
        
        return {
            "status": "success",
            "message": f"Refreshed vector store with {count} circulars",
            "count": count,
        }


if __name__ == "__main__":
    # Demo: Test the RAG interface
    logging.basicConfig(level=logging.INFO)
    
    rag = RAGInterface()
    
    print("\n" + "="*60)
    print("RegPilot RAG Interface - Demo")
    print("="*60)
    
    # Test 1: Search
    print("\nTest 1: Searching for 'KYC compliance requirements'...")
    results = rag.search_circulars("KYC compliance requirements", top_k=5)
    
    if results:
        print(f"✓ Found {len(results)} results:")
        for r in results:
            print(f"  - {r['title']} (score: {r['score']:.2f})")
    else:
        print("✗ No results found (vector store may be empty)")
    
    # Test 2: Get status
    print("\nTest 2: Checking RAG status...")
    status = rag.get_status()
    print(f"✓ Total circulars: {status['total_circulars']}")
    print(f"✓ Ready: {status['ready']}")
    print(f"✓ Embedding model: {status['embedding_model']}")
    
    # Test 3: Get specific circular
    if results:
        print("\nTest 3: Getting specific circular...")
        circular = rag.get_circular(results[0]['id'])
        if circular:
            print(f"✓ Retrieved: {circular['title']}")
        else:
            print("✗ Failed to retrieve circular")
    
    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60 + "\n")
