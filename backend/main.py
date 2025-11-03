"""
AutoLabMate Backend - FastAPI server
Main API endpoints for lab automation workflows
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import logging
from pathlib import Path
import os
import asyncio
from database.session import init_db

try:
    from agents.planner import PlannerAgent
    from agents.executor import ExecutorAgent
    from agents.monitor import MonitorAgent
    from database.models import Experiment, AnalysisPlan, Report
    from database.session import get_db_session
    from tools.vector_store import VectorStore
    from tools.calendar_scheduler import CalendarScheduler
    from tools.github_integration import GitHubIntegration
except ImportError:
    # Handle relative imports when running as module
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from agents.planner import PlannerAgent
    from agents.executor import ExecutorAgent
    from agents.monitor import MonitorAgent
    from database.models import Experiment, AnalysisPlan, Report
    from database.session import get_db_session
    from tools.vector_store import VectorStore
    from tools.calendar_scheduler import CalendarScheduler
    from tools.github_integration import GitHubIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoLabMate API",
    description="AI-powered lab automation and report generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.on_event("startup")
async def on_startup():
    """Initialize database tables on app startup"""
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tools
vector_store = VectorStore()
calendar_scheduler = CalendarScheduler()
github_integration = GitHubIntegration()

# Initialize agents
planner_agent = PlannerAgent(vector_store)
executor_agent = ExecutorAgent()
monitor_agent = MonitorAgent(executor_agent)


# ===== Pydantic Models =====

class PlanRequest(BaseModel):
    """Request to generate an analysis plan"""
    dataset_path: str
    experiment_description: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = None


class PlanResponse(BaseModel):
    """Response containing the generated plan"""
    plan_id: str
    experiment_id: str
    steps: List[Dict[str, Any]]
    estimated_duration: str
    confidence_score: float = Field(ge=0, le=1)


class ExecuteRequest(BaseModel):
    """Request to execute a plan"""
    plan_id: str
    user_modifications: Optional[Dict[str, Any]] = None


class ExecuteResponse(BaseModel):
    """Response from plan execution"""
    execution_id: str
    status: str
    current_step: int
    total_steps: int
    logs: List[str]
    estimated_remaining: Optional[str] = None


class ReportResponse(BaseModel):
    """Response with report information"""
    report_id: str
    experiment_id: str
    pdf_path: str
    notebook_path: str
    metadata_path: str
    generated_at: str


class LogEntry(BaseModel):
    """Log entry for execution monitoring"""
    timestamp: str
    level: str
    message: str
    step: Optional[int] = None


# ===== API Endpoints =====

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "AutoLabMate API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "vector_store": vector_store.is_available(),
            "calendar": calendar_scheduler.is_available(),
            "github": github_integration.is_available()
        }
    }


@app.post("/api/upload", response_model=Dict[str, str])
async def upload_dataset(
    file: UploadFile = File(...),
    experiment_description: Optional[str] = None
):
    """
    Upload a dataset file (CSV, JSON, etc.) for analysis
    
    Args:
        file: Dataset file to upload
        experiment_description: Optional description of the experiment
        
    Returns:
        Dictionary with dataset path and experiment ID
    """
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("/app/uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Uploaded file: {file.filename} to {file_path}")
        
        # Create experiment record in database
        async with get_db_session() as session:
            experiment = Experiment(
                filename=file.filename,
                file_path=str(file_path),
                description=experiment_description,
                status="uploaded"
            )
            session.add(experiment)
            await session.commit()
            await session.refresh(experiment)
            experiment_id = experiment.id
        
        return {
            "dataset_path": f"/app/uploads/{file.filename}",
            "experiment_id": experiment_id,
            "filename": file.filename,
            "message": "Dataset uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/plan", response_model=PlanResponse)
async def generate_plan(request: PlanRequest):
    """
    Generate an analysis plan based on uploaded dataset
    
    Args:
        request: PlanRequest with dataset path and optional context
        
    Returns:
        PlanResponse with step-by-step analysis plan
    """
    try:
        dataset_path = request.dataset_path
        if not dataset_path.startswith("/app/"):
            dataset_path = f"/app{dataset_path}"
        logger.info(f"Generating plan for dataset: {request.dataset_path}")
        
        # Generate plan using PlannerAgent
        plan_result = await planner_agent.generate_plan(
            dataset_path=request.dataset_path,
            description=request.experiment_description,
            additional_context=request.additional_context or {}
        )
        
        # Save plan to database
        async with get_db_session() as session:
            experiment = await session.get(Experiment, request.experiment_id) if hasattr(request, 'experiment_id') else None
            
            analysis_plan = AnalysisPlan(
                experiment_id=experiment.id if experiment else None,
                steps=plan_result["steps"],
                metadata=plan_result.get("metadata", {})
            )
            session.add(analysis_plan)
            await session.commit()
            await session.refresh(analysis_plan)
            plan_id = analysis_plan.id
        
        logger.info(f"Plan generated successfully: {plan_id}")
        
        return PlanResponse(
            plan_id=str(plan_id),
            experiment_id=str(experiment.id if experiment else ""),
            steps=plan_result["steps"],
            estimated_duration=plan_result.get("estimated_duration", "10 minutes"),
            confidence_score=plan_result.get("confidence_score", 0.8)
        )
        
    except Exception as e:
        logger.error(f"Plan generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")


@app.post("/api/execute", response_model=ExecuteResponse)
async def execute_plan(
    request: ExecuteRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute an analysis plan and generate report
    
    Args:
        request: ExecuteRequest with plan_id
        background_tasks: FastAPI background task manager
        
    Returns:
        ExecuteResponse with execution status and logs
    """
    try:
        logger.info(f"Executing plan: {request.plan_id}")
        
        # Get plan from database
        async with get_db_session() as session:
            analysis_plan = await session.get(AnalysisPlan, request.plan_id)
            if not analysis_plan:
                raise HTTPException(status_code=404, detail="Plan not found")
            
            steps = analysis_plan.steps
            if isinstance(steps, str):
                import json
                steps = json.loads(steps)
        
        # Create execution record
        execution_id = f"exec_{request.plan_id}"
        
        # Add background task for execution
        background_tasks.add_task(
            _execute_plan_background,
            execution_id,
            request.plan_id,
            steps,
            request.user_modifications
        )
        
        logger.info(f"Execution started: {execution_id}")
        
        return ExecuteResponse(
            execution_id=execution_id,
            status="running",
            current_step=0,
            total_steps=len(steps),
            logs=["Execution started"],
            estimated_remaining=f"{len(steps) * 2} minutes"
        )
        
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


