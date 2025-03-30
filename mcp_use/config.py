"""
Configuration loader for MCP session.

This module provides functionality to load MCP configuration from JSON files.
"""

import json
from typing import Any

from .connectors import BaseConnector, HttpConnector, StdioConnector, WebSocketConnector
from .session import MCPSession


def load_config_file(filepath: str) -> dict[str, Any]:
    """Load a configuration file.

    Args:
        filepath: Path to the configuration file

    Returns:
        The parsed configuration
    """
    with open(filepath) as f:
        return json.load(f)


def create_connector_from_config(server_config: dict[str, Any]) -> BaseConnector:
    """Create a connector based on server configuration.

    Args:
        server_config: The server configuration section

    Returns:
        A configured connector instance
    """
    # Stdio connector (command-based)
    if "command" in server_config and "args" in server_config:
        return StdioConnector(
            command=server_config["command"],
            args=server_config["args"],
            env=server_config.get("env", None),
        )

    # HTTP connector
    elif "url" in server_config:
        return HttpConnector(
            url=server_config["url"],
            headers=server_config.get("headers", None),
            auth=server_config.get("auth", None),
        )

    # WebSocket connector
    elif "ws_url" in server_config:
        return WebSocketConnector(
            url=server_config["ws_url"],
            headers=server_config.get("headers", None),
            auth=server_config.get("auth", None),
        )

    raise ValueError("Cannot determine connector type from config")


def create_session_from_config(
    filepath: str,
    server_name: str | None = None,
) -> MCPSession:
    """Create an MCPSession from a configuration file.

    Args:
        filepath: Path to the configuration file
        server_name: Name of the server to use from config, uses first if None

    Returns:
        Configured MCPSession instance
    """
    config = load_config_file(filepath)

    # Get server config
    servers = config.get("mcpServers", {})
    if not servers:
        raise ValueError("No MCP servers defined in config")

    # If server_name not specified, use the first one
    if not server_name:
        server_name = next(iter(servers.keys()))

    if server_name not in servers:
        raise ValueError(f"Server '{server_name}' not found in config")

    server_config = servers[server_name]
    connector = create_connector_from_config(server_config)

    return MCPSession(connector)
