<div align="center" style="margin: 0 auto; max-width: 80%;">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="static/logo_white.svg">
    <source media="(prefers-color-scheme: light)" srcset="static/logo_black.svg">
    <img alt="mcp use logo" src="./static/logo-white.svg" width="80%" style="margin: 20px auto;">
  </picture>
</div>

<h1 align="center">Unified MCP Client Library </h1>
<p align="center">
    <a href="https://pypi.org/project/mcp_use/" alt="PyPI Version">
        <img src="https://img.shields.io/pypi/v/mcp_use.svg"/></a>
    <a href="https://pypi.org/project/mcp_use/" alt="PyPI Downloads">
        <img src="https://static.pepy.tech/badge/mcp-use" /></a>
    <a href="https://pypi.org/project/mcp_use/" alt="Python Versions">
        <img src="https://img.shields.io/pypi/pyversions/mcp_use.svg" /></a>
    <a href="https://docs.mcp-use.io" alt="Documentation">
        <img src="https://img.shields.io/badge/docs-mcp--use.io-blue" /></a>
    <a href="https://mcp-use.io" alt="Website">
        <img src="https://img.shields.io/badge/website-mcp--use.io-blue" /></a>
    <a href="https://github.com/pietrozullo/mcp-use/blob/main/LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/pietrozullo/mcp-use" /></a>
    <a href="https://github.com/astral-sh/ruff" alt="Code style: Ruff">
        <img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" /></a>
    <a href="https://github.com/pietrozullo/mcp-use/stargazers" alt="GitHub stars">
        <img src="https://img.shields.io/github/stars/pietrozullo/mcp-use?style=social" /></a>
    </p>
    <p align="center">
    <a href="https://x.com/pietrozullo" alt="Twitter Follow - Pietro">
        <img src="https://img.shields.io/twitter/follow/Pietro?style=social" /></a>
    <a href="https://x.com/pederzh" alt="Twitter Follow - Luigi">
        <img src="https://img.shields.io/twitter/follow/Luigi?style=social" /></a>
    <a href="https://discord.gg/XkNkSkMz3V" alt="Discord">
        <img src="https://dcbadge.limes.pink/api/server/https://discord.gg/XkNkSkMz3V?style=flat" /></a>
</p>
🌐 MCP-Use is the open source way to connect **any LLM to any MCP server** and build custom agents that have tool access, without using closed source or application clients.

