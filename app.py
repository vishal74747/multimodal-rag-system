import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple
import time

# Core libraries
from PIL import Image
import pypdf
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

# Page config
st.set_page_config(
    page_title="Multi-Modal RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(120deg, #1E88E5, #7C4DFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
    }
    .answer-box {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== PROCESSING CLASSES ====================

class TextProcessor:
    """Process text into chunks for embedding."""
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def process(self, text: str, source: str, page: int = None) -> List[Dict]:
        chunks = self.splitter.split_text(text)
        processed = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'content': chunk,
                'modality': 'text',
                'source': source,
                'chunk_index': i,
                'total_chunks': len(chunks)
            }
            if page is not None:
                chunk_data['page'] = page
            processed.append(chunk_data)
        return processed


class PDFProcessor:
    """Extract text and images from PDFs."""
    def __init__(self, text_processor: TextProcessor):
        self.text_processor = text_processor
    
    def extract_from_pdf(self, pdf_file, temp_dir: str) -> Tuple[List[Dict], List[Dict]]:
        """Extract text chunks and images from PDF."""
        all_text_chunks = []
        all_images = []
        
        reader = pypdf.PdfReader(pdf_file)
        total_pages = len(reader.pages)
        
        for page_num in range(total_pages):
            page = reader.pages[page_num]
            
            # Extract text
            text = page.extract_text()
            if text.strip():
                chunks = self.text_processor.process(
                    text=text,
                    source=pdf_file.name,
                    page=page_num + 1
                )
                all_text_chunks.extend(chunks)
            
            # Extract images
            if '/XObject' in page['/Resources']:
                xObject = page['/Resources']['/XObject'].get_object()
                
                for obj_name in xObject:
                    obj = xObject[obj_name]
                    
                    if obj['/Subtype'] == '/Image':
                        try:
                            # Get image data
                            size = (obj['/Width'], obj['/Height'])
                            data = obj.get_data()
                            
                            if obj['/ColorSpace'] == '/DeviceRGB':
                                mode = "RGB"
                            else:
                                mode = "P"
                            
                            # Create image
                            img = Image.frombytes(mode, size, data)
                            
                            # Save image
                            img_filename = f"{pdf_file.name}_page{page_num+1}_img{len(all_images)}.png"
                            img_path = os.path.join(temp_dir, img_filename)
                            img.save(img_path)
                            
                            all_images.append({
                                'image_path': img_path,
                                'source': pdf_file.name,
                                'page': page_num + 1,
                                'modality': 'image'
                            })
                        except:
                            continue
        
        return all_text_chunks, all_images


class ImageProcessor:
    """Generate captions for images using BLIP."""
    def __init__(self, processor, model):
        self.processor = processor
        self.model = model
    
    def generate_caption(self, image_path: str) -> str:
        """Generate caption for a single image."""
        try:
            image = Image.open(image_path).convert('RGB')
            inputs = self.processor(image, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=100,
                    num_beams=5,
                    early_stopping=True
                )
            
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def process_batch(self, image_metadata: List[Dict]) -> List[Dict]:
        """Process multiple images and add captions."""
        captioned = []
        for img_data in image_metadata:
            caption = self.generate_caption(img_data['image_path'])
            img_data['content'] = caption
            img_data['caption'] = caption
            captioned.append(img_data)
        return captioned


