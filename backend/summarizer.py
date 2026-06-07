"""
LLM Summarization for RegPilot

Generates AI summaries using OpenRouter API.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class CircularSummarizer:
    """Summarizes RBI circulars using OpenRouter API."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize summarizer with OpenRouter.
        
        Args:
            api_key: OpenRouter API key (reads from OPENROUTER_API_KEY env var if not provided)
            model: Model name (defaults to meta-llama/llama-2-70b-chat)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", "meta-llama/llama-2-70b-chat")
        self.client = None
        
        if not self.api_key:
            logger.warning("OpenRouter API key not found. AI summaries will be disabled.")
            return
        
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            logger.info(f"OpenRouter initialized with model: {self.model}")
        except ImportError:
            logger.error("OpenAI package not installed. Run: pip install openai")
            self.client = None
    
    def summarize(self, text: str, max_length: int = 200) -> str:
        """
        Summarize circular text using OpenRouter.
        
        Args:
            text: Circular text to summarize
            max_length: Max summary length
        
        Returns:
            AI-generated summary
        """
        if not self.client or not self.api_key:
            logger.warning("OpenRouter not configured. Returning text truncation.")
            return text[:max_length] + "..." if len(text) > max_length else text
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a compliance expert. Summarize this RBI circular in {max_length} words for compliance officers. Focus on: deadlines, compliance requirements, affected entities."
                    },
                    {
                        "role": "user",
                        "content": text[:3000]  # Limit to first 3000 chars
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            summary = response.choices[0].message.content
            logger.info(f"Generated summary using {self.model}")
            return summary
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def extract_deadline(self, text: str) -> Optional[str]:
        """Extract compliance deadline from text."""
        if not self.client or not self.api_key:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract the compliance deadline from this RBI circular. Return only the date in YYYY-MM-DD format, or 'None' if not found."
                    },
                    {
                        "role": "user",
                        "content": text[:2000]
                    }
                ],
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Deadline extraction error: {e}")
            return None
    
    def classify_severity(self, text: str) -> str:
        """Classify circular severity level."""
        if not self.client or not self.api_key:
            return "medium"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Classify the severity of this RBI circular. Return ONLY one word: 'critical', 'high', 'medium', or 'low'."
                    },
                    {
                        "role": "user",
                        "content": text[:2000]
                    }
                ],
                max_tokens=10
            )
            severity = response.choices[0].message.content.strip().lower()
            if severity in ["critical", "high", "medium", "low"]:
                return severity
            return "medium"
        except Exception as e:
            logger.error(f"Severity classification error: {e}")
            return "medium"