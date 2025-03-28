"""
Tool converter for different LLM providers.

This module provides utilities for converting between MCP tool schemas
and LLM-specific formats.
"""

from enum import Enum, auto
from typing import Any

from .formats import AnthropicToolFormat, OpenAIToolFormat, ToolFormat


class ModelProvider(Enum):
    """Enum for supported model providers."""

    OPENAI = auto()
    ANTHROPIC = auto()

    @classmethod
    def from_string(cls, value: str) -> "ModelProvider":
        """Convert a string to a ModelProvider enum.

        Args:
            value: The string to convert.

        Returns:
            The corresponding ModelProvider enum value.

        Raises:
            ValueError: If the string is not a valid model provider.
        """
        value = value.lower()
        if value in ("openai", "open_ai", "open-ai"):
            return cls.OPENAI
        elif value in ("anthropic", "claude"):
            return cls.ANTHROPIC
        else:
            raise ValueError(f"Unsupported model provider: {value}")


class ToolConverter:
    """Converter for MCP tools to different LLM formats.

    This class provides utilities for converting between MCP tool schemas
    and LLM-specific formats.
    """

    _format_classes: dict[ModelProvider, type[ToolFormat]] = {
        ModelProvider.OPENAI: OpenAIToolFormat,
        ModelProvider.ANTHROPIC: AnthropicToolFormat,
    }

    def __init__(self, provider: str | ModelProvider) -> None:
        """Initialize a new tool converter.

        Args:
            provider: The model provider to convert tools for.
                Can be a string or a ModelProvider enum.

        Raises:
            ValueError: If the provider is not supported.
        """
        if isinstance(provider, str):
            self.provider = ModelProvider.from_string(provider)
        else:
            self.provider = provider

        # Create an instance of the appropriate format class
        format_class = self._format_classes.get(self.provider)
        if not format_class:
            raise ValueError(f"Unsupported model provider: {provider}")

        self._format = format_class()

    def convert_tools(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert a list of MCP tools to the LLM-specific format.

        Args:
            tools: The list of MCP tools to convert.

        Returns:
            The converted tools in the LLM-specific format.
        """
        return [self._format.convert_tool(tool) for tool in tools]

    def convert_tool_call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Convert a tool call to the MCP format.

        Args:
            name: The name of the tool being called.
            arguments: The arguments for the tool call.

        Returns:
            The converted tool call in the MCP format.
        """
        return self._format.convert_tool_call(name, arguments)

    def parse_tool_calls(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse tool calls from an LLM response.

        Args:
            response: The response from the LLM.

        Returns:
            A list of parsed tool calls, each containing 'name' and 'arguments' keys.
        """
        return self._format.parse_tool_call(response)
