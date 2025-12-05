"""
LangGraph Agent Implementation
A conversational agent with memory and tool-calling capabilities using LangGraph.
Supports both OpenAI and Watsonx LLMs via LiteLLM proxy.
"""

from typing import TypedDict, Annotated, Sequence, Optional, Literal, Union
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .tools import fetch_application, summarize_application
from .llm_providers import create_llm
from .config import LLMConfig, create_llm_config


# Define the agent state
class AgentState(TypedDict):
    """State of the agent conversation."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


class LangGraphAgent:
    """A conversational agent built with LangGraph."""
    
    def __init__(self, config: Optional[Union[LLMConfig, dict]] = None):
        """
        Initialize the LangGraph agent.
        
        Environment Variables:
            LLM_PROVIDER: The LLM provider to use (default: "openai")
            MODEL_NAME: The model name (default: "gpt-4o-mini")
            TEMPERATURE: The temperature for response generation (default: 0.7)
            WATSONX_API_KEY: Watsonx API key (required for Watsonx provider)
            WATSONX_PROJECT_ID: Watsonx project ID (required for Watsonx provider)
            WATSONX_URL: Watsonx URL (default: "https://us-south.ml.cloud.ibm.com")
            VLLM_API_BASE: vLLM API base URL (required for vLLM provider)
            VLLM_API_KEY: vLLM API key (optional, for authenticated endpoints)
        
        Args:
            config: LLMConfig object or dict with configuration. If None, loads from environment variables.
        """
        self.tools = [fetch_application, summarize_application]
        
        # Create or use provided configuration
        if config is not None:
            if isinstance(config, dict):
                self.config = create_llm_config(**config)
            else:
                self.config = config
        else:
            # Create config from environment variables
            self.config = LLMConfig.from_env()
        
        # Store config values for easy access
        self.provider = self.config.provider
        self.model_name = self.config.model_name
        self.temperature = self.config.temperature
        
        # Create LLM using the configuration
        self.llm = create_llm(**self.config.to_dict())
        
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build the graph
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        return workflow
    
    def _call_model(self, state: AgentState) -> AgentState:
        """Call the language model with the current state."""
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if the agent should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, continue to tools node
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        
        # Otherwise, end the conversation
        return "end"
    
    def run(self, user_input: str, conversation_history: Optional[list] = None) -> dict:
        """
        Run the agent with a user input.
        
        Args:
            user_input: The user's message
            conversation_history: Optional list of previous messages
            
        Returns:
            Dictionary containing the response and updated conversation history
        """
        # Initialize messages
        messages = conversation_history if conversation_history else []
        messages.append(HumanMessage(content=user_input))
        
        # Run the graph
        result = self.app.invoke({"messages": messages})
        
        # Extract the final response
        final_messages = result["messages"]
        last_message = final_messages[-1]
        
        return {
            "response": last_message.content,
            "conversation_history": final_messages,
            "tool_calls": getattr(last_message, "tool_calls", [])
        }
    
    def stream(self, user_input: str, conversation_history: Optional[list] = None):
        """
        Stream the agent's response.
        
        Args:
            user_input: The user's message
            conversation_history: Optional list of previous messages
            
        Yields:
            Chunks of the agent's response
        """
        messages = conversation_history if conversation_history else []
        messages.append(HumanMessage(content=user_input))
        
        for chunk in self.app.stream({"messages": messages}):
            yield chunk


def create_agent(config: Optional[Union[LLMConfig, dict]] = None) -> LangGraphAgent:
    """
    Factory function to create a LangGraph agent.
    
    Environment Variables:
        LLM_PROVIDER: The LLM provider to use (default: "openai")
        MODEL_NAME: The model name (default: "gpt-4o-mini")
        TEMPERATURE: The temperature for response generation (default: 0.7)
        WATSONX_API_KEY: Watsonx API key (required for Watsonx provider)
        WATSONX_PROJECT_ID: Watsonx project ID (required for Watsonx provider)
        WATSONX_URL: Watsonx URL (default: "https://us-south.ml.cloud.ibm.com")
        VLLM_API_BASE: vLLM API base URL (required for vLLM provider)
        VLLM_API_KEY: vLLM API key (optional, for authenticated endpoints)
    
    Args:
        config: LLMConfig object or dict with configuration. If None, loads from environment variables.
        
    Returns:
        A configured LangGraphAgent instance
        
    Examples:
        # Create agent from environment variables
        agent = create_agent()
        
        # Create agent with LLMConfig object
        config = LLMConfig(provider="watsonx", model_name="ibm/granite-13b-chat-v2")
        agent = create_agent(config)
        
        # Create agent with config dictionary
        agent = create_agent({"provider": "openai", "model_name": "gpt-4o-mini"})
    """
    return LangGraphAgent(config=config)

# Made with Bob
