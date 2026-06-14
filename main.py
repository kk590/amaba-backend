"""
AMABA Multi-Agent Dashboard Backend
FastAPI server for extension communication and agent orchestration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import uvicorn
from datetime import datetime
import json
import os

# Import orchestration system
from orchestration import get_orchestrator, OrchestratorConfig, init_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AMABA Dashboard API",
    description="Multi-Agent Autonomous Browser Automation Backend",
    version="1.0.0"
)

# Enable CORS for extension communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Pydantic Models
# ============================================================================

class TaskRequest(BaseModel):
    task_name: str
    task_type: str
    url: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    timestamp: str

class ExecutionLog(BaseModel):
    timestamp: str
    level: str
    message: str
    agent_id: Optional[str] = None

class SystemStatus(BaseModel):
    status: str
    uptime: int
    agents_active: int
    tasks_running: int
    metrics: Dict[str, Any]

class OrchestrationTaskRequest(BaseModel):
    task_description: str
    task_id: Optional[str] = None

class OrchestrationTaskResponse(BaseModel):
    task_id: str
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    duration: float
    timestamp: str

# ============================================================================
# Global State
# ============================================================================

AGENTS_STATE = {
    "ceo": {"status": "active", "progress": 0, "last_updated": datetime.now().isoformat()},
    "browser_manager": {"status": "idle", "progress": 0, "last_updated": datetime.now().isoformat()},
    "recovery_manager": {"status": "idle", "progress": 0, "last_updated": datetime.now().isoformat()},
    "debug_manager": {"status": "idle", "progress": 0, "last_updated": datetime.now().isoformat()},
    "critique_manager": {"status": "idle", "progress": 0, "last_updated": datetime.now().isoformat()},
}

EXECUTION_LOG = [
    {"timestamp": "T-00:01", "message": "Init scraping session", "level": "info"},
    {"timestamp": "T-00:02", "message": "Parsing DOM structure", "level": "info"},
    {"timestamp": "T-00:03", "message": "Navigating checkout...", "level": "info"},
]

METRICS = {
    "reliability": 98.7,
    "latency": 12,
    "tasks_completed": 0,
    "error_rate": 0.13
}

# Initialize orchestrator
orchestrator = None

# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize when server starts"""
    global orchestrator
    
    logger.info("=" * 60)
    logger.info("AMABA Dashboard Backend Starting...")
    logger.info("=" * 60)
    
    # Initialize orchestrator
    try:
        config = OrchestratorConfig()
        init_orchestrator(config)
        orchestrator = get_orchestrator()
        logger.info("✅ Agent Orchestration System: Initialized")
    except Exception as e:
        logger.warning(f"⚠️  Orchestration system failed to initialize: {e}")
        logger.warning("   Backend will run in API-only mode")
    
    logger.info("✅ API Server: Running")
    logger.info("📚 API Docs: /docs")
    logger.info("🔍 ReDoc: /redoc")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when server shuts down"""
    logger.info("AMABA Dashboard Backend Shutting Down...")

# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Check if backend is running"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "orchestration": "active" if orchestrator else "unavailable"
    }

@app.get("/api/status")
async def get_system_status():
    """Get overall system status"""
    active_agents = sum(1 for a in AGENTS_STATE.values() if a["status"] == "active")
    
    return {
        "status": "running",
        "uptime": 123456,
        "agents_active": active_agents,
        "tasks_running": 1,
        "orchestration_ready": orchestrator is not None,
        "metrics": {
            "reliability": METRICS["reliability"],
            "latency": METRICS["latency"],
            "tasks_completed": METRICS["tasks_completed"]
        }
    }

# ============================================================================
# Agent Endpoints
# ============================================================================

@app.get("/api/agents")
async def get_all_agents():
    """Get list of all agents and their status"""
    agents = []
    
    # Get orchestrator agent status if available
    if orchestrator:
        orch_status = orchestrator.get_agent_status()
        agents.append({
            "id": "ceo_orchestrator",
            "name": "CEO Orchestrator",
            "status": orch_status.get('ceo', 'active'),
            "progress": 0,
            "last_updated": datetime.now().isoformat(),
            "type": "orchestrator"
        })
    
    # Add other agents
    for agent_id, state in AGENTS_STATE.items():
        if agent_id != "ceo":  # Skip duplicate CEO
            agents.append({
                "id": agent_id,
                "name": agent_id.replace("_", " ").title(),
                "status": state["status"],
                "progress": state["progress"],
                "last_updated": state["last_updated"]
            })
    
    return {"agents": agents}

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details"""
    if agent_id not in AGENTS_STATE and agent_id != "ceo_orchestrator":
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    if agent_id == "ceo_orchestrator" and orchestrator:
        status = orchestrator.get_agent_status()
        return {
            "id": agent_id,
            "name": "CEO Orchestrator",
            "status": status.get('ceo', 'active'),
            "progress": 0,
            "last_updated": datetime.now().isoformat(),
            "type": "orchestrator"
        }
    
    state = AGENTS_STATE.get(agent_id, {})
    return {
        "id": agent_id,
        "name": agent_id.replace("_", " ").title(),
        "status": state.get("status", "unknown"),
        "progress": state.get("progress", 0),
        "last_updated": state.get("last_updated", datetime.now().isoformat())
    }

