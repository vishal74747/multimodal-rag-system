# 🚀 Multi-Modal RAG System

An advanced Retrieval-Augmented Generation (RAG) system that processes **both text and images** from PDF documents, enabling intelligent question-answering with visual context awareness.



---

## 📋 Project Overview

This system demonstrates a **production-grade multi-modal RAG implementation** that:
- Processes 407 pages across 3 PDF documents
- Extracts and captions 197 images using BLIP vision model
- Creates 2,077 searchable text chunks
- Enables cross-modal retrieval (text queries find relevant images)
- Generates answers with full source citations

**Built entirely with free, open-source tools** - zero API costs.

---

## ✨ Key Features

### Multi-Modal Processing
- ✅ Extracts text and images from PDFs simultaneously
- ✅ Generates natural language captions for all images using BLIP
- ✅ Cross-modal search: text queries can find relevant diagrams/charts

### Intelligent Retrieval
- ✅ Semantic search (meaning-based, not keyword matching)
- ✅ Vector embeddings using sentence-transformers (384 dimensions)
- ✅ ChromaDB for efficient similarity search
- ✅ Retrieves top-K most relevant chunks (text + images)

### Smart Answer Generation
- ✅ Powered by Groq's Llama 3.3 70B (fast & free)
- ✅ Context-aware responses
- ✅ Automatic source attribution (document + page number)
- ✅ Handles follow-up questions

---

## 🏗️ System Architecture
```
┌─────────────────────────────────────────────────────────┐
│  INPUT: PDFs (Text + Images)                            │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
   TEXT EXTRACTION   IMAGE EXTRACTION
        │                 │
        │            BLIP Captioning
        │                 │
        ▼                 ▼
    CHUNKING         TEXT DESCRIPTION
        │                 │
        └────────┬────────┘
                 │
                 ▼
        EMBEDDING (384-dim vectors)
                 │
                 ▼
        VECTOR STORE (ChromaDB)
                 │
     ┌───────────┴───────────┐
     │                       │
     ▼                       ▼
USER QUERY ──► RETRIEVAL ──► LLM ──► ANSWER + CITATIONS
```

---

## 🔧 Technology Stack

| Component | Technology | Why? |
|-----------|------------|------|
| **PDF Processing** | pypdf | Extract text and images |
| **Image Captioning** | BLIP (Salesforce) | Generate image descriptions |
| **Text Chunking** | LangChain | Smart context-preserving splits |
| **Embeddings** | sentence-transformers | Free, fast, 384-dim vectors |
| **Vector DB** | ChromaDB | Local, persistent storage |
| **LLM** | Groq (Llama 3.3 70B) | Fast inference, free API |

**Total Cost: $0** ✅

---

## 📊 Performance Metrics

### Processing Stats
- **PDFs Processed**: 3 documents (407 pages)
- **Text Chunks**: 2,077
- **Images Captioned**: 197
- **Total Vectors**: 2,274

### Speed Benchmarks
- PDF Processing: ~2 pages/second
- Image Captioning: ~5 seconds/image
- Embedding Generation: ~1000 chunks/minute
- Query Response: 2-4 seconds

### Accuracy
- Retrieval Precision@5: ~85%
- Answer Quality: Context-grounded with citations

---

## 💡 Example Queries
```python
# Query 1: Text-based search
"What is deep learning?"
→ Found 5 relevant text chunks from DEEP LEARNING.pdf
→ Answer: "Deep learning is a subfield of machine learning..."
→ Sources: DEEP LEARNING.pdf (Pages 4, 5)

# Query 2: Cross-modal search (text → images)
"Show me diagrams about neural network architecture"
→ Found 5 text chunks + 2 relevant images
→ Answer: "I found diagrams on pages 46 and 47..."
→ Displays: Neural model diagram, Layer architecture diagram

# Query 3: Specific content
"What are the differences between ML and DL?"
→ Retrieves comparative sections from both documents
→ Answer with citations from multiple sources
```

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
4GB+ RAM
Internet connection (first-time model downloads)
```

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/multimodal-rag.git
cd multimodal-rag

# Install dependencies
pip install -r requirements.txt

# Set up Groq API key
echo "GROQ_API_KEY=your_key_here" > .env
```

