# 🚀 Deployment Guide

## Quick Deployment Options

### 🌟 Option 1: Streamlit Cloud (FREE & EASIEST)

**Best for**: Quick deployment, free hosting, easy updates

1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/multimodal-rag.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repo
   - Main file: `app.py`
   - Click "Deploy"!

3. **Add Secrets** (Optional)
   - In Streamlit Cloud dashboard → Settings → Secrets
   - Add your Groq API key:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```

**Your app will be live at**: `https://YOUR_USERNAME-multimodal-rag.streamlit.app`

---

### 🎨 Option 2: Hugging Face Spaces (FREE)

**Best for**: ML community, easy sharing, GPU access

1. **Create Space**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Choose "Streamlit" as SDK
   - Name your space

2. **Upload Files**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/your-space
   cd your-space
   cp /path/to/your/files/* .
   git add .
   git commit -m "Add RAG system"
   git push
   ```

3. **Add Secrets**
   - In Space settings → Repository secrets
   - Add `GROQ_API_KEY`

**Your app will be live at**: `https://huggingface.co/spaces/YOUR_USERNAME/your-space`

---

### 🔧 Option 3: Render (FREE)

**Best for**: Custom domains, more control

1. **Create `render.yaml`**
   ```yaml
   services:
     - type: web
       name: multimodal-rag
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: streamlit run app.py --server.port $PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.9.0
   ```

2. **Deploy**
   - Go to [render.com](https://render.com)
   - New → Web Service
   - Connect your GitHub repo
   - Auto-detects `render.yaml`
   - Click "Create Web Service"

3. **Add Environment Variables**
   - In service dashboard → Environment
   - Add `GROQ_API_KEY`

---

### 🐳 Option 4: Docker (LOCAL or CLOUD)

**Best for**: Production, scalability

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8501

   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and Run**
   ```bash
   docker build -t multimodal-rag .
   docker run -p 8501:8501 multimodal-rag
   ```

3. **Deploy to Cloud**
   - Push to Docker Hub
   - Deploy on AWS ECS, Google Cloud Run, or Azure Container Instances

---

## 📊 Comparison Table

| Platform | Cost | Setup Time | Custom Domain | GPU | Storage |
|----------|------|------------|---------------|-----|---------|
| **Streamlit Cloud** | Free | 5 min | ✅ (Pro) | ❌ | Limited |
| **HF Spaces** | Free | 10 min | ❌ | ✅ (Paid) | Good |
| **Render** | Free | 15 min | ✅ | ❌ | Limited |
| **Docker** | Varies | 30 min | ✅ | ✅ | Custom |

---

## 🎯 Recommended: Streamlit Cloud

For internship applications and portfolios, **Streamlit Cloud** is the best choice:

✅ **Free forever**
✅ **5-minute setup**
✅ **Auto-updates from GitHub**
✅ **Professional URL**
✅ **Built-in secrets management**
✅ **Easy to share**

---

## 🔑 Getting Your Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free)
3. Create API key
4. Copy and save it
5. Add to your deployment platform

**Free tier includes:**
- 14,400 requests/day
- Fast inference
- Multiple models

---

## 📱 Sharing Your App

Once deployed, add it to your:

- **LinkedIn**: Post with screenshots
- **Resume**: Add under "Projects"
- **GitHub README**: Link prominently
- **Portfolio**: Embed or link
- **Internship Applications**: Include demo link

---

## 🐛 Troubleshooting

### App crashes on startup
- Check Python version (3.9+)
- Verify all dependencies installed
- Check API key is set correctly

### Slow loading
- First time loads models (~2 min)
- Subsequent uses are faster
- Consider caching strategies

### Out of memory
- Reduce chunk size
- Process fewer PDFs at once
- Use lighter embedding model

---

## 📈 Next Steps

1. **Deploy** using Streamlit Cloud
2. **Test** with different PDFs
3. **Share** the link
4. **Get feedback**
5. **Iterate** and improve

Good luck with your internship applications! 🚀
