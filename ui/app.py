import os
import sys
import ssl

# Set BEFORE any HuggingFace imports
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''
ssl._create_default_https_context = ssl._create_unverified_context

import streamlit as st
from pathlib import Path
from typing import List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from backend.document_processor import DocumentLoader, DocumentProcessor
from backend.vector_store import ChromaVectorStore

# Configure Streamlit
st.set_page_config(
    page_title="Local KnowledgeBase Document Manager - MCP",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FFB81C;
        margin-bottom: 1rem;
    }
    .source-doc {
        background-color: #f0f0f0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "vector_store" not in st.session_state:
    with st.spinner("Initializing vector store..."):
        st.session_state.vector_store = ChromaVectorStore()

if "vector_store_info" not in st.session_state:
    st.session_state.vector_store_info = None

# Sidebar
with st.sidebar:
    st.markdown("# ⚙️ Settings & Controls")
    
    st.markdown("### 📁 Document Management")
    
    # Show vector store info
    if st.button("📊 Refresh Vector Store Info", use_container_width=True):
        st.session_state.vector_store_info = st.session_state.vector_store.get_collection_info()
    
    if st.session_state.vector_store_info:
        st.metric("Documents in Store", st.session_state.vector_store_info.get("document_count", 0))
        st.caption(f"Model: {st.session_state.vector_store_info.get('embedding_model')}")
    
    # File upload section
    st.markdown("### ⬆️ Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose Word/PowerPoint/PDF/Text files to add to knowledge base",
        type=["docx", "pptx", "pdf", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("📥 Process & Add to Vector Store", use_container_width=True):
            with st.spinner("Processing documents..."):
                try:
                    # Save uploaded files
                    saved_files = []
                    for uploaded_file in uploaded_files:
                        file_path = Path(settings.UPLOAD_DOCS_PATH) / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        saved_files.append(str(file_path))
                    
                    # Load and process documents
                    all_documents = []
                    for file_path in saved_files:
                        docs = DocumentLoader.load_document(file_path)
                        all_documents.extend(docs)
                    
                    # Process (chunk) documents
                    processor = DocumentProcessor()
                    processed_docs = processor.process_documents(all_documents)
                    
                    # Add to vector store
                    doc_ids = st.session_state.vector_store.add_documents(processed_docs)
                    
                    st.success(f"✅ Added {len(doc_ids)} document chunks to the knowledge base!")
                    
                    # Refresh info
                    st.session_state.vector_store_info = st.session_state.vector_store.get_collection_info()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error processing documents: {str(e)}")
    
    # Clear vector store
    st.markdown("### 🔥 Danger Zone")
    if st.button("🗑️ Clear All Documents", use_container_width=True):
        if st.session_state.get("confirm_clear"):
            st.session_state.vector_store.delete_collection()
            # Refresh info to reflect empty collection
            st.session_state.vector_store_info = st.session_state.vector_store.get_collection_info()
            st.success("✅ Vector store cleared!")
            st.session_state.confirm_clear = False
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.warning("Click again to confirm")
    else:
        st.session_state.confirm_clear = False
    
    # System info
    st.markdown("### ℹ️ System Info")
    st.caption(f"📍 Mode: {'🔒 Confidential' if settings.CONFIDENTIAL_MODE else '🌐 Open'}")
    st.caption(f" Chroma DB: {settings.CHROMA_DB_PATH}")

# Main content
col1, col2 = st.columns([0.1, 0.9])
with col2:
    st.markdown('<p class="main-header">📚 Document Management - MCP Server</p>', unsafe_allow_html=True)

st.markdown("---")

# MCP Status
st.markdown("### 🔗 MCP Server Status")
st.info("🚀 MCP Server is running independently. Use document upload above to manage the knowledge base.")

# Document Statistics
if st.session_state.vector_store_info:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents", st.session_state.vector_store_info.get("document_count", 0))
    with col2:
        st.metric("Collection", st.session_state.vector_store_info.get("collection_name", "N/A"))
    with col3:
        st.metric("Model", st.session_state.vector_store_info.get("embedding_model", "N/A"))

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8rem;'>
    🔒 <strong>Local Only</strong> - Document management for MCP Server.
    All data is stored locally and available via MCP protocol.
    </div>
""", unsafe_allow_html=True)
