"""
RBI Circular Parser

Converts raw HTML to structured JSON with AI-generated summaries.
Uses Claude API for compliance insights.
"""

import os
import json
import re
import logging
from typing import Dict, Optional, List
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CircularParser:
    """Parses RBI circular HTML and generates AI summaries."""
    
    def __init__(self):
        """Initialize parser."""
        self.anthropic_client = None
        try:
            import anthropic
            self.anthropic_client = anthropic.Anthropic()
        except ImportError:
            logger.warning("Anthropic SDK not available. AI summaries will use fallback.")
    
    def parse_html(self, html: str, circular_id: str) -> Dict:
        """
        Parse HTML circular into structured format.
        
        Args:
            html: Raw HTML content
            circular_id: Unique identifier
        
        Returns:
            Parsed circular dictionary
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract text content
        text_content = soup.get_text(separator=' ', strip=True)
        text_content = re.sub(r'\s+', ' ', text_content)
        
        # Extract title (usually in h1 or title tag)
        title = self._extract_title(soup)
        
        # Extract metadata
        deadline = self._extract_deadline(text_content)
        applicability = self._extract_applicability(text_content)
        tags = self._extract_tags(text_content, title)
        requirements = self._extract_requirements(text_content)
        
        # Generate AI summary
        ai_summary = self._generate_ai_summary(text_content, title)
        
        # Determine severity
        severity = self._determine_severity(tags, requirements)
        
        return {
            "id": circular_id,
            "title": title,
            "date": datetime.now().isoformat(),
            "deadline": deadline,
            "applicability": applicability,
            "tags": tags,
            "severity": severity,
            "status": "active",
            "ai_summary": ai_summary,
            "requirements": requirements,
            "full_text": text_content[:2000],  # Store first 2000 chars
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract circular title."""
        # Try common title locations
        for selector in ['h1', 'h2', 'title', 'meta[property="og:title"]']:
            element = soup.select_one(selector)
            if element:
                title = element.get('content') or element.get_text(strip=True)
                if title:
                    return title[:200]
        return "RBI Circular"
    
    def _extract_deadline(self, text: str) -> Optional[str]:
        """Extract compliance deadline from text."""
        # Look for common date patterns
        date_patterns = [
            r'\b(\d{2}[-/]\d{2}[-/]\d{4})\b',
            r'\b(202[0-9][-/]\d{2}[-/]\d{2})\b',
            r'by\s+(\d{1,2}\s+\w+\s+202[0-9])',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_applicability(self, text: str) -> List[str]:
        """Extract applicable entities."""
        applicable = []
        
        keywords = {
            "Banks": ["banks", "banking institutions", "commercial banks"],
            "NBFCs": ["nbfc", "non-banking", "non-bank"],
            "Fintech": ["fintech", "digital payment", "payment system"],
            "Insurance": ["insurance", "insurer"],
            "All Financial Institutions": ["all financial", "scheduled", "rbi regulated"],
        }
        
        text_lower = text.lower()
        for entity, keywords_list in keywords.items():
            if any(kw in text_lower for kw in keywords_list):
                applicable.append(entity)
        
        return applicable if applicable else ["Banks", "NBFCs"]
    
    def _extract_tags(self, text: str, title: str) -> List[str]:
        """Extract tags based on content."""
        tags = []
        
        tag_keywords = {
            "KYC": ["kyc", "know your customer"],
            "Compliance": ["compliance", "regulatory", "requirement"],
            "Cybersecurity": ["cyber", "security", "data protection"],
            "Liquidity": ["liquidity", "cash", "reserve"],
            "Risk Management": ["risk", "management", "capital"],
            "Digital Banking": ["digital", "online", "mobile"],
            "AML": ["aml", "anti-money", "anti money"],
            "Reporting": ["report", "disclosure", "filing"],
        }
        
        combined_text = (text + " " + title).lower()
        for tag, keywords in tag_keywords.items():
            if any(kw in combined_text for kw in keywords):
                tags.append(tag)
        
        return tags if tags else ["Compliance"]
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract compliance requirements."""
        requirements = []
        
        # Look for sentences with requirement keywords
        sentences = text.split('. ')
        requirement_keywords = ["shall", "must", "required", "should", "need to"]
        
        for sentence in sentences[:5]:  # First 5 relevant sentences
            if any(kw in sentence.lower() for kw in requirement_keywords):
                clean = re.sub(r'\s+', ' ', sentence.strip())
                if len(clean) > 20:
                    requirements.append(clean[:150])
        
        return requirements[:3]  # Return up to 3 requirements
    
    def _generate_ai_summary(self, text: str, title: str) -> str:
        """Generate AI summary using Claude API."""
        if not self.anthropic_client:
            return self._generate_fallback_summary(text, title)
        
        try:
            # Use Claude to generate summary
            prompt = f"""Summarize this RBI circular in 2-3 sentences for compliance officers:

Title: {title}

Content: {text[:1000]}

Summary:"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            summary = response.content[0].text.strip()
            return summary
        
        except Exception as e:
            logger.warning(f"Failed to generate AI summary: {e}")
            return self._generate_fallback_summary(text, title)
    
    def _generate_fallback_summary(self, text: str, title: str) -> str:
        """Generate fallback summary without AI."""
        sentences = text.split('. ')
        summary = '. '.join(sentences[:2])
        if len(summary) > 200:
            summary = summary[:200] + "..."
        return summary
    
    def _determine_severity(self, tags: List[str], requirements: List[str]) -> str:
        """Determine severity level."""
        high_severity_keywords = ["immediately", "urgent", "critical", "mandatory"]
        
        if any(kw in str(tags + requirements).lower() for kw in high_severity_keywords):
            return "high"
        elif "KYC" in tags or "Cybersecurity" in tags:
            return "high"
        elif "Compliance" in tags:
            return "medium"
        else:
            return "low"
    
    def parse_file(self, html_file: str, circular_id: str, output_dir: str = "./data/processed_circulars") -> str:
        """
        Parse an HTML file and save as JSON.
        
        Args:
            html_file: Path to HTML file
            circular_id: Circular identifier
            output_dir: Output directory for JSON
        
        Returns:
            Path to output JSON file
        """
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html = f.read()
            
            parsed = self.parse_html(html, circular_id)
            
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{circular_id}.json")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved parsed circular to {output_file}")
            return output_file
        
        except Exception as e:
            logger.error(f"Failed to parse {html_file}: {e}")
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    parser = CircularParser()
    print("\nCircularParser initialized successfully")
    print("Use: parser.parse_file('path/to/html', 'RBI/2024/001')")
