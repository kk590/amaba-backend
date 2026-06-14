# AMABA Dashboard Backend

Multi-Agent Autonomous Browser Automation Backend with CEO Orchestration System.

## 🚀 Features

- **Multi-Agent Orchestration**: CEO agent coordinates specialized managers
  - 🌐 Browser Manager: Navigation, interaction, extraction
  - 🔧 Recovery Manager: Failure handling and retries
  - 🐛 Debug Manager: Error analysis and fixes
  - ✅ Critique Manager: Output validation
  
- **FastAPI Backend**: High-performance async REST API
- **Render.com Ready**: Pre-configured for cloud deployment
- **Docker Support**: Local development with Docker Compose
- **Comprehensive Logging**: Structured logging and monitoring
- **API Documentation**: Auto-generated with Swagger/OpenAPI

## 📋 Requirements

- Python 3.11+
- pip or uv package manager
- Git (for dependency installation)
- Docker (optional, for containerized deployment)

## 🔧 Local Setup

### 1. Clone and Navigate

```bash
git clone <your-repo>
cd amaba-backend
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run Development Server

```bash
# Option 1: Direct uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Using Python
python main.py
```

The server will start at `http://localhost:8000`

### 6. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🐳 Docker Development

### Quick Start with Docker Compose

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f amaba-backend

# Stop services
docker-compose down
```

### Build Docker Image Manually

```bash
# Build image
docker build -t amaba-backend:latest .

# Run container
docker run -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  amaba-backend:latest
```

## ☁️ Deploy to Render

### Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Create account at https://render.com
3. **Environment Variables**: Have your configuration ready

### Step-by-Step Deployment

1. **Connect Repository**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the correct branch (main/master)

2. **Configure Service**
   - **Name**: `amaba-backend`
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   ```
   PYTHONUNBUFFERED=true
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ORCHESTRATION_MAX_STEPS=15
   ORCHESTRATION_TIMEOUT=300
   HF_API_KEY=your_key_here
   ```

4. **Configure Scaling**
   - **Instance Type**: Standard
   - **Instance Count**: 1 (auto-scale up to 3)
   - **Disk Size**: 1 GB

5. **Add Health Check**
   - Path: `/health`
   - Check interval: 30s
   - Timeout: 10s

6. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - Watch deployment logs in real-time

### Verify Deployment

```bash
# Check health
curl https://your-service.onrender.com/health

# Check API docs
# Visit https://your-service.onrender.com/docs in browser

# Test orchestration
curl -X POST https://your-service.onrender.com/api/orchestrator/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Navigate to example.com and extract the title"
  }'
```

## 📡 API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /api/status` - System status
- `GET /` - API info

### Agents
- `GET /api/agents` - List all agents
- `GET /api/agents/{agent_id}` - Get agent details
- `POST /api/agents/{agent_id}/start` - Start agent
- `POST /api/agents/{agent_id}/stop` - Stop agent

### Orchestration (NEW)
- `GET /api/orchestrator/status` - Orchestrator status
- `POST /api/orchestrator/run` - Run task through orchestration
- `GET /api/orchestrator/history` - Execution history

### Tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{task_id}` - Get task status

### Browser
- `POST /api/browser/navigate` - Navigate to URL
- `POST /api/browser/scrape` - Scrape with selector
- `POST /api/browser/click` - Click element

### Logs
- `GET /api/logs` - Get logs
- `POST /api/logs` - Add log entry

### Metrics
- `GET /api/metrics` - Get system metrics

## 🎯 Using the Orchestration System

### Example: Run a Task

```bash
curl -X POST http://localhost:8000/api/orchestrator/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Navigate to google.com and search for Python programming",
    "task_id": "search_001"
  }'
```

### Example: Check History

```bash
curl http://localhost:8000/api/orchestrator/history?limit=5
```

### Python Client Example

```python
import requests

# Get orchestrator status
response = requests.get("http://localhost:8000/api/orchestrator/status")
print(response.json())

# Run a task
task_data = {
    "task_description": "Automate checkout process",
    "task_id": "checkout_001"
}
response = requests.post(
    "http://localhost:8000/api/orchestrator/run",
    json=task_data
)
result = response.json()
print(f"Task {result['task_id']}: {result['success']}")
```

## 🔐 Environment Variables

Key environment variables for Render deployment:

```
# Server
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO

# Orchestration
ORCHESTRATION_MAX_STEPS=15
ORCHESTRATION_TIMEOUT=300

# HuggingFace (if using inference)
HF_API_KEY=your_token_here

# Database (optional)
DATABASE_URL=sqlite:///./amaba.db
```

## 📊 Monitoring & Logging

### View Logs in Render

1. Go to your service dashboard
2. Click "Logs" tab
3. Filter by level (INFO, ERROR, WARNING)

### Local Logging

Configure in `.env`:

```
LOG_LEVEL=DEBUG  # More verbose
LOG_FORMAT=json  # Structured logs
```

## 🚨 Troubleshooting

### Deployment Issues

**Issue**: Build fails with "No module named 'smolagents'"

**Solution**:
```bash
pip install --upgrade pip
pip install smolagents
```

**Issue**: Port already in use

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process (replace PID)
kill -9 <PID>
```

**Issue**: Render deployment timeout

**Solution**: 
- Check if dependencies are too large
- Ensure build command completes in <15 minutes
- Try building locally first: `pip install -r requirements.txt`

### Runtime Issues

**Issue**: Orchestration returns 503 Service Unavailable

**Solution**:
- Check if smolagents library loaded correctly
- Verify HF_API_KEY environment variable is set
- Check server logs for initialization errors

## 📦 Project Structure

```
amaba-backend/
├── main.py                 # FastAPI application
├── orchestration.py        # Multi-agent orchestration system
├── browser_tools.py        # Browser automation tools
├── db_tools.py            # Database tools
├── requirements.txt       # Python dependencies
├── render.yaml           # Render configuration
├── docker-compose.yml    # Docker compose setup
├── Dockerfile            # Docker image definition
├── .env.example          # Environment template
├── build.sh              # Build script
└── README.md             # This file
```

## 🔄 CI/CD Pipeline (Optional)

Add to `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          curl -X POST https://api.render.com/deploy/srv-${{ secrets.RENDER_SERVICE_ID }}?key=${{ secrets.RENDER_API_KEY }}
```

## 📚 Additional Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Render Documentation](https://render.com/docs)
- [Docker Documentation](https://docs.docker.com/)
- [Uvicorn Docs](https://www.uvicorn.org/)

## 📄 License

MIT License - Feel free to use this project for your needs.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For issues, questions, or contributions:
- Open an GitHub Issue
- Check existing documentation
- Review API docs at `/docs` endpoint

---

**Happy automating! 🤖**
