"""
mcpeer - A model-agnostic MCP (Multi-Channel Platform) library for LLMs.

This library provides a unified interface for connecting different LLMs
to MCP tools through existing LangChain adapters.
"""

from .agents.mcpagent import MCPAgent
from .connectors import BaseConnector, HttpConnector, StdioConnector, WebSocketConnector
from .session import MCPSession
from .tools.converter import ModelProvider, ToolConverter

__version__ = "0.1.0"
__all__ = [
    "MCPAgent",
    "MCPSession",
    "BaseConnector",
    "StdioConnector",
    "WebSocketConnector",
    "HttpConnector",
    "ModelProvider",
    "ToolConverter",
]
