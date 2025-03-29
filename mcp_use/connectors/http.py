"""
HTTP connector for MCP implementations.

This module provides a connector for communicating with MCP implementations
through HTTP APIs.
"""

from typing import Any

import aiohttp

from .base import BaseConnector


class HttpConnector(BaseConnector):
    """Connector for MCP implementations using HTTP transport.

    This connector uses HTTP requests to communicate with remote MCP implementations.
    """

    def __init__(
        self, base_url: str, auth_token: str | None = None, headers: dict[str, str] | None = None
    ):
        """Initialize a new HTTP connector.

        Args:
            base_url: The base URL of the MCP HTTP API.
            auth_token: Optional authentication token.
            headers: Optional additional headers.
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.headers = headers or {}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        self.session: aiohttp.ClientSession | None = None

    async def connect(self) -> None:
        """Establish a connection to the MCP implementation."""
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def disconnect(self) -> None:
        """Close the connection to the MCP implementation."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _request(self, method: str, endpoint: str, data: dict[str, Any] | None = None) -> Any:
        """Send an HTTP request to the MCP API.

        Args:
            method: The HTTP method (GET, POST, etc.).
            endpoint: The API endpoint path.
            data: Optional request data.

        Returns:
            The parsed JSON response.
        """
        if not self.session:
            raise RuntimeError("HTTP session is not connected")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        if method.upper() == "GET" and data:
            # For GET requests, convert data to query parameters
            async with self.session.get(url, params=data) as response:
                response.raise_for_status()
                return await response.json()
        else:
            # For other methods, send data as JSON body
            async with self.session.request(method, url, json=data) as response:
                response.raise_for_status()
                return await response.json()

    async def initialize(self) -> dict[str, Any]:
        """Initialize the MCP session and return session information."""
        return await self._request("POST", "initialize")

    async def list_tools(self) -> list[dict[str, Any]]:
        """List all available tools from the MCP implementation."""
        result = await self._request("GET", "tools")
        return result.get("tools", [])

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call an MCP tool with the given arguments."""
        return await self._request("POST", f"tools/{name}", arguments)

    async def list_resources(self) -> list[dict[str, Any]]:
        """List all available resources from the MCP implementation."""
        result = await self._request("GET", "resources")
        return result

    async def read_resource(self, uri: str) -> tuple[bytes, str]:
        """Read a resource by URI."""
        # For resources, we may need to handle binary data
        if not self.session:
            raise RuntimeError("HTTP session is not connected")

        url = f"{self.base_url}/resources/read"

        async with self.session.get(url, params={"uri": uri}) as response:
            response.raise_for_status()

            # Check if this is a JSON response or binary data
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                data = await response.json()
                content = data.get("content", b"")
                mime_type = data.get("mimeType", "")

                # If content is base64 encoded, decode it
                if isinstance(content, str):
                    import base64

                    content = base64.b64decode(content)

                return content, mime_type
            else:
                # Assume binary response
                content = await response.read()
                return content, content_type

    async def request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Send a raw request to the MCP implementation."""
        # For custom methods, we'll use the RPC-style endpoint
        return await self._request("POST", "rpc", {"method": method, "params": params or {}})
