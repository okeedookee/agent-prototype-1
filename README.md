# SLO Agent

A conversational AI agent built with LangGraph, featuring tool-calling capabilities, memory management, and streaming support. Supports OpenAI, IBM Watsonx, and vLLM via LiteLLM proxy.

## Features

- **State Management**: Built on LangGraph's state graph architecture for robust conversation flow
- **Tool Integration**: Includes tools (calculator, search, fetch_application) that can be easily extended
- **Instana MCP Integration**: Fetch application configurations via Instana MCP server
- **Memory**: Maintains conversation history across multiple turns
- **Streaming Support**: Stream responses in real-time
- **Type Safety**: Fully typed with Python type hints
- **Standard Python Package**: Follows Python packaging best practices
- **Multi-Provider Support**: Works with OpenAI, IBM Watsonx, and vLLM via LiteLLM proxy

## Project Structure

```
slo-agent/
├── src/
│   └── slo_agent/
│       ├── __init__.py      # Package initialization
│       ├── agent.py         # Main LangGraph agent implementation
│       ├── config.py        # LLM configuration management
│       ├── llm_providers.py # LLM provider factory for extensibility
│       └── tools.py         # Agent tools (calculator, search, fetch_application)
├── examples/
│   ├── basic_usage.py       # Basic usage examples
│   ├── conversation_memory.py  # Multi-turn conversation demo
│   ├── interactive_chat.py  # Interactive chat interface
│   ├── watsonx_usage.py     # IBM Watsonx integration example
│   ├── vllm_usage.py        # vLLM integration example
│   ├── config_usage.py      # Configuration object usage
│   ├── instana_integration.py  # Instana MCP integration example
│   ├── fetch_application_by_id.py  # Fetch specific Instana application
│   └── custom_llm_provider.py  # Direct LLM provider factory usage
├── tests/
│   ├── __init__.py
│   └── test_agent.py        # Unit tests
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore patterns
├── pyproject.toml           # Project metadata and dependencies
├── requirements.txt         # Python dependencies (for pip)
└── README.md                # This file
```

## Installation

### Option 1: Install as a Package (Recommended)

1. Clone this repository:
```bash
git clone <repository-url>
cd slo-agent
```

2. Install the package in development mode:
```bash
pip install -e .
```

3. Set up your environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your configuration:

For OpenAI:
```
LLM_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
TEMPERATURE=0.7
OPENAI_API_KEY=your_actual_api_key_here
```

For IBM Watsonx:
```
LLM_PROVIDER=watsonx
MODEL_NAME=ibm/granite-13b-chat-v2
TEMPERATURE=0.7
WATSONX_API_KEY=your_watsonx_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

For vLLM:
```
LLM_PROVIDER=vllm
MODEL_NAME=meta-llama/Llama-2-7b-chat-hf
TEMPERATURE=0.7
VLLM_API_BASE=http://localhost:8000/v1
VLLM_API_KEY=EMPTY
```

For Instana MCP Integration (stdio mode):
```
INSTANA_BASE_URL=https://your-instana-instance.instana.io
INSTANA_API_TOKEN=your_instana_api_token_here
INSTANA_MCP_SERVER_PATH=npx
INSTANA_MCP_SERVER_ARGS=-y @instana/mcp-server-instana
```

**Note:**
- All LLM configuration can now be set via environment variables. If you set these variables, you don't need to pass them as parameters when creating the agent.
- The Instana MCP server runs in stdio mode. Install it with: `npm install -g @instana/mcp-server-instana`

### Option 2: Install Dependencies Only

If you just want to run the examples without installing the package:

```bash
pip install -r requirements.txt
```

### Option 3: Install with Development Tools

For development with testing and linting tools:

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Usage with OpenAI

```python
from slo_agent import create_agent

# Option 1: Use environment variables (recommended)
# Set LLM_PROVIDER, MODEL_NAME, and TEMPERATURE in .env
agent = create_agent()

# Option 2: Specify parameters explicitly
agent = create_agent(
    provider="openai",
    model_name="gpt-4o-mini",
    temperature=0.7
)

# Option 3: Mix environment variables and explicit parameters
# Environment variables are used as defaults, explicit parameters override them
agent = create_agent(temperature=0.5)  # Uses MODEL_NAME and LLM_PROVIDER from env