class VectorStore:
    """Manage vector embeddings and search."""
    def __init__(self, embedding_model, collection_name: str = "multimodal_rag"):
        self.embedding_model = embedding_model
        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Create unique collection
        timestamp = int(time.time())
        self.collection_name = f"{collection_name}_{timestamp}"
        self.collection = self.client.create_collection(name=self.collection_name)
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to vector store."""
        embeddings = []
        docs = []
        metadatas = []
        ids = []
        
        for i, doc in enumerate(documents):
            embedding = self.embedding_model.encode(doc['content']).tolist()
            embeddings.append(embedding)
            docs.append(doc['content'])
            
            metadata = {
                'modality': doc['modality'],
                'source': doc['source'],
                'page': str(doc.get('page', 'N/A'))
            }
            if 'image_path' in doc:
                metadata['image_path'] = doc['image_path']
            
            metadatas.append(metadata)
            ids.append(f"doc_{i}")
        
        self.collection.add(
            embeddings=embeddings,
            documents=docs,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 5, modality_filter: str = None):
        """Search for relevant documents."""
        query_embedding = self.embedding_model.encode(query).tolist()
        
        where_filter = None
        if modality_filter:
            where_filter = {"modality": modality_filter}
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )
        
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': 1 - results['distances'][0][i]
            })
        
        return formatted_results


class Retriever:
    """Retrieve relevant documents from vector store."""
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    def retrieve(self, query: str, n_results: int = 5, include_images: bool = True):
        """Retrieve mixed text and image results."""
        # Get text results
        text_results = self.vector_store.search(
            query=query,
            n_results=n_results,
            modality_filter='text'
        )
        
        # Get image results if requested
        if include_images:
            try:
                image_results = self.vector_store.search(
                    query=query,
                    n_results=max(2, n_results // 3),
                    modality_filter='image'
                )
                
                # Combine and sort
                results = text_results + image_results
                results.sort(key=lambda x: x['score'], reverse=True)
                results = results[:n_results]
            except:
                # If no images, just return text
                results = text_results
        else:
            results = text_results
        
        return results
    
    def retrieve_with_context(self, query: str, n_results: int = 5) -> Dict:
        """Retrieve and format context for LLM."""
        results = self.retrieve(query, n_results=n_results)
        
        context_parts = []
        sources = set()
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            modality = metadata['modality']
            source = metadata['source']
            page = metadata['page']
            content = result['content']
            
            sources.add(f"{source} (Page {page})")
            
            if modality == 'text':
                context_parts.append(
                    f"[Source {i}: {source}, Page {page}]\n{content}\n"
                )
            elif modality == 'image':
                context_parts.append(
                    f"[Image {i}: {source}, Page {page}]\n"
                    f"Image description: {content}\n"
                )
        
        return {
            'query': query,
            'results': results,
            'context_text': "\n".join(context_parts),
            'sources': sorted(list(sources)),
            'num_text': sum(1 for r in results if r['metadata']['modality'] == 'text'),
            'num_images': sum(1 for r in results if r['metadata']['modality'] == 'image')
        }


class QASystem:
    """Question answering with Groq LLM."""
    def __init__(self, retriever: Retriever, groq_api_key: str):
        self.retriever = retriever
        self.groq_client = Groq(api_key=groq_api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def answer(self, query: str, n_results: int = 5) -> Dict:
        """Generate answer for query."""
        context = self.retriever.retrieve_with_context(query, n_results=n_results)
        
        prompt = f"""You are a helpful AI assistant answering questions based on provided context from PDF documents.

CONTEXT:
{context['context_text']}

QUESTION: {query}

INSTRUCTIONS:
1. Answer using ONLY the information from the context above
2. If context contains relevant images, mention what they show
3. Cite sources by mentioning document name and page number
4. If you cannot answer from context, say "I don't have enough information in the provided documents"
5. Be specific and concise
6. If multiple documents discuss the topic, synthesize the information

ANSWER:"""
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Error generating answer: {str(e)}"
        
        return {
            'answer': answer,
            'sources': context['sources'],
            'num_text': context['num_text'],
            'num_images': context['num_images'],
            'retrieved_chunks': context['results']
        }


# ==================== CACHED MODELS ====================

@st.cache_resource
def load_vision_model():
    """Load BLIP vision model (cached)."""
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model


@st.cache_resource
def load_embedding_model():
    """Load sentence embedding model (cached)."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model


# ==================== SESSION STATE ====================

if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'qa_system' not in st.session_state:
    st.session_state.qa_system = None
if 'documents_processed' not in st.session_state:
    st.session_state.documents_processed = False
if 'stats' not in st.session_state:
    st.session_state.stats = {}


# ==================== MAIN UI ====================

