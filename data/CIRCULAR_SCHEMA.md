# RBI Circular JSON Schema

## Overview

This document describes the JSON schema for processed RBI circulars used in the RegPilot RAG pipeline.

## Schema Definition

```json
{
  "id": "RBI/2024/001",
  "title": "Master Direction on Know Your Customer (KYC)",
  "date": "2024-05-22T10:30:00",
  "deadline": "2024-12-31",
  "applicability": ["Banks", "NBFCs", "Fintech"],
  "tags": ["KYC", "Compliance", "AML"],
  "severity": "high",
  "status": "active",
  "ai_summary": "...",
  "requirements": ["requirement1", "requirement2", "requirement3"],
  "full_text": "..."
}
```

## Field Descriptions

### id (string, required)
- Unique identifier for the circular
- Format: `RBI/YYYY/NNN`
- Example: `RBI/2024/001`

### title (string, required)
- Full title of the circular
- Max length: 200 characters
- Example: "Master Direction on Know Your Customer (KYC)"

### date (string, required)
- Publication date in ISO 8601 format
- Format: `YYYY-MM-DDTHH:MM:SS`
- Example: "2024-05-22T10:30:00"

### deadline (string, optional)
- Compliance deadline in ISO date format
- Format: `YYYY-MM-DD`
- Example: "2024-12-31"
- Null if no deadline

### applicability (array of strings, required)
- List of entities this circular applies to
- Valid values:
  - "Banks"
  - "NBFCs"
  - "Fintech"
  - "Insurance"
  - "All Financial Institutions"
- Example: ["Banks", "NBFCs"]

### tags (array of strings, required)
- Classification tags for categorization
- Valid values:
  - "KYC"
  - "Compliance"
  - "Cybersecurity"
  - "Liquidity"
  - "Risk Management"
  - "Digital Banking"
  - "AML"
  - "Reporting"
- Example: ["KYC", "Compliance", "AML"]

### severity (string, required)
- Importance level
- Valid values:
  - "high" - Immediate action required
  - "medium" - Action needed within 90 days
  - "low" - General information
- Example: "high"

### status (string, required)
- Current status of the circular
- Valid values:
  - "active" - Currently in effect
  - "superseded" - Replaced by newer version
  - "deprecated" - No longer applicable
- Example: "active"

### ai_summary (string, required)
- AI-generated summary (max 200 characters)
- Generated using Claude API
- Contains key points for compliance officers
- Example: "Banks must update KYC forms within 30 days..."

### requirements (array of strings, required)
- List of specific compliance requirements (max 3)
- Extracted from circular text
- Max 150 characters per requirement
- Example:
  ```json
  [
    "Update KYC forms with additional fields",
    "Conduct fresh KYC for existing customers",
    "Maintain proper documentation"
  ]
  ```

### full_text (string, required)
- First 2000 characters of circular content
- Used for semantic search embeddings
- Contains original text from circular
- Example: "The RBI has issued revised Master Direction on KYC..."

## Data Types Reference

| Type | Description | Example |
|------|-------------|---------|
| string | Text data | "Master Direction..." |
| number | Numeric values | 2024, 1.5 |
| boolean | True/False | true, false |
| array | List of values | ["KYC", "Compliance"] |
| object | Nested object | {...} |
| null | No value | null |

## Validation Rules

1. **id**: Must match format `RBI/YYYY/NNN`
2. **title**: 10-200 characters
3. **date**: Valid ISO 8601 datetime
4. **deadline**: Valid ISO 8601 date (if provided)
5. **applicability**: Non-empty array, valid values only
6. **tags**: Non-empty array, valid values only
7. **severity**: One of [high, medium, low]
8. **status**: One of [active, superseded, deprecated]
9. **ai_summary**: 10-200 characters
10. **requirements**: Array of 1-3 items, max 150 chars each
11. **full_text**: 100-2000 characters

## Processing Pipeline

```
Raw HTML
    ↓
[Parser] - Extract title, metadata
    ↓
[Loader] - Parse HTML content
    ↓
[AI] - Generate summary & tags
    ↓
[Validator] - Check schema compliance
    ↓
JSON Output (this schema)
    ↓
[Vector Store] - Create embeddings
    ↓
[Search Ready]
```

## Example JSON

```json
{
  "id": "RBI/2024/001",
  "title": "Master Direction on Know Your Customer (KYC)",
  "date": "2024-05-22T10:30:00",
  "deadline": "2024-12-31",
  "applicability": ["Banks", "NBFCs"],
  "tags": ["KYC", "Compliance", "AML", "Reporting"],
  "severity": "high",
  "status": "active",
  "ai_summary": "The RBI has issued revised KYC norms. All banks and financial institutions must update their KYC forms within 90 days. Enhanced due diligence is required for high-risk customers.",
  "requirements": [
    "Update KYC forms with additional beneficial owner information",
    "Conduct fresh KYC for existing customers within 90 days",
    "Implement enhanced due diligence for high-risk customers"
  ],
  "full_text": "The Reserve Bank of India (RBI) has issued revised Master Direction on KYC norms applicable to all scheduled commercial banks, payment banks, and NBFCs. The key requirements include: 1. Update of KYC forms 2. Fresh KYC for existing customers 3. Enhanced due diligence..."
}
```

## Changes & Versioning

This schema is version 1.0 (May 2024).

### Possible Future Changes
- Add `regulatory_body` field
- Add `implementation_cost` estimate
- Add `affected_products` list
- Add `exemptions` array

## Notes

- All text fields are stored in UTF-8 encoding
- Dates follow ISO 8601 standard
- Search uses the `full_text` field for embeddings
- Metadata fields used for filtering in search results
- JSON is stored with 2-space indentation for readability
