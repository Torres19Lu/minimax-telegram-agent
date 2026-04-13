import os
from typing import Optional


def duckduckgo_search(query: str, max_results: int = 5) -> str:
    """Use DuckDuckGo to search the web."""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return "DuckDuckGo search is not available (missing dependency)."

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            if not results:
                return "No results found on DuckDuckGo."
            lines = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "")
                body = r.get("body", "")
                href = r.get("href", "")
                lines.append(f"[{i}] {title}\n{body}\nURL: {href}")
            return "\n\n".join(lines)
    except Exception as e:
        return f"DuckDuckGo search failed: {e}"


def tavily_search(query: str, max_results: int = 5) -> str:
    """Use Tavily to search the web. Requires TAVILY_API_KEY env var."""
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return "Tavily search is not configured (missing TAVILY_API_KEY)."

    try:
        from tavily import TavilyClient
    except ImportError:
        return "Tavily search is not available (missing dependency)."

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=max_results)
        results = response.get("results", [])
        if not results:
            return "No results found on Tavily."
        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            content = r.get("content", "")
            url = r.get("url", "")
            lines.append(f"[{i}] {title}\n{content}\nURL: {url}")
        return "\n\n".join(lines)
    except Exception as e:
        return f"Tavily search failed: {e}"


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web. Try Tavily first, fallback to DuckDuckGo."""
    tavily_result = tavily_search(query, max_results)
    if not tavily_result.startswith("Tavily search is not") and not tavily_result.startswith("Tavily search failed"):
        return f"[Search source: Tavily]\n\n{tavily_result}"
    ddgs_result = duckduckgo_search(query, max_results)
    if not ddgs_result.startswith("DuckDuckGo search is not") and not ddgs_result.startswith("DuckDuckGo search failed"):
        return f"[Search source: DuckDuckGo]\n\n{ddgs_result}"
    return f"Web search failed.\nTavily: {tavily_result}\nDuckDuckGo: {ddgs_result}"
