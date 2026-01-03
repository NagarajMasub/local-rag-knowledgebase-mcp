from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import settings


class DocumentProcessor:
    """Process documents by chunking them into smaller pieces"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        chunked_docs = []
        
        for doc in documents:
            chunks = self.text_splitter.split_text(doc.page_content)
            
            for chunk_idx, chunk in enumerate(chunks):
                metadata = doc.metadata.copy()
                metadata["chunk_index"] = chunk_idx
                
                chunked_docs.append(
                    Document(
                        page_content=chunk,
                        metadata=metadata
                    )
                )
        
        return chunked_docs
