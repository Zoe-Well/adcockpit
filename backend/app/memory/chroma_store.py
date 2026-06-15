"""Chroma vector store — RAG long-term memory.

Stores historical optimization records for retrieval-augmented generation.
Fallback: in-memory list if Chroma not available.
"""
import json
from typing import List, Dict, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.utils import embedding_functions
    _client = chromadb.Client(chromadb.Settings(anonymized_telemetry=False, is_persistent=False))
    _collection = _client.get_or_create_collection(
        name="optimization_history",
        metadata={"hnsw:space": "cosine"}
    )
    _CHROMA_OK = True
except Exception:
    _CHROMA_OK = False

# Fallback in-memory store
_fallback_records: List[Dict] = []


def add_record(plan_id: str, params: dict, changes: list, roi_before: float,
               roi_after: float, platform: str = ""):
    """Add an optimization record to the vector store."""
    doc = json.dumps({
        "plan_id": plan_id, "params": params, "changes": changes,
        "roi_before": roi_before, "roi_after": roi_after,
        "platform": platform, "timestamp": datetime.now().isoformat(),
    }, ensure_ascii=False)

    if _CHROMA_OK:
        _collection.add(
            documents=[doc],
            metadatas=[{"plan_id": plan_id, "roi_before": roi_before, "roi_after": roi_after}],
            ids=[f"{plan_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"],
        )
    else:
        _fallback_records.append(json.loads(doc))
        # Also persist to local JSON
        try:
            from backend.app.memory.local_store import save_optimization_record
            save_optimization_record(json.loads(doc))
        except Exception:
            pass


def search_similar(query: str, k: int = 3) -> List[Dict]:
    """Search for similar historical optimization records."""
    if _CHROMA_OK:
        results = _collection.query(query_texts=[query], n_results=k)
        docs = results.get("documents", [[]])[0]
        return [json.loads(d) for d in docs]
    else:
        # Simple keyword match fallback
        matches = []
        for r in _fallback_records:
            if any(kw in json.dumps(r, ensure_ascii=False) for kw in query.split()):
                matches.append(r)
        return matches[:k]


def get_recent(k: int = 5) -> List[Dict]:
    """Get most recent records."""
    if _CHROMA_OK:
        results = _collection.get(limit=k)
        return [json.loads(d) for d in results.get("documents", [])]
    return _fallback_records[-k:]
