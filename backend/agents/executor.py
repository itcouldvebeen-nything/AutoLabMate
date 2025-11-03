"""
Executor Agent - Executes analysis plans
Runs Python notebooks/scripts in sandboxed environment
"""

import logging
import os
import json
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import nbformat
from nbconvert import PythonExporter
import time

logger = logging.getLogger(__name__)


class ExecutorAgent:
    """
    Executor Agent runs analysis plan steps
    
    Responsibilities:
    - Execute Python code safely
    - Generate Jupyter notebooks
    - Run data analysis steps
    - Produce intermediate outputs
    - Handle errors and retries
    """
    
    def __init__(self):
        """Initialize Executor Agent"""
        self.work_dir = Path("./workspace")
        self.work_dir.mkdir(exist_ok=True)
        self.use_sandbox = os.getenv("USE_SANDBOX", "true").lower() == "true"
    
    async def execute_plan(
        self,
        plan_id: str,
        steps: List[Dict],
        modifications: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete analysis plan
        
        Args:
            plan_id: ID of the plan
            steps: List of step dictionaries
            modifications: Optional user modifications to steps
            
        Returns:
            Execution result with outputs and status
        """
        try:
            logger.info(f"Executing plan {plan_id} with {len(steps)} steps")
            
            # Create workspace for this execution
            exec_dir = self.work_dir / plan_id
            exec_dir.mkdir(exist_ok=True)
            
            # Create Jupyter notebook
            notebook_path = exec_dir / "analysis.ipynb"
            notebook = self._create_notebook(steps, modifications)
            nbformat.write(notebook, notebook_path)
            
            # Execute notebook
            result = await self._execute_notebook(notebook_path, exec_dir)
            
            # Generate report
            report_path = await self._generate_report(exec_dir, result)
            
            logger.info(f"Plan execution completed: {plan_id}")
            
            return {
                "status": "success",
                "plan_id": plan_id,
                "notebook_path": str(notebook_path),
                "report_path": str(report_path),
                "outputs": result["outputs"],
                "execution_time": result["execution_time"]
            }
            
        except Exception as e:
            logger.error(f"Plan execution error: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "plan_id": plan_id
            }
    
    def _create_notebook(
        self,
        steps: List[Dict],
        modifications: Optional[Dict]
    ) -> nbformat.NotebookNode:
        """
        Create Jupyter notebook from plan steps
        
        Args:
            steps: List of step dictionaries
            modifications: Optional modifications
            
        Returns:
            Notebook object
        """
        notebook = nbformat.v4.new_notebook()
        
        # Add title cell
        notebook.cells.append(nbformat.v4.new_markdown_cell(
            "# AutoLabMate Analysis Report\n"
            "Generated automatically from experimental data"
        ))
        
        # Add import cell
        imports_cell = nbformat.v4.new_code_cell(
            """# Standard data science imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configure plotting
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")"""
        )
        notebook.cells.append(imports_cell)
        
        # Add cells for each step
        for step in steps:
            # Apply modifications if any
            if modifications and step.get("step_number") in modifications.get("steps", {}):
                step = {**step, **modifications["steps"][step["step_number"]]}
            
            # Add step header
            header = f"## Step {step.get('step_number')}: {step.get('name')}"
            notebook.cells.append(nbformat.v4.new_markdown_cell(header))
            
            # Add code cell for step
            code_cell = self._generate_step_code(step)
            notebook.cells.append(nbformat.v4.new_code_cell(code_cell))
        
        # Add report generation cell
        notebook.cells.append(nbformat.v4.new_markdown_cell("## Report Summary"))
        notebook.cells.append(nbformat.v4.new_code_cell(
            """# Generate summary
print("Analysis completed successfully!")
print(f"Total execution time: {execution_time:.2f} seconds")"""
        ))
        
        return notebook
    
    def _generate_step_code(self, step: Dict) -> str:
        """
        Generate Python code for a step
        
        Args:
            step: Step dictionary
            
        Returns:
            Python code string
        """
        action = step.get("action")
        parameters = step.get("parameters", {})
        
        if action == "load_data":
            return f"""# Load and validate data
df = pd.read_{parameters.get('file_type', 'csv').replace('.', '')}(
    '{parameters.get('file_path', '')}'
)
print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
print(df.head())"""
        
        elif action == "compute_stats":
            columns = parameters.get('columns', [])
            if columns:
                return f"""# Compute descriptive statistics
stats_df = df[{columns}].describe()
print(stats_df)"""
            return """# Compute descriptive statistics
stats_df = df.describe()
print(stats_df)"""
        
        elif action == "create_plot":
            plot_type = parameters.get('plot_type', 'histogram')
            column = parameters.get('column', df.columns[0] if 'df' in globals() else '')
            
            if plot_type == "histogram":
                return f"""# Create histogram
plt.figure(figsize=(10, 6))
plt.hist(df['{column}'], bins=30, edgecolor='black')
plt.title(f'Distribution of {column}')
plt.xlabel(column)
plt.ylabel('Frequency')
plt.grid(True, alpha=0.3)
plt.savefig(f'plots/{column}_histogram.png', dpi=300, bbox_inches='tight')
plt.show()"""
            
            elif plot_type == "scatter":
                x_col = parameters.get('x', df.columns[0] if 'df' in globals() else '')
                y_col = parameters.get('y', df.columns[1] if 'df' in globals() else '')
                return f"""# Create scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(df['{x_col}'], df['{y_col}'], alpha=0.6)
plt.title(f'{y_col} vs {x_col}')
plt.xlabel(x_col)
plt.ylabel(y_col)
plt.grid(True, alpha=0.3)
plt.savefig(f'plots/{x_col}_{y_col}_scatter.png', dpi=300, bbox_inches='tight')
plt.show()"""
            
        elif action == "compute_correlations":
            columns = parameters.get('columns', [])
            if columns:
                return f"""# Compute correlation matrix
corr = df[{columns}].corr()
print(corr)

# Visualize correlation
plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, square=True)
plt.title('Correlation Matrix')
plt.tight_layout()
plt.savefig('plots/correlation_matrix.png', dpi=300, bbox_inches='tight')
plt.show()"""
        
        elif action == "generate_report":
            return """# Report generation handled by backend
print("Report generation completed")"""
        
        # Default fallback
        return f"""# Execute: {step.get('name')}
# Action: {action}
print(f"Executing step {step.get('step_number')}")"""
    
    async def _execute_notebook(
        self,
        notebook_path: Path,
        exec_dir: Path
    ) -> Dict[str, Any]:
        """
        Execute Jupyter notebook
        
        Args:
            notebook_path: Path to notebook
            exec_dir: Execution directory
            
        Returns:
            Execution results
        """
        start_time = time.time()
        
        try:
            # Create output directory for plots
            plots_dir = exec_dir / "plots"
            plots_dir.mkdir(exist_ok=True)
            
            # Convert notebook to Python script
            exporter = PythonExporter()
            script, _ = exporter.from_file(notebook_path)
            
            # Write Python script
            script_path = exec_dir / "analysis.py"
            with open(script_path, "w") as f:
                f.write(script)
            
            # Execute Python script
            result = subprocess.run(
                ["python", str(script_path)],
                cwd=str(exec_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            # Collect outputs
            outputs = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
            logger.info(f"Notebook executed: {result.returncode}, time: {execution_time:.2f}s")
            
            return {
                "outputs": outputs,
                "execution_time": execution_time,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Notebook execution timeout")
            return {
                "outputs": {"error": "Execution timeout"},
                "execution_time": time.time() - start_time,
                "success": False
            }
        except Exception as e:
            logger.error(f"Notebook execution error: {str(e)}")
            return {
                "outputs": {"error": str(e)},
                "execution_time": time.time() - start_time,
                "success": False
            }
    
    async def _generate_report(
        self,
        exec_dir: Path,
        result: Dict[str, Any]
    ) -> Path:
        """
        Generate final PDF report
        
        Args:
            exec_dir: Execution directory
            result: Execution results
            
        Returns:
            Path to generated report
        """
        try:
            # Generate markdown report
            md_path = exec_dir / "report.md"
            with open(md_path, "w") as f:
                f.write("# AutoLabMate Experimental Report\n\n")
                f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("## Analysis Results\n\n")
                f.write("Analysis completed successfully.\n\n")
                
                if result.get("success"):
                    f.write(f"Execution time: {result['execution_time']:.2f} seconds\n\n")
                    
                    # Add summary of outputs if available
                    if result.get("outputs", {}).get("stdout"):
                        f.write("## Execution Log\n\n```\n")
                        f.write(result["outputs"]["stdout"])
                        f.write("\n```\n\n")
            
            # Convert to PDF using weasyprint or similar
            pdf_path = exec_dir / "report.pdf"
            try:
                from weasyprint import HTML
                from markdown import markdown
                
                # Convert markdown to HTML
                html_content = markdown(md_path.read_text())
                full_html = f"""
                <html>
                    <head>
                        <style>
                            body {{ font-family: Arial, sans-serif; padding: 40px; }}
                            h1 {{ color: #2c3e50; }}
                            h2 {{ color: #34495e; margin-top: 30px; }}
                            pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                        </style>
                    </head>
                    <body>{html_content}</body>
                </html>
                """
                
                HTML(string=full_html).write_pdf(pdf_path)
                
            except Exception as e:
                logger.warning(f"PDF generation failed: {str(e)}, using markdown")
                pdf_path = md_path
            
            logger.info(f"Report generated: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            raise

