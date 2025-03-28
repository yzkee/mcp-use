# Model-Agnostic MCP Library for LLMs

A Python library that lets any LLM (Language Learning Model) use MCP (Multi-Channel Platform) tools through a unified interface. The goal is to let developers easily connect any LLM to tools like web browsing, file operations, etc.

## Core Concept

- Leverage existing LangChain adapters rather than reinventing them
- Focus on bridging MCPs and LangChain's tool ecosystem

## Key Components

### Connectors

Bridge to MCP implementations:

- `stdio.py`: For local MCP processes
- `websocket.py`: For remote WebSocket MCPs
- `http.py`: For HTTP API MCPs

### Tool Conversion

Convert between MCP and LangChain formats:

- Convert MCP tool schemas to formats needed by different LLMs
- Support OpenAI function calling, Anthropic tool format, etc.

### Session Management

Handle connection lifecycle:

- Authenticate and initialize MCP connections
- Discover and register available tools
- Handle tool calling with proper error management

### Agent Integration

Ready-to-use agent implementations:

- Pre-configured for MCP tool usage
- Optimized prompts for tool selection

## Installation

```bash
pip install mcpeer
```

Or install from source:

```bash
git clone https://github.com/pietrozullo/mcpeer.git
cd mcpeer
pip install -e .
```

## Quick Start

Here's a simple example to get you started:

```python
import asyncio
from mcp import StdioServerParameters
from mcpeer import MCPAgent

async def main():
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="npx",
        args=["@playwright/mcp@latest"],
    )

    # Create a model-agnostic MCP client
    mcp_client = MCPAgent(
        server_params=server_params,
        model_provider="anthropic",  # Or "openai"
        model_name="claude-3-7-sonnet-20250219",  # Or "gpt-4o" for OpenAI
        temperature=0.7
    )

    # Initialize the client
    await mcp_client.initialize()

    # Run a query using the agent with tools
    result = await mcp_client.run_query(
        "Using internet tell me how many people work at OpenAI"
    )

    print("Result:")
    print(result)

    # Close the client
    await mcp_client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Simplified Usage

You can also use the simplified interface that handles connector lifecycle management automatically:

```python
import asyncio
from langchain_openai import ChatOpenAI
from mcpeer import MCPAgent
from mcpeer.connectors.stdio import StdioConnector

async def main():
    # Create the connector
    connector = StdioConnector(
        command="npx",
        args=["@playwright/mcp@latest"],
    )

    # Create the LLM
    llm = ChatOpenAI(model="gpt-4o-mini")

    # Create MCP client
    mcp_client = MCPAgent(connector=connector, llm=llm, max_steps=30)

    # Run a query - MCPAgent handles connector lifecycle internally
    result = await mcp_client.run(
        "Using internet tell me how many people work at OpenAI",
        # manage_connector=True is the default
    )

    print("Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Usage

See the `examples` directory for more advanced usage examples:

- `basic_usage.py`: Shows basic usage with different models
- `simplified_usage.py`: Shows how to use automatic connector lifecycle management
- `websocket_example.py`: Shows how to connect to a remote MCP over WebSocket

## Requirements

- Python 3.8+
- MCP implementation (like Playwright MCP)
- LangChain and appropriate model libraries (OpenAI, Anthropic, etc.)

## License

MIT
