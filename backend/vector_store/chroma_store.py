from typing import List
from pathlib import Path
import os
import ssl

# MUST be set BEFORE importing anything from transformers/sentence_transformers
# os.environ['HF_HUB_OFFLINE'] = '1'  # Force offline mode - use only local cached models
# os.environ['TRANSFORMERS_OFFLINE'] = '1'  # Force offline for transformers

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from config.settings import settings


class ChromaVectorStore:
    """Manages Chroma vector database for document storage and retrieval"""
    
    def __init__(self):
        """Initialize embeddings and vector store"""
        # Use HuggingFace embeddings from locally saved model files
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        
        self.vector_store = None
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize or load existing Chroma vector store"""
        self.vector_store = Chroma(
            collection_name=settings.VECTOR_STORE_COLLECTION,
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_DB_PATH,
            client_settings=None  # Use default settings for local Chroma
        )
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store"""
        if not documents:
            print("No documents to add")
            return []
        
        try:
            doc_ids = self.vector_store.add_documents(
                documents=documents,
                ids=None  # Let Chroma generate IDs
            )
            print(f"Successfully added {len(doc_ids)} documents to vector store")
            self.vector_store.persist()  # Persist to disk
            return doc_ids
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            raise
    
    def search_documents(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            raise
    
    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """Search for similar documents with similarity scores"""
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            print(f"Error searching documents with scores: {e}")
            raise
    
    def get_retriever(self, k: int = 5):
        """Get a LangChain retriever from the vector store"""
        return self.vector_store.as_retriever(search_kwargs={"k": k})
    
    def delete_collection(self):
        """Delete the entire collection"""
        try:
            # Prefer deleting the collection via the client to ensure a clean reset
            collection_name = self.vector_store._collection.name
            client = self.vector_store._client

            # Drop the collection entirely
            client.delete_collection(name=collection_name)

            # Recreate an empty collection using the same settings
            self._initialize_store()
            print("Collection deleted and reinitialized successfully")
        except Exception as e:
            print(f"Error deleting collection: {e}")
    
    def get_collection_info(self) -> dict:
        """Get information about the current collection"""
        try:
            collection = self.vector_store._collection
            count = collection.count()
            return {
                "collection_name": settings.VECTOR_STORE_COLLECTION,
                "document_count": count,
                "embedding_model": settings.EMBEDDING_MODEL
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {}
