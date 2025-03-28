"""
LangChain agent implementation for MCP tools.

This module provides a LangChain agent implementation that can use MCP tools
through a unified interface.
"""

from typing import Any, NoReturn

from jsonschema_pydantic import jsonschema_to_pydantic
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools import BaseTool
from langchain_core.tools import BaseTool as CoreBaseTool
from langchain_core.tools import ToolException
from pydantic import BaseModel

from mcpeer.types import TextContent

from ..connectors.base import BaseConnector


class LangChainAgent:
    """LangChain agent that can use MCP tools.

    This agent uses LangChain's agent framework to interact with MCP tools
    through a unified interface.
    """

    def __init__(
        self, connector: BaseConnector, llm: BaseLanguageModel, max_steps: int = 5
    ) -> None:
        """Initialize a new LangChain agent.

        Args:
            connector: The MCP connector to use.
            llm: The LangChain LLM to use.
            max_steps: The maximum number of steps to take.
        """
        self.connector = connector
        self.llm = llm
        self.max_steps = max_steps
        self.tools: list[BaseTool] = []
        self.agent: AgentExecutor | None = None

    async def initialize(self) -> None:
        """Initialize the agent and its tools."""
        self.tools = await self._create_langchain_tools()
        self.agent = self._create_agent()

    def fix_schema(self, schema: dict) -> dict:
        """Convert JSON Schema 'type': ['string', 'null'] to 'anyOf' format.

        Args:
            schema: The JSON schema to fix.

        Returns:
            The fixed JSON schema.
        """
        if isinstance(schema, dict):
            if "type" in schema and isinstance(schema["type"], list):
                schema["anyOf"] = [{"type": t} for t in schema["type"]]
                del schema["type"]  # Remove 'type' and standardize to 'anyOf'
            for key, value in schema.items():
                schema[key] = self.fix_schema(value)  # Apply recursively
        return schema

    async def _create_langchain_tools(self) -> list[CoreBaseTool]:
        """Create LangChain tools from MCP tools.

        Returns:
            A list of LangChain tools created from MCP tools.
        """
        tools = self.connector.tools
        local_connector = self.connector

        # Wrap MCP tools into LangChain tools
        langchain_tools: list[CoreBaseTool] = []
        for tool in tools:
            # Define adapter class to convert MCP tool to LangChain format
            class McpToLangChainAdapter(CoreBaseTool):
                name: str = tool.name or "NO NAME"
                description: str = tool.description or ""
                # Convert JSON schema to Pydantic model for argument validation
                args_schema: type[BaseModel] = jsonschema_to_pydantic(
                    self.fix_schema(tool.inputSchema)  # Apply schema conversion
                )
                connector: BaseConnector = local_connector
                handle_tool_error: bool = True

                def _run(self, **kwargs: Any) -> NoReturn:
                    """Synchronous run method that always raises an error.

                    Raises:
                        NotImplementedError: Always raises this error because MCP tools
                            only support async operations.
                    """
                    raise NotImplementedError("MCP tools only support async operations")

                async def _arun(self, **kwargs: Any) -> Any:
                    """Asynchronously execute the tool with given arguments.

                    Args:
                        kwargs: The arguments to pass to the tool.

                    Returns:
                        The result of the tool execution.

                    Raises:
                        ToolException: If tool execution fails.
                    """
                    print(f'MCP tool: "{self.name}" received input: {kwargs}')

                    try:
                        result = await self.connector.call_tool(self.name, kwargs)

                        if hasattr(result, "isError") and result.isError:
                            raise ToolException(
                                f"Tool execution failed: {result.content}"
                            )

                        if not hasattr(result, "content"):
                            return str(result)

                        try:
                            result_content_text = "\n\n".join(
                                item.text
                                for item in result.content
                                if isinstance(item, TextContent)
                            )

                        except KeyError as e:
                            result_content_text = (
                                f"Error in parsing result.content: {str(e)}; "
                                f"contents: {repr(result.content)}"
                            )

                        # Log rough result size for monitoring
                        size = len(result_content_text.encode())
                        print(f'MCP tool "{self.name}" received result (size: {size})')

                        # If no text content, return a clear message
                        # describing the situation.
                        result_content_text = (
                            result_content_text
                            or "No text content available in response"
                        )

                        return result_content_text

                    except Exception as e:
                        if self.handle_tool_error:
                            return f"Error executing MCP tool: {str(e)}"
                        raise

            langchain_tools.append(McpToLangChainAdapter())

        # Log available tools for debugging
        for tool in langchain_tools:
            print(f"- {tool.name}")

        return langchain_tools

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent.

        Returns:
            An initialized AgentExecutor.
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant that can use tools to help users.",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=self.max_steps,
            input_key="input",  # Explicitly set the input key
        )

    async def run(
        self,
        query: str,
        max_steps: int | None = None,
        chat_history: list | None = None,
    ) -> str:
        """Run the agent on a query.

        Args:
            query: The query to run.
            max_steps: Optional maximum number of steps to take.
            chat_history: Optional chat history.

        Returns:
            The result of running the query.

        Raises:
            RuntimeError: If the MCP client is not initialized.
        """
        if not self.agent:
            raise RuntimeError("MCP client is not initialized")

        if max_steps is not None:
            self.agent.max_iterations = max_steps

        # Initialize empty chat history if none provided
        if chat_history is None:
            chat_history = []

        # Invoke with all required variables
        result = await self.agent.ainvoke(
            {"input": query, "chat_history": chat_history}
        )

        return result["output"]
