"""
Tools for the LangGraph Agent
Define custom tools that the agent can use.
"""

import json
import os
from typing import Optional
from langchain_core.tools import tool

from .mcp_client import MCPClient


def get_instana_application(application_id: str, mcp_server_path: Optional[str] = None) -> dict:
    """
    Get Instana application configuration by ID using Instana MCP server (stdio mode).
    Implements proper MCP protocol initialization sequence.
    
    Args:
        application_id: The Instana application ID
        mcp_server_path: Path to the MCP server executable (from env if not provided)
        
    Returns:
        Application configuration from Instana via MCP
    """
    # Get Instana credentials for MCP environment
    instana_base_url = os.getenv("INSTANA_BASE_URL")
    instana_api_token = os.getenv("INSTANA_API_TOKEN")
    
    if not instana_base_url or not instana_api_token:
        return {
            "error": "Instana credentials not configured",
            "message": "Set INSTANA_BASE_URL and INSTANA_API_TOKEN environment variables"
        }
    
    try:
        # Use MCP client with context manager for automatic cleanup
        with MCPClient(server_path=mcp_server_path) as client:
            # Prepare environment variables for MCP server
            env = os.environ.copy()
            env["INSTANA_BASE_URL"] = instana_base_url
            env["INSTANA_API_TOKEN"] = instana_api_token
            
            # Connect to MCP server
            success, error_msg = client.connect(env=env)
            if not success:
                return {
                    "error": "MCP connection failed",
                    "message": error_msg,
                    "application_id": application_id
                }
            
            # Call the tool
            tool_response = client.call_tool("get_application_config", {"id": application_id})
            
            if not tool_response:
                return {
                    "error": "No response from tool call",
                    "message": "MCP server did not respond to tool call",
                    "application_id": application_id
                }
            
            # Handle error response
            if "error" in tool_response:
                return {
                    "error": "MCP tool call failed",
                    "message": str(tool_response["error"]),
                    "application_id": application_id
                }
            
            # Extract application data from MCP response
            if "result" in tool_response and "content" in tool_response["result"]:
                content = tool_response["result"]["content"]
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
            
    except Exception as e:
        return {
            "error": "Failed to fetch application from Instana MCP",
            "message": str(e),
            "application_id": application_id
        }


@tool
def summarize_application(application_id: str) -> str:
    """
    Fetch and summarize application configuration from Instana by application ID.
    
    Args:
        application_id: The Instana application ID to summarize
        
    Returns:
        A formatted summary of the application configuration
    """
    # Fetch application data from Instana
    app_data = get_instana_application(application_id)
    
    # Handle errors
    if "error" in app_data:
        return f"Error: {app_data['message']}"
    
    # Extract data
    data = app_data.get("data", {})
    
    # Build summary
    summary_parts = []
    summary_parts.append(f"Application ID: {application_id}")
    
    if isinstance(data, dict):
        # Add label if available
        if "label" in data:
            summary_parts.append(f"Name: {data['label']}")
        
        # Add boundary scope
        if "boundaryScope" in data:
            summary_parts.append(f"Boundary Scope: {data['boundaryScope']}")
        
        # Add services count
        if "services" in data:
            services = data["services"]
            if isinstance(services, list):
                summary_parts.append(f"Services: {len(services)} configured")
                # List service names if available
                service_names = [s.get("name", "Unknown") for s in services if isinstance(s, dict)]
                if service_names:
                    summary_parts.append(f"Service Names: {', '.join(service_names)}")
        
        # Add tags if available
        if "tags" in data:
            tags = data["tags"]
            if isinstance(tags, list) and tags:
                summary_parts.append(f"Tags: {', '.join(str(t) for t in tags)}")
        
        # Add any other relevant fields
        for key in ["createdAt", "updatedAt", "description"]:
            if key in data:
                summary_parts.append(f"{key.replace('_', ' ').title()}: {data[key]}")
    else:
        # If data is not a dict, just include it as text
        summary_parts.append(f"Data: {data}")
    
    return "\n".join(summary_parts)


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
