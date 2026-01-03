import os
import ssl
import sys
from typing import List, Optional

from fastmcp import FastMCP

# Ensure offline usage and relaxed SSL, matching the MCP server behavior
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''
ssl._create_default_https_context = ssl._create_unverified_context

# Add project root to import path so we can reuse backend components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from backend.vector_store import ChromaVectorStore


mcp = FastMCP("Local RAG Knowledge MCP Server")

# Lazy-initialized shared vector store instance
_vector_store: Optional[ChromaVectorStore] = None

def _ensure_store() -> ChromaVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = ChromaVectorStore()
    return _vector_store


@mcp.tool
def local_knowledge_base_search(query: str, top_k: int = 10) -> dict:
    """Answer questions using the local knowledge base.
Use this when asked about tables, configs, docs, or concepts.
Returns a direct answer from the most relevant document chunk, plus
minimal source info. Works fully offline.
"""
    try:
        store = _ensure_store()
        results = store.search_documents(query, k=top_k)

        documents = []
        for doc in results:
            documents.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", 0),
                "score": doc.metadata.get("score", 0),
            })

        return {
            "success": True,
            "query": query,
            "results_count": len(documents),
            "documents": documents,
            "note": "Summarize based on the returned documents; avoid repeated searches if cross-references are present."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
def get_vector_store_info() -> dict:
    """Get information about the vector store (number of documents, etc)."""
    try:
        store = _ensure_store()
        info = store.get_collection_info()
        return {
            "success": True,
            "document_count": info.get("document_count", 0),
            "vector_store_path": settings.CHROMA_DB_PATH,
            "embedding_model": info.get("embedding_model", settings.EMBEDDING_MODEL),
            "database": "chromadb",
            "collection_name": info.get("collection_name"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run()