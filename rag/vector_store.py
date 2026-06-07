"""
FAISS-based Vector Store for RegPilot RAG Pipeline

Lightweight vector database for semantic search of RBI circulars.
Uses FAISS for efficient similarity search with persistent storage.
"""

import json
import os
import hashlib
import logging
from typing import List, Dict, Tuple, Optional
import numpy as np

try:
    import faiss
except ImportError:
    faiss = None

logger = logging.getLogger(__name__)


class CircularVectorStore:
    """FAISS-based vector store for RBI circulars."""
    
    def __init__(self, index_path: str = "./rag/faiss_index.bin", metadata_path: str = "./rag/faiss_metadata.json"):
        """
        Initialize vector store.
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to metadata JSON file
        """
        if faiss is None:
            raise ImportError("FAISS not installed. Run: pip install faiss-cpu")
        
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = {}
        self.dimension = 768  # Default embedding dimension
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded existing index with {len(self.metadata)} circulars")
            except Exception as e:
                logger.warning(f"Failed to load index: {e}. Creating new one.")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = {}
        logger.info("Created new FAISS index")
    
    def add_circular(self, circular_id: str, text: str, metadata: Dict) -> None:
        """
        Add a circular to the vector store.
        
        Args:
            circular_id: Unique identifier (e.g., "RBI/2024/001")
            text: Full text for embedding
            metadata: Additional metadata (title, deadline, etc.)
        """
        # Generate embedding (demo: hash-based; replace with real embeddings for production)
        embedding = self._generate_embedding(text)
        embedding = np.array([embedding], dtype=np.float32)
        
        # Add to FAISS index
        self.index.add(embedding)
        
        # Store metadata
        self.metadata[circular_id] = {
            "id": circular_id,
            "title": metadata.get("title", ""),
            "deadline": metadata.get("deadline", ""),
            "applicability": metadata.get("applicability", []),
            "tags": metadata.get("tags", []),
            "severity": metadata.get("severity", "medium"),
            "status": metadata.get("status", "active"),
            "ai_summary": metadata.get("ai_summary", ""),
            "full_text": text[:500],  # Store first 500 chars for reference
        }
        logger.debug(f"Added circular {circular_id} to vector store")
    
    def search(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar circulars.
        
        Args:
            query_text: Search query
            top_k: Number of results to return
        
        Returns:
            List of matching circulars with scores
        """
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query_text)
        query_embedding = np.array([query_embedding], dtype=np.float32)
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        circular_ids = list(self.metadata.keys())
        
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(circular_ids):
                circular_id = circular_ids[idx]
                # Convert L2 distance to similarity score (0-1 range)
                similarity = 1 / (1 + dist)
                
                meta = self.metadata[circular_id]
                results.append({
                    "id": circular_id,
                    "title": meta.get("title", ""),
                    "score": float(similarity),
                    "deadline": meta.get("deadline", ""),
                    "applicability": meta.get("applicability", []),
                    "tags": meta.get("tags", []),
                    "severity": meta.get("severity", ""),
                    "status": meta.get("status", ""),
                    "ai_summary": meta.get("ai_summary", ""),
                })
        
        return results
    
    def get_circular(self, circular_id: str) -> Optional[Dict]:
        """Get a circular by ID."""
        if circular_id in self.metadata:
            return self.metadata[circular_id]
        return None
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text (demo: hash-based).
        
        For production, replace with:
        - sentence-transformers: model.encode(text)
        - Anthropic embeddings API
        """
        # Demo implementation: create fixed-size hash-based embedding
        # This ensures consistent embeddings for the same text
        text_hash = hashlib.md5(text.encode()).digest()
        
        # Create embedding by extending hash across dimension
        embedding = []
        for i in range(self.dimension):
            byte_idx = (i * 16) // self.dimension
            bit_idx = (i * 8) % 8
            byte_val = text_hash[byte_idx % len(text_hash)]
            bit_val = (byte_val >> bit_idx) & 1
            embedding.append(bit_val if bit_val else 0.5)
        
        # Add some randomness based on text characteristics
        text_len = len(text)
        word_count = len(text.split())
        
        for i in range(min(50, self.dimension)):
            embedding[i] = (embedding[i] + (text_len % 256) / 256.0) / 2
        
        for i in range(min(50, 50, self.dimension)):
            embedding[i + 50] = (embedding[i + 50] + (word_count % 256) / 256.0) / 2
        
        return embedding
    
    def save(self) -> None:
        """Save index and metadata to disk."""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logger.info(f"Saved index and metadata ({len(self.metadata)} circulars)")
    
    def clear(self) -> None:
        """Clear the vector store."""
        self._create_new_index()
        self.metadata = {}
        logger.info("Cleared vector store")
    
    def get_stats(self) -> Dict:
        """Get vector store statistics."""
        return {
            "total_circulars": len(self.metadata),
            "embedding_dimension": self.dimension,
            "index_size": os.path.getsize(self.index_path) if os.path.exists(self.index_path) else 0,
            "ready": self.index.ntotal > 0,
        }


if __name__ == "__main__":
    from pathlib import Path

    store = CircularVectorStore()

    pdf_folder = Path("./data/raw_circulars")

    for pdf_file in pdf_folder.glob("*.pdf"):
        with open(pdf_file, "rb") as f:
            text = f.read().decode(errors="ignore")

        store.add_circular(
            circular_id=pdf_file.stem,
            text=text,
            metadata={
                "title": pdf_file.stem,
                "tags": ["RBI", "Circular"],
                "severity": "medium"
            }
        )

        print(f"Indexed: {pdf_file.name}")

    store.save()
    print("All PDFs indexed successfully!")