💬 Get started quickly - chat with your servers on our <b>hosted version</b>! <b>[Try mcp-use chat *(beta)* ](https://chat.mcp-use.io)</b>.

💡 Let developers easily connect any LLM to tools like web browsing, file operations, and more.

# Features

## ✨ Key Features
<table>
  <tr>
    <th width="400">Feature</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>🔄 <a href="#quick-start"><strong>Ease of use</strong></a></td>
    <td>Create your first MCP capable agent you need only 6 lines of code</td>
  </tr>
  <tr>
    <td>🤖 <a href="#installing-langchain-providers"><strong>LLM Flexibility</strong></a></td>
    <td>Works with any langchain supported LLM that supports tool calling (OpenAI, Anthropic, Groq, LLama etc.)</td>
  </tr>
  <tr>
    <td>🌐 <a href="https://mcp-use.io/builder"><strong>Code Builder</strong></a></td>
    <td>Explore MCP capabilities and generate starter code with the interactive <a href="https://mcp-use.io/builder">code builder</a>.</td>
  </tr>
  <tr>
    <td>🔗 <a href="#http-connection-example"><strong>HTTP Support</strong></a></td>
    <td>Direct connection to MCP servers running on specific HTTP ports</td>
  </tr>
  <tr>
    <td>⚙️ <a href="#dynamic-server-selection-server-manager"><strong>Dynamic Server Selection</strong></a></td>
    <td>Agents can dynamically choose the most appropriate MCP server for a given task from the available pool</td>
  </tr>
  <tr>
    <td>🧩 <a href="#multi-server-support"><strong>Multi-Server Support</strong></a></td>
    <td>Use multiple MCP servers simultaneously in a single agent</td>
  </tr>
  <tr>
    <td>🛡️ <a href="#tool-access-control"><strong>Tool Restrictions</strong></a></td>
    <td>Restrict potentially dangerous tools like file system or network access</td>
  </tr>
  <tr>
    <td>🔧 <a href="#build-a-custom-agent"><strong>Custom Agents</strong></a></td>
    <td>Build your own agents with any framework using the LangChain adapter or create new adapters</td>
  </tr>
  <tr>
    <td>❓ <a href="https://mcp-use.io/what-should-we-build-next"><strong>What should we build next</strong></a></td>
    <td>Let us know what you'd like us to build next</td>
  </tr>
</table>

# Quick start

With pip:

```bash
pip install mcp-use
```

Or install from source:

```bash
git clone https://github.com/pietrozullo/mcp-use.git
cd mcp-use
pip install -e .
```

### Installing LangChain Providers

mcp_use works with various LLM providers through LangChain. You'll need to install the appropriate LangChain provider package for your chosen LLM. For example:

```bash
# For OpenAI
pip install langchain-openai

# For Anthropic
pip install langchain-anthropic
```
For other providers, check the [LangChain chat models documentation](https://python.langchain.com/docs/integrations/chat/) and add your API keys for the provider you want to use to your `.env` file.

```bash
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

> **Important**: Only models with tool calling capabilities can be used with mcp_use. Make sure your chosen model supports function calling or tool use.

### Spin up your agent:

```python
import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

async def main():
    # Load environment variables
    load_dotenv()

    # Create configuration dictionary
    config = {
      "mcpServers": {
        "playwright": {
          "command": "npx",
          "args": ["@playwright/mcp@latest"],
          "env": {
            "DISPLAY": ":1"
          }
        }
      }
    }

    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(config)

    # Create LLM
    llm = ChatOpenAI(model="gpt-4o")

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    # Run the query
    result = await agent.run(
        "Find the best restaurant in San Francisco",
    )
    print(f"\nResult: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

You can also add the servers configuration from a config file like this:

```python
client = MCPClient.from_config_file(
        os.path.join("browser_mcp.json")
    )
```

Example configuration file (`browser_mcp.json`):

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {
        "DISPLAY": ":1"
      }
    }
  }
}
```

For other settings, models, and more, check out the documentation.

## Streaming Agent Output

MCP-Use supports asynchronous streaming of agent output using the `astream` method on `MCPAgent`. This allows you to receive incremental results, tool actions, and intermediate steps as they are generated by the agent, enabling real-time feedback and progress reporting.

### How to use

Call `agent.astream(query)` and iterate over the results asynchronously:

```python
async for chunk in agent.astream("Find the best restaurant in San Francisco"):
    print(chunk["messages"], end="", flush=True)
```

Each chunk is a dictionary containing keys such as `actions`, `steps`, `messages`, and (on the last chunk) `output`. This enables you to build responsive UIs or log agent progress in real time.

#### Example: Streaming in Practice

```python
import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