# Run a simple query
result = agent.run("What is 25 * 47?")
print(result['response'])
```

### Using IBM Watsonx via LiteLLM Proxy

```python
from slo_agent import create_agent

# Option 1: Use environment variables (recommended)
# Set LLM_PROVIDER=watsonx, MODEL_NAME, WATSONX_API_KEY, etc. in .env
agent = create_agent()

# Option 2: Specify parameters explicitly
agent = create_agent(
    provider="watsonx",
    model_name="ibm/granite-13b-chat-v2",
    temperature=0.7,
    watsonx_api_key="your_api_key",
    watsonx_project_id="your_project_id",
    watsonx_url="https://us-south.ml.cloud.ibm.com"
)

# Option 3: Mix environment variables and explicit parameters
agent = create_agent(provider="watsonx")  # Uses other settings from env

# Run a simple query
result = agent.run("What is 25 * 47?")
print(result['response'])
```

### Using vLLM

```python
from slo_agent import create_agent

# Option 1: Use environment variables (recommended)
# Set LLM_PROVIDER=vllm, MODEL_NAME, VLLM_API_BASE in .env
agent = create_agent()

# Option 2: Specify parameters explicitly
agent = create_agent(
    provider="vllm",
    model_name="meta-llama/Llama-2-7b-chat-hf",
    temperature=0.7,
    vllm_api_base="http://localhost:8000/v1",
    vllm_api_key="EMPTY"  # Use "EMPTY" for local vLLM without authentication
)

# Option 3: Mix environment variables and explicit parameters
agent = create_agent(provider="vllm")  # Uses other settings from env

# Run a simple query
result = agent.run("What is 25 * 47?")
print(result['response'])
```

### Multi-turn Conversation

```python
from slo_agent import create_agent

agent = create_agent()
conversation_history = []

# First turn
result = agent.run("My name is Alice", conversation_history)
conversation_history = result['conversation_history']
print(result['response'])

# Second turn - agent remembers the context
result = agent.run("What's my name?", conversation_history)
conversation_history = result['conversation_history']
print(result['response'])
```

### Streaming Responses

```python
from slo_agent import create_agent

agent = create_agent()

for chunk in agent.stream("Tell me a story"):
    print(chunk)
```

### Running the Examples

The `examples/` directory contains several demonstration scripts:

1. **Basic Usage**:
```bash
python examples/basic_usage.py
```

2. **Conversation Memory**:
```bash
python examples/conversation_memory.py
```

3. **Interactive Chat**:
```bash
python examples/interactive_chat.py
```

4. **Watsonx Integration**:
```bash
python examples/watsonx_usage.py
```

5. **vLLM Integration**:
```bash
python examples/vllm_usage.py
```

6. **Custom LLM Provider**:
```bash
python examples/custom_llm_provider.py
```

7. **Instana MCP Integration**:
```bash
python examples/instana_integration.py
```

8. **Fetch Application by ID**:
```bash
python examples/fetch_application_by_id.py
```

These examples demonstrate:
- Simple conversations
- Tool usage (calculator, search, fetch_application)
- Multi-turn conversations with memory
- Interactive chat mode
- IBM Watsonx integration via LiteLLM
- vLLM integration via LiteLLM
- Instana MCP integration for application monitoring
- Direct usage of the LLM provider factory

## Architecture

The agent is built using LangGraph's state graph pattern:

```
┌─────────┐
│  Start  │
└────┬────┘
     │
     ▼
┌─────────┐
│  Agent  │◄─────┐
└────┬────┘      │
     │           │
     ▼           │
  Should         │
 Continue?       │
     │           │
     ├─Yes───────┤
     │           │
     │      ┌────┴────┐
     │      │  Tools  │
     │      └─────────┘
     │
     ▼ No
  ┌─────┐
  │ End │
  └─────┘
