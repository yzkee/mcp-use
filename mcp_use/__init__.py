"""
mcp_use - An MCP library for LLMs.

This library provides a unified interface for connecting different LLMs
to MCP tools through existing LangChain adapters.
"""

from .agents.mcpagent import MCPAgent
from .client import MCPClient
from .config import create_session_from_config, load_config_file
from .connectors import BaseConnector, HttpConnector, StdioConnector, WebSocketConnector
from .logging import logger
from .session import MCPSession

__version__ = "0.0.3"
__all__ = [
    "MCPAgent",
    "MCPClient",
    "MCPSession",
    "BaseConnector",
    "StdioConnector",
    "WebSocketConnector",
    "HttpConnector",
    "create_session_from_config",
    "load_config_file",
    "logger",
]
