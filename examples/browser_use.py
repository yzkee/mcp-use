"""
Basic usage example for the Model-Agnostic MCP Library for LLMs.

This example demonstrates how to use the pymcp library to connect
any LLM to MCP tools through a unified interface.
"""

import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from mcpeer import MCPAgent
from mcpeer.connectors.stdio import StdioConnector


async def run():
    """Run the example."""
    # Load environment variables
    load_dotenv()

    # Create the stdio connector
    print("Creating stdio connector...")

    connector = StdioConnector(
        command="npx",
        args=["@playwright/mcp@latest"],
        env={"DISPLAY": ":1"},
    )

    # connector = StdioConnector(
    #     command="npx",
    #     args=["-y", "@modelcontextprotocol/server-puppeteer",],
    #     env={"DISPLAY": ":1"},
    # )

    # Create the LangChain LLM
    print("Creating LangChain LLM...")
    llm = ChatOpenAI(
        model="gpt-4o-mini",
    )

    # llm = ChatAnthropic(
    #     model="claude-3-7-sonnet-20240229",
    # )

    # Create MCP client
    print("Creating MCP client...")
    mcp_client = MCPAgent(connector=connector, llm=llm, max_steps=30)

    try:
        # Run a query
        print("\nRunning query...")
        result = await mcp_client.run(
            "Go on google flight and tell me how much it costs to go from Zurich to Munich "
            "next weekm I want the cheapest option?",
            max_steps=30,
        )
        print(f"\nResult: {result}")

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run())
