#!/usr/bin/env python3
"""
FastAPI MCP Server with Google Gemini CLI Integration
Demonstrates a Model Context Protocol (MCP) server with To-Do list management.

FIXES APPLIED:
1. Replaced deprecated @app.on_event("startup") with lifespan context manager
2. Added comprehensive error handling for all endpoints
3. Improved data validation and column name handling for Excel files
4. Enhanced logging with safe JSON serialization and atomic writes
5. Added proper timeout and encoding handling for subprocess calls
6. Implemented graceful error recovery for corrupted log files
7. Added new /tasks/pending endpoint for direct access
8. Improved Gemini CLI availability checking before execution
9. Enhanced HTTP status code handling in CLI script
10. Added proper cleanup and error reporting throughout
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Configure logging with better error handling
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Global variables
tasks_df: Optional[pd.DataFrame] = None
LOG_FILE = "query_log.json"

# Lifespan context manager for proper startup/shutdown handling
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting MCP Server with Gemini Integration...")
    load_tasks_data()
    logger.info("✅ Server startup completed")
    yield
    # Shutdown
    logger.info("🛑 Server shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="MCP Server with Gemini Integration",
    description="A Model Context Protocol server demonstrating To-Do list management and Gemini CLI integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TaskQuery(BaseModel):
    query: str = "all"  # "pending", "done", "all", or specific status

class GeminiRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gemini-pro"

class TaskResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    count: int
    query: str

class GeminiResponse(BaseModel):
    success: bool
    response: str
    error: Optional[str] = None

def load_tasks_data():
    """Load tasks from JSON file on server startup with improved error handling."""
    global tasks_df
    try:
        json_file = Path("tasks.json")
        if json_file.exists():
            # Read JSON file with error handling
            with open(json_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            # Convert to DataFrame
            tasks_df = pd.DataFrame(tasks_data)
            
            # Validate required columns exist
            required_columns = ['id', 'task', 'status']
            missing_columns = [col for col in required_columns if col not in tasks_df.columns]
            
            if missing_columns:
                logger.warning(f"⚠️ Missing required columns: {missing_columns}")
                # Try to find similar column names
                for missing_col in missing_columns:
                    for col in tasks_df.columns:
                        if missing_col.lower() in col.lower():
                            tasks_df = tasks_df.rename(columns={col: missing_col})
                            logger.info(f"🔄 Renamed column '{col}' to '{missing_col}'")
                            break
            
            # Clean and validate data
            tasks_df = tasks_df.dropna(subset=['id', 'task'])  # Remove rows with missing essential data
            tasks_df['status'] = tasks_df['status'].astype(str).str.lower().str.strip()  # Normalize status values
            
            logger.info(f"✅ Loaded {len(tasks_df)} tasks from tasks.json")
            logger.info(f"📊 Available statuses: {tasks_df['status'].unique().tolist()}")
            
        else:
            logger.warning("⚠️ tasks.json not found. Creating sample data...")
            create_sample_tasks()
            # Reload from the created JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            tasks_df = pd.DataFrame(tasks_data)
            logger.info(f"✅ Created and loaded {len(tasks_df)} sample tasks")
            
    except FileNotFoundError:
        logger.error("❌ tasks.json file not found and could not be created")
        tasks_df = pd.DataFrame()
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in tasks.json: {e}")
        tasks_df = pd.DataFrame()
    except Exception as e:
        logger.error(f"❌ Error loading tasks: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        tasks_df = pd.DataFrame()

def create_sample_tasks():
    """Create sample tasks data if tasks.json doesn't exist."""
    sample_data = [
        {
            "id": 1,
            "task": "Complete project documentation",
            "status": "pending",
            "due_date": "2024-01-20"
        },
        {
            "id": 2,
            "task": "Review code changes",
            "status": "done",
            "due_date": "2024-01-15"
        },
        {
            "id": 3,
            "task": "Update database schema",
            "status": "pending",
            "due_date": "2024-01-25"
        },
        {
            "id": 4,
            "task": "Fix authentication bug",
            "status": "in_progress",
            "due_date": "2024-01-18"
        },
        {
            "id": 5,
            "task": "Deploy to production",
            "status": "pending",
            "due_date": "2024-01-22"
        }
    ]
    
    with open("tasks.json", 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    logger.info("📊 Created sample tasks.json file")

def log_query(endpoint: str, request_data: Dict, response_data: Dict):
    """Log all requests and responses to query_log.json with improved error handling."""
    try:
        # Create log entry with safe serialization
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "request": _safe_serialize(request_data),
            "response": _safe_serialize(response_data)
        }
        
        # Load existing logs or create new list
        logs = []
        if Path(LOG_FILE).exists():
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                # Ensure logs is a list
                if not isinstance(logs, list):
                    logs = []
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(f"⚠️ Corrupted log file, starting fresh: {e}")
                logs = []
        
        # Add new log entry
        logs.append(log_entry)
        
        # Limit log size to prevent file from growing too large (keep last 1000 entries)
        if len(logs) > 1000:
            logs = logs[-1000:]
            logger.info("📝 Log file trimmed to last 1000 entries")
        
        # Save updated logs with atomic write
        temp_file = f"{LOG_FILE}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        # Atomic move
        Path(temp_file).rename(LOG_FILE)
            
    except Exception as e:
        logger.error(f"❌ Error logging query: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")

