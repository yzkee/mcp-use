"""
Base connector for MCP implementations.

This module provides the base connector interface that all MCP connectors
must implement.
"""

from abc import ABC, abstractmethod
from typing import Any

from mcpeer.types import Tool


class BaseConnector(ABC):
    """Base class for MCP connectors.

    This class defines the interface that all MCP connectors must implement.
    """

    @abstractmethod
    async def connect(self) -> None:
        """Establish a connection to the MCP implementation."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection to the MCP implementation."""
        pass

    @abstractmethod
    async def initialize(self) -> dict[str, Any]:
        """Initialize the MCP session and return session information."""
        pass

    @property
    @abstractmethod
    def tools(self) -> list[Tool]:
        """Get the list of available tools."""
        pass

    @abstractmethod
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call an MCP tool with the given arguments."""
        pass

    @abstractmethod
    async def list_resources(self) -> list[dict[str, Any]]:
        """List all available resources from the MCP implementation."""
        pass

    @abstractmethod
    async def read_resource(self, uri: str) -> tuple[bytes, str]:
        """Read a resource by URI."""
        pass

    @abstractmethod
    async def request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Send a raw request to the MCP implementation."""
        pass
