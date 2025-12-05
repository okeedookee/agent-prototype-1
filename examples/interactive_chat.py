"""
Interactive chat example with the SLO Agent
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
    """Run an interactive chat session with the agent."""
    
    print("=" * 50)
    print("Interactive Chat Mode")
    print("=" * 50)
    print("Type 'quit', 'exit', or 'q' to end the conversation\n")
    
    # Create the agent
    agent = create_agent()
    conversation_history = []
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            result = agent.run(user_input, conversation_history)
            conversation_history = result['conversation_history']
            print(f"Agent: {result['response']}\n")
            
            # Show tool usage if any
            if result['tool_calls']:
                tool_names = [tc['name'] for tc in result['tool_calls']]
                print(f"[Tools used: {', '.join(tool_names)}]\n")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")


if __name__ == "__main__":
    main()

# Made with Bob
