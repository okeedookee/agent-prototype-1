"""
Example: Summarize application from Instana using MCP

This example demonstrates how to use the summarize_application tool
to fetch and format application configuration from Instana.

Prerequisites:
1. Set INSTANA_BASE_URL and INSTANA_API_TOKEN in your .env file
2. Set INSTANA_MCP_SERVER_PATH and INSTANA_MCP_SERVER_ARGS for your MCP server
3. Ensure the Instana MCP server is accessible
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
    """Summarize application from Instana."""
    
    print("=" * 50)
    print("Summarize Application from Instana")
    print("=" * 50)
    print(f"MCP Server: {os.getenv('INSTANA_MCP_SERVER_PATH', 'npx')} {os.getenv('INSTANA_MCP_SERVER_ARGS', '-y @instana/mcp-server-instana')}")
    print("=" * 50)
    
    # Create the agent
    print("\nInitializing agent...")
    agent = create_agent()
    print(f"Agent initialized with model: {agent.model_name}\n")
    
    # Example application IDs
    app_ids = [
        "HFoOdED4Qlu_0MPRQBbOuw",
        "8rwDuom6TGSGB-YhFfn4VA"
    ]
    
    # Example 1: Direct summarization request
    print("=" * 50)
    print("Example 1: Summarize Application")
    print("=" * 50)
    
    query = f"Summarize the application with ID {app_ids[0]}"
    print(f"User: {query}")
    
    result = agent.run(query)
    print(f"\nAgent: {result['response']}")
    
    if result['tool_calls']:
        print(f"\nTools used: {[tc['name'] for tc in result['tool_calls']]}")
    print()
    
    # Example 2: Conversational request
    print("=" * 50)
    print("Example 2: Conversational Request")
    print("=" * 50)
    
    query = f"Can you give me a summary of the Instana application {app_ids[1]}?"
    print(f"User: {query}")
    
    result = agent.run(query)
    print(f"\nAgent: {result['response']}")
    
    if result['tool_calls']:
        print(f"\nTools used: {[tc['name'] for tc in result['tool_calls']]}")
    print()
    
    # Example 3: Multiple applications with context
    print("=" * 50)
    print("Example 3: Compare Applications")
    print("=" * 50)
    
    conversation_history = []
    
    # First application
    query1 = f"Summarize application {app_ids[0]}"
    print(f"User: {query1}")
    
    result1 = agent.run(query1, conversation_history)
    conversation_history = result1['conversation_history']
    print(f"\nAgent: {result1['response']}\n")
    
    # Second application
    query2 = f"Now summarize application {app_ids[1]}"
    print(f"User: {query2}")
    
    result2 = agent.run(query2, conversation_history)
    conversation_history = result2['conversation_history']
    print(f"\nAgent: {result2['response']}\n")
    
    # Comparison question
    query3 = "What are the main differences between these two applications?"
    print(f"User: {query3}")
    
    result3 = agent.run(query3, conversation_history)
    print(f"\nAgent: {result3['response']}\n")
    
    print("=" * 50)
    print("Examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    # Check if Instana credentials are configured
    instana_base_url = os.getenv("INSTANA_BASE_URL")
    instana_api_token = os.getenv("INSTANA_API_TOKEN")
    
    if not instana_base_url or not instana_api_token:
        print("Warning: Instana credentials not configured")
        print("Set INSTANA_BASE_URL and INSTANA_API_TOKEN in your .env file")
        print("The examples will fail without proper credentials\n")
    else:
        print(f"Using Instana instance: {instana_base_url}\n")
    
    main()

# Made with Bob