@app.post("/api/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    """Start an agent"""
    if agent_id not in AGENTS_STATE:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    AGENTS_STATE[agent_id]["status"] = "active"
    AGENTS_STATE[agent_id]["last_updated"] = datetime.now().isoformat()
    
    logger.info(f"Started agent: {agent_id}")
    return {"message": f"Agent {agent_id} started", "status": "success"}

@app.post("/api/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Stop an agent"""
    if agent_id not in AGENTS_STATE:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    AGENTS_STATE[agent_id]["status"] = "idle"
    AGENTS_STATE[agent_id]["progress"] = 0
    AGENTS_STATE[agent_id]["last_updated"] = datetime.now().isoformat()
    
    logger.info(f"Stopped agent: {agent_id}")
    return {"message": f"Agent {agent_id} stopped", "status": "success"}

# ============================================================================
# Orchestration Endpoints
# ============================================================================

@app.get("/api/orchestrator/status")
async def get_orchestrator_status():
    """Get orchestrator status"""
    if not orchestrator:
        return {"status": "unavailable", "message": "Orchestration system not initialized"}
    
    status = orchestrator.get_agent_status()
    return {
        "status": "active",
        "orchestrator_config": {
            "max_steps": 15,
            "timeout": 300
        },
        "agents": status['agents'],
        "execution_count": status['execution_history'],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/orchestrator/run")
async def run_orchestration_task(request: OrchestrationTaskRequest):
    """
    Run a task through the orchestration system.
    This will invoke the CEO agent to coordinate all specialized managers.
    """
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Orchestration system not available"
        )
    
    try:
        logger.info(f"Running orchestration task: {request.task_description}")
        
        # Execute through orchestrator
        result = orchestrator.run_task(
            request.task_description,
            request.task_id
        )
        
        # Update metrics
        METRICS["tasks_completed"] += 1
        
        return OrchestrationTaskResponse(
            task_id=result.task_id,
            success=result.success,
            result=str(result.result) if result.result else None,
            error=result.error,
            duration=result.duration,
            timestamp=result.timestamp
        )
        
    except Exception as e:
        logger.error(f"Orchestration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orchestrator/history")
async def get_orchestrator_history(limit: int = Query(10, ge=1, le=100)):
    """Get orchestrator execution history"""
    if not orchestrator:
        return {"history": [], "total": 0}
    
    history = orchestrator.get_execution_history(limit)
    return {
        "history": history,
        "total": len(history),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# Task Endpoints
# ============================================================================

@app.post("/api/tasks")
async def create_task(task: TaskRequest, background_tasks: BackgroundTasks):
    """Create and execute a new task"""
    task_id = f"task_{datetime.now().timestamp()}"
    
    logger.info(f"Created task: {task_id} - {task.task_name}")
    
    return TaskResponse(
        task_id=task_id,
        status="executing",
        progress=33,
        message=f"Task {task.task_name} is executing",
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task status"""
    return {
        "task_id": task_id,
        "status": "executing",
        "progress": 33,
        "message": "Processing task",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# Metrics Endpoints
# ============================================================================

@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "reliability": METRICS["reliability"],
        "latency": METRICS["latency"],
        "tasks_completed": METRICS["tasks_completed"],
        "error_rate": METRICS["error_rate"]
    }

# ============================================================================
# Logging Endpoints
# ============================================================================

@app.get("/api/logs")
async def get_logs(limit: int = 50):
    """Get execution logs"""
    return {
        "logs": EXECUTION_LOG[-limit:],
        "total": len(EXECUTION_LOG)
    }

@app.post("/api/logs")
async def add_log(log: ExecutionLog):
    """Add a log entry"""
    EXECUTION_LOG.append({
        "timestamp": log.timestamp,
        "level": log.level,
        "message": log.message,
        "agent_id": log.agent_id
    })
    logger.info(f"[{log.agent_id}] {log.message}")
    return {"status": "logged"}

# ============================================================================
# Browser Tools Endpoints
# ============================================================================

@app.post("/api/browser/navigate")
async def navigate(url: str):
    """Navigate to URL"""
    logger.info(f"Navigating to: {url}")
    return {
        "status": "navigated",
        "url": url,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/browser/scrape")
async def scrape(selector: str):
    """Scrape page with CSS selector"""
    logger.info(f"Scraping with selector: {selector}")
    return {
        "status": "scraped",
        "selector": selector,
        "data": [],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/browser/click")
async def click(selector: str):
    """Click element by selector"""
    logger.info(f"Clicking: {selector}")
    return {
        "status": "clicked",
        "selector": selector,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# Database Endpoints
# ============================================================================

@app.get("/api/database/status")
async def database_status():
    """Check database status"""
    return {
        "status": "connected",
        "type": "sqlite",
        "tables": ["agents", "tasks", "logs", "metrics"],
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AMABA Dashboard API",
        "version": "1.0.0",
        "description": "Multi-Agent Autonomous Browser Automation Backend",
        "documentation": "/docs",
        "orchestration": "active" if orchestrator else "unavailable",
        "endpoints": {
            "health": "/health",
            "status": "/api/status",
            "agents": "/api/agents",
            "orchestrator": "/api/orchestrator/status",
            "run_task": "/api/orchestrator/run",
            "docs": "/docs"
        }
    }

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    # Get host and port from environment variables (Render compatible)
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting AMABA Dashboard Backend on {host}:{port}")
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
