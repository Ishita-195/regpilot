"""
PDF Ingestion Pipeline for RegPilot

Reads PDFs from data/raw_circulars/, extracts text, builds structured JSON
in data/processed_circulars/, and creates the FAISS index.

Run from project root:
    python data/ingest_pdfs.py
"""

import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ── PDF text extraction ───────────────────────────────────────────────────────

def extract_pdf_text(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        logger.error("pypdf not installed. Run: pip install pypdf")
        return ""

    try:
        reader = PdfReader(str(pdf_path))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text.strip())
        return "\n\n".join(pages)
    except Exception as e:
        logger.error(f"Failed to read {pdf_path.name}: {e}")
        return ""


# ── Metadata extraction ───────────────────────────────────────────────────────

def detect_circular_id(text: str, filename: str) -> str:
    """Try to find the RBI reference number in the first 3000 chars."""
    patterns = [
        r'RBI/\d{4}[-–]\d{2,4}/\d+',   # RBI/2024-25/67
        r'RBI/\d{4}/\d{1,4}',           # RBI/2024/001
        r'DNBR\.[A-Z.]+/\d+/[0-9.]+/\d{4}-\d{2}',
        r'DoS\.[A-Z.]+/\d+/[0-9.]+/\d{4}-\d{2}',
    ]
    for pattern in patterns:
        m = re.search(pattern, text[:3000], re.IGNORECASE)
        if m:
            ref = m.group(0)
            # Normalise RBI/2024-25/67  →  RBI/2024/067
            m2 = re.match(r'RBI/(\d{4})-\d{2,4}/(\d+)', ref)
            if m2:
                return f"RBI/{m2.group(1)}/{int(m2.group(2)):03d}"
            return ref
    # Last resort: use first 12 chars of the hashed filename
    stem = Path(filename).stem[:12]
    return f"RBI/PDF/{stem}"


def extract_date(text: str) -> str:
    months = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12",
    }
    patterns = [
        (r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})', "dmy"),
        (r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(20\d{2})', "mdy"),
        (r'(20\d{2})[-/](\d{2})[-/](\d{2})', "ymd"),
        (r'(\d{2})[./](\d{2})[./](20\d{2})', "dmy2"),
    ]
    search = text[:2000]
    for pattern, fmt in patterns:
        m = re.search(pattern, search, re.IGNORECASE)
        if not m:
            continue
        g = m.groups()
        try:
            if fmt == "dmy":
                return f"{g[2]}-{months[g[1].lower()]}-{int(g[0]):02d}"
            if fmt == "mdy":
                return f"{g[2]}-{months[g[0].lower()]}-{int(g[1]):02d}"
            if fmt == "ymd":
                return f"{g[0]}-{g[1]}-{g[2]}"
            if fmt == "dmy2":
                return f"{g[2]}-{g[1]}-{int(g[0]):02d}"
        except (KeyError, ValueError):
            continue
    return datetime.now().strftime("%Y-%m-%d")


