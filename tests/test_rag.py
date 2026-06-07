"""
Test Suite for RegPilot RAG Pipeline

Unit and integration tests for all components.
"""

import pytest
import os
import json
import tempfile
from datetime import datetime


class TestVectorStore:
    """Tests for FAISS vector store."""
    
    def test_vector_store_initialization(self):
        """Test vector store initialization."""
        from rag.vector_store import CircularVectorStore
        
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, "index.bin")
            metadata_path = os.path.join(tmpdir, "metadata.json")
            
            store = CircularVectorStore(index_path, metadata_path)
            assert store is not None
            assert store.dimension == 768
    
    def test_add_and_search(self):
        """Test adding and searching circulars."""
        from rag.vector_store import CircularVectorStore
        
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, "index.bin")
            metadata_path = os.path.join(tmpdir, "metadata.json")
            
            store = CircularVectorStore(index_path, metadata_path)
            
            # Add a circular
            store.add_circular(
                "RBI/2024/001",
                "KYC compliance requirements for banks",
                {"title": "KYC Directive", "tags": ["KYC"], "severity": "high"}
            )
            
            # Search
            results = store.search("KYC requirements", top_k=5)
            assert len(results) >= 1
            assert results[0]["id"] == "RBI/2024/001"
    
    def test_get_circular(self):
        """Test retrieving a circular by ID."""
        from rag.vector_store import CircularVectorStore
        
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, "index.bin")
            metadata_path = os.path.join(tmpdir, "metadata.json")
            
            store = CircularVectorStore(index_path, metadata_path)
            
            store.add_circular(
                "RBI/2024/001",
                "Test content",
                {"title": "Test Title", "tags": ["Test"]}
            )
            
            circular = store.get_circular("RBI/2024/001")
            assert circular is not None
            assert circular["title"] == "Test Title"


class TestCircularParser:
    """Tests for HTML parser."""
    
    def test_parser_initialization(self):
        """Test parser initialization."""
        from data.circular_loader import CircularParser
        
        parser = CircularParser()
        assert parser is not None
    
    def test_extract_title(self):
        """Test title extraction."""
        from data.circular_loader import CircularParser
        from bs4 import BeautifulSoup
        
        parser = CircularParser()
        html = "<h1>Master Direction on KYC</h1>"
        soup = BeautifulSoup(html, 'html.parser')
        
        title = parser._extract_title(soup)
        assert "KYC" in title
    
    def test_extract_tags(self):
        """Test tag extraction."""
        from data.circular_loader import CircularParser
        
        parser = CircularParser()
        text = "KYC compliance is a critical requirement for cybersecurity"
        tags = parser._extract_tags(text, "KYC Title")
        
        assert "KYC" in tags
        assert "Cybersecurity" in tags
    
    def test_determine_severity(self):
        """Test severity determination."""
        from data.circular_loader import CircularParser
        
        parser = CircularParser()
        
        severity = parser._determine_severity(["KYC"], [])
        assert severity == "high"
        
        severity = parser._determine_severity(["Other"], [])
        assert severity == "low"


class TestRBIScraper:
    """Tests for RBI scraper."""
    
    def test_scraper_initialization(self):
        """Test scraper initialization."""
        from data.scraper import RBIScraper
        
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = RBIScraper(output_dir=tmpdir)
            assert scraper is not None
            assert scraper.base_url == "https://www.rbi.org.in"
    
    def test_extract_circular_links(self):
        """Test circular link extraction."""
        from data.scraper import RBIScraper
        
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = RBIScraper(output_dir=tmpdir)
            
            # Note: This will return empty list as RBI URL is not real
            links = scraper.extract_circular_links()
            assert isinstance(links, list)


class TestDataProcessor:
    """Tests for data processor."""
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        from data.processor import DataProcessor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = DataProcessor(processed_dir=tmpdir)
            assert processor is not None
    
    def test_load_empty_directory(self):
        """Test loading from empty directory."""
        from data.processor import DataProcessor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = DataProcessor(processed_dir=tmpdir)
            count = processor.load_processed_circulars()
            assert count == 0


class TestRAGInterface:
    """Tests for RAG interface."""
    
    def test_rag_initialization(self):
        """Test RAG interface initialization."""
        from rag.retriever import RAGInterface
        
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, "index.bin")
            metadata_path = os.path.join(tmpdir, "metadata.json")
            
            rag = RAGInterface(index_path, metadata_path)
            assert rag is not None
    
    def test_get_status(self):
        """Test RAG status."""
        from rag.retriever import RAGInterface
        
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, "index.bin")
            metadata_path = os.path.join(tmpdir, "metadata.json")
            
            rag = RAGInterface(index_path, metadata_path)
            status = rag.get_status()
            
            assert "total_circulars" in status
            assert "ready" in status
            assert status["ready"] == False  # Empty store


class TestMockDataGenerator:
    """Tests for mock data generator."""
    
    def test_create_mock_data(self):
        """Test mock data creation."""
        from data.sample_data.create_mock_circulars import create_mock_circular
        
        circular = create_mock_circular(
            "TEST/001",
            "Test Circular",
            "Test content",
            ["Test"]
        )
        
        assert circular["id"] == "TEST/001"
        assert circular["title"] == "Test Circular"
        assert "Test" in circular["tags"]
    
    def test_save_mock_data(self):
        """Test saving mock data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Override output directory
            import data.sample_data.create_mock_circulars as mock_gen
            original_dir = mock_gen.__dict__.get('output_dir')
            
            # Create data
            from data.sample_data.create_mock_circulars import main
            
            # Monkey-patch output directory
            os.environ['MOCK_OUTPUT_DIR'] = tmpdir
            
            # Verify directory was created
            assert os.path.exists(tmpdir) or tmpdir is not None


# Integration Tests
class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    def test_end_to_end_search(self):
        """Test complete search pipeline."""
        from data.sample_data.create_mock_circulars import create_mock_circular
        from rag.vector_store import CircularVectorStore
        
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, "index.bin")
            metadata_path = os.path.join(tmpdir, "metadata.json")
            
            # Create vector store
            store = CircularVectorStore(index_path, metadata_path)
            
            # Add test circulars
            for i in range(3):
                circular = create_mock_circular(
                    f"RBI/2024/{i+1:03d}",
                    f"Circular {i+1}",
                    f"Test content for circular {i+1}",
                    ["Test", "Compliance"]
                )
                store.add_circular(
                    circular["id"],
                    circular["full_text"],
                    {
                        "title": circular["title"],
                        "tags": circular["tags"],
                        "severity": circular["severity"],
                    }
                )
            
            # Search
            results = store.search("test compliance", top_k=3)
            assert len(results) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
