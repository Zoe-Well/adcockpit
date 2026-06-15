"""Local JSON file persistence — zero dependency, human-readable.

Data files stored in: backend/data/
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read(filename: str, default: list | dict = None) -> list | dict:
    """Read JSON file, return default if missing or corrupt."""
    path = DATA_DIR / filename
    if not path.exists():
        return default if default is not None else []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return default if default is not None else []


def _write(filename: str, data):
    """Write data to JSON file atomically."""
    path = DATA_DIR / filename
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


# ====== Campaign Plan Storage ======

def save_plans(platform: str, plans: List[Dict]):
    """Save platform campaign data."""
    _write(f"plans_{platform}.json", plans)


def load_plans(platform: str) -> List[Dict]:
    """Load platform campaign data."""
    return _read(f"plans_{platform}.json", [])


# ====== Optimization History (RAG records) ======

def save_optimization_record(record: Dict):
    """Append an optimization record to history."""
    history = _read("optimization_history.json", [])
    record["saved_at"] = datetime.now().isoformat()
    history.append(record)
    _write("optimization_history.json", history)


def get_optimization_history(limit: int = 20) -> List[Dict]:
    """Get recent optimization records, newest first."""
    history = _read("optimization_history.json", [])
    return list(reversed(history))[:limit]


def search_optimization_history(query: str) -> List[Dict]:
    """Simple text search in optimization history."""
    history = _read("optimization_history.json", [])
    results = []
    for r in reversed(history):
        text = json.dumps(r, ensure_ascii=False).lower()
        if any(kw in text for kw in query.lower().split()):
            results.append(r)
    return results[:5]


# ====== Content Production Records ======

def save_content_record(record: Dict):
    """Save a content production record."""
    records = _read("content_records.json", [])
    record["saved_at"] = datetime.now().isoformat()
    records.append(record)
    _write("content_records.json", records)


def get_content_records(limit: int = 10) -> List[Dict]:
    """Get recent content production records."""
    records = _read("content_records.json", [])
    return list(reversed(records))[:limit]


# ====== Feishu Document URLs ======

def save_feishu_url(doc_type: str, url: str, title: str = ""):
    """Record a Feishu document URL for reference."""
    urls = _read("feishu_urls.json", [])
    urls.append({"type": doc_type, "url": url, "title": title, "created_at": datetime.now().isoformat()})
    _write("feishu_urls.json", urls)
