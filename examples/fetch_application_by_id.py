"""
Example: Fetch application by Instana ID using MCP

This example demonstrates how to fetch application configuration
from Instana using a specific application ID via the Instana MCP server (stdio mode).

Prerequisites:
1. Set INSTANA_BASE_URL and INSTANA_API_TOKEN in your .env file
2. Set INSTANA_MCP_SERVER_PATH (default: npx) and INSTANA_MCP_SERVER_ARGS (default: -y @instana/mcp-server-instana)
3. Ensure the Instana MCP server package is installed: npm install -g @instana/mcp-server-instana
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
    """Fetch application by Instana ID."""
    
    print("=" * 50)
    print("Fetch Application by Instana ID (MCP stdio mode)")
    print("=" * 50)
    print(f"MCP Server: {os.getenv('INSTANA_MCP_SERVER_PATH', 'npx')} {os.getenv('INSTANA_MCP_SERVER_ARGS', '-y @instana/mcp-server-instana')}")
    print("=" * 50)
    
    # Create the agent
    print("\nInitializing agent...")
    agent = create_agent()
    print(f"Agent initialized with model: {agent.model_name}\n")
    
    # Instana application ID
    app_id = "8rwDuom6TGSGB-YhFfn4VA"
    
    # Example 1: Direct query with application ID
    print("=" * 50)
    print("Example 1: Fetch Application by ID")
    print("=" * 50)
    
    query = f"Fetch the application configuration from Instana for application ID {app_id}"
    print(f"User: {query}")
    
    result = agent.run(query)
    print(f"Agent: {result['response']}")
    
    if result['tool_calls']:
        print(f"\nTools used: {[tc['name'] for tc in result['tool_calls']]}")
    print()
    
    # Example 2: Conversational query
    print("=" * 50)
    print("Example 2: Conversational Query")
    print("=" * 50)
    
    query = f"Can you get me the details for the application with ID {app_id} from Instana?"
    print(f"User: {query}")
    
    result = agent.run(query)
    print(f"Agent: {result['response']}")
    
    if result['tool_calls']:
        print(f"\nTools used: {[tc['name'] for tc in result['tool_calls']]}")
    print()
    
    # Example 3: Follow-up question with context
    print("=" * 50)
    print("Example 3: Follow-up with Context")
    print("=" * 50)
    
    conversation_history = []
    
    # First query
    query1 = f"Fetch application {app_id} from Instana"
    print(f"User: {query1}")
    
    result1 = agent.run(query1, conversation_history)
    conversation_history = result1['conversation_history']
    print(f"Agent: {result1['response']}\n")
    
    # Follow-up query
    query2 = "What services are configured for this application?"
    print(f"User: {query2}")
    
    result2 = agent.run(query2, conversation_history)
    print(f"Agent: {result2['response']}\n")
    
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
        print("The examples will use mock data instead of real Instana data\n")
    else:
        print(f"Using Instana instance: {instana_base_url}\n")
    
    main()

# Made with Bob