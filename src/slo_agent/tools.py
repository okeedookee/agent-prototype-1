"""
Tools for the LangGraph Agent
Define custom tools that the agent can use.
"""

import json
import os
import subprocess
from typing import Optional
from langchain_core.tools import tool


@tool
def search_tool(query: str) -> str:
    """Search for information on the web."""
    # This is a mock implementation - replace with actual search API
    return f"Search results for: {query}"


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return f"The result is: {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"


def get_instana_application(application_id: str, mcp_server_path: Optional[str] = None) -> dict:
    """
    Get Instana application configuration by ID using Instana MCP server (stdio mode).
    
    Args:
        application_id: The Instana application ID
        mcp_server_path: Path to the MCP server executable (from env if not provided)
        
    Returns:
        Application configuration from Instana via MCP
    """
    # Get MCP server path from environment or use default
    server_path = mcp_server_path or os.getenv("INSTANA_MCP_SERVER_PATH", "npx")
    server_args = os.getenv("INSTANA_MCP_SERVER_ARGS", "-y @instana/mcp-server-instana").split()
    
    # Get Instana credentials for MCP environment
    instana_base_url = os.getenv("INSTANA_BASE_URL")
    instana_api_token = os.getenv("INSTANA_API_TOKEN")
    
    if not instana_base_url or not instana_api_token:
        return {
            "error": "Instana credentials not configured",
            "message": "Set INSTANA_BASE_URL and INSTANA_API_TOKEN environment variables"
        }
    
    try:
        # Prepare environment variables for MCP server
        env = os.environ.copy()
        env["INSTANA_BASE_URL"] = instana_base_url
        env["INSTANA_API_TOKEN"] = instana_api_token
        
        # MCP JSON-RPC request to call get_application_config tool
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_application_config",
                "arguments": {
                    "id": application_id
                }
            }
        }
        
        # Output the JSON-RPC payload for debugging
        request_json = json.dumps(request, indent=2)
        print(f"\n[MCP Request to {server_path} {' '.join(server_args)}]")
        print(request_json)
        print()
        
        # Call MCP server via stdio
        process = subprocess.Popen(
            [server_path] + server_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True
        )
        
        # Send request and get response
        stdout, stderr = process.communicate(input=request_json + "\n", timeout=30)
        
        # Output the response for debugging
        if stdout:
            print(f"[MCP Response]")
            print(stdout)
            print()
        
        if process.returncode != 0:
            return {
                "error": "MCP server process failed",
                "message": stderr or "Unknown error",
                "application_id": application_id
            }
        
        # Parse response
        result = json.loads(stdout)
        
        # Extract application data from MCP response
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"]
            if isinstance(content, list) and len(content) > 0:
                # Get the text content from MCP response
                text_content = content[0].get("text", "")
                try:
                    # Try to parse as JSON if possible
                    app_data = json.loads(text_content)
                    return {
                        "id": application_id,
                        "data": app_data,
                        "source": "mcp-instana"
                    }
                except json.JSONDecodeError:
                    # Return as text if not valid JSON
                    return {
                        "id": application_id,
                        "data": text_content,
                        "source": "mcp-instana"
                    }
        
        return {
            "error": "Application not found",
            "message": f"Could not find application with ID {application_id}",
            "application_id": application_id
        }
        
    except subprocess.TimeoutExpired:
        return {
            "error": "MCP server timeout",
            "message": "MCP server did not respond within 30 seconds",
            "application_id": application_id
        }
    except Exception as e:
        return {
            "error": "Failed to fetch application from Instana MCP",
            "message": str(e),
            "application_id": application_id
        }


@tool
def fetch_application(application_name: str, application_id: Optional[str] = None) -> str:
    """
    Fetch application details and metadata.
    If application_id is provided, fetches configuration from Instana MCP.
    
    Args:
        application_name: The name of the application to fetch
        application_id: Optional Instana application ID for fetching from Instana
        
    Returns:
        Application details including status, version, and configuration
    """
    # If application_id is provided, fetch from Instana
    if application_id:
        instana_data = get_instana_application(application_id)
        
        if "error" in instana_data:
            return f"Error fetching application '{application_name}' from Instana: {instana_data['message']}"
        
        # Format Instana response
        app_label = instana_data.get("label", application_name)
        app_id = instana_data.get("id", application_id)
        
        result = f"Application '{app_label}' (ID: {app_id}) from Instana:\n"
        result += f"- Boundary Scope: {instana_data.get('boundaryScope', 'N/A')}\n"
        
        # Add service configuration if available
        if "services" in instana_data:
            result += f"- Services: {len(instana_data['services'])} configured\n"
        
        # Add any additional metadata
        if "tags" in instana_data:
            result += f"- Tags: {', '.join(instana_data['tags'])}\n"
        
        return result
    
    # Default mock implementation for non-Instana applications
    return f"Application '{application_name}' details: Status=Running, Version=1.0.0, Instances=3"

# Made with Bob
