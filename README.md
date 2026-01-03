# Local RAG MCP Server

A fully local RAG-based knowledge base system with an MCP (Model Context Protocol) server. It enables document upload and search through AI assistants using MCP, while guaranteeing that all documents and embeddings remain local with zero external data exposure.

## 🌟 Features

- **📚 Document Management**: Streamlit interface for uploading and managing documents
- **🔗 MCP Protocol**: Exposes documents via Model Context Protocol for AI assistants
- **🔒 100% Local**: All data stays on your machine - no cloud uploads
- **📄 Multiple Formats**: Word (`.docx`), PowerPoint (`.pptx`), PDF (`.pdf`), Text (`.txt`)
- **⚡ Fast Search**: Vector embeddings with Chroma DB
- **🤖 AI Ready**: Works with GitHub Copilot and other MCP-compatible AI assistants

## 🚀 Setup

### Clone and Install

```bash
# Clone the project
git clone <repository-url>
cd local-rag-mcp

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```


## 📖 Usage

### Start the Streamlit UI

```bash
streamlit run ui/app.py
```
### Start the MCP Server

```bash
python mcp/server.py
```

### Upload Documents

1. Open the Streamlit UI at `http://localhost:8501`
2. Use the sidebar to upload `.docx`, `.pptx`, `.pdf`, or `.txt` files
3. Click "📥 Process & Add to Vector Store"
4. Documents are automatically chunked and embedded

### Configure with GitHub Copilot (VS Code)

Add this to your VS Code `settings.json` to integrate with GitHub Copilot:

```json
{
"servers": {
        "local-rag-knowledgebase-mcp": {
          "type": "stdio",
          "command": "<VENV_PATH>/Scripts/python.exe",
          "args": ["<PROJECT_ROOT>/mcp/server.py"],
          "cwd": "<PROJECT_ROOT>",
          "env": {
            "CHROMA_DB_PATH": "<PROJECT_ROOT>/data/chroma_db",
            "EMBEDDING_MODEL": "all-MiniLM-L6-v2"
          }
        }
      }
}
```


## 🏗️ Project Structure

```
local-rag-mcp/
├── mcp/server.py              # FastMCP server for protocol access
├── ui/app.py                  # Streamlit document management interface
├── backend/
│   ├── document_processor/    # Load and chunk documents
│   └── vector_store/          # Chroma DB + HuggingFace embeddings
├── config/settings.py         # Configuration
├── data/
│   ├── chroma_db/             # Local vector database
│   └── uploaded_docs/         # Document storage
└── requirements.txt           # Dependencies
```

## 📝 Notes

- **First Run**: Will download embedding model (`all-MiniLM-L6-v2`)
- **Storage**: Documents stored in `data/uploaded_docs/`, embeddings in `data/chroma_db/`
- **Privacy**: Everything runs locally, no data leaves your machine