async def main():
    load_dotenv()
    client = MCPClient.from_config_file("browser_mcp.json")
    llm = ChatOpenAI(model="gpt-4o")
    agent = MCPAgent(llm=llm, client=client, max_steps=30)
    async for chunk in agent.astream("Look for job at nvidia for machine learning engineer."):
        print(chunk["messages"], end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```

This streaming interface is ideal for applications that require real-time updates, such as chatbots, dashboards, or interactive notebooks.

# Example Use Cases

## Web Browsing with Playwright

```python
import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

async def main():
    # Load environment variables
    load_dotenv()

    # Create MCPClient from config file
    client = MCPClient.from_config_file(
        os.path.join(os.path.dirname(__file__), "browser_mcp.json")
    )

    # Create LLM
    llm = ChatOpenAI(model="gpt-4o")
    # Alternative models:
    # llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    # llm = ChatGroq(model="llama3-8b-8192")

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    # Run the query
    result = await agent.run(
        "Find the best restaurant in San Francisco USING GOOGLE SEARCH",
        max_steps=30,
    )
    print(f"\nResult: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Airbnb Search

```python
import asyncio
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from mcp_use import MCPAgent, MCPClient

async def run_airbnb_example():
    # Load environment variables
    load_dotenv()

    # Create MCPClient with Airbnb configuration
    client = MCPClient.from_config_file(
        os.path.join(os.path.dirname(__file__), "airbnb_mcp.json")
    )

    # Create LLM - you can choose between different models
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    try:
        # Run a query to search for accommodations
        result = await agent.run(
            "Find me a nice place to stay in Barcelona for 2 adults "
            "for a week in August. I prefer places with a pool and "
            "good reviews. Show me the top 3 options.",
            max_steps=30,
        )
        print(f"\nResult: {result}")
    finally:
        # Ensure we clean up resources properly
        if client.sessions:
            await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(run_airbnb_example())
```

Example configuration file (`airbnb_mcp.json`):

```json
{
  "mcpServers": {
    "airbnb": {
      "command": "npx",
      "args": ["-y", "@openbnb/mcp-server-airbnb"]
    }
  }
}
```

## Blender 3D Creation

```python
import asyncio
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from mcp_use import MCPAgent, MCPClient

async def run_blender_example():
    # Load environment variables
    load_dotenv()

    # Create MCPClient with Blender MCP configuration
    config = {"mcpServers": {"blender": {"command": "uvx", "args": ["blender-mcp"]}}}
    client = MCPClient.from_dict(config)

    # Create LLM
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    try:
        # Run the query
        result = await agent.run(
            "Create an inflatable cube with soft material and a plane as ground.",
            max_steps=30,
        )
        print(f"\nResult: {result}")
    finally:
        # Ensure we clean up resources properly
        if client.sessions:
            await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(run_blender_example())
```

# Configuration File Support

MCP-Use supports initialization from configuration files, making it easy to manage and switch between different MCP server setups:

```python
import asyncio
from mcp_use import create_session_from_config

async def main():
    # Create an MCP session from a config file
    session = create_session_from_config("mcp-config.json")

    # Initialize the session
    await session.initialize()

    # Use the session...

    # Disconnect when done
    await session.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## HTTP Connection Example

MCP-Use supports HTTP connections, allowing you to connect to MCP servers running on specific HTTP ports. This feature is particularly useful for integrating with web-based MCP servers.

Here's an example of how to use the HTTP connection feature:

```python
import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

async def main():
    """Run the example using a configuration file."""
    # Load environment variables
    load_dotenv()

    config = {
        "mcpServers": {
            "http": {
                "url": "http://localhost:8931/sse"
            }
        }
    }

    # Create MCPClient from config file
    client = MCPClient.from_dict(config)

    # Create LLM
    llm = ChatOpenAI(model="gpt-4o")

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    # Run the query
    result = await agent.run(
        "Find the best restaurant in San Francisco USING GOOGLE SEARCH",
        max_steps=30,
    )
    print(f"\nResult: {result}")

if __name__ == "__main__":
    # Run the appropriate example
    asyncio.run(main())
```

This example demonstrates how to connect to an MCP server running on a specific HTTP port. Make sure to start your MCP server before running this example.

# Multi-Server Support

MCP-Use allows configuring and connecting to multiple MCP servers simultaneously using the `MCPClient`. This enables complex workflows that require tools from different servers, such as web browsing combined with file operations or 3D modeling.

## Configuration

You can configure multiple servers in your configuration file:

```json
{
  "mcpServers": {
    "airbnb": {
      "command": "npx",
      "args": ["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {
        "DISPLAY": ":1"
      }
    }
  }
}
```

## Usage

The `MCPClient` class provides methods for managing connections to multiple servers. When creating an `MCPAgent`, you can provide an `MCPClient` configured with multiple servers.

By default, the agent will have access to tools from all configured servers. If you need to target a specific server for a particular task, you can specify the `server_name` when calling the `agent.run()` method.

```python
# Example: Manually selecting a server for a specific task
result = await agent.run(
    "Search for Airbnb listings in Barcelona",
    server_name="airbnb" # Explicitly use the airbnb server
)

result_google = await agent.run(
    "Find restaurants near the first result using Google Search",
    server_name="playwright" # Explicitly use the playwright server
)
```

## Dynamic Server Selection (Server Manager)

For enhanced efficiency and to reduce potential agent confusion when dealing with many tools from different servers, you can enable the Server Manager by setting `use_server_manager=True` during `MCPAgent` initialization.

When enabled, the agent intelligently selects the correct MCP server based on the tool chosen by the LLM for a specific step. This minimizes unnecessary connections and ensures the agent uses the appropriate tools for the task.

```python
import asyncio
from mcp_use import MCPClient, MCPAgent
from langchain_anthropic import ChatAnthropic

async def main():
    # Create client with multiple servers
    client = MCPClient.from_config_file("multi_server_config.json")

    # Create agent with the client
    agent = MCPAgent(
        llm=ChatAnthropic(model="claude-3-5-sonnet-20240620"),
        client=client,
        use_server_manager=True  # Enable the Server Manager
    )

    try:
        # Run a query that uses tools from multiple servers
        result = await agent.run(
            "Search for a nice place to stay in Barcelona on Airbnb, "
            "then use Google to find nearby restaurants and attractions."
        )
        print(result)
    finally:
        # Clean up all sessions
        await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(main())
```

# Tool Access Control

MCP-Use allows you to restrict which tools are available to the agent, providing better security and control over agent capabilities:

```python
import asyncio
from mcp_use import MCPAgent, MCPClient
from langchain_openai import ChatOpenAI

async def main():
    # Create client
    client = MCPClient.from_config_file("config.json")

    # Create agent with restricted tools
    agent = MCPAgent(
        llm=ChatOpenAI(model="gpt-4"),
        client=client,
        disallowed_tools=["file_system", "network"]  # Restrict potentially dangerous tools
    )

    # Run a query with restricted tool access
    result = await agent.run(
        "Find the best restaurant in San Francisco"
    )
    print(result)

    # Clean up
    await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(main())
```

# Sandboxed Execution

MCP-Use supports running MCP servers in a sandboxed environment using E2B's cloud infrastructure. This allows you to run MCP servers without having to install dependencies locally, making it easier to use tools that might have complex setups or system requirements.

## Installation

To use sandboxed execution, you need to install the E2B dependency:

```bash
# Install mcp-use with E2B support
pip install "mcp-use[e2b]"

# Or install the dependency directly
pip install e2b-code-interpreter
```

You'll also need an E2B API key. You can sign up at [e2b.dev](https://e2b.dev) to get your API key.

## Configuration

To enable sandboxed execution, use the sandbox parameter when creating your `MCPClient`:

```python
import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
from mcp_use.types.sandbox import SandboxOptions

async def main():
    # Load environment variables (needs E2B_API_KEY)
    load_dotenv()

    # Define MCP server configuration
    server_config = {
        "mcpServers": {
            "everything": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-everything"],
            }
        }
    }

    # Define sandbox options
    sandbox_options: SandboxOptions = {
        "api_key": os.getenv("E2B_API_KEY"),  # API key can also be provided directly
        "sandbox_template_id": "base",  # Use base template
    }

    # Create client with sandboxed mode enabled
    client = MCPClient(
        config=server_config,
        sandbox=True,
        sandbox_options=sandbox_options,

    )

    # Create agent with the sandboxed client
    llm = ChatOpenAI(model="gpt-4o")
    agent = MCPAgent(llm=llm, client=client)

    # Run your agent
    result = await agent.run("Use the command line tools to help me add 1+1")
    print(result)

    # Clean up
    await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(main())
```

## Sandbox Options

The `SandboxOptions` type provides configuration for the sandbox environment:

| Option                 | Description                                                                              | Default               |
| ---------------------- | ---------------------------------------------------------------------------------------- | --------------------- |
| `api_key`              | E2B API key. Required - can be provided directly or via E2B_API_KEY environment variable | None                  |
| `sandbox_template_id`  | Template ID for the sandbox environment                                                  | "base"                |
| `supergateway_command` | Command to run supergateway                                                              | "npx -y supergateway" |

## Benefits of Sandboxed Execution

- **No local dependencies**: Run MCP servers without installing dependencies locally
- **Isolation**: Execute code in a secure, isolated environment
- **Consistent environment**: Ensure consistent behavior across different systems
- **Resource efficiency**: Offload resource-intensive tasks to cloud infrastructure

# Build a Custom Agent:

You can also build your own custom agent using the LangChain adapter:

```python
import asyncio
from langchain_openai import ChatOpenAI
from mcp_use.client import MCPClient
from mcp_use.adapters.langchain_adapter import LangChainAdapter
from dotenv import load_dotenv

load_dotenv()


async def main():
    # Initialize MCP client
    client = MCPClient.from_config_file("examples/browser_mcp.json")
    llm = ChatOpenAI(model="gpt-4o")

    # Create adapter instance
    adapter = LangChainAdapter()
    # Get LangChain tools with a single line
    tools = await adapter.create_tools(client)

    # Create a custom LangChain agent
    llm_with_tools = llm.bind_tools(tools)
    result = await llm_with_tools.ainvoke("What tools do you have avilable ? ")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())