def extract_title(text: str, filename: str) -> str:
    """
    RBI PDFs have a consistent header layout:
      [Hindi]
      ___ RESERVE BANK OF INDIA ___
      www.rbi.org.in
      RBI/YYYY-YY/NNN          ← reference line (anchor)
      DeptCode...   Date       ← skip 1 more line
      <Actual title – 1-3 lines, ends with year>
      Please refer... / In exercise of...   ← body starts here

    Strategy: locate the RBI reference line, skip one more line, then
    collect subsequent lines as the title until the body begins.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    rbi_ref = re.compile(r'^RBI/\d{4}[-–]\d{2,4}/\d+', re.IGNORECASE)
    body_start = re.compile(
        r'^(please refer|in exercise|in view|accordingly|whereas|'
        r'all (scheduled|commercial|primary|urban|rural)|dear sir|madam)',
        re.IGNORECASE
    )

    # Find the index of the RBI reference line
    ref_idx = None
    for i, line in enumerate(lines[:20]):
        if rbi_ref.match(line):
            ref_idx = i
            break

    if ref_idx is not None:
        # Skip the reference line and the department-code/date line after it
        start = ref_idx + 2
        candidate = []
        for line in lines[start:start + 6]:
            if body_start.match(line):
                break
            candidate.append(line)
            # Title ends when the line closes with a year
            if re.search(r'\d{4}\s*\.?\s*$', line):
                break
        if candidate:
            title = re.sub(r"\s+", " ", " ".join(candidate)).strip()
            return title[:250]

    # Fallback: first line that looks like a directive title
    directive = re.compile(
        r'(master direction|circular|guideline|framework|norms|directions?,?\s+\d{4}|'
        r'notification|instruction|advisory)',
        re.IGNORECASE
    )
    for line in lines[:30]:
        if directive.search(line) and 20 < len(line) < 250:
            return line
    for line in lines[:15]:
        if len(line) > 25:
            return line[:200]
    return f"RBI Circular – {Path(filename).stem[:20]}"


def infer_category(text: str, title: str) -> str:
    combined = (text[:3000] + " " + title).lower()
    mapping = [
        ("KYC/AML",         ["kyc", "know your customer", "anti-money laundering", "aml", "ckyc"]),
        ("Digital Lending",  ["digital lending", "lending service provider", "lsp"]),
        ("Cybersecurity",    ["cyber security", "cybersecurity", "information security", "soc ", "penetration"]),
        ("Prudential Norms", ["prudential", "npa", "asset classification", "income recognition", "irac", "provisioning"]),
        ("Payments",         ["prepaid payment", "ppi", "upi", "wallet", "payment instrument"]),
        ("Green Finance",    ["green deposit", "green finance", "sustainable finance", "esg"]),
        ("Capital Adequacy", ["capital adequacy", "crar", "basel", "tier 1", "tier 2"]),
        ("Fraud Prevention", ["fraud", "forgery", "counterfeit"]),
        ("Interest Rates",   ["interest rate", "base rate", "mclr"]),
    ]
    for category, keywords in mapping:
        if any(kw in combined for kw in keywords):
            return category
    return "Regulatory"


def extract_tags(text: str, title: str) -> List[str]:
    combined = (text[:3000] + " " + title).lower()
    tag_map = {
        "KYC":            ["kyc", "know your customer"],
        "AML":            ["aml", "anti-money laundering"],
        "Cybersecurity":  ["cyber", "information security"],
        "Compliance":     ["compliance", "regulatory"],
        "Digital Banking":["digital banking", "online banking", "mobile banking"],
        "Risk Management":["risk management", "risk framework"],
        "Reporting":      ["reporting", "disclosure", "filing"],
        "Capital":        ["capital adequacy", "crar"],
        "Payments":       ["payment", "upi", "ppi"],
        "Lending":        ["lending", "loan", "credit"],
    }
    tags = [tag for tag, kws in tag_map.items() if any(kw in combined for kw in kws)]
    return tags[:5] or ["Compliance"]


def determine_severity(text: str, tags: List[str]) -> str:
    low = text[:3000].lower()
    if any(kw in low for kw in ["immediately", "with immediate effect", "forthwith"]):
        return "critical"
    if "KYC" in tags or "Cybersecurity" in tags or "AML" in tags:
        return "high"
    if any(kw in low for kw in ["shall", "must", "mandatory"]):
        return "high"
    return "medium"


def extract_requirements(text: str) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    found = []
    for s in sentences[:80]:
        s = s.strip()
        if any(kw in s.lower() for kw in ["shall", "must", "required to", "directed to", "need to"]):
            clean = re.sub(r"\s+", " ", s)
            if 30 < len(clean) < 200:
                found.append(clean)
            if len(found) >= 3:
                break
    return found


def build_summary(text: str, title: str, tags: List[str], category: str) -> str:
    reqs = extract_requirements(text)
    deadline_m = re.search(
        r"(?:by|within|before)\s+(\d{1,2}\s+\w+\s+20\d{2}|\d+\s+days?)",
        text[:3000], re.IGNORECASE
    )
    deadline_str = f" Deadline: {deadline_m.group(1)}." if deadline_m else ""
    tag_str = ", ".join(tags[:3])
    if reqs:
        return f"{category} circular: '{title[:80]}'. Key requirement: {reqs[0][:150]}.{deadline_str} Related: {tag_str}."
    return f"{category} directive covering {tag_str} for regulated entities.{deadline_str}"


# ── Per-PDF processing ────────────────────────────────────────────────────────

def process_pdf(pdf_path: Path, output_dir: Path) -> Optional[Dict]:
    logger.info(f"Processing: {pdf_path.name}")
    text = extract_pdf_text(pdf_path)
    if not text or len(text) < 100:
        logger.warning(f"  Skipping: insufficient text ({len(text)} chars)")
        return None
    logger.info(f"  Extracted {len(text):,} characters")

    circular_id  = detect_circular_id(text, pdf_path.name)
    title        = extract_title(text, pdf_path.name)
    date_issued  = extract_date(text)
    category     = infer_category(text, title)
    tags         = extract_tags(text, title)
    severity     = determine_severity(text, tags)
    requirements = extract_requirements(text)
    ai_summary   = build_summary(text, title, tags, category)

    circular = {
        "id":          circular_id,
        "title":       title,
        "date_issued": date_issued,
        "category":    category,
        "severity":    severity,
        "status":      "draft",
        "content":     text[:600].replace("\n", " ").strip(),
        "ai_summary":  ai_summary,
        "tasks":       [],
        # RAG fields
        "full_text":      text[:5000],
        "tags":           tags,
        "applicability":  ["Banks", "NBFCs"],
        "requirements":   requirements,
        "source_file":    pdf_path.name,
    }

    safe_id   = re.sub(r"[^A-Za-z0-9_-]", "_", circular_id)
    out_path  = output_dir / f"{safe_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(circular, f, indent=2, ensure_ascii=False)

    logger.info(f"  Saved → {out_path.name}  (id={circular_id})")
    return circular


# ── FAISS index builder ───────────────────────────────────────────────────────

def build_faiss_index(processed_dir: Path) -> int:
    logger.info("\nBuilding FAISS index…")
    try:
        from data.processor import DataProcessor
        processor = DataProcessor(processed_dir=str(processed_dir))
        count = processor.load_processed_circulars()
        logger.info(f"FAISS index ready – {count} entries")
        return count
    except Exception as e:
        logger.warning(f"FAISS index build failed (non-fatal): {e}")
        return 0


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    raw_dir       = PROJECT_ROOT / "data" / "raw_circulars"
    processed_dir = PROJECT_ROOT / "data" / "processed_circulars"
    processed_dir.mkdir(exist_ok=True)

    # Use case-insensitive dedup so Windows doesn't yield .PDF and .pdf twice
    seen = set()
    pdf_files = []
    for p in sorted(raw_dir.iterdir()):
        if p.suffix.lower() == ".pdf" and p.name.lower() not in seen:
            seen.add(p.name.lower())
            pdf_files.append(p)
    if not pdf_files:
        logger.error(f"No PDFs found in {raw_dir}")
        sys.exit(1)

    logger.info(f"Found {len(pdf_files)} PDF(s) in {raw_dir}\n")

    results = []
    for pdf_path in pdf_files:
        circular = process_pdf(pdf_path, processed_dir)
        if circular:
            results.append(circular)

    logger.info(f"\nProcessed {len(results)}/{len(pdf_files)} PDFs successfully")

    faiss_count = build_faiss_index(processed_dir) if results else 0

    print(f"\n{'='*55}")
    print("Ingestion complete")
    print(f"  PDFs processed : {len(results)}/{len(pdf_files)}")
    print(f"  FAISS entries  : {faiss_count}")
    print(f"  JSON output    : {processed_dir}")
    print(f"{'='*55}\n")
    return results


if __name__ == "__main__":
    main()
