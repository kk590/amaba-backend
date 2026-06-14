# 📦 Deployment Guide - Render.com

This guide provides step-by-step instructions for deploying AMABA Backend to Render.com.

## ✅ Prerequisites

- [ ] GitHub account with your code repository
- [ ] Render account (free at https://render.com)
- [ ] Basic understanding of environment variables

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository

1. **Ensure all files are in your repository root:**
   ```
   amaba-backend/
   ├── main.py
   ├── orchestration.py
   ├── browser_tools.py
   ├── db_tools.py
   ├── requirements.txt
   ├── render.yaml
   ├── Dockerfile
   ├── README.md
   └── .env.example
   ```

2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add orchestration and deployment config"
   git push origin main
   ```

### Step 2: Connect to Render

1. **Visit Render Dashboard**
   - Go to https://dashboard.render.com
   - Sign in with GitHub (click "GitHub" button)
   - Authorize Render to access your repositories

2. **Create New Service**
   - Click **"New +"** button (top-right)
   - Select **"Web Service"**
   - Find your repository in the list
   - Click **"Connect"**

### Step 3: Configure Service Settings

**Basic Settings:**
- **Name**: `amaba-backend`
- **Environment**: Select your branch (usually `main`)
- **Region**: Choose closest to your users
- **Runtime**: Select `Python 3.11`

**Build & Deploy:**
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Settings:**
- **Instance Type**: Free (for testing) or Standard (for production)
- **Plan**: Standard
- **Disk**: 1 GB

### Step 4: Add Environment Variables

Click the **"Environment"** tab and add these variables:

| Key | Value | Purpose |
|-----|-------|---------|
| `PYTHONUNBUFFERED` | `true` | Disable output buffering |
| `ENVIRONMENT` | `production` | Environment mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `HOST` | `0.0.0.0` | Server host (required for Render) |
| `PORT` | `$PORT` | Use Render's dynamic port |
| `ORCHESTRATION_MAX_STEPS` | `15` | Max agent steps |
| `ORCHESTRATION_TIMEOUT` | `300` | Task timeout in seconds |

**Optional (if using HuggingFace models):**
- `HF_API_KEY` | Your HuggingFace token | For model inference

### Step 5: Configure Health Check

Render will automatically set up health checks:
- **Health Check Path**: `/health`
- **Check Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Failure Threshold**: 3 failed checks

### Step 6: Review & Deploy

1. **Review all settings** - Make sure everything is correct
2. **Click "Create Web Service"** - Start the deployment
3. **Watch the build logs** - You'll see real-time deployment progress

### Step 7: Verify Deployment

Once deployment completes (usually 5-10 minutes):

```bash
# Replace YOUR_SERVICE_URL with your actual Render URL
SERVICE_URL="https://your-service.onrender.com"

# 1. Check health
curl $SERVICE_URL/health

# 2. Check API status
curl $SERVICE_URL/api/status

# 3. Test orchestration
curl -X POST $SERVICE_URL/api/orchestrator/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Test orchestration system"
  }'

# 4. View API docs (in browser)
# Visit: $SERVICE_URL/docs
```

## 📊 Monitoring Your Deployment

### View Logs
1. Go to your service dashboard on Render
2. Click the **"Logs"** tab
3. Watch real-time server logs
4. Filter by log level (ERROR, WARNING, INFO)

### Monitor Performance
1. Click the **"Metrics"** tab
2. View CPU, Memory, Disk usage
3. Monitor request rates and response times

### Get Service URL
- Your service URL appears at the top of the dashboard
- Format: `https://service-name-xxxxx.onrender.com`
- Share this URL with frontend or clients

## 🔄 Updating Your Deployment

### Auto-Deploy from GitHub
- Every push to your main branch automatically triggers a new deployment
- Watch the logs to see build and deployment progress
- Service restarts with zero downtime

### Manual Redeploy
1. Go to your service dashboard
2. Click the **"Deploys"** tab
3. Find the deployment you want
4. Click **"Redeploy"** button

### Rollback to Previous Version
1. Go to **"Deploys"** tab
2. Find the working deployment
3. Click the three-dot menu
4. Select **"Redeploy This Commit"**

## 🚨 Troubleshooting

### Build Fails

**Error: "No module named 'smolagents'"**
- Make sure `smolagents` is in `requirements.txt`
- Render runs: `pip install -r requirements.txt`
- Update locally first: `pip install smolagents`

**Error: "Build exceeded 15 minutes"**
- Reduce number of dependencies
- Pre-compile heavy packages locally
- Check if `playwright` or `selenium` need system packages

### Deployment Fails

**Error: "Health check failed"**
- Ensure `/health` endpoint works
- Check environment variables are set
- Review logs for startup errors

**Error: "Port already in use"**
- Render manages port assignment via `$PORT` env var
- Make sure start command uses `$PORT`
- Don't hardcode port numbers

### Runtime Issues

**Service crashes after deployment**
- Check logs for error messages
- Verify all imports are available
- Test locally: `pip install -r requirements.txt`

**High memory usage**
- Check for memory leaks
- Reduce number of concurrent workers
- Consider upgrading instance type

**Slow API responses**
- Monitor metrics in Render dashboard
- Consider caching responses
- Scale up instance type if needed

## 📈 Scaling Configuration

### Auto-scaling
Add to `render.yaml`:
```yaml
scaling:
  minInstances: 1
  maxInstances: 3
  targetMemoryUtilization: 75
  targetCpuUtilization: 70
```

### Manual Scaling
1. Go to service settings
2. Click "Instance Count"
3. Adjust scale settings
4. Click "Save"

## 💰 Cost Estimation

- **Free tier**: Limited free hours, suitable for testing
- **Standard plan**: $7/month + usage, for production
- **Pro plan**: $18/month, for critical services

## 🔐 Security

### Environment Variables Best Practices

1. **Never commit `.env` file** (add to `.gitignore`)
2. **Use strong API keys** for sensitive services
3. **Rotate credentials regularly**
4. **Use service-specific tokens** when possible
5. **Review who has access** to environment variables

### CORS Security
Current setup allows all origins (`*`). For production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📚 Advanced Configuration

### Custom Domain
1. Go to service settings
2. Scroll to "Custom Domain"
3. Add your domain
4. Update DNS records at your domain provider

### SSL/TLS
- Render automatically provisions SSL certificates
- HTTPS is enabled by default
- No additional configuration needed

### Backup Strategies
- Use external database services (Render PostgreSQL)
- Export data regularly
- Maintain GitHub repository as backup

## 🆘 Getting Help

### Resources
- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- GitHub Issues: Create issue in your repository
- Render Support: https://render.com/support

### Contact Info
- Email: support@render.com
- Status Page: https://status.render.com
- Community Discord: Link available on Render website

## ✨ Next Steps After Deployment

1. **Monitor service** - Check logs and metrics regularly
2. **Set up alerts** - Get notified of errors
3. **Test thoroughly** - Verify all endpoints work
4. **Document API** - Share `/docs` endpoint with team
5. **Plan upgrades** - Monitor usage and scale as needed

---

**Congratulations! Your AMABA Backend is now live on Render! 🎉**
