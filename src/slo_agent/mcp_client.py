"""
MCP (Model Context Protocol) Client Module

This module provides a client for communicating with MCP servers using the stdio transport.
It handles the protocol initialization, tool calls, and connection management.
"""

import json
import os
import subprocess
from typing import Optional, Tuple, Dict, Any


class MCPClient:
    """Client for communicating with MCP servers via stdio."""
    
    def __init__(self, server_path: Optional[str] = None, server_args: Optional[str] = None):
        """
        Initialize the MCP client.
        
        Args:
            server_path: Path to the MCP server executable (default: from env or "npx")
            server_args: Arguments for the MCP server (default: from env or "-y @instana/mcp-server-instana")
        """
        self.server_path = server_path or os.getenv("INSTANA_MCP_SERVER_PATH", "npx")
        self.server_args = server_args or os.getenv("INSTANA_MCP_SERVER_ARGS", "-y @instana/mcp-server-instana")
        self.process: Optional[subprocess.Popen] = None
        self._initialized = False
    
    def _parse_server_args(self) -> list:
        """Parse server arguments into a list."""
        if isinstance(self.server_args, str):
            return self.server_args.split()
        return self.server_args
    
    def _send_and_receive(self, request: dict) -> Optional[dict]:
        """
        Send a request and read the response.
        
        Args:
            request: The JSON-RPC request to send
            
        Returns:
            The JSON-RPC response or None if failed
        """
        if not self.process or not self.process.stdin or not self.process.stdout:
            return None
        
        try:
            request_json = json.dumps(request)
            self.process.stdin.write(request_json + '\n')
            self.process.stdin.flush()
            
            # Read response line
            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
        except Exception:
            return None
        
        return None
    
    def connect(self, env: Optional[Dict[str, str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Start the MCP server process and initialize the connection.
        
        Args:
            env: Optional environment variables to pass to the server
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if self._initialized:
            return True, None
        
        try:
            # Build command
            server_args_list = self._parse_server_args()
            command = [self.server_path] + server_args_list
            
            # Use provided env or copy current environment
            process_env = env if env is not None else os.environ.copy()
            
            # Start MCP server process
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=process_env,
                text=True,
                bufsize=1
            )
            
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
            
            init_response = self._send_and_receive(init_request)
            
            if not init_response:
                self.disconnect()
                return False, "No initialization response from MCP server"
            
            # Step 2: Send initialized notification
            initialized_notif = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            if self.process.stdin:
                self.process.stdin.write(json.dumps(initialized_notif) + '\n')
                self.process.stdin.flush()
            
            self._initialized = True
            return True, None
            
        except Exception as e:
            self.disconnect()
            return False, f"Failed to connect to MCP server: {str(e)}"
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[dict]:
        """
        Call an MCP tool with the given arguments.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            The tool response or None if failed
        """
        if not self._initialized:
            return None
        
        tool_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        return self._send_and_receive(tool_request)
    
    def disconnect(self):
        """Disconnect from the MCP server and cleanup resources."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                pass
            finally:
                self.process = None
                self._initialized = False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.disconnect()


def create_instana_mcp_client() -> MCPClient:
    """
    Create an MCP client configured for Instana with credentials from environment.
    
    Returns:
        Configured MCPClient instance
        
    Raises:
        ValueError: If required Instana credentials are not set
    """
    instana_base_url = os.getenv("INSTANA_BASE_URL")
    instana_api_token = os.getenv("INSTANA_API_TOKEN")
    
    if not instana_base_url or not instana_api_token:
        raise ValueError(
            "Instana credentials not configured. "
            "Set INSTANA_BASE_URL and INSTANA_API_TOKEN environment variables"
        )
    
    return MCPClient()


# Made with Bob