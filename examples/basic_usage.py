"""
Basic usage example of the SLO Agent
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
    """Run basic examples with the agent."""
    
    # Create the agent (uses environment variables or defaults)
    print("Initializing SLO Agent...")
    agent = create_agent()
    print(f"Agent initialized with model: {agent.model_name}\n")
    
    # Example 1: Simple conversation
    print("=" * 50)
    print("Example 1: Simple Conversation")
    print("=" * 50)
    
    result = agent.run("Hello! What can you help me with?")
    print(f"User: Hello! What can you help me with?")
    print(f"Agent: {result['response']}\n")
    
    # Example 2: Using the calculator tool
    print("=" * 50)
    print("Example 2: Using Calculator Tool")
    print("=" * 50)
    
    result = agent.run("What is 25 * 47 + 123?")
    print(f"User: What is 25 * 47 + 123?")
    print(f"Agent: {result['response']}")
    if result['tool_calls']:
        print(f"Tools used: {[tc['name'] for tc in result['tool_calls']]}\n")
    
    # Example 3: Using the fetch_application tool
    print("=" * 50)
    print("Example 3: Using Fetch Application Tool")
    print("=" * 50)
    
    result = agent.run("Fetch details for the robot-shop application")
    print(f"User: Fetch details for the robot-shop application")
    print(f"Agent: {result['response']}\n")


if __name__ == "__main__":
    main()

# Made with Bob
