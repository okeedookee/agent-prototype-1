"""
Example: Using the LLM Provider Factory directly

This example demonstrates how to use the LLM provider factory
to create LLM instances independently of the agent.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.slo_agent import create_llm, LLMProviderFactory

# Load environment variables
load_dotenv()


def main():
    """Demonstrate direct usage of the LLM provider factory."""
    
    print("=" * 50)
    print("LLM Provider Factory Examples")
    print("=" * 50)
    
    # Example 1: Create OpenAI LLM using convenience function
    print("\nExample 1: Creating OpenAI LLM")
    print("-" * 50)
    openai_llm = create_llm(
        provider="openai",
        model_name="gpt-4o-mini",
        temperature=0.7
    )
    print(f"Created OpenAI LLM: {openai_llm.model}")
    
    # Example 2: Create Watsonx LLM using factory class
    print("\nExample 2: Creating Watsonx LLM")
    print("-" * 50)
    try:
        watsonx_llm = LLMProviderFactory.create_llm(
            provider="watsonx",
            model_name="ibm/granite-13b-chat-v2",
            temperature=0.7
        )
        print(f"Created Watsonx LLM: {watsonx_llm.model}")
    except ValueError as e:
        print(f"Note: {e}")
        print("Set WATSONX_API_KEY and WATSONX_PROJECT_ID to use Watsonx")
    
    # Example 3: Using environment variable for model name
    print("\nExample 3: Using MODEL_NAME environment variable")
    print("-" * 50)
    llm = create_llm(provider="openai", temperature=0.5)
    print(f"Created LLM with model from env: {llm.model}")
    
    # Example 4: Test the LLM with a simple query
    print("\nExample 4: Testing the LLM")
    print("-" * 50)
    response = openai_llm.invoke("Say hello in one sentence")
    print(f"Response: {response.content}")
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()

# Made with Bob