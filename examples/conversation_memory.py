"""
Example demonstrating conversation memory across multiple turns
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
    """Demonstrate multi-turn conversation with memory."""
    
    print("=" * 50)
    print("Multi-turn Conversation with Memory")
    print("=" * 50)
    
    # Create the agent
    agent = create_agent()
    conversation_history = []
    
    # First turn
    result = agent.run("My name is Alice and I'm a software engineer", conversation_history)
    conversation_history = result['conversation_history']
    print(f"User: My name is Alice and I'm a software engineer")
    print(f"Agent: {result['response']}\n")
    
    # Second turn - agent should remember the name
    result = agent.run("What's my name?", conversation_history)
    conversation_history = result['conversation_history']
    print(f"User: What's my name?")
    print(f"Agent: {result['response']}\n")
    
    # Third turn - agent should remember the profession
    result = agent.run("What do I do for work?", conversation_history)
    conversation_history = result['conversation_history']
    print(f"User: What do I do for work?")
    print(f"Agent: {result['response']}\n")
    
    # Fourth turn - complex query using context
    result = agent.run("Can you calculate 15 * 8 and tell me if that's a good number of hours for me to work this week?", conversation_history)
    conversation_history = result['conversation_history']
    print(f"User: Can you calculate 15 * 8 and tell me if that's a good number of hours for me to work this week?")
    print(f"Agent: {result['response']}\n")


if __name__ == "__main__":
    main()

# Made with Bob
