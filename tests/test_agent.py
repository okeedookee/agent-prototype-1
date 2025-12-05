"""
Unit tests for the SLO Agent
"""

import pytest
from unittest.mock import Mock, patch
from src.slo_agent import create_agent, LangGraphAgent


class TestLangGraphAgent:
    """Test cases for LangGraphAgent class."""
    
    def test_agent_creation(self):
        """Test that agent can be created successfully."""
        with patch('src.slo_agent.agent.ChatOpenAI'):
            agent = create_agent()
            assert isinstance(agent, LangGraphAgent)
            assert agent.tools is not None
            assert len(agent.tools) == 3
    
    def test_agent_with_custom_params(self):
        """Test agent creation with custom parameters."""
        with patch('src.slo_agent.agent.ChatOpenAI') as mock_llm:
            agent = create_agent(model_name="gpt-4", temperature=0.5)
            mock_llm.assert_called_once_with(model="gpt-4", temperature=0.5)
    
    def test_state_graph_structure(self):
        """Test that the state graph is properly structured."""
        with patch('src.slo_agent.agent.ChatOpenAI'):
            agent = create_agent()
            assert agent.graph is not None
            assert agent.app is not None


class TestTools:
    """Test cases for agent tools."""
    
    def test_calculator_tool(self):
        """Test calculator tool functionality."""
        from src.slo_agent.tools import calculator
        
        result = calculator.invoke({"expression": "2 + 2"})
        assert "4" in result
        
        result = calculator.invoke({"expression": "10 * 5"})
        assert "50" in result
    
    def test_calculator_error_handling(self):
        """Test calculator handles invalid expressions."""
        from src.slo_agent.tools import calculator
        
        result = calculator.invoke({"expression": "invalid"})
        assert "Error" in result
    
    def test_search_tool(self):
        """Test search tool returns expected format."""
        from src.slo_agent.tools import search_tool
        
        result = search_tool.invoke({"query": "test query"})
        assert "test query" in result
        assert "Search results" in result
    
    def test_weather_tool(self):
        """Test weather tool returns expected format."""
        from src.slo_agent.tools import get_weather
        
        result = get_weather.invoke({"location": "New York"})
        assert "New York" in result
        assert "weather" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
