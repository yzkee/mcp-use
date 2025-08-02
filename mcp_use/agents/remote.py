"""
Remote agent implementation for executing agents via API.
"""

import os
from collections.abc import AsyncGenerator
from typing import TypeVar

import httpx
from langchain.schema import BaseMessage
from pydantic import BaseModel

from ..logging import logger

T = TypeVar("T", bound=BaseModel)


class RemoteAgent:
    """Agent that executes remotely via API."""

    def __init__(self, agent_id: str, api_key: str | None = None, base_url: str = "https://cloud.mcp-use.com"):
        """Initialize remote agent.

        Args:
            agent_id: The ID of the remote agent to execute
            api_key: API key for authentication. If None, will check MCP_USE_API_KEY env var
            base_url: Base URL for the remote API
        """
        self.agent_id = agent_id
        self.base_url = base_url

        # Handle API key validation
        if api_key is None:
            api_key = os.getenv("MCP_USE_API_KEY")

        if not api_key:
            raise ValueError(
                "API key is required for remote execution. "
                "Please provide it as a parameter or set the MCP_USE_API_KEY environment variable."
            )

        self.api_key = api_key
        # Configure client with reasonable timeouts for agent execution
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,  # 10 seconds to establish connection
                read=300.0,  # 5 minutes to read response (agents can take time)
                write=10.0,  # 10 seconds to send request
                pool=10.0,  # 10 seconds to get connection from pool
            )
        )

    async def run(
        self,
        query: str,
        max_steps: int | None = None,
        manage_connector: bool = True,
        external_history: list[BaseMessage] | None = None,
        output_schema: type[T] | None = None,
    ) -> str | T:
        """Run a query on the remote agent.

        Args:
            query: The query to execute
            max_steps: Maximum number of steps (default: 10)
            manage_connector: Ignored for remote execution
            external_history: Ignored for remote execution (not supported yet)
            output_schema: Ignored for remote execution (not supported yet)

        Returns:
            The result from the remote agent execution
        """
        if output_schema is not None:
            logger.warning("Structured output (output_schema) is not yet supported for remote execution")

        if external_history is not None:
            logger.warning("External history is not yet supported for remote execution")

        payload = {"query": query, "max_steps": max_steps or 10}

        headers = {"Content-Type": "application/json", "x-api-key": self.api_key}

        url = f"{self.base_url}/api/v1/agents/{self.agent_id}/run"

        try:
            logger.info(f"🌐 Executing query on remote agent {self.agent_id}")
            response = await self._client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            logger.info("✅ Remote execution completed successfully")

            # The API should return the result directly as a string
            if isinstance(result, dict) and "result" in result:
                return result["result"]
            elif isinstance(result, str):
                return result
            else:
                return str(result)

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Remote execution failed with status {e.response.status_code}: {e.response.text}")
            raise RuntimeError(f"Remote agent execution failed: {e.response.status_code} - {e.response.text}") from e
        except httpx.TimeoutException as e:
            logger.error(f"❌ Remote execution timed out: {e}")
            raise RuntimeError(
                "Remote agent execution timed out. The server may be overloaded or the query is taking too long to "
                "process. Try again or use a simpler query."
            ) from e
        except httpx.ConnectError as e:
            logger.error(f"❌ Remote execution connection error: {e}")
            raise RuntimeError(
                f"Remote agent connection failed: Cannot connect to {self.base_url}. "
                f"Check if the server is running and the URL is correct."
            ) from e
        except Exception as e:
            logger.error(f"❌ Remote execution error: {e}")
            raise RuntimeError(f"Remote agent execution failed: {str(e)}") from e

    async def stream(
        self,
        query: str,
        max_steps: int | None = None,
        _manage_connector: bool = True,
        external_history: list[BaseMessage] | None = None,
        _track_execution: bool = True,
        output_schema: type[T] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream the agent execution via remote API.

        Args:
            query: The query to execute
            max_steps: Maximum number of steps (default: 10)
            manage_connector: Ignored for remote execution
            external_history: Ignored for remote execution (not supported yet)
            track_execution: Ignored for remote execution
            output_schema: Ignored for remote execution (not supported yet)

        Yields:
            Streaming response chunks from the remote agent
        """
        if output_schema is not None:
            logger.warning("Structured output (output_schema) is not yet supported for remote streaming")

        if external_history is not None:
            logger.warning("External history is not yet supported for remote streaming")

        payload = {"query": query, "max_steps": max_steps or 10}

        headers = {"Content-Type": "application/json", "x-api-key": self.api_key}

        url = f"{self.base_url}/api/v1/agents/{self.agent_id}/stream"

        try:
            logger.info(f"🌐 Starting streaming execution on remote agent {self.agent_id}")

            async with self._client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()

                async for chunk in response.aiter_text():
                    if chunk.strip():  # Only yield non-empty chunks
                        yield chunk

            logger.info("✅ Remote streaming completed successfully")

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Remote streaming failed with status {e.response.status_code}: {e.response.text}")
            raise RuntimeError(f"Remote agent streaming failed: {e.response.status_code} - {e.response.text}") from e
        except httpx.TimeoutException as e:
            logger.error(f"❌ Remote streaming timed out: {e}")
            raise RuntimeError(
                "Remote agent streaming timed out. The server may be overloaded or the query is taking too long to "
                "process."
            ) from e
        except httpx.ConnectError as e:
            logger.error(f"❌ Remote streaming connection error: {e}")
            raise RuntimeError(
                f"Remote agent streaming connection failed: Cannot connect to {self.base_url}. "
                f"Check if the server is running and the URL is correct."
            ) from e
        except Exception as e:
            logger.error(f"❌ Remote streaming error: {e}")
            raise RuntimeError(f"Remote agent streaming failed: {str(e)}") from e

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
        logger.info("🔌 Remote agent client closed")
