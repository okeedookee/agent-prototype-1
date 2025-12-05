"""
Tools for the LangGraph Agent
Define custom tools that the agent can use.
"""

import json
import os
import subprocess
from typing import Optional
from langchain_core.tools import tool


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
    # Get MCP server path and args from environment or use defaults
    server_path = mcp_server_path or os.getenv("INSTANA_MCP_SERVER_PATH", "npx")
    server_args = os.getenv("INSTANA_MCP_SERVER_ARGS", "-y @instana/mcp-server-instana")
    
    # Parse server args - handle both space-separated strings and lists
    if isinstance(server_args, str):
        server_args_list = server_args.split()
    else:
        server_args_list = server_args
    
    # Get Instana credentials for MCP environment
    instana_base_url = os.getenv("INSTANA_BASE_URL")
    instana_api_token = os.getenv("INSTANA_API_TOKEN")
    
    if not instana_base_url or not instana_api_token:
        return {
            "error": "Instana credentials not configured",
            "message": "Set INSTANA_BASE_URL and INSTANA_API_TOKEN environment variables"
        }
    
    process = None
    try:
        # Prepare environment variables for MCP server
        env = os.environ.copy()
        env["INSTANA_BASE_URL"] = instana_base_url
        env["INSTANA_API_TOKEN"] = instana_api_token
        
        # Build command with server path and args
        command = [server_path] + server_args_list
        
        # Start MCP server process
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1
        )
        
        def send_and_receive(request, request_name=""):
            """Send a request and read the response"""
            if process.stdin:
                request_json = json.dumps(request)
                print(f"\n[MCP Request - {request_name}]")
                print(request_json)
                process.stdin.write(request_json + '\n')
                process.stdin.flush()
            
            # Read response line
            if process.stdout:
                response_line = process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    print(f"\n[MCP Response - {request_name}]")
                    print(json.dumps(response, indent=2))
                    return response
            return None
        
        # Step 1: Initialize MCP connection
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "slo-agent", "version": "1.0"}
            }
        }
        
        print(f"\n[MCP Initializing connection to {server_path} {' '.join(server_args_list)}]")
        init_response = send_and_receive(init_request, "initialize")
        
        if not init_response:
            process.terminate()
            return {
                "error": "MCP initialization failed",
                "message": "No initialization response from MCP server",
                "application_id": application_id
            }
        
        # Step 2: Send initialized notification
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        if process.stdin:
            notif_json = json.dumps(initialized_notif)
            print(f"\n[MCP Notification - initialized]")
            print(notif_json)
            process.stdin.write(notif_json + '\n')
            process.stdin.flush()
        
        # Step 3: Call the tool
        tool_request = {
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
        
        tool_response = send_and_receive(tool_request, "tools/call")
        
        # Cleanup
        if process:
            process.terminate()
            process.wait(timeout=2)
        
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
                    print(f"[MCP Response received successfully]")
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
        if process:
            process.terminate()
        return {
            "error": "MCP server timeout",
            "message": "MCP server did not respond within timeout period",
            "application_id": application_id
        }
    except Exception as e:
        if process:
            process.terminate()
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
