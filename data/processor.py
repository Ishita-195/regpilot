"""
Data Processor for RegPilot RAG Pipeline

Loads processed circulars into FAISS vector store.
Orchestrates the data pipeline.
"""

import os
import json
import glob
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DataProcessor:
    """Orchestrates loading data into the RAG system."""
    
    def __init__(self, processed_dir: str = "./data/processed_circulars"):
        """Initialize processor."""
        self.processed_dir = processed_dir
        self.vector_store = None
    
    def load_processed_circulars(self, processed_dir: Optional[str] = None) -> int:
        """
        Load all processed circulars into vector store.
        
        Args:
            processed_dir: Optional directory override
        
        Returns:
            Number of loaded circulars
        """
        if processed_dir:
            self.processed_dir = processed_dir
        
        from rag.vector_store import CircularVectorStore
        
        self.vector_store = CircularVectorStore()
        
        # Clear existing index
        self.vector_store.clear()
        
        # Find all JSON files in processed_circulars
        json_files = glob.glob(os.path.join(self.processed_dir, "*.json"))
        
        if not json_files:
            logger.warning(f"No JSON files found in {self.processed_dir}")
            return 0
        
        count = 0
        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    circular = json.load(f)
                
                # Extract data
                circular_id = circular.get("id")
                full_text = circular.get("full_text", "")
                
                # Create metadata
                metadata = {
                    "title": circular.get("title", ""),
                    "deadline": circular.get("deadline", ""),
                    "applicability": circular.get("applicability", []),
                    "tags": circular.get("tags", []),
                    "severity": circular.get("severity", "medium"),
                    "status": circular.get("status", "active"),
                    "ai_summary": circular.get("ai_summary", ""),
                }
                
                # Add to vector store
                self.vector_store.add_circular(circular_id, full_text, metadata)
                count += 1
                
                logger.debug(f"Loaded {circular_id}")
            
            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}")
        
        # Save the index
        self.vector_store.save()
        
        logger.info(f"Loaded {count} circulars into vector store")
        return count


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("RegPilot Data Processor")
    print("="*60)
    
    processor = DataProcessor()
    count = processor.load_processed_circulars()
    
    print(f"\n[SUCCESS] Loaded {count} circulars into RAG system")
    
    if count == 0:
        print("\nNo circulars found. Create sample data first:")
        print("  python data/sample_data/create_mock_circulars.py")
    
    print("="*60 + "\n")
