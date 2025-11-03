"""
Planner Agent - Generates analysis plans from datasets
Uses LLM to reason about appropriate analysis steps
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
from openai import OpenAI

try:
    from tools.vector_store import VectorStore
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.vector_store import VectorStore

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    Planner Agent generates step-by-step analysis plans
    
    Responsibilities:
    - Analyze dataset structure and content
    - Generate appropriate analysis pipeline
    - Estimate execution time and complexity
    - Provide confidence score for plan quality
    """
    
    def __init__(self, vector_store: VectorStore):
        """
        Initialize Planner Agent
        
        Args:
            vector_store: Vector store for RAG context
        """
        self.vector_store = vector_store
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "mock")
        ) if not os.getenv("MOCK_MODE", "true").lower() == "true" else None
        self.use_mock = os.getenv("MOCK_MODE", "true").lower() == "true"
    
    async def generate_plan(
        self,
        dataset_path: str,
        description: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an analysis plan for the given dataset
        
        Args:
            dataset_path: Path to uploaded dataset
            description: Optional experiment description
            additional_context: Additional context for planning
            
        Returns:
            Dictionary with plan details (steps, duration, confidence)
        """
        try:
            logger.info(f"Generating plan for dataset: {dataset_path}")
            
            # Analyze dataset structure
            dataset_info = await self._analyze_dataset(dataset_path)
            
            # Retrieve relevant context from vector store
            context = await self._get_rag_context(dataset_info)
            
            # Generate plan using LLM or mock
            if self.use_mock:
                plan = self._generate_mock_plan(dataset_info, description)
            else:
                plan = await self._generate_llm_plan(
                    dataset_info,
                    description,
                    context,
                    additional_context
                )
            
            logger.info(f"Plan generated with {len(plan['steps'])} steps")
            
            return plan
            
        except Exception as e:
            logger.error(f"Plan generation error: {str(e)}")
            raise
    
    async def _analyze_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """
        Analyze dataset structure and infer characteristics
        
        Args:
            dataset_path: Path to dataset file
            
        Returns:
            Dictionary with dataset metadata
        """
        try:
            if dataset_path.startswith("/uploads/"):
                dataset_path = f"/app{dataset_path}"

            path = Path(dataset_path)
            
            # Ensure correct path inside Docker container
            if not os.path.exists(dataset_path):
                alt_path = f"/app{dataset_path}" if dataset_path.startswith("/uploads") else dataset_path
                if os.path.exists(alt_path):
                    dataset_path = alt_path
            # Detect file type and load
            if path.suffix == ".csv":
                df = pd.read_csv(dataset_path, nrows=100)  # Sample for speed
            elif path.suffix == ".json":
                df = pd.read_json(dataset_path)
            else:
                return {"error": f"Unsupported file type: {path.suffix}"}
            
            return {
                "file_type": path.suffix,
                "file_size": path.stat().st_size,
                "columns": list(df.columns),
                "row_count": len(df),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "sample_rows": df.head(3).to_dict("records"),
                "has_nulls": df.isnull().any().to_dict(),
                "numeric_columns": list(df.select_dtypes(include=['number']).columns),
                "categorical_columns": list(df.select_dtypes(include=['object']).columns)
            }
            
        except Exception as e:
            logger.error(f"Dataset analysis error: {str(e)}")
            return {"error": str(e)}
    
    async def _get_rag_context(self, dataset_info: Dict) -> List[Dict]:
        """
        Retrieve relevant context from vector store
        
        Args:
            dataset_info: Dataset metadata
            
        Returns:
            List of relevant context documents
        """
        try:
            # Query vector store with dataset characteristics
            query_text = f"Dataset with columns: {', '.join(dataset_info.get('columns', []))}"
            
            results = await self.vector_store.search(
                query=query_text,
                top_k=5
            )
            
            return results
            
        except Exception as e:
            logger.warning(f"RAG context retrieval error: {str(e)}")
            return []
    
    def _generate_mock_plan(
        self,
        dataset_info: Dict,
        description: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate a mock analysis plan (for demo/testing)
        
        Args:
            dataset_info: Dataset metadata
            description: Optional description
            
        Returns:
            Mock plan dictionary
        """
        # Define standard analysis steps based on data characteristics
        steps = [
            {
                "step_number": 1,
                "name": "Data Loading and Validation",
                "action": "load_data",
                "parameters": {
                    "file_path": dataset_info.get("file_path", ""),
                    "file_type": dataset_info.get("file_type", ".csv")
                },
                "expected_output": "validated_dataframe",
                "estimated_time": "30s"
            },
            {
                "step_number": 2,
                "name": "Descriptive Statistics",
                "action": "compute_stats",
                "parameters": {
                    "columns": dataset_info.get("numeric_columns", [])
                },
                "expected_output": "statistics_summary",
                "estimated_time": "1m"
            }
        ]
        
        # Add plotting step if numeric columns exist
        if dataset_info.get("numeric_columns"):
            steps.append({
                "step_number": len(steps) + 1,
                "name": f"Visualization: {dataset_info['numeric_columns'][0]} Distribution",
                "action": "create_plot",
                "parameters": {
                    "plot_type": "histogram",
                    "column": dataset_info['numeric_columns'][0]
                },
                "expected_output": "plot_image",
                "estimated_time": "1m"
            })
        
        # Add correlation analysis for multiple numeric columns
        numeric_cols = dataset_info.get("numeric_columns", [])
        if len(numeric_cols) >= 2:
            steps.append({
                "step_number": len(steps) + 1,
                "name": "Correlation Analysis",
                "action": "compute_correlations",
                "parameters": {
                    "columns": numeric_cols[:5]
                },
                "expected_output": "correlation_matrix",
                "estimated_time": "2m"
            })
        
        # Add report generation step
        steps.append({
            "step_number": len(steps) + 1,
            "name": "Generate Report",
            "action": "generate_report",
            "parameters": {
                "format": "pdf",
                "include_plots": True
            },
            "expected_output": "lab_report.pdf",
            "estimated_time": "3m"
        })
        
        return {
            "steps": steps,
            "estimated_duration": f"{len(steps) * 2} minutes",
            "confidence_score": 0.85,
            "metadata": {
                "generated_by": "mock_planner",
                "dataset_characteristics": dataset_info
            }
        }
    
    async def _generate_llm_plan(
        self,
        dataset_info: Dict,
        description: Optional[str],
        context: List[Dict],
        additional_context: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Generate plan using OpenAI LLM
        
        Args:
            dataset_info: Dataset metadata
            description: Experiment description
            context: RAG context from vector store
            additional_context: Additional context
            
        Returns:
            Generated plan dictionary
        """
        # Build prompt for LLM
        prompt = self._build_planning_prompt(
            dataset_info,
            description,
            context,
            additional_context
        )
        
        # Call OpenAI API
        response = self.openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": "You are an expert data analyst that generates step-by-step analysis plans for lab experiments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        result = json.loads(response.choices[0].message.content)
        
        # Validate and format result
        plan = {
            "steps": result.get("steps", []),
            "estimated_duration": result.get("estimated_duration", "10 minutes"),
            "confidence_score": result.get("confidence_score", 0.7),
            "metadata": {
                "generated_by": "llm_planner",
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "dataset_characteristics": dataset_info
            }
        }
        
        return plan
    
    def _build_planning_prompt(
        self,
        dataset_info: Dict,
        description: Optional[str],
        context: List[Dict],
        additional_context: Optional[Dict]
    ) -> str:
        """Build LLM prompt for plan generation"""
        
        prompt = f"""Generate a step-by-step analysis plan for a lab experiment dataset.

Dataset Information:
- File type: {dataset_info.get('file_type', 'unknown')}
- Columns: {', '.join(dataset_info.get('columns', []))}
- Number of rows: {dataset_info.get('row_count', 0)}
- Numeric columns: {', '.join(dataset_info.get('numeric_columns', []))}
- Categorical columns: {', '.join(dataset_info.get('categorical_columns', []))}

Description: {description or 'Not provided'}

Previous similar experiments:
{json.dumps(context[:3], indent=2) if context else 'None'}

Additional context: {json.dumps(additional_context, indent=2) if additional_context else 'None'}

Generate a JSON response with this exact structure:
{{
    "steps": [
        {{
            "step_number": 1,
            "name": "Step name",
            "action": "action_type",
            "parameters": {{"key": "value"}},
            "expected_output": "output_description",
            "estimated_time": "duration"
        }}
    ],
    "estimated_duration": "total time",
    "confidence_score": 0.0-1.0
}}

The steps should follow this sequence:
1. Data loading and validation
2. Exploratory data analysis (descriptive statistics, distributions)
3. Statistical analysis (correlations, significance tests)
4. Visualizations (plots, charts)
5. Interpretation and conclusions
6. Report generation

Return only valid JSON, no additional text.
"""
        return prompt

