# Deployment Guide

Complete guide to deploying your RAG System.

## 🎯 Quick Deploy Options

### Option 1: Streamlit Cloud (Easiest for UI Only)

**Time**: 5 minutes | **Cost**: FREE

1. **Prepare your repository**:
```bash
# Make sure .env.example exists (it does)
# Make sure requirements.txt is updated (it is)
```

2. **Modify for Streamlit Cloud**:

Create `streamlit_cloud_app.py`:
```python
# This version works without the full backend
import streamlit as st

st.set_page_config(page_title="RAG System Demo", page_icon="🤖")

st.title("🤖 RAG System Demo")
st.write("This is a demo showcasing the UI. For full functionality, run locally or deploy the full stack.")

# Add demo screenshots
st.image("screenshots/demo.png")

# Link to GitHub
st.markdown("[View Full Project on GitHub](https://github.com/YOUR_USERNAME/enterprise-rag-system)")
```

3. **Deploy**:
- Go to [share.streamlit.io](https://share.streamlit.io)
- Click "New app"
- Select your repo
- Main file: `streamlit_cloud_app.py`
- Click "Deploy"

**URL**: `https://YOUR-USERNAME-enterprise-rag-system.streamlit.app`

---

### Option 2: Hugging Face Spaces (Full Stack)

**Time**: 15 minutes | **Cost**: FREE

1. **Create Space**:
- Go to [huggingface.co/spaces](https://huggingface.co/spaces)
- Click "Create new Space"
- Choose "Docker"
- Name: `enterprise-rag-system`

2. **Create `Dockerfile.hf`**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app
COPY . .

# Expose ports
EXPOSE 7860

# Run Streamlit (HF Spaces uses port 7860)
CMD ["streamlit", "run", "ui/app.py", "--server.port=7860", "--server.address=0.0.0.0"]
```

3. **Push to HF**:
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/enterprise-rag-system
git push hf main
```

**URL**: `https://huggingface.co/spaces/YOUR_USERNAME/enterprise-rag-system`

---

### Option 3: Railway (Full Stack with Backend)

**Time**: 10 minutes | **Cost**: $5/month (free trial)

1. **Install Railway CLI**:
```bash
npm install -g @railway/cli
```

2. **Deploy**:
```bash
cd /Users/odubey/Desktop/Projects/Git\ Projects/RAG

# Login
railway login

# Initialize
railway init

# Deploy
railway up

# Add custom domain (optional)
railway domain
```

3. **Set Environment Variables** in Railway dashboard:
```
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**URL**: Provided by Railway (e.g., `your-app.railway.app`)

---

### Option 4: DigitalOcean App Platform

**Time**: 15 minutes | **Cost**: $5/month

1. **Create account**: [digitalocean.com](https://digitalocean.com)

2. **Deploy**:
- Click "Apps" → "Create App"
- Connect GitHub repository
- Select `enterprise-rag-system`
- DigitalOcean auto-detects Dockerfile
- Click "Next" → "Deploy"

3. **Configure**:
- Add environment variables
- Set up custom domain (optional)

**URL**: `your-app.ondigitalocean.app`

---

### Option 5: Google Cloud Run

**Time**: 20 minutes | **Cost**: Often free tier

1. **Setup**:
```bash
# Install gcloud CLI
brew install google-cloud-sdk

# Login
gcloud auth login

# Create project
gcloud projects create rag-system-PROJECT_ID
gcloud config set project rag-system-PROJECT_ID
```

2. **Deploy**:
```bash
# Build
gcloud builds submit --tag gcr.io/rag-system-PROJECT_ID/rag-app

# Deploy
gcloud run deploy rag-app \
  --image gcr.io/rag-system-PROJECT_ID/rag-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**URL**: Provided by Cloud Run

---

### Option 6: AWS (Most Control)

**Time**: 30-60 minutes | **Cost**: $5-10/month

1. **Launch EC2 Instance**:
- Ubuntu 22.04
- t2.medium (2 vCPU, 4GB RAM)
- 20GB storage

2. **Setup**:
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install -y docker.io docker-compose git

# Clone repo
git clone https://github.com/YOUR_USERNAME/enterprise-rag-system
cd enterprise-rag-system

# Deploy
docker-compose up -d
```

3. **Configure security group** to allow ports 8000, 8501

4. **Access**: `http://your-instance-ip:8501`

---

## 📱 Mobile Access

All deployment options provide URLs accessible from:
- ✅ Desktop browsers
- ✅ Mobile browsers (iOS/Android)
- ✅ Tablets
- ✅ Any device with internet

---

## 🔐 Access Control

### Public Access (Demo)
Anyone with the link can access.

### Private Access (Production)
Add authentication:

```python
# In ui/app.py, add at the top:
import streamlit as st

def check_password():
    """Returns True if password is correct."""
    def password_entered():
        if st.session_state["password"] == "YOUR_SECRET_PASSWORD":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", 
                     on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", 
                     on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# Rest of your app...
```

---

## 🌐 Custom Domain

### With Streamlit Cloud
- Upgrade to Teams plan ($250/month)
- Or use CNAME with your domain

### With Other Platforms (Free/Cheap)
1. Buy domain from Namecheap/GoDaddy ($10/year)
2. Add DNS records:
```
Type: A
Host: @
Value: YOUR_SERVER_IP

Type: CNAME
Host: www
Value: your-app.railway.app
```

---

## 📊 Sharing Options Summary

| Method | Cost | Setup Time | Best For |
|--------|------|------------|----------|
| GitHub Only | Free | 5 min | Code review, recruiters |
| Streamlit Cloud | Free | 5 min | Quick UI demo |
| HuggingFace | Free | 15 min | Full demo |
| Railway | $5/mo | 10 min | Production demo |
| DigitalOcean | $5/mo | 15 min | Production |
| Google Cloud | ~Free | 20 min | Scalable prod |
| AWS EC2 | $5-10/mo | 30 min | Full control |

---

## 🎯 Recommended Approach

### For Recruiters & Portfolio:
1. **GitHub** (shows code quality)
2. **Streamlit Cloud** (quick demo)
3. **Screenshots** in README
4. **2-min video** walkthrough

### For Technical Interviews:
1. **GitHub** (full code)
2. **Local setup** (shows it works)
3. **Architecture docs** (shows design thinking)

### For Production Use:
1. **Railway** or **DigitalOcean** (reliable)
2. **Custom domain** (professional)
3. **Authentication** (secure)
4. **Monitoring** (observability)

---

## 📝 Pre-Deployment Checklist

- [ ] Push code to GitHub
- [ ] Add screenshots to README
- [ ] Test locally with `docker-compose up`
- [ ] Remove sensitive data from `.env`
- [ ] Update README with your info
- [ ] Create demo video (optional)
- [ ] Test API endpoints
- [ ] Test UI flows
- [ ] Document any issues
- [ ] Prepare demo script

---

## 🚀 Quick Deploy Commands

### Streamlit Cloud
```bash
# No commands needed - just use web interface
# Go to share.streamlit.io
```

### Railway
```bash
railway login
railway init
railway up
railway domain  # Get URL
```

### Docker Compose (Self-hosted)
```bash
docker-compose up -d
```

### Check Deployment
```bash
# Health check
curl https://your-app-url.com/health

# Test query
curl -X POST https://your-app-url.com/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```

---

## 🆘 Troubleshooting

### Deployment Fails
- Check logs: `docker-compose logs`
- Verify environment variables
- Check port conflicts

### Can't Access URL
- Check firewall rules
- Verify security groups (AWS)
- Check CORS settings

### Out of Memory
- Reduce batch sizes in config
- Use smaller embedding model
- Upgrade instance size

---

## 📧 Support

For deployment issues:
1. Check logs first
2. Review platform documentation
3. Check GitHub Issues
4. Contact platform support

---

**Choose your deployment method and get started! 🚀**