def _safe_serialize(data: Any) -> Any:
    """Safely serialize data for JSON logging, handling non-serializable objects."""
    try:
        if isinstance(data, dict):
            return {k: _safe_serialize(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [_safe_serialize(item) for item in data]
        elif isinstance(data, (str, int, float, bool, type(None))):
            return data
        else:
            # Convert non-serializable objects to string
            return str(data)
    except Exception:
        return str(data)

# Removed deprecated @app.on_event("startup") - now handled by lifespan context manager

@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "message": "MCP Server with Gemini Integration",
        "version": "1.0.0",
        "endpoints": {
            "tasks": "/tasks",
            "gemini": "/gemini",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "tasks_loaded": len(tasks_df) if tasks_df is not None else 0,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/tasks", response_model=TaskResponse)
async def get_tasks(request: TaskQuery):
    """
    Get tasks based on query parameter with improved error handling.
    Supports: 'pending', 'done', 'all', or any specific status.
    """
    try:
        # Validate tasks data is loaded
        if tasks_df is None:
            error_msg = "Tasks data not loaded. Server may not have started properly."
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        if tasks_df.empty:
            error_msg = "No tasks data available. JSON file may be empty or corrupted."
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Validate required columns exist
        if 'status' not in tasks_df.columns:
            error_msg = "Required 'status' column not found in JSON file"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        query = request.query.lower().strip()
        
        # Handle different query types
        if query == "all":
            filtered_df = tasks_df.copy()
        else:
            # Filter by status with case-insensitive matching
            filtered_df = tasks_df[tasks_df['status'].str.lower() == query]
        
        # Convert to list of dictionaries with safe serialization
        tasks_list = []
        for _, row in filtered_df.iterrows():
            try:
                task_dict = row.to_dict()
                # Ensure all values are JSON serializable
                safe_task = _safe_serialize(task_dict)
                tasks_list.append(safe_task)
            except Exception as e:
                logger.warning(f"⚠️ Skipping task row due to serialization error: {e}")
                continue
        
        response = TaskResponse(
            success=True,
            data=tasks_list,
            count=len(tasks_list),
            query=query
        )
        
        # Log the request and response
        log_query("/tasks", request.dict(), response.dict())
        
        logger.info(f"📋 Tasks query '{query}' returned {len(tasks_list)} results")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_response = TaskResponse(
            success=False,
            data=[],
            count=0,
            query=request.query
        )
        
        log_query("/tasks", request.dict(), error_response.dict())
        logger.error(f"❌ Unexpected error in /tasks endpoint: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/gemini", response_model=GeminiResponse)
async def call_gemini(request: GeminiRequest):
    """
    Forward prompt to Gemini CLI and return response with improved error handling.
    """
    try:
        # Validate input
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Check if Gemini CLI is available
        try:
            # Test if gemini command exists
            subprocess.run(["gemini", "--version"], capture_output=True, text=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            error_response = GeminiResponse(
                success=False,
                response="",
                error="Gemini CLI not found or not accessible. Please install and configure Gemini CLI."
            )
            log_query("/gemini", request.dict(), error_response.dict())
            logger.error("❌ Gemini CLI not found or not accessible")
            raise HTTPException(status_code=404, detail="Gemini CLI not found")
        
        # Prepare Gemini CLI command with proper escaping
        cmd = ["gemini", "chat", "--model", request.model or "gemini-pro", "--prompt", request.prompt.strip()]
        
        logger.info(f"🤖 Calling Gemini CLI with prompt: {request.prompt[:100]}...")
        
        # Execute Gemini CLI command with improved error handling
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # Increased timeout to 60 seconds
            encoding='utf-8',
            errors='replace'  # Handle encoding errors gracefully
        )
        
        if result.returncode == 0:
            response_text = result.stdout.strip()
            if not response_text:
                response_text = "No response received from Gemini CLI"
                logger.warning("⚠️ Empty response from Gemini CLI")
            
            response = GeminiResponse(
                success=True,
                response=response_text,
                error=None
            )
            logger.info("✅ Gemini CLI executed successfully")
        else:
            error_msg = result.stderr.strip() or f"Gemini CLI failed with exit code {result.returncode}"
            response = GeminiResponse(
                success=False,
                response="",
                error=error_msg
            )
            logger.error(f"❌ Gemini CLI error: {error_msg}")
        
        # Log the request and response
        log_query("/gemini", request.dict(), response.dict())
        
        return response
        
    except subprocess.TimeoutExpired:
        error_response = GeminiResponse(
            success=False,
            response="",
            error="Gemini CLI timeout (60s). The request took too long to process."
        )
        log_query("/gemini", request.dict(), error_response.dict())
        logger.error("⏰ Gemini CLI timeout")
        raise HTTPException(status_code=408, detail="Gemini CLI timeout")
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
        
    except Exception as e:
        error_response = GeminiResponse(
            success=False,
            response="",
            error=f"Unexpected error: {str(e)}"
        )
        log_query("/gemini", request.dict(), error_response.dict())
        logger.error(f"❌ Unexpected error in /gemini endpoint: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/logs")
async def get_logs():
    """Get all query logs with improved error handling."""
    try:
        if Path(LOG_FILE).exists():
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            return {"logs": logs, "count": len(logs)}
        else:
            return {"logs": [], "count": 0}
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"❌ Error reading logs (corrupted file): {e}")
        raise HTTPException(status_code=500, detail="Log file is corrupted")
    except Exception as e:
        logger.error(f"❌ Error reading logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/pending")
async def get_pending_tasks():
    """Get pending tasks directly (convenience endpoint)."""
    try:
        # Use the existing tasks endpoint logic
        request = TaskQuery(query="pending")
        response = await get_tasks(request)
        return response
    except Exception as e:
        logger.error(f"❌ Error in /tasks/pending endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting MCP Server with Gemini Integration...")
    print("📊 Loading tasks data...")
    
    # Load tasks data before starting server (redundant with lifespan, but ensures data is loaded)
    load_tasks_data()
    
    print("✅ Server ready!")
    print("🌐 Server will be available at: http://localhost:5001")
    print("📚 API Documentation: http://localhost:5001/docs")
    print("🔧 Available endpoints:")
    print("   • POST /tasks - Get tasks with query parameter")
    print("   • GET  /tasks/pending - Get pending tasks directly")
    print("   • POST /gemini - Send prompt to Gemini AI")
    print("   • GET  /health - Health check")
    print("   • GET  /logs - View query logs")
    
    try:
        uvicorn.run(
            "server:app",
            host="0.0.0.0",
            port=5001,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)