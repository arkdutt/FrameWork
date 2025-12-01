"""
FastAPI main application for the filmmaker app.
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config.settings import settings
from .database.mongodb import MongoDB
from .database.project_repo import ProjectRepository
from .models.schemas import (
    CreateProjectRequest,
    ProjectResponse,
    RunProjectRequest,
    UpdateScriptRequest
)
from .orchestrator.pipeline import Pipeline
from .websocket.progress import WebSocketManager
from .agents.change_detection_agent import ChangeDetectionAgent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    # Startup
    print(" Starting filmmaker app...")
    await MongoDB.connect()
    print(" Application ready")
    
    yield
    
    # Shutdown
    print(" Shutting down...")
    await MongoDB.disconnect()
    print(" Shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="Filmmaker AI App",
    description="AI-powered pre-production tool for filmmakers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline and change detection agent
pipeline = Pipeline()
change_agent = ChangeDetectionAgent()


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Filmmaker AI App",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/projects/create", response_model=ProjectResponse)
async def create_project(request: CreateProjectRequest):
    """
    Create a new project.
    
    Args:
        request: Project creation request
        
    Returns:
        Created project
    """
    try:
        # Create project in database
        project = await ProjectRepository.create_project(
            user_prompt=request.user_prompt,
            title=request.title
        )
        
        print(f" Created project: {project['_id']}")
        
        return project
        
    except Exception as e:
        print(f" Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """
    Get project by ID.
    
    Args:
        project_id: Project ID
        
    Returns:
        Project data
    """
    try:
        project = await ProjectRepository.get_project(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Error getting project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/{project_id}/run")
async def run_project(
    project_id: str,
    request: RunProjectRequest,
    background_tasks: BackgroundTasks
):
    """
    Run the pipeline for a project.
    
    Args:
        project_id: Project ID
        request: Run request
        background_tasks: Background tasks
        
    Returns:
        Status message
    """
    try:
        # Check if project exists
        project = await ProjectRepository.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if already completed
        if project.get("status") == "completed" and not request.force_rerun:
            return {
                "message": "Project already completed",
                "project_id": project_id
            }
        
        # Run pipeline in background
        background_tasks.add_task(pipeline.run, project_id)
        
        print(f" Started pipeline for project: {project_id}")
        
        return {
            "message": "Pipeline started",
            "project_id": project_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Error running project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/projects/{project_id}/script")
async def update_script(
    project_id: str,
    request: UpdateScriptRequest,
    background_tasks: BackgroundTasks
):
    """
    Update script and intelligently regenerate downstream artifacts if needed.
    
    Args:
        project_id: Project ID
        request: Update request with new script
        background_tasks: Background tasks
        
    Returns:
        Analysis of changes and regeneration status
    """
    try:
        # Check if project exists
        project = await ProjectRepository.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        old_script = project.get("script", "")
        new_script = request.script
        
        # If no previous script, just save it
        if not old_script:
            await ProjectRepository.update_script(project_id, new_script)
            print(f" Script saved for project {project_id} (no previous script)")
            return {
                "message": "Script saved successfully",
                "project_id": project_id,
                "should_regenerate": False,
                "reason": "No previous script to compare"
            }
        
        # Analyze changes
        print(f" Analyzing script changes for project {project_id}...")
        analysis = await change_agent.analyze_changes(old_script, new_script)
        
        # Save the new script
        await ProjectRepository.update_script(project_id, new_script)
        print(f" Script updated for project {project_id}")
        
        # If changes are significant, regenerate downstream artifacts
        if analysis['should_regenerate']:
            print(f" Changes are significant, regenerating downstream artifacts...")
            print(f"   Reason: {analysis['reason']}")
            
            # Clear existing storyboard and shot list to trigger regeneration
            if analysis['regenerate_storyboard']:
                await ProjectRepository.save_storyboard(project_id, None)
            if analysis['regenerate_shot_list']:
                await ProjectRepository.save_shot_list(project_id, None)
            
            # Run pipeline in background (will skip script, regenerate storyboard + shot list)
            background_tasks.add_task(pipeline.run, project_id, skip_script=True)
            
            return {
                "message": "Script updated and regeneration started",
                "project_id": project_id,
                "should_regenerate": True,
                "regenerate_storyboard": analysis['regenerate_storyboard'],
                "regenerate_shot_list": analysis['regenerate_shot_list'],
                "reason": analysis['reason'],
                "change_summary": analysis['change_summary'],
                "change_percentage": analysis['change_percentage']
            }
        else:
            print(f" Changes are minor, no regeneration needed")
            print(f"   Reason: {analysis['reason']}")
            
            return {
                "message": "Script updated (no regeneration needed)",
                "project_id": project_id,
                "should_regenerate": False,
                "reason": analysis['reason'],
                "change_summary": analysis['change_summary'],
                "change_percentage": analysis['change_percentage']
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Error updating script: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for real-time progress updates.
    
    Args:
        websocket: WebSocket connection
        project_id: Project ID
    """
    manager = WebSocketManager.manager
    
    try:
        await manager.connect(websocket, project_id)
        
        # Keep connection alive
        while True:
            try:
                # Wait for messages (heartbeat) with timeout
                data = await websocket.receive_text()
                
                # Echo back for heartbeat
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except Exception as e:
                # Connection closed or error receiving message
                print(f"  WebSocket receive error: {str(e)}")
                break
                
    except WebSocketDisconnect:
        print(f" WebSocket disconnected normally for project {project_id}")
    except Exception as e:
        print(f" WebSocket error: {str(e)}")
    finally:
        manager.disconnect(websocket, project_id)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        db = MongoDB.database
        if db is None:
            raise Exception("Database not connected")
        
        return {
            "status": "healthy",
            "database": "connected"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )


