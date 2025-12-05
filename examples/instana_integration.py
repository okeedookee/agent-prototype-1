"""
Example: Using the fetch_application tool with Instana MCP integration

This example demonstrates how to use the fetch_application tool
to retrieve application configuration from Instana via the MCP server (stdio mode).

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
    """Demonstrate fetch_application tool with Instana integration."""
    
    print("=" * 50)
    print("Instana Integration Example")
    print("=" * 50)
    
    # Create the agent
    print("\nInitializing agent...")
    agent = create_agent()
    print("Agent initialized!\n")
    
    # Example 1: Fetch application without Instana (mock data)
    print("=" * 50)
    print("Example 1: Fetch Application (Mock Data)")
    print("=" * 50)
    
    result = agent.run("Fetch details for the robot-shop application")
    print(f"User: Fetch details for the robot-shop application")
    print(f"Agent: {result['response']}\n")
    
    # Example 2: Fetch application from Instana with application ID
    print("=" * 50)
    print("Example 2: Fetch Application from Instana")
    print("=" * 50)
    
    # Replace with your actual Instana application ID
    instana_app_id = "your-instana-application-id"
    
    result = agent.run(
        f"Fetch details for the robot-shop application with Instana ID {instana_app_id}"
    )
    print(f"User: Fetch details for the robot-shop application with Instana ID {instana_app_id}")
    print(f"Agent: {result['response']}\n")
    
    # Example 3: Conversational query about application
    print("=" * 50)
    print("Example 3: Conversational Query")
    print("=" * 50)
    
    result = agent.run(
        "Can you get me the configuration for application ID abc123 from Instana?"
    )
    print(f"User: Can you get me the configuration for application ID abc123 from Instana?")
    print(f"Agent: {result['response']}\n")


if __name__ == "__main__":
    # Check if Instana credentials are configured
    instana_base_url = os.getenv("INSTANA_BASE_URL")
    instana_api_token = os.getenv("INSTANA_API_TOKEN")
    
    if not instana_base_url or not instana_api_token:
        print("Warning: Instana credentials not configured")
        print("Set INSTANA_BASE_URL and INSTANA_API_TOKEN in your .env file")
        print("The examples will use mock data instead of real Instana data\n")
    
    main()

# Made with Bob