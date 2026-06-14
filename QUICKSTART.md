# 🚀 Quick Start Guide

## 60-Second Setup

### 1️⃣ Install & Run (Local)

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

**Server ready at:** http://localhost:8000

### 2️⃣ Test the API

```bash
# Check health
curl http://localhost:8000/health

# View documentation
# Open in browser: http://localhost:8000/docs
```

### 3️⃣ Run Orchestration Task

```bash
curl -X POST http://localhost:8000/api/orchestrator/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Navigate to example.com and extract page title"
  }'
```

---

## 🐳 Docker Quick Start

```bash
# Using Docker Compose (simplest)
docker-compose up

# Or build and run manually
docker build -t amaba-backend .
docker run -p 8000:8000 amaba-backend
```

---

## ☁️ Deploy to Render (5 minutes)

### Prerequisites
- GitHub account with your code pushed
- Render account (free at render.com)

### Steps

1. **Go to Render Dashboard**
   - https://dashboard.render.com

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect GitHub repo
   - Select correct branch

3. **Configure**
   - Name: `amaba-backend`
   - Runtime: Python 3.11
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables**
   - Click "Environment" tab
   - Add key-value pairs:
     ```
     PYTHONUNBUFFERED=true
     ENVIRONMENT=production
     ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait ~5 minutes for build and deployment

6. **Verify**
   ```bash
   curl https://your-service.onrender.com/health
   ```

---

## 📊 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/docs` | GET | API documentation |
| `/api/status` | GET | System status |
| `/api/agents` | GET | List agents |
| `/api/orchestrator/status` | GET | Orchestrator status |
| `/api/orchestrator/run` | POST | Run task |
| `/api/orchestrator/history` | GET | Task history |

---

## 🔍 Troubleshooting

### Port 8000 already in use?
```bash
# Find process
lsof -i :8000

# Kill it (replace PID)
kill -9 <PID>
```

### Dependencies not installing?
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Docker issues?
```bash
# Clean up
docker-compose down -v
docker system prune

# Rebuild
docker-compose up --build
```

---

## 📖 Next Steps

1. **Read Full README.md** - Comprehensive documentation
2. **Check API Docs** - Visit `/docs` for interactive API explorer
3. **Customize** - Update `.env` with your configuration
4. **Deploy** - Follow Render deployment guide above

---

## ✨ You're All Set!

Your AMABA Backend is ready to:
- 🌐 Manage browser automation
- 🤖 Orchestrate multi-agent tasks
- 📡 Provide REST APIs
- ☁️ Scale on Render

Happy automating! 🚀
