"""
Example: Using the agent with vLLM via LiteLLM proxy

This example demonstrates how to use the LangGraph agent with vLLM
as the LLM provider through LiteLLM's OpenAI-compatible API support.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.slo_agent import create_agent

# Load environment variables
load_dotenv()


def main():
    """Run the agent with vLLM."""
    
    # Create agent with vLLM provider using config
    # The agent will use LiteLLM to connect to vLLM's OpenAI-compatible API
    from src.slo_agent import LLMConfig
    
    config = LLMConfig(
        provider="vllm",
        model_name="meta-llama/Llama-2-7b-chat-hf",
        temperature=0.7
        # vLLM credentials are loaded from environment variables automatically
    )
    agent = create_agent(config)
    
    print("vLLM Agent initialized successfully!")
    print("=" * 50)
    
    # Example 1: Simple question
    print("\nExample 1: Simple question")
    print("-" * 50)
    result = agent.run("What is the capital of France?")
    print(f"Response: {result['response']}")
    
    # Example 2: Conversation with memory
    print("\n\nExample 3: Conversation with memory")
    print("-" * 50)
    conversation_history = []
    
    # First message
    result1 = agent.run(
        "My name is Alice and I love Python programming.",
        conversation_history=conversation_history
    )
    print(f"User: My name is Alice and I love Python programming.")
    print(f"Agent: {result1['response']}")
    
    # Second message (agent should remember the name)
    result2 = agent.run(
        "What's my name and what do I love?",
        conversation_history=result1['conversation_history']
    )
    print(f"\nUser: What's my name and what do I love?")
    print(f"Agent: {result2['response']}")
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    # Check if required environment variables are set
    vllm_api_base = os.getenv("VLLM_API_BASE")
    
    if not vllm_api_base:
        print("Error: Missing required environment variable:")
        print("  - VLLM_API_BASE")
        print("\nPlease set this variable in your .env file or environment.")
        print("See .env.example for reference.")
        print("\nExample: VLLM_API_BASE=http://localhost:8000/v1")
    else:
        main()

# Made with Bob