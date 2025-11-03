"""
Monitor Agent - Monitors execution progress
Tracks step completion, logs, and handles retries
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MonitorAgent:
    """
    Monitor Agent tracks execution progress
    
    Responsibilities:
    - Track step completion
    - Collect execution logs
    - Handle retries on failure
    - Provide status updates
    - Estimate remaining time
    """
    
    def __init__(self, executor_agent):
        """
        Initialize Monitor Agent
        
        Args:
            executor_agent: Reference to ExecutorAgent
        """
        self.executor = executor_agent
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.logs: Dict[str, List[Dict[str, Any]]] = {}
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get current status of an execution
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Status dictionary with progress and logs
        """
        try:
            # Get execution from storage
            execution = self.executions.get(execution_id, {})
            
            # Get logs for this execution
            log_entries = self.logs.get(execution_id, [])
            
            # Return status
            return {
                "status": execution.get("status", "unknown"),
                "current_step": execution.get("current_step", 0),
                "total_steps": execution.get("total_steps", 0),
                "logs": [log["message"] for log in log_entries[-50:]],  # Last 50 logs
                "estimated_remaining": execution.get("estimated_remaining"),
                "progress_percent": (
                    execution.get("current_step", 0) / execution.get("total_steps", 1) * 100
                    if execution.get("total_steps", 0) > 0 else 0
                )
            }
            
        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_logs(self, experiment_id: str) -> List[Dict[str, Any]]:
        """
        Get all logs for an experiment
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            List of log entries
        """
        return self.logs.get(experiment_id, [])
    
    async def add_log(
        self,
        execution_id: str,
        level: str,
        message: str,
        step: Optional[int] = None
    ):
        """
        Add a log entry
        
        Args:
            execution_id: Execution ID
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            message: Log message
            step: Optional step number
        """
        try:
            if execution_id not in self.logs:
                self.logs[execution_id] = []
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "message": message,
                "step": step
            }
            
            self.logs[execution_id].append(log_entry)
            
            # Log to console as well
            logger.log(
                getattr(logging, level.upper(), logging.INFO),
                f"[{execution_id}] {message}"
            )
            
        except Exception as e:
            logger.error(f"Logging error: {str(e)}")
    
    async def update_execution_status(
        self,
        execution_id: str,
        status: str,
        current_step: Optional[int] = None,
        total_steps: Optional[int] = None,
        estimated_remaining: Optional[str] = None
    ):
        """
        Update execution status
        
        Args:
            execution_id: Execution ID
            status: New status
            current_step: Current step number
            total_steps: Total number of steps
            estimated_remaining: Estimated remaining time
        """
        try:
            if execution_id not in self.executions:
                self.executions[execution_id] = {}
            
            self.executions[execution_id].update({
                "status": status,
                "current_step": current_step or self.executions[execution_id].get("current_step"),
                "total_steps": total_steps or self.executions[execution_id].get("total_steps"),
                "estimated_remaining": estimated_remaining,
                "last_updated": datetime.utcnow().isoformat()
            })
            
            await self.add_log(execution_id, "INFO", f"Status updated: {status}")
            
        except Exception as e:
            logger.error(f"Status update error: {str(e)}")
    
    async def handle_step_completion(
        self,
        execution_id: str,
        step_number: int,
        success: bool,
        output: Optional[Any] = None
    ):
        """
        Handle completion of a step
        
        Args:
            execution_id: Execution ID
            step_number: Completed step number
            success: Whether step succeeded
            output: Step output (optional)
        """
        try:
            if success:
                await self.add_log(
                    execution_id,
                    "INFO",
                    f"Step {step_number} completed successfully",
                    step=step_number
                )
            else:
                await self.add_log(
                    execution_id,
                    "ERROR",
                    f"Step {step_number} failed",
                    step=step_number
                )
            
            # Update current step in status
            await self.update_execution_status(
                execution_id,
                "running",
                current_step=step_number
            )
            
        except Exception as e:
            logger.error(f"Step completion handling error: {str(e)}")

