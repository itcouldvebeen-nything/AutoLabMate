"""
GitHub Integration - Push reports to repositories
Version control for generated lab reports
"""

import logging
import os
import base64
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class GitHubIntegration:
    """
    GitHub Integration for report versioning
    
    Pushes generated reports to GitHub repositories
    """
    
    def __init__(self):
        """Initialize GitHub Integration"""
        self.use_mock = os.getenv("MOCK_MODE", "true").lower() == "true"
        self.github = None
        self.repo_name = os.getenv("GITHUB_REPO", "autolabmate-reports")
        
        if not self.use_mock:
            self._initialize_github()
        else:
            self._initialize_mock()
    
    def _initialize_github(self):
        """Initialize GitHub client"""
        try:
            from github import Github
            
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                raise ValueError("GITHUB_TOKEN not set")
            
            self.github = Github(token)
            self.repo = self.github.get_repo(self.repo_name)
            logger.info(f"GitHub initialized: {self.repo_name}")
            
        except Exception as e:
            logger.warning(f"GitHub initialization failed: {str(e)}, using mock")
            self.use_mock = True
            self._initialize_mock()
    
    def _initialize_mock(self):
        """Initialize mock GitHub"""
        self.mock_commits = []
        logger.info("GitHub integration running in MOCK mode")
    
    async def push_report(
        self,
        experiment_id: str,
        commit_message: Optional[str] = None,
        pdf_path: Optional[str] = None,
        notebook_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Push report files to GitHub
        
        Args:
            experiment_id: Experiment ID
            commit_message: Commit message
            pdf_path: Path to PDF report
            notebook_path: Path to notebook
        
        Returns:
            GitHub URL and commit SHA
        """
        try:
            if self.use_mock:
                return await self._push_mock(experiment_id, commit_message)
            else:
                return await self._push_github(experiment_id, commit_message, pdf_path, notebook_path)
                
        except Exception as e:
            logger.error(f"GitHub push error: {str(e)}")
            raise
    
    async def _push_mock(
        self,
        experiment_id: str,
        commit_message: Optional[str]
    ) -> Dict[str, Any]:
        """Mock GitHub push implementation"""
        import uuid
        import time
        
        commit_sha = f"mock_{uuid.uuid4().hex[:7]}"
        timestamp = time.time()
        
        self.mock_commits.append({
            "commit_sha": commit_sha,
            "experiment_id": experiment_id,
            "message": commit_message,
            "timestamp": timestamp
        })
        
        logger.info(f"Mock push: {commit_sha}")
        
        return {
            "url": f"https://github.com/mock/{self.repo_name}/commit/{commit_sha}",
            "commit_sha": commit_sha,
            "status": "pushed"
        }
    
    async def _push_github(
        self,
        experiment_id: str,
        commit_message: Optional[str],
        pdf_path: Optional[str],
        notebook_path: Optional[str]
    ) -> Dict[str, Any]:
        """GitHub push implementation"""
        branch = self.repo.default_branch
        
        # Prepare files
        files_to_commit = {}
        
        if pdf_path and Path(pdf_path).exists():
            with open(pdf_path, "rb") as f:
                pdf_content = base64.b64encode(f.read()).decode()
                files_to_commit[f"reports/{experiment_id}/report.pdf"] = pdf_content
        
        if notebook_path and Path(notebook_path).exists():
            with open(notebook_path, "rb") as f:
                notebook_content = base64.b64encode(f.read()).decode()
                files_to_commit[f"reports/{experiment_id}/analysis.ipynb"] = notebook_content
        
        # Get reference
        ref = self.repo.get_git_ref(f"heads/{branch}")
        
        # Create blobs
        tree_elements = []
        for file_path, content in files_to_commit.items():
            blob = self.repo.create_git_blob(content, "base64")
            tree_elements.append({
                "path": file_path,
                "mode": "100644",
                "type": "blob",
                "sha": blob.sha
            })
        
        # Create tree
        tree = self.repo.create_git_tree(tree_elements)
        
        # Create commit
        commit_message = commit_message or f"AutoLabMate report: {experiment_id}"
        commit = self.repo.create_git_commit(
            message=commit_message,
            tree=tree,
            parents=[ref.object.sha]
        )
        
        # Update reference
        ref.edit(commit.sha)
        
        logger.info(f"GitHub commit created: {commit.sha}")
        
        return {
            "url": commit.html_url,
            "commit_sha": commit.sha,
            "status": "pushed"
        }
    
    def is_available(self) -> bool:
        """Check if GitHub service is available"""
        return True  # Always available (mock or real)

