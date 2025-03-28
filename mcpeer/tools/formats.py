"""
Tool format definitions for different LLM providers.

This module provides type definitions and interfaces for converting
MCP tool schemas to formats required by different LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Any


class ToolFormat(ABC):
    """Base class for LLM tool formats.

    This abstract class defines the interface for converting MCP tool schemas
    to the format required by a specific LLM provider.
    """

    @abstractmethod
    def convert_tool(self, tool: dict[str, Any]) -> dict[str, Any]:
        """Convert an MCP tool schema to the LLM-specific format.

        Args:
            tool: The MCP tool schema to convert.

        Returns:
            The converted tool in the LLM-specific format.
        """
        pass

    @abstractmethod
    def convert_tool_call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Convert a tool call from the LLM format to the MCP format.

        Args:
            name: The name of the tool being called.
            arguments: The arguments for the tool call.

        Returns:
            The converted tool call in the MCP format.
        """
        pass

    @abstractmethod
    def parse_tool_call(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse tool calls from the LLM response.

        Args:
            response: The response from the LLM.

        Returns:
            A list of parsed tool calls, each containing 'name' and 'arguments' keys.
        """
        pass


class OpenAIToolFormat(ToolFormat):
    """Tool format for OpenAI models.

    This class converts between MCP tool schemas and the format required by
    OpenAI's function calling API.
    """

    def convert_tool(self, tool: dict[str, Any]) -> dict[str, Any]:
        """Convert an MCP tool schema to the OpenAI function format.

        Args:
            tool: The MCP tool schema to convert.

        Returns:
            The converted tool in the OpenAI function format.
        """
        return {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("inputSchema", {}),
            },
        }

    def convert_tool_call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Convert a tool call from the OpenAI format to the MCP format.

        Args:
            name: The name of the tool being called.
            arguments: The arguments for the tool call.

        Returns:
            The converted tool call in the MCP format.
        """
        return {"name": name, "arguments": arguments}

    def parse_tool_call(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse tool calls from the OpenAI response.

        Args:
            response: The response from OpenAI.

        Returns:
            A list of parsed tool calls, each containing 'name' and 'arguments' keys.
        """
        tool_calls = []

        # Navigate through the response structure to find tool calls
        for message in response.get("choices", [{}])[0].get("message", {}).get("tool_calls", []):
            if message.get("type") == "function":
                function = message.get("function", {})
                name = function.get("name", "")

                # Parse the arguments
                arguments = {}
                args_str = function.get("arguments", "{}")
                try:
                    import json

                    arguments = json.loads(args_str)
                except Exception:
                    pass

                tool_calls.append({"name": name, "arguments": arguments})

        return tool_calls


class AnthropicToolFormat(ToolFormat):
    """Tool format for Anthropic models.

    This class converts between MCP tool schemas and the format required by
    Anthropic's tool use API.
    """

    def convert_tool(self, tool: dict[str, Any]) -> dict[str, Any]:
        """Convert an MCP tool schema to the Anthropic tool format.

        Args:
            tool: The MCP tool schema to convert.

        Returns:
            The converted tool in the Anthropic tool format.
        """
        return {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "input_schema": tool.get("inputSchema", {}),
        }

    def convert_tool_call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Convert a tool call from the Anthropic format to the MCP format.

        Args:
            name: The name of the tool being called.
            arguments: The arguments for the tool call.

        Returns:
            The converted tool call in the MCP format.
        """
        return {"name": name, "arguments": arguments}

    def parse_tool_call(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse tool calls from the Anthropic response.

        Args:
            response: The response from Anthropic.

        Returns:
            A list of parsed tool calls, each containing 'name' and 'arguments' keys.
        """
        tool_calls = []

        # Navigate through the response structure to find tool calls
        content_blocks = response.get("content", [])
        for block in content_blocks:
            if block.get("type") == "tool_use":
                tool_use = block.get("tool_use", {})
                name = tool_use.get("name", "")
                arguments = tool_use.get("input", {})

                tool_calls.append({"name": name, "arguments": arguments})

        return tool_calls