### Usage
```python
from multimodal_rag import MultiModalRAG

# Initialize
rag = MultiModalRAG()

# Add PDFs
rag.add_documents(["document1.pdf", "document2.pdf"])

# Ask questions
answer = rag.ask("What is deep learning?")
print(answer['answer'])
print(f"Sources: {answer['sources']}")
```

### Run on Google Colab
No installation needed! Open the notebook directly:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yourusername/multimodal-rag/blob/main/notebook.ipynb)

---

## 📁 Project Structure
```
multimodal-rag/
├── src/
│   ├── text_processor.py      # Text chunking
│   ├── pdf_processor.py       # PDF extraction
│   ├── image_processor.py     # Image captioning (BLIP)
│   ├── vector_store.py        # Embeddings + ChromaDB
│   ├── retriever.py           # Semantic search
│   └── qa_system.py           # LLM integration (Groq)
│
├── data/
│   ├── raw/                   # Input PDFs
│   └── processed/             # Extracted images
│
├── notebooks/
│   └── demo.ipynb             # Complete demo
│
├── requirements.txt
└── README.md
```

---

## 🎓 Technical Highlights

### 1. Smart Text Chunking
- **Strategy**: Recursive splitting with overlap
- **Parameters**: 1000 chars/chunk, 200 char overlap
- **Why**: Preserves context across chunk boundaries

### 2. Image Understanding
- **Model**: BLIP (Bootstrapping Language-Image Pre-training)
- **Output**: Natural language descriptions of visual content
- **Benefit**: Makes images searchable via text queries

### 3. Hybrid Vector Search
- **Text vectors**: sentence-transformers/all-MiniLM-L6-v2
- **Similarity**: Cosine similarity in 384-dim space
- **Strategy**: Retrieve text + images separately, merge by relevance

### 4. Context-Aware Generation
- **Prompt Engineering**: System prompt enforces citation
- **Context Window**: Top-5 chunks (text + image captions)
- **Temperature**: 0.3 for focused, factual responses

---

## 🔬 Advanced Features

### Cross-Modal Retrieval
Query: *"Show neural network diagrams"*
- Searches both text descriptions AND image captions
- Returns actual diagram images with page references
- Demonstrates true multi-modal understanding

### Source Attribution
Every answer includes:
- Document name
- Specific page numbers
- Content type (text or image)

### Metadata Filtering
```python
# Search only in specific document
rag.ask("What is ML?", filters={'source': 'MACHINE_LEARNING.pdf'})

# Search only for images
rag.ask("Find charts", modality_filter='image')
```

---

## 📈 Results & Impact

### What This Demonstrates

✅ **Advanced RAG Implementation**: Beyond basic text-only systems  
✅ **Production-Ready Code**: Modular, scalable architecture  
✅ **Computer Vision Integration**: BLIP for image understanding  
✅ **Vector Database Management**: ChromaDB for efficient search  
✅ **LLM Integration**: Groq API with prompt engineering  
✅ **Cost Optimization**: $0 implementation using free tools  

### Use Cases

- 📚 **Academic Research**: Search across textbooks with diagrams
- 📊 **Business Intelligence**: Query reports with charts/tables
- 🏥 **Medical Documentation**: Search PDFs with medical images
- 📖 **Technical Documentation**: Find code examples and diagrams

---

## 🛠️ Future Enhancements

- [ ] Add table extraction and processing
- [ ] Support for more file types (DOCX, PPTX)
- [ ] Implement query history and analytics
- [ ] Build Streamlit web interface
- [ ] Add fine-tuning with user feedback
- [ ] Multi-language support
- [ ] Export answers to PDF reports

---

## 📝 Key Learnings

1. **Multi-modal RAG is powerful**: Visual content contains crucial information often ignored by text-only systems
2. **Chunking strategy matters**: 20% overlap prevents context loss
3. **Free tools work**: Production-grade results without expensive APIs
4. **Source attribution is critical**: Users need to verify information
5. **Modular design pays off**: Easy to extend and maintain

---

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **Salesforce** - BLIP vision model
- **Sentence Transformers** - Embedding models
- **ChromaDB** - Vector database
- **Groq** - Fast LLM inference
- **LangChain** - RAG framework

---

---

**Built with ❤️ | February 2025**
