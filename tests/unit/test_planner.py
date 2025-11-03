"""
Unit tests for PlannerAgent
"""

import pytest
from agents.planner import PlannerAgent
from tools.vector_store import VectorStore
from unittest.mock import Mock, patch


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing"""
    store = Mock(spec=VectorStore)
    store.search.return_value = []
    store.is_available.return_value = True
    return store


@pytest.fixture
def planner_agent(mock_vector_store):
    """Create PlannerAgent instance with mocked dependencies"""
    return PlannerAgent(mock_vector_store)


@pytest.mark.asyncio
async def test_analyze_dataset_csv(planner_agent, tmp_path):
    """Test dataset analysis for CSV files"""
    # Create test CSV
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "col1,col2,col3\n"
        "1.0,2.0,3.0\n"
        "4.0,5.0,6.0\n"
        "7.0,8.0,9.0\n"
    )
    
    result = await planner_agent._analyze_dataset(str(csv_file))
    
    assert "file_type" in result
    assert result["file_type"] == ".csv"
    assert "columns" in result
    assert len(result["columns"]) == 3
    assert "col1" in result["columns"]


@pytest.mark.asyncio
async def test_generate_mock_plan(planner_agent):
    """Test mock plan generation"""
    dataset_info = {
        "file_type": ".csv",
        "columns": ["sensor1", "sensor2", "temperature"],
        "numeric_columns": ["sensor1", "sensor2", "temperature"],
        "categorical_columns": [],
        "row_count": 100
    }
    
    plan = planner_agent._generate_mock_plan(dataset_info, "Test experiment")
    
    assert "steps" in plan
    assert len(plan["steps"]) >= 4  # At least 4 steps
    assert "estimated_duration" in plan
    assert "confidence_score" in plan
    assert plan["confidence_score"] > 0


@pytest.mark.asyncio
async def test_plan_steps_contain_required_fields(planner_agent):
    """Test that generated plan steps have required fields"""
    dataset_info = {
        "file_type": ".csv",
        "columns": ["sensor1", "sensor2"],
        "numeric_columns": ["sensor1", "sensor2"],
        "categorical_columns": [],
        "row_count": 50
    }
    
    plan = planner_agent._generate_mock_plan(dataset_info, None)
    
    for step in plan["steps"]:
        assert "step_number" in step
        assert "name" in step
        assert "action" in step
        assert "estimated_time" in step


@pytest.mark.asyncio
async def test_full_plan_generation(planner_agent, tmp_path):
    """Test complete plan generation workflow"""
    # Create test dataset
    csv_file = tmp_path / "experiment.csv"
    csv_file.write_text(
        "timestamp,value\n"
        "2024-01-01 10:00:00,42.5\n"
        "2024-01-01 10:05:00,43.2\n"
        "2024-01-01 10:10:00,44.1\n"
    )
    
    plan_result = await planner_agent.generate_plan(
        dataset_path=str(csv_file),
        description="Test experiment"
    )
    
    assert "steps" in plan_result
    assert "estimated_duration" in plan_result
    assert "confidence_score" in plan_result
    assert len(plan_result["steps"]) > 0


@pytest.mark.asyncio
async def test_planner_with_numeric_columns_only(planner_agent):
    """Test plan generation with only numeric columns"""
    dataset_info = {
        "file_type": ".csv",
        "columns": ["x", "y", "z"],
        "numeric_columns": ["x", "y", "z"],
        "categorical_columns": [],
        "row_count": 1000
    }
    
    plan = planner_agent._generate_mock_plan(dataset_info, None)
    
    # Should include plotting step
    has_plot_step = any("plot" in step.get("action", "") for step in plan["steps"])
    assert has_plot_step
    
    # Should include correlation step
    has_corr_step = any("correlation" in step.get("action", "").lower() or 
                       "correlation" in step.get("name", "").lower() 
                       for step in plan["steps"])
    assert has_corr_step or len(dataset_info["numeric_columns"]) < 2


def test_build_planning_prompt(planner_agent):
    """Test LLM prompt construction"""
    dataset_info = {
        "file_type": ".csv",
        "columns": ["col1", "col2"],
        "numeric_columns": ["col1"],
        "categorical_columns": ["col2"]
    }
    
    prompt = planner_agent._build_planning_prompt(
        dataset_info,
        "Test description",
        [],
        None
    )
    
    assert "Test description" in prompt
    assert "col1" in prompt
    assert "JSON" in prompt
    assert "steps" in prompt.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

