"""Dependency-free public contract for the optional arXiv MCP server."""

from __future__ import annotations

UPSTREAM_CORE_TOOL_NAMES = (
    "search_papers",
    "download_paper",
    "list_papers",
    "read_paper",
    "get_abstract",
)
DOWNLOAD_SOURCE_TOOL_NAME = "download_source"
ADVERTISED_TOOL_NAMES = (*UPSTREAM_CORE_TOOL_NAMES, DOWNLOAD_SOURCE_TOOL_NAME)

__all__ = ["ADVERTISED_TOOL_NAMES", "DOWNLOAD_SOURCE_TOOL_NAME", "UPSTREAM_CORE_TOOL_NAMES"]
