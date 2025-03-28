"""
StdIO connector for MCP implementations.

This module provides a connector for communicating with MCP implementations
through the standard input/output streams.
"""

from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool

from .base import BaseConnector


class StdioConnector(BaseConnector):
    """Connector for MCP implementations using stdio transport.

    This connector uses the stdio transport to communicate with MCP implementations
    that are executed as child processes.
    """

    def __init__(
        self,
        command: str = "npx",
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ):
        """Initialize a new stdio connector.

        Args:
            command: The command to execute.
            args: Optional command line arguments.
            env: Optional environment variables.
        """
        self.command = command
        self.args = args or ["@playwright/mcp@latest"]
        self.env = env
        self.client: ClientSession | None = None
        self._stdio_ctx = None
        self._tools: list[Tool] | None = None

    async def connect(self) -> None:
        """Establish a connection to the MCP implementation."""
        server_params = StdioServerParameters(command=self.command, args=self.args, env=self.env)
        self._stdio_ctx = stdio_client(server_params)
        read_stream, write_stream = await self._stdio_ctx.__aenter__()
        self.client = ClientSession(read_stream, write_stream, sampling_callback=None)
        await self.client.__aenter__()

    async def disconnect(self) -> None:
        """Close the connection to the MCP implementation."""
        try:
            if self.client:
                await self.client.__aexit__(None, None, None)
            if self._stdio_ctx:
                await self._stdio_ctx.__aexit__(None, None, None)
        finally:
            # Always clean up references even if there were errors
            self.client = None
            self._stdio_ctx = None
            self._tools = None

    async def __aenter__(self) -> "StdioConnector":
        """Enter the async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager."""
        await self.disconnect()

    async def initialize(self) -> dict[str, Any]:
        """Initialize the MCP session and return session information."""
        if not self.client:
            raise RuntimeError("MCP client is not connected")

        # Initialize the session
        result = await self.client.initialize()

        # Get available tools
        tools_result = await self.client.list_tools()
        self._tools = tools_result.tools

        return result

    @property
    def tools(self) -> list[Tool]:
        """Get the list of available tools."""
        if not self._tools:
            raise RuntimeError("MCP client is not initialized")
        return self._tools

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call an MCP tool with the given arguments."""
        if not self.client:
            raise RuntimeError("MCP client is not connected")
        return await self.client.call_tool(name, arguments)

    async def list_resources(self) -> list[dict[str, Any]]:
        """List all available resources from the MCP implementation."""
        if not self.client:
            raise RuntimeError("MCP client is not connected")
        resources = await self.client.list_resources()
        return resources

    async def read_resource(self, uri: str) -> tuple[bytes, str]:
        """Read a resource by URI."""
        if not self.client:
            raise RuntimeError("MCP client is not connected")
        resource = await self.client.read_resource(uri)
        return resource.content, resource.mimeType

    async def request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Send a raw request to the MCP implementation."""
        if not self.client:
            raise RuntimeError("MCP client is not connected")
        return await self.client.request({"method": method, "params": params or {}})