```

### Components

1. **AgentState**: TypedDict defining the conversation state with message history
2. **Tools**: Decorated functions that the agent can call (@tool decorator)
3. **State Graph**: Defines the flow between agent reasoning and tool execution
4. **LLM Provider Factory**: Extensible factory for creating LLM instances from different providers
5. **LLM**: OpenAI, Watsonx, or vLLM model with tool binding for function calling
6. **LiteLLM Proxy**: Built-in proxy for accessing Watsonx, vLLM, and other LLM providers

## Available Tools

The agent comes with three example tools:

1. **calculator**: Evaluates mathematical expressions
   ```python
   "What is 123 + 456?"
   ```

2. **search_tool**: Mock web search (replace with actual API)
   ```python
   "Search for information about Python"
   ```

3. **get_weather**: Mock weather lookup (replace with actual API)
   ```python
   "What's the weather in San Francisco?"
   ```

## Customization

### Adding New Tools

1. Create a new tool in `src/slo_agent/tools.py`:

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(param: str) -> str:
    """Description of what the tool does."""
    # Your implementation here
    return "Result"
```

2. Export it in `src/slo_agent/__init__.py`:

```python
from .tools import calculator, search_tool, get_weather, my_custom_tool

__all__ = [
    "LangGraphAgent",
    "create_agent",
    "calculator",
    "search_tool",
    "get_weather",
    "my_custom_tool",
]
```

3. Add it to the agent's tool list in `src/slo_agent/agent.py`:

```python
from .tools import search_tool, calculator, get_weather, my_custom_tool

# In __init__:
self.tools = [search_tool, calculator, get_weather, my_custom_tool]
```

### Using the LLM Provider Factory

The agent now uses an extensible LLM provider factory that makes it easy to add support for new LLM providers. All configuration can be loaded from environment variables:

```python
from slo_agent import create_llm

# Option 1: Use environment variables (recommended)
# Set LLM_PROVIDER, MODEL_NAME, TEMPERATURE in .env
llm = create_llm()

# Option 2: Create an OpenAI LLM with explicit parameters
llm = create_llm(provider="openai", model_name="gpt-4", temperature=0.7)

# Option 3: Create a Watsonx LLM with explicit parameters
llm = create_llm(
    provider="watsonx",
    model_name="ibm/granite-13b-chat-v2",
    temperature=0.7,
    watsonx_api_key="your_api_key",
    watsonx_project_id="your_project_id"
)

# Option 4: Use the factory class for more control
from slo_agent import LLMProviderFactory

llm = LLMProviderFactory.create_llm(
    provider="openai",
    model_name="gpt-4o-mini",
    temperature=0.5
)
```

**Environment Variables:**
- `LLM_PROVIDER`: The LLM provider to use (default: "openai")
- `MODEL_NAME`: The model name (default: "gpt-4o-mini")
- `TEMPERATURE`: The temperature for response generation (default: 0.7)
- `OPENAI_API_KEY`: OpenAI API key (required for OpenAI provider)
- `WATSONX_API_KEY`: Watsonx API key (required for Watsonx provider)
- `WATSONX_PROJECT_ID`: Watsonx project ID (required for Watsonx provider)
- `WATSONX_URL`: Watsonx URL (default: "https://us-south.ml.cloud.ibm.com")
- `VLLM_API_BASE`: vLLM API base URL (required for vLLM provider)
- `VLLM_API_KEY`: vLLM API key (optional, use "EMPTY" for local instances)

### Adding Support for New LLM Providers

To add support for a new LLM provider, extend the `LLMProviderFactory` class in `src/slo_agent/llm_providers.py`:

```python
@staticmethod
def _create_custom_llm(
    model_name: str,
    temperature: float,
    **kwargs
) -> ChatLiteLLM:
    """Create a custom LLM instance."""
    # Your implementation here
    return ChatLiteLLM(
        model=f"custom/{model_name}",
        temperature=temperature,
        **kwargs
    )
```

Then update the `create_llm` method to handle the new provider:

```python
if provider == "custom":
    return LLMProviderFactory._create_custom_llm(
        model_name=model_name,
        temperature=temperature,
        **kwargs
    )
```

### Changing the Model

You can use different models from OpenAI or Watsonx:

```python
# Use GPT-4 (OpenAI)
agent = create_agent(model_name="gpt-4", temperature=0.7)

# Use GPT-3.5 Turbo (OpenAI)
agent = create_agent(model_name="gpt-3.5-turbo", temperature=0.5)

# Use Granite model (Watsonx)
agent = create_agent(
    model_name="ibm/granite-13b-chat-v2",
    temperature=0.7,
    provider="watsonx"
)

# Use Llama model (Watsonx)
agent = create_agent(
    model_name="meta-llama/llama-2-70b-chat",
    temperature=0.7,
    provider="watsonx"
)
```

