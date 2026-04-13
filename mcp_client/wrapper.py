import json
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MiniMaxMCPClient:
    """Async MCP client wrapper for minimax-coding-plan-mcp."""

    def __init__(self, api_key: str, api_host: str = "https://api.minimaxi.com"):
        self.api_key = api_key
        self.api_host = api_host
        self._session: Optional[ClientSession] = None
        self._read = None
        self._write = None
        self._context = None

    async def connect(self):
        """Initialize the MCP stdio connection."""
        server_params = StdioServerParameters(
            command="uvx",
            args=["minimax-coding-plan-mcp", "-y"],
            env={
                "MINIMAX_API_KEY": self.api_key,
                "MINIMAX_API_HOST": self.api_host,
            },
        )
        self._context = stdio_client(server_params)
        self._read, self._write = await self._context.__aenter__()
        self._session = ClientSession(self._read, self._write)
        await self._session.__aenter__()
        await self._session.initialize()

    async def disconnect(self):
        """Gracefully close the MCP connection."""
        if self._session:
            await self._session.__aexit__(None, None, None)
            self._session = None
        if self._context:
            await self._context.__aexit__(None, None, None)
            self._context = None

    async def web_search(self, query: str) -> str:
        """Call the MCP web_search tool."""
        if not self._session:
            return "MCP client is not connected."
        try:
            result = await self._session.call_tool(
                "web_search",
                arguments={"query": query},
            )
            # Extract text content from result
            texts = [c.text for c in result.content if hasattr(c, "text")]
            return "\n".join(texts) or "(no search results)"
        except Exception as e:
            return f"MCP web_search failed: {e}"

    async def understand_image(self, prompt: str, image_source: str) -> str:
        """Call the MCP understand_image tool."""
        if not self._session:
            return "MCP client is not connected."
        try:
            result = await self._session.call_tool(
                "understand_image",
                arguments={"prompt": prompt, "image_source": image_source},
            )
            texts = [c.text for c in result.content if hasattr(c, "text")]
            return "\n".join(texts) or "(no image analysis results)"
        except Exception as e:
            return f"MCP understand_image failed: {e}"
