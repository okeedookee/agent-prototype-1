"""
Example: Using the agent with IBM Watsonx via LiteLLM proxy

This example demonstrates how to use the LangGraph agent with IBM Watsonx
as the LLM provider through LiteLLM's built-in proxy support.
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
    """Run the agent with Watsonx."""
    
    # Create agent with Watsonx provider using config
    # The agent will use LiteLLM as a proxy to access Watsonx
    from src.slo_agent import LLMConfig
    
    config = LLMConfig(
        provider="watsonx",
        model_name=os.getenv("MODEL_NAME", "ibm/granite-13b-chat-v2"),
        temperature=0.7
        # Credentials are loaded from environment variables automatically
    )
    agent = create_agent(config)
    
    print("Watsonx Agent initialized successfully!")
    print("=" * 50)
    
    # Example 1: Simple question
    print("\nExample 1: Simple question")
    print("-" * 50)
    result = agent.run("What is the capital of France?")
    print(f"Response: {result['response']}")
    
    # Example 2: Using tools
    print("\n\nExample 2: Using calculator tool")
    print("-" * 50)
    result = agent.run("What is 25 * 47?")
    print(f"Response: {result['response']}")
    if result['tool_calls']:
        print(f"Tools used: {[tc['name'] for tc in result['tool_calls']]}")
    
    # Example 3: Conversation with memory
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
    required_vars = ["WATSONX_API_KEY", "WATSONX_PROJECT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("See .env.example for reference.")
    else:
        main()

# Made with Bob
