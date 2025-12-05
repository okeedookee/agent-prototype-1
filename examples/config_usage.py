"""
Example: Using LLMConfig object for agent configuration

This example demonstrates how to use the LLMConfig object
to configure the agent with different approaches.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.slo_agent import create_agent, LLMConfig, create_llm_config

# Load environment variables
load_dotenv()


def main():
    """Demonstrate different ways to configure the agent using LLMConfig."""
    
    print("=" * 50)
    print("LLMConfig Usage Examples")
    print("=" * 50)
    
    # Example 1: Create agent with environment variables (default)
    print("\nExample 1: Using Environment Variables")
    print("-" * 50)
    agent1 = create_agent()
    print(f"Agent created with config: {agent1.config}")
    
    result = agent1.run("What is 5 + 3?")
    print(f"Response: {result['response']}\n")
    
    # Example 2: Create agent with LLMConfig object
    print("\nExample 2: Using LLMConfig Object")
    print("-" * 50)
    config = LLMConfig(
        provider="watsonx",
        model_name="ibm/granite-13b-chat-v2",
        temperature=0.5
    )
    agent2 = create_agent(config=config)
    print(f"Agent created with config: {agent2.config}")
    
    result = agent2.run("What is 10 * 4?")
    print(f"Response: {result['response']}\n")
    
    # Example 3: Create agent with config dictionary
    print("\nExample 3: Using Config Dictionary")
    print("-" * 50)
    config_dict = {
        "provider": "openai",
        "model_name": "gpt-4o-mini",
        "temperature": 0.7
    }
    agent3 = create_agent(config=config_dict)
    print(f"Agent created with config: {agent3.config}")
    
    result = agent3.run("What is 15 - 7?")
    print(f"Response: {result['response']}\n")
    
    # Example 4: Create config from factory function
    print("\nExample 4: Using create_llm_config Factory")
    print("-" * 50)
    config = create_llm_config(
        provider="vllm",
        model_name="meta-llama/Llama-2-7b-chat-hf",
        temperature=0.8,
        vllm_api_base="http://localhost:8000/v1"
    )
    agent4 = create_agent(config=config)
    print(f"Agent created with config: {agent4.config}")
    
    result = agent4.run("What is 20 / 5?")
    print(f"Response: {result['response']}\n")
    
    # Example 5: Create config from environment only
    print("\nExample 5: Using LLMConfig.from_env()")
    print("-" * 50)
    config = LLMConfig.from_env()
    agent5 = create_agent(config=config)
    print(f"Agent created with config: {agent5.config}")
    
    result = agent5.run("What is 100 - 25?")
    print(f"Response: {result['response']}\n")
    
    # Example 6: Convert config to dictionary
    print("\nExample 6: Config to Dictionary")
    print("-" * 50)
    config = LLMConfig(
        provider="watsonx",
        model_name="ibm/granite-13b-chat-v2",
        temperature=0.6
    )
    config_dict = config.to_dict()
    print(f"Config as dictionary: {config_dict}\n")
    
    print("=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()

# Made with Bob