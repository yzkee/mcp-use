"""
Basic usage example for the Model-Agnostic MCP Library for LLMs.

This example demonstrates how to use the mcpeer library to connect
any LLM to MCP tools through a unified interface.
"""

import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from mcpeer import MCPAgent
from mcpeer.connectors.stdio import StdioConnector


async def run():
    # Load environment variables
    load_dotenv()

    connector = StdioConnector(
        command="npx",
        args=["@playwright/mcp@latest"],
        env={"DISPLAY": ":1"},
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
    )

    mcp_client = MCPAgent(connector=connector, llm=llm, max_steps=30)

    result = await mcp_client.run(
        "Go on google flight and tell me how much it costs to go from Zurich to Munich "
        "next weekm I want the cheapest option?",
        max_steps=30,
    )
    print(f"\nResult: {result}")


if __name__ == "__main__":
    asyncio.run(run())
