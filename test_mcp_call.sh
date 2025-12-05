#!/bin/bash
# Test script for MCP tool call with proper initialization

# Check if required arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <tool_name> <arguments_json>"
    echo "Example: $0 get_application_config '{\"id\":\"8rwDuom6TGSGB-YhFfn4VA\"}'"
    exit 1
fi

TOOL_NAME="$1"
ARGUMENTS="$2"

# Use Python to handle the MCP protocol communication
python3 - "$TOOL_NAME" "$ARGUMENTS" << 'EOF'
import sys
import json
import subprocess
import time

tool_name = sys.argv[1]
arguments = sys.argv[2]

# Start the MCP server
proc = subprocess.Popen(
    ['mcp-instana', '--transport', 'stdio'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    bufsize=1
)

def send_and_receive(request):
    """Send a request and read the response"""
    proc.stdin.write(json.dumps(request) + '\n')
    proc.stdin.flush()
    
    # Read response line
    response_line = proc.stdout.readline()
    if response_line:
        return json.loads(response_line.strip())
    return None

try:
    # Step 1: Initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-cli", "version": "1.0"}
        }
    }
    
    print("Initializing...", file=sys.stderr)
    init_response = send_and_receive(init_request)
    
    if not init_response:
        print("Error: No initialization response", file=sys.stderr)
        sys.exit(1)
    
    # Step 2: Send initialized notification
    initialized_notif = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    proc.stdin.write(json.dumps(initialized_notif) + '\n')
    proc.stdin.flush()
    time.sleep(0.1)
    
    # Step 3: Call the tool
    print(f"Calling tool: {tool_name}", file=sys.stderr)
    tool_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": json.loads(arguments)
        }
    }
    
    tool_response = send_and_receive(tool_request)
    
    if tool_response:
        # Pretty print the result
        if "result" in tool_response:
            print(json.dumps(tool_response["result"], indent=2))
        elif "error" in tool_response:
            print(f"Error: {tool_response['error']}", file=sys.stderr)
            sys.exit(1)
        else:
            print(json.dumps(tool_response, indent=2))
    else:
        print("Error: No response from tool call", file=sys.stderr)
        sys.exit(1)
        
finally:
    proc.terminate()
    proc.wait(timeout=2)
EOF
