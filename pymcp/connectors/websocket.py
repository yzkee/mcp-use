"""
WebSocket connector for MCP implementations.

This module provides a connector for communicating with MCP implementations
through WebSocket connections.
"""

import asyncio
import json
import uuid
from typing import Any

import websockets
from websockets.client import WebSocketClientProtocol

from .base import BaseConnector


class WebSocketConnector(BaseConnector):
    """Connector for MCP implementations using WebSocket transport.

    This connector uses WebSockets to communicate with remote MCP implementations.
    """

    def __init__(
        self, url: str, auth_token: str | None = None, headers: dict[str, str] | None = None
    ):
        """Initialize a new WebSocket connector.

        Args:
            url: The WebSocket URL to connect to.
            auth_token: Optional authentication token.
            headers: Optional additional headers.
        """
        self.url = url
        self.auth_token = auth_token
        self.headers = headers or {}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        self.ws: WebSocketClientProtocol | None = None
        self.pending_requests: dict[str, asyncio.Future] = {}

    async def connect(self) -> None:
        """Establish a connection to the MCP implementation."""
        self.ws = await websockets.connect(self.url, extra_headers=self.headers)

        # Start the message receiver task
        self._receiver_task = asyncio.create_task(self._receive_messages())

    async def _receive_messages(self) -> None:
        """Continuously receive and process messages from the WebSocket."""
        if not self.ws:
            raise RuntimeError("WebSocket is not connected")

        try:
            async for message in self.ws:
                # Parse the message
                data = json.loads(message)

                # Check if this is a response to a pending request
                request_id = data.get("id")
                if request_id and request_id in self.pending_requests:
                    future = self.pending_requests.pop(request_id)
                    if "result" in data:
                        future.set_result(data["result"])
                    elif "error" in data:
                        future.set_exception(Exception(data["error"]))
        except Exception as e:
            # If the websocket connection was closed or errored,
            # reject all pending requests
            for future in self.pending_requests.values():
                if not future.done():
                    future.set_exception(e)

    async def disconnect(self) -> None:
        """Close the connection to the MCP implementation."""
        if self._receiver_task:
            self._receiver_task.cancel()
            try:
                await self._receiver_task
            except asyncio.CancelledError:
                pass

        if self.ws:
            await self.ws.close()
            self.ws = None

        # Reject any pending requests
        for future in self.pending_requests.values():
            if not future.done():
                future.set_exception(ConnectionError("WebSocket disconnected"))
        self.pending_requests.clear()

    async def _send_request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Send a request and wait for a response."""
        if not self.ws:
            raise RuntimeError("WebSocket is not connected")

        # Create a request ID
        request_id = str(uuid.uuid4())

        # Create a future to receive the response
        future = asyncio.Future()
        self.pending_requests[request_id] = future

        # Send the request
        await self.ws.send(json.dumps({"id": request_id, "method": method, "params": params or {}}))

        # Wait for the response
        try:
            return await future
        except Exception as e:
            # Remove the request from pending requests
            self.pending_requests.pop(request_id, None)
            raise e

    async def initialize(self) -> dict[str, Any]:
        """Initialize the MCP session and return session information."""
        return await self._send_request("initialize")

    async def list_tools(self) -> list[dict[str, Any]]:
        """List all available tools from the MCP implementation."""
        result = await self._send_request("tools/list")
        return result.get("tools", [])

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call an MCP tool with the given arguments."""
        return await self._send_request("tools/call", {"name": name, "arguments": arguments})

    async def list_resources(self) -> list[dict[str, Any]]:
        """List all available resources from the MCP implementation."""
        result = await self._send_request("resources/list")
        return result

    async def read_resource(self, uri: str) -> tuple[bytes, str]:
        """Read a resource by URI."""
        result = await self._send_request("resources/read", {"uri": uri})
        return result.get("content", b""), result.get("mimeType", "")

    async def request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Send a raw request to the MCP implementation."""
        return await self._send_request(method, params)