async def _execute_plan_background(
    execution_id: str,
    plan_id: str,
    steps: List[Dict],
    user_modifications: Optional[Dict]
):
    """Background task to execute plan"""
    try:
        # Execute steps using ExecutorAgent
        result = await executor_agent.execute_plan(
            plan_id=plan_id,
            steps=steps,
            modifications=user_modifications
        )
        
        logger.info(f"Execution completed: {execution_id}")
        
    except Exception as e:
        logger.error(f"Background execution error: {str(e)}")


@app.get("/api/execute/{execution_id}", response_model=ExecuteResponse)
async def get_execution_status(execution_id: str):
    """
    Get current status of a plan execution
    
    Args:
        execution_id: ID of the execution
        
    Returns:
        ExecuteResponse with current status
    """
    try:
        # Get status from MonitorAgent
        status = await monitor_agent.get_execution_status(execution_id)
        
        return ExecuteResponse(
            execution_id=execution_id,
            status=status["status"],
            current_step=status["current_step"],
            total_steps=status["total_steps"],
            logs=status["logs"],
            estimated_remaining=status.get("estimated_remaining")
        )
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.get("/api/report/{experiment_id}", response_model=ReportResponse)
async def get_report(experiment_id: str):
    """
    Retrieve generated report for an experiment
    
    Args:
        experiment_id: ID of the experiment
        
    Returns:
        ReportResponse with report paths
    """
    try:
        # Get report from database
        async with get_db_session() as session:
            report = await session.get(Report, experiment_id)
            if not report:
                raise HTTPException(status_code=404, detail="Report not found")
            
            return ReportResponse(
                report_id=str(report.id),
                experiment_id=str(report.experiment_id),
                pdf_path=report.pdf_path,
                notebook_path=report.notebook_path,
                metadata_path=report.metadata_path,
                generated_at=str(report.generated_at)
            )
            
    except Exception as e:
        logger.error(f"Report retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report retrieval failed: {str(e)}")


@app.get("/api/report/{experiment_id}/download")
async def download_report(experiment_id: str):
    """
    Download the generated PDF report
    
    Args:
        experiment_id: ID of the experiment
        
    Returns:
        PDF file download
    """
    try:
        async with get_db_session() as session:
            report = await session.get(Report, experiment_id)
            if not report or not Path(report.pdf_path).exists():
                raise HTTPException(status_code=404, detail="Report not found")
            
            return FileResponse(
                path=report.pdf_path,
                filename=f"autolabmate_report_{experiment_id}.pdf",
                media_type="application/pdf"
            )
            
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.get("/api/logs/{experiment_id}", response_model=List[LogEntry])
async def get_logs(experiment_id: str):
    """
    Retrieve execution logs for an experiment
    
    Args:
        experiment_id: ID of the experiment
        
    Returns:
        List of LogEntry objects
    """
    try:
        logs = await monitor_agent.get_logs(experiment_id)
        
        return [
            LogEntry(
                timestamp=log["timestamp"],
                level=log["level"],
                message=log["message"],
                step=log.get("step")
            )
            for log in logs
        ]
        
    except Exception as e:
        logger.error(f"Logs retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Logs retrieval failed: {str(e)}")


@app.post("/api/schedule")
async def schedule_experiment(experiment_data: Dict[str, Any]):
    """
    Schedule equipment booking using Google Calendar
    
    Args:
        experiment_data: Experiment details for scheduling
        
    Returns:
        Confirmation with calendar event ID
    """
    try:
        result = await calendar_scheduler.schedule_experiment(experiment_data)
        
        return {
            "status": "scheduled",
            "event_id": result["event_id"],
            "calendar_url": result.get("calendar_url")
        }
        
    except Exception as e:
        logger.error(f"Scheduling error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")


@app.post("/api/github/push")
async def push_to_github(request: Dict[str, Any]):
    """
    Push final report to GitHub repository
    
    Args:
        request: Request with experiment_id and optional commit message
        
    Returns:
        Confirmation with GitHub URL
    """
    try:
        result = await github_integration.push_report(
            experiment_id=request["experiment_id"],
            commit_message=request.get("commit_message", "Auto-generated report")
        )
        
        return {
            "status": "pushed",
            "github_url": result["url"],
            "commit_sha": result.get("commit_sha")
        }
        
    except Exception as e:
        logger.error(f"GitHub push error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GitHub push failed: {str(e)}")

async def init_database():
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    )

