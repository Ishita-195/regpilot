"""
Mock Circular Data Generator for RegPilot

Creates sample RBI circulars for testing the RAG pipeline.
"""

import os
import json
from datetime import datetime, timedelta


def create_mock_circular(circular_id: str, title: str, content: str, tags: list, deadline_days: int = 90) -> dict:
    """Create a mock circular."""
    deadline = datetime.now() + timedelta(days=deadline_days)
    
    return {
        "id": circular_id,
        "title": title,
        "date": datetime.now().isoformat(),
        "deadline": deadline.strftime("%Y-%m-%d"),
        "applicability": ["Banks", "NBFCs"],
        "tags": tags,
        "severity": "high" if "KYC" in tags or "Cyber" in tags else "medium",
        "status": "active",
        "ai_summary": content[:200],
        "requirements": [
            "Update systems within 30 days",
            "Ensure compliance by deadline",
            "Submit confirmation to RBI",
        ],
        "full_text": content,
    }


def main():
    """Generate mock circular data."""
    output_dir = "./data/processed_circulars"
    os.makedirs(output_dir, exist_ok=True)
    
    circulars = [
        create_mock_circular(
            "RBI/2024/001",
            "Master Direction on Know Your Customer (KYC)",
            """
            The Reserve Bank of India (RBI) has issued revised Master Direction on KYC norms.
            All banks and financial institutions must update their KYC forms to capture additional
            information about beneficial owners. The deadline for compliance is March 31, 2024.
            
            Key Requirements:
            - Update KYC forms with additional fields
            - Conduct fresh KYC for existing customers within 90 days
            - Implement enhanced due diligence for high-risk customers
            - Maintain proper documentation and records
            
            This circular applies to all scheduled commercial banks, NBFCs, and payment banks.
            Banks must ensure that all customer-facing staff are trained on the new requirements.
            """,
            ["KYC", "Compliance", "AML", "Reporting"]
        ),
        
        create_mock_circular(
            "RBI/2024/002",
            "Cyber Security and Resilience Framework for Banks",
            """
            The RBI has released an updated Cyber Security and Resilience Framework applicable
            to all banks. This framework sets standards for information security, data protection,
            and business continuity planning.
            
            Key Requirements:
            - Implement end-to-end encryption for all customer data
            - Conduct annual security audits and penetration testing
            - Establish incident response and recovery procedures
            - Provide cybersecurity training to all employees
            - Report cyber incidents to RBI within 6 hours
            
            The framework covers technology, people, and process dimensions of cybersecurity.
            Banks must comply with these requirements by December 31, 2024.
            """,
            ["Cybersecurity", "Risk Management", "Digital Banking", "Compliance"]
        ),
        
        create_mock_circular(
            "RBI/2024/003",
            "Guidelines on Liquidity Risk Management",
            """
            The RBI has issued comprehensive guidelines on liquidity risk management for banks.
            These guidelines aim to ensure that banks maintain adequate liquidity buffers and
            manage their funding needs effectively.
            
            Key Requirements:
            - Maintain Liquidity Coverage Ratio (LCR) of at least 100%
            - Maintain Net Stable Funding Ratio (NSFR) of at least 100%
            - Develop contingency funding plans
            - Regular stress testing of liquidity scenarios
            - Board-level oversight of liquidity management
            
            These guidelines are effective immediately and banks must ensure compliance
            with all provisions by the end of the current financial year.
            """,
            ["Liquidity", "Risk Management", "Compliance", "Reporting"]
        ),
    ]
    
    # Save each circular as JSON
    for circular in circulars:
        filename = os.path.join(output_dir, f"{circular['id']}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(circular, f, indent=2, ensure_ascii=False)
        print(f"✓ Created {circular['id']}: {circular['title']}")
    
    print(f"\n✓ Generated {len(circulars)} mock circulars in {output_dir}")
    return len(circulars)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RegPilot Mock Circular Generator")
    print("="*60 + "\n")
    
    count = main()
    
    print("\nNext steps:")
    print("1. Load into vector store: python data/processor.py")
    print("2. Test search: python rag/retriever.py")
    print("="*60 + "\n")