### Adjusting Temperature

Control response randomness (0.0 = deterministic, 1.0 = creative):

```python
agent = create_agent(temperature=0.0)  # More focused
agent = create_agent(temperature=1.0)  # More creative
```

## API Reference

### `create_agent(model_name, temperature, provider, watsonx_api_key, watsonx_project_id, watsonx_url, vllm_api_base, vllm_api_key)`

Factory function to create a LangGraph agent. All parameters can be loaded from environment variables.

**Parameters:**
- `model_name` (Optional[str]): Model name (loaded from MODEL_NAME env var if not provided, defaults to "gpt-4o-mini")
- `temperature` (Optional[float]): Response temperature 0.0-1.0 (loaded from TEMPERATURE env var if not provided, defaults to 0.7)
- `provider` (Optional[str]): LLM provider - "openai", "watsonx", or "vllm" (loaded from LLM_PROVIDER env var if not provided, defaults to "openai")
- `watsonx_api_key` (Optional[str]): Watsonx API key (loaded from WATSONX_API_KEY env var if not provided)
- `watsonx_project_id` (Optional[str]): Watsonx project ID (loaded from WATSONX_PROJECT_ID env var if not provided)
- `watsonx_url` (Optional[str]): Watsonx URL (loaded from WATSONX_URL env var if not provided, defaults to "https://us-south.ml.cloud.ibm.com")
- `vllm_api_base` (Optional[str]): vLLM API base URL (loaded from VLLM_API_BASE env var if not provided)
- `vllm_api_key` (Optional[str]): vLLM API key (loaded from VLLM_API_KEY env var if not provided, defaults to "EMPTY")

**Environment Variables:**
- `LLM_PROVIDER`: The LLM provider to use
- `MODEL_NAME`: The model name
- `TEMPERATURE`: The temperature for response generation
- `WATSONX_API_KEY`: Watsonx API key
- `WATSONX_PROJECT_ID`: Watsonx project ID
- `WATSONX_URL`: Watsonx URL
- `VLLM_API_BASE`: vLLM API base URL
- `VLLM_API_KEY`: vLLM API key

**Returns:** `LangGraphAgent` instance

### `LangGraphAgent.run(user_input, conversation_history)`

Run the agent with a user input.

**Parameters:**
- `user_input` (str): The user's message
- `conversation_history` (Optional[list]): Previous messages

**Returns:** Dictionary with:
- `response` (str): The agent's response
- `conversation_history` (list): Updated message history
- `tool_calls` (list): Tools that were called

### `LangGraphAgent.stream(user_input, conversation_history)`

Stream the agent's response.

**Parameters:**
- `user_input` (str): The user's message
- `conversation_history` (Optional[list]): Previous messages

**Yields:** Chunks of the agent's response

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=src/slo_agent --cov-report=html
```

## Development

### Code Formatting

Format code with Black:

```bash
black src/ tests/ examples/
```

### Type Checking

Run type checking with mypy:

```bash
mypy src/
```

### Linting

Lint code with flake8:

```bash
flake8 src/ tests/ examples/
```

## Requirements

- Python 3.11+
- OpenAI API key (for OpenAI provider)
- IBM Watsonx API key and Project ID (for Watsonx provider)
- Dependencies listed in `pyproject.toml` and `requirements.txt`

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to extend this agent with:
- Additional tools and integrations
- Enhanced error handling
- Persistent storage for conversation history
- Support for other LLM providers via LiteLLM
- Advanced routing logic
- Custom Watsonx model configurations

## Troubleshooting

### Import Errors

If you see import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### API Key Issues

Make sure your `.env` file contains valid API keys:

For OpenAI:
```bash
echo $OPENAI_API_KEY  # Should print your key
```

For Watsonx:
```bash
echo $WATSONX_API_KEY  # Should print your key
echo $WATSONX_PROJECT_ID  # Should print your project ID
```

### Tool Execution Errors

Check that tool functions return strings and handle errors gracefully.

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [IBM Watsonx Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [LiteLLM Documentation](https://docs.litellm.ai/)