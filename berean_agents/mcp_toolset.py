"""
mcp_toolset.py — connects ADK agents to the Scripture MCP server.

This is the MCP-server course concept in action: the agents get their Scripture
tools from a real Model Context Protocol server (launched over stdio), not from
hand-written Python functions baked into the agent.
"""

from __future__ import annotations

from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters

from .config import MCP_COMMAND, MCP_ARGS, REPO_ROOT


def build_scripture_toolset(tool_filter: list[str] | None = None) -> MCPToolset:
    """Return an MCPToolset bound to the Berean Scripture MCP server.

    Args:
        tool_filter: optional allow-list of tool names (least-privilege). For
            example a specialist that only needs lookups can be restricted to
            ['get_passage', 'search_by_theme', 'cross_references'].
    """
    return MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=MCP_COMMAND,
                args=MCP_ARGS,
                cwd=str(REPO_ROOT),
            ),
        ),
        # Security: scope which tools each agent may call (Day 4 least-privilege).
        tool_filter=tool_filter,
    )
