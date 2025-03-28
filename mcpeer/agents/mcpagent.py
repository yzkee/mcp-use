"""
Model-Agnostic MCP: Main integration module.

This module provides the main MCPAgent class that integrates all components
to provide a simple interface for using MCP tools with different LLMs.
"""

from langchain.schema.language_model import BaseLanguageModel

from mcpeer.connectors.base import BaseConnector

from .langchain_agent import LangChainAgent


class MCPAgent:
    """Main class for using MCP tools with various LLM providers.

    This class provides a unified interface for using MCP tools with different LLM providers
    through LangChain's agent framework.
    """

    def __init__(
        self,
        connector: BaseConnector,
        llm: BaseLanguageModel,
        max_steps: int = 5,
        auto_initialize: bool = False,
    ):
        """Initialize a new MCPAgent instance.

        Args:
            connector: The MCP connector to use.
            llm: The LangChain LLM to use.
            max_steps: The maximum number of steps to take.
            auto_initialize: Whether to automatically initialize the agent when run is called.
        """
        self.connector = connector
        self.llm = llm
        self.max_steps = max_steps
        self.auto_initialize = auto_initialize
        self._initialized = False

        self._agent: LangChainAgent | None = None

    async def initialize(self) -> None:
        """Initialize the MCP client and agent."""
        # Create the agent
        self._agent = LangChainAgent(
            connector=self.connector, llm=self.llm, max_steps=self.max_steps
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
            if self.connector:
                await self.connector.disconnect()
            self._initialized = False
        except Exception as e:
            print(f"Warning: Error during client closure: {e}")
            # Still try to clean up even if there was an error
            self._agent = None

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
        if manage_connector:
            # Handle connector lifecycle internally
            try:
                # Connect to the connector if not already connected
                await self.connector.connect()

                # Initialize the connector
                await self.connector.initialize()

                # Initialize the agent if not already initialized
                if not self._initialized or not self._agent:
                    await self.initialize()

                # Run the query
                if not self._agent:
                    raise RuntimeError("MCP client failed to initialize")

                return await self._agent.run(query, max_steps)
            finally:
                # Make sure to clean up the connection regardless of success/failure
                await self.close()
        else:
            # Caller is managing connector lifecycle
            if not self._initialized and self.auto_initialize:
                await self.initialize()

            if not self._agent:
                raise RuntimeError("MCP client is not initialized")

            return await self._agent.run(query, max_steps)