```

# Debugging

MCP-Use provides a built-in debug mode that increases log verbosity and helps diagnose issues in your agent implementation.

## Enabling Debug Mode

There are two primary ways to enable debug mode:

### 1. Environment Variable (Recommended for One-off Runs)

Run your script with the `DEBUG` environment variable set to the desired level:

```bash
# Level 1: Show INFO level messages
DEBUG=1 python3.11 examples/browser_use.py

# Level 2: Show DEBUG level messages (full verbose output)
DEBUG=2 python3.11 examples/browser_use.py
```

This sets the debug level only for the duration of that specific Python process.

Alternatively you can set the following environment variable to the desired logging level:

```bash
export MCP_USE_DEBUG=1 # or 2
```

### 2. Setting the Debug Flag Programmatically

You can set the global debug flag directly in your code:

```python
import mcp_use

mcp_use.set_debug(1)  # INFO level
# or
mcp_use.set_debug(2)  # DEBUG level (full verbose output)
```

### 3. Agent-Specific Verbosity

If you only want to see debug information from the agent without enabling full debug logging, you can set the `verbose` parameter when creating an MCPAgent:

```python
# Create agent with increased verbosity
agent = MCPAgent(
    llm=your_llm,
    client=your_client,
    verbose=True  # Only shows debug messages from the agent
)
```

This is useful when you only need to see the agent's steps and decision-making process without all the low-level debug information from other components.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=pietrozullo/mcp-use&type=Date)](https://www.star-history.com/#pietrozullo/mcp-use&Date)

# Contributing

We love contributions! Feel free to open issues for bugs or feature requests. Look at [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Contributors

Thanks to all our amazing contributors!

<a href="https://github.com/mcp-use/mcp-use/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=mcp-use/mcp-use" />
</a>


## Top Starred Dependents

<!-- gh-dependents-info-used-by-start -->

<table>
  <tr>
    <th width="400">Repository</th>
    <th>Stars</th>
  </tr>
</table>

<!-- gh-dependents-info-used-by-end -->

# Requirements

- Python 3.11+
- MCP implementation (like Playwright MCP)
- LangChain and appropriate model libraries (OpenAI, Anthropic, etc.)

# License

MIT
# Citation

If you use MCP-Use in your research or project, please cite:

```bibtex
@software{mcp_use2025,
  author = {Zullo, Pietro},
  title = {MCP-Use: MCP Library for Python},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/pietrozullo/mcp-use}
}
```