st.markdown('<div class="main-header">🤖 Multi-Modal RAG System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Document Q&A with Vision & Vector Search</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key
    groq_api_key = st.text_input(
        "🔑 Groq API Key",
        type="password",
        help="Get your free API key from console.groq.com",
        placeholder="gsk_..."
    )
    
    st.divider()
    
    # File Upload
    st.subheader("📄 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF documents to create your knowledge base"
    )
    
    # Processing Options
    with st.expander("🎛️ Advanced Options"):
        chunk_size = st.slider("Chunk Size", 500, 2000, 1000, 100)
        chunk_overlap = st.slider("Chunk Overlap", 0, 500, 200, 50)
        include_images = st.checkbox("Extract & Caption Images", value=True)
    
    st.divider()
    
    # Process Button
    process_disabled = not (uploaded_files and groq_api_key)
    
    if st.button("🚀 Process Documents", type="primary", disabled=process_disabled, use_container_width=True):
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Initialize processors
            text_processor = TextProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            pdf_processor = PDFProcessor(text_processor)
            embedding_model = load_embedding_model()
            
            # Process PDFs
            all_text_chunks = []
            all_images = []
            
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            for idx, pdf_file in enumerate(uploaded_files):
                progress_text.text(f"Processing: {pdf_file.name}")
                
                text_chunks, images = pdf_processor.extract_from_pdf(pdf_file, temp_dir)
                all_text_chunks.extend(text_chunks)
                all_images.extend(images)
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            progress_text.text("Processing complete!")
            
            # Process images if any
            all_documents = all_text_chunks.copy()
            
            if include_images and all_images:
                progress_text.text("Captioning images...")
                vision_processor, vision_model = load_vision_model()
                image_processor = ImageProcessor(vision_processor, vision_model)
                
                captioned_images = image_processor.process_batch(all_images)
                all_documents.extend(captioned_images)
                progress_text.text(f"Captioned {len(captioned_images)} images!")
            
            # Create vector store
            progress_text.text("Creating embeddings...")
            vector_store = VectorStore(embedding_model)
            vector_store.add_documents(all_documents)
            
            # Create retriever and QA system
            retriever = Retriever(vector_store)
            qa_system = QASystem(retriever, groq_api_key)
            
            # Save to session state
            st.session_state.vector_store = vector_store
            st.session_state.qa_system = qa_system
            st.session_state.documents_processed = True
            st.session_state.stats = {
                'total_docs': len(all_documents),
                'text_chunks': len(all_text_chunks),
                'images': len(all_images) if include_images else 0,
                'pdf_count': len(uploaded_files)
            }
            
            progress_bar.empty()
            progress_text.empty()
            
            st.success("✅ Documents processed successfully!")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Error processing documents: {str(e)}")
    
    # Display stats if processed
    if st.session_state.documents_processed:
        st.divider()
        st.subheader("📊 Statistics")
        stats = st.session_state.stats
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📚 PDFs", stats['pdf_count'])
            st.metric("📝 Text Chunks", stats['text_chunks'])
        with col2:
            st.metric("🖼️ Images", stats['images'])
            st.metric("💾 Total Items", stats['total_docs'])
    
    st.divider()
    
    # Info section
    with st.expander("ℹ️ About"):
        st.markdown("""
        **Multi-Modal RAG System**
        
        This application uses:
        - 🔍 **Vector Search**: Semantic similarity search
        - 🖼️ **Vision AI**: BLIP image captioning
        - 🤖 **LLM**: Groq (Llama 3.3 70B)
        - 📚 **Embeddings**: all-MiniLM-L6-v2
        
        **How to use:**
        1. Enter your Groq API key
        2. Upload PDF documents
        3. Click "Process Documents"
        4. Ask questions in the chat!
        """)


# Main Chat Interface
if st.session_state.documents_processed:
    st.header("💬 Ask Questions")
    
    # Query input
    query = st.text_input(
        "Ask a question about your documents:",
        placeholder="e.g., What is deep learning? or Show me diagrams about neural networks",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        n_results = st.selectbox("Results", [3, 5, 7, 10], index=1)
    
    if st.button("🔍 Search & Answer", type="primary", use_container_width=True):
        if query:
            with st.spinner("Searching and generating answer..."):
                result = st.session_state.qa_system.answer(query, n_results=n_results)
                
                # Display answer
                st.markdown("### 💡 Answer")
                st.markdown(f'<div class="answer-box">{result["answer"]}</div>', unsafe_allow_html=True)
                
                # Display sources
                st.markdown("### 📚 Sources")
                for source in result['sources']:
                    st.markdown(f'<div class="source-box">📄 {source}</div>', unsafe_allow_html=True)
                
                # Display retrieval stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📝 Text Chunks", result['num_text'])
                with col2:
                    st.metric("🖼️ Images", result['num_images'])
                with col3:
                    st.metric("📊 Total Retrieved", result['num_text'] + result['num_images'])
                
                # Show retrieved chunks (expandable)
                with st.expander("🔍 View Retrieved Content"):
                    for i, chunk in enumerate(result['retrieved_chunks'], 1):
                        st.markdown(f"**Result {i}** ({chunk['metadata']['modality']}) - Score: {chunk['score']:.3f}")
                        st.caption(f"Source: {chunk['metadata']['source']} (Page {chunk['metadata']['page']})")
                        st.text(chunk['content'][:300] + "...")
                        st.divider()
        else:
            st.warning("Please enter a question!")
    
    # Example questions
    with st.expander("💡 Example Questions"):
        st.markdown("""
        - What is the main topic of these documents?
        - Explain the key concepts discussed
        - Show me diagrams or charts
        - Summarize the content from [specific document]
        - What are the differences between [concept A] and [concept B]?
        """)

else:
    # Welcome screen
    st.info("👈 Upload PDF documents and click 'Process Documents' to get started!")
    
    st.markdown("### 🌟 Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📄 Text Extraction**
        - Smart chunking
        - Context preservation
        - Multiple PDFs
        """)
    
    with col2:
        st.markdown("""
        **🖼️ Image Understanding**
        - Automatic extraction
        - AI-powered captions
        - Visual search
        """)
    
    with col3:
        st.markdown("""
        **🤖 Intelligent Q&A**
        - Source citations
        - Multi-document synthesis
        - Context-aware answers
        """)

# Footer
st.divider()
st.caption("Built with Streamlit • Powered by Groq, BLIP, and ChromaDB")
