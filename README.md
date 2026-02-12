# 🤖 Multi-Modal RAG System

An intelligent document Q&A system that combines **text extraction**, **image understanding**, and **vector search** to answer questions from PDF documents.

## 🌟 Features

- **📄 PDF Processing**: Extracts text and images from any PDF
- **🖼️ Image Understanding**: Uses BLIP AI to caption images
- **🔍 Semantic Search**: Vector-based similarity search
- **🤖 Intelligent Answers**: Powered by Groq's Llama 3.3 70B
- **📚 Multi-Document**: Query across multiple PDFs simultaneously
- **💬 Interactive Chat**: User-friendly web interface

## 🚀 Live Demo

Deploy this app for free on multiple platforms!

### Option 1: Streamlit Cloud (Recommended)

1. Push this code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Deploy!

### Option 2: Hugging Face Spaces

1. Create account at [huggingface.co](https://huggingface.co)
2. Create new Space (Streamlit)
3. Upload files
4. Auto-deploys!

### Option 3: Render

1. Create account at [render.com](https://render.com)
2. New Web Service
3. Connect repo
4. Deploy!

## 🛠️ Local Setup

### Prerequisites

- Python 3.9+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd multimodal-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📖 How to Use

1. **Get API Key**: Sign up at [console.groq.com](https://console.groq.com) for a free API key
2. **Upload PDFs**: Upload one or more PDF documents
3. **Process**: Click "Process Documents" to create the knowledge base
4. **Ask Questions**: Type your questions in the chat interface
5. **Get Answers**: Receive AI-generated answers with source citations

## 🔧 Technical Stack

- **Frontend**: Streamlit
- **LLM**: Groq (Llama 3.3 70B)
- **Embeddings**: all-MiniLM-L6-v2 (Sentence Transformers)
- **Vector DB**: ChromaDB
- **Vision**: BLIP (Salesforce)
- **PDF Processing**: pypdf, Pillow
- **Chunking**: LangChain

## 📊 Architecture

```
PDF Upload → Text Extraction → Chunking → Embedding
              ↓
         Image Extraction → BLIP Captioning → Embedding
                                ↓
                         Vector Database (ChromaDB)
                                ↓
                    User Query → Semantic Search
                                ↓
                    Retrieved Context → Groq LLM
                                ↓
                         AI-Generated Answer
```

## 🎯 Use Cases

- **Research**: Query across multiple academic papers
- **Documentation**: Search technical documentation
- **Legal**: Analyze contracts and legal documents
- **Education**: Study from textbooks and lecture notes
- **Business**: Extract insights from reports

## 🔐 Environment Variables

Create a `.streamlit/secrets.toml` file for deployment:

```toml
GROQ_API_KEY = "your_api_key_here"
```

## 📝 Example Questions

- "What is deep learning?"
- "Explain neural networks with examples"
- "Show me diagrams about machine learning"
- "Summarize the key points from document X"
- "Compare concept A and concept B"

## 🚧 Limitations

- Free Groq tier has rate limits
- Large PDFs take longer to process
- Image extraction depends on PDF structure
- First-time model loading takes 1-2 minutes

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this for your projects!

## 🙏 Acknowledgments

- Groq for fast LLM inference
- Salesforce for BLIP vision model
- Streamlit for the web framework
- Anthropic for Claude (used in development)

## 📧 Contact

Created for internship applications - showcasing ML/AI engineering skills!

---

**⭐ Star this repo if you found it useful!**
