"""
MCP: Main integration module.

This module provides the main MCPAgent class that integrates all components
to provide a simple interface for using MCP tools with different LLMs.
"""

from langchain.schema.language_model import BaseLanguageModel

from mcp_use.client import MCPClient
from mcp_use.connectors.base import BaseConnector
from mcp_use.session import MCPSession

from ..logging import logger
from .langchain_agent import LangChainAgent


class MCPAgent:
    """Main class for using MCP tools with various LLM providers.

    This class provides a unified interface for using MCP tools with different LLM providers
    through LangChain's agent framework.
    """

    def __init__(
        self,
        llm: BaseLanguageModel,
        client: MCPClient | None = None,
        connector: BaseConnector | None = None,
        server_name: str | None = None,
        max_steps: int = 5,
        auto_initialize: bool = False,
    ):
        """Initialize a new MCPAgent instance.

        Args:
            llm: The LangChain LLM to use.
            client: The MCPClient to use. If provided, connector is ignored.
            connector: The MCP connector to use if client is not provided.
            server_name: The name of the server to use if client is provided.
            max_steps: The maximum number of steps to take.
            auto_initialize: Whether to automatically initialize the agent when run is called.
        """
        self.llm = llm
        self.client = client
        self.connector = connector
        self.server_name = server_name
        self.max_steps = max_steps
        self.auto_initialize = auto_initialize
        self._initialized = False

        # Either client or connector must be provided
        if not client and not connector:
            raise ValueError("Either client or connector must be provided")

        self._agent: LangChainAgent | None = None
        self._session: MCPSession | None = None

    async def initialize(self) -> None:
        """Initialize the MCP client and agent."""
        # If using client, get or create a session
        if self.client:
            try:
                self._session = self.client.get_session(self.server_name)
            except ValueError:
                self._session = await self.client.create_session(self.server_name)
            connector_to_use = self._session.connector
        else:
            # Using direct connector
            connector_to_use = self.connector
            await connector_to_use.connect()
            await connector_to_use.initialize()

        # Create the agent
        self._agent = LangChainAgent(
            connector=connector_to_use, llm=self.llm, max_steps=self.max_steps
        )

        # Initialize the agent
        await self._agent.initialize()
        self._initialized = True

    async def close(self) -> None:
        """Close the MCP connection."""
        try:
            if self._agent:
                # Clean up the agent first
                self._agent = None

            # If using client with session, close the session through client
            if self.client and self._session:
                await self.client.close_session(self.server_name)
            # If using direct connector, disconnect
            elif self.connector:
                await self.connector.disconnect()

            self._initialized = False
        except Exception as e:
            logger.warning(f"Warning: Error during agent closure: {e}")
            # Still try to clean up even if there was an error
            self._agent = None
            self._initialized = False

    async def run(
        self, query: str, max_steps: int | None = None, manage_connector: bool = True
    ) -> str:
        """Run a query using the MCP tools.

        This method handles connecting to the MCP server, initializing the agent,
        running the query, and then cleaning up the connection.

        Args:
            query: The query to run.
            max_steps: Optional maximum number of steps to take.
            manage_connector: Whether to handle the connector lifecycle internally.
                If True, this method will connect, initialize, and disconnect from
                the connector automatically. If False, the caller is responsible
                for managing the connector lifecycle.

        Returns:
            The result of running the query.
        """
        result = ""
        try:
            if manage_connector:
                # Initialize if needed
                if not self._initialized or not self._agent:
                    await self.initialize()

                # Run the query
                if not self._agent:
                    raise RuntimeError("MCP client failed to initialize")

                result = await self._agent.run(query, max_steps)
            else:
                # Caller is managing connector lifecycle
                if not self._initialized and self.auto_initialize:
                    await self.initialize()

                if not self._agent:
                    raise RuntimeError("MCP client is not initialized")

                result = await self._agent.run(query, max_steps)

            return result
        finally:
            # Make sure to clean up the connection if we're managing it
            if manage_connector and not self.client:
                await self.close()
