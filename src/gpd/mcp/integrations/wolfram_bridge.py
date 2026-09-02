"""GPD-owned stdio bridge for the Wolfram remote MCP service."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

import mcp_types as types
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.server.context import ServerRequestContext
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from gpd.mcp import managed_integrations as _managed_integrations
from gpd.version import __version__ as GPD_VERSION

WOLFRAM_MANAGED_INTEGRATION = _managed_integrations.WOLFRAM_MANAGED_INTEGRATION
WOLFRAM_MANAGED_SERVER_KEY = _managed_integrations.WOLFRAM_MANAGED_SERVER_KEY
WOLFRAM_BRIDGE_MODULE = _managed_integrations.WOLFRAM_BRIDGE_MODULE
WOLFRAM_MCP_API_KEY_ENV_VAR = _managed_integrations.WOLFRAM_MCP_API_KEY_ENV_VAR
WOLFRAM_MCP_DEFAULT_ENDPOINT = _managed_integrations.WOLFRAM_MCP_DEFAULT_ENDPOINT
WOLFRAM_MCP_ENDPOINT_ENV_VAR = _managed_integrations.WOLFRAM_MCP_ENDPOINT_ENV_VAR

DEFAULT_WOLFRAM_MCP_ENDPOINT = WOLFRAM_MCP_DEFAULT_ENDPOINT
GPD_WOLFRAM_MCP_API_KEY_ENV = WOLFRAM_MCP_API_KEY_ENV_VAR

_CONNECT_TIMEOUT_SECONDS = 10.0
_READ_TIMEOUT_SECONDS = 300.0


def _paginated_params(cursor: str | None) -> types.PaginatedRequestParams | None:
    return types.PaginatedRequestParams(cursor=cursor) if cursor else None


def resolve_endpoint(env: Mapping[str, str] | None = None) -> str:
    """Return the Wolfram MCP endpoint URL, defaulting to the official service."""
    source = os.environ if env is None else env
    return WOLFRAM_MANAGED_INTEGRATION.resolved_endpoint(source)


def resolve_api_key(env: Mapping[str, str] | None = None) -> str:
    """Return the bearer token for the Wolfram MCP service.

    The canonical env var is the only supported auth source.
    """
    source = os.environ if env is None else env
    return WOLFRAM_MANAGED_INTEGRATION.resolve_api_key(source)


def build_auth_headers(api_key: str) -> dict[str, str]:
    """Build the bearer-token headers used for the remote MCP connection."""
    return {"Authorization": f"Bearer {api_key}"}


@dataclass(frozen=True, slots=True)
class WolframBridgeConfig:
    """Runtime configuration for the Wolfram bridge."""

    api_key: str = field(repr=False)
    endpoint: str = DEFAULT_WOLFRAM_MCP_ENDPOINT


def load_settings(env: Mapping[str, str] | None = None) -> WolframBridgeConfig:
    """Load bridge settings from the environment without persisting secrets."""
    source = os.environ if env is None else env
    return WolframBridgeConfig(endpoint=resolve_endpoint(source), api_key=resolve_api_key(source))


class WolframBridge:
    """Thin proxy around the remote Wolfram MCP service."""

    def __init__(self, config: WolframBridgeConfig) -> None:
        self.config = config
        self._session: ClientSession | None = None

    @property
    def session(self) -> ClientSession:
        if self._session is None:
            raise RuntimeError("Wolfram bridge session is not open")
        return self._session

    @asynccontextmanager
    async def open(self):
        headers = build_auth_headers(self.config.api_key)
        async with sse_client(
            self.config.endpoint,
            headers=headers,
            timeout=_CONNECT_TIMEOUT_SECONDS,
            sse_read_timeout=_READ_TIMEOUT_SECONDS,
        ) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                self._session = session
                try:
                    yield self
                finally:
                    self._session = None

    async def list_tools(self, cursor: str | None = None) -> types.ListToolsResult:
        return await self.session.list_tools(params=_paginated_params(cursor))

    async def call_tool(self, name: str, arguments: dict[str, object] | None) -> types.CallToolResult:
        return await self.session.call_tool(name, arguments)

    async def list_resources(self, cursor: str | None = None) -> types.ListResourcesResult:
        return await self.session.list_resources(params=_paginated_params(cursor))

    async def read_resource(self, uri: str) -> types.ReadResourceResult:
        return await self.session.read_resource(uri)

    async def list_prompts(self, cursor: str | None = None) -> types.ListPromptsResult:
        return await self.session.list_prompts(params=_paginated_params(cursor))

    async def get_prompt(self, name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
        return await self.session.get_prompt(name, arguments)

    async def list_resource_templates(self, cursor: str | None = None) -> types.ListResourceTemplatesResult:
        return await self.session.list_resource_templates(params=_paginated_params(cursor))


def build_server(config: WolframBridgeConfig) -> tuple[Server, WolframBridge]:
    """Build the local stdio MCP server that proxies the remote Wolfram service."""
    bridge = WolframBridge(config)

    @asynccontextmanager
    async def lifespan(_server: Server):
        async with bridge.open():
            yield bridge

    async def _list_tools(
        _context: ServerRequestContext,
        params: types.PaginatedRequestParams | None,
    ) -> types.ListToolsResult:
        return await bridge.list_tools(params.cursor if params else None)

    async def _call_tool(
        _context: ServerRequestContext,
        params: types.CallToolRequestParams,
    ) -> types.CallToolResult:
        return await bridge.call_tool(params.name, params.arguments)

    async def _list_resources(
        _context: ServerRequestContext,
        params: types.PaginatedRequestParams | None,
    ) -> types.ListResourcesResult:
        return await bridge.list_resources(params.cursor if params else None)

    async def _read_resource(
        _context: ServerRequestContext,
        params: types.ReadResourceRequestParams,
    ) -> types.ReadResourceResult:
        return await bridge.read_resource(params.uri)

    async def _list_prompts(
        _context: ServerRequestContext,
        params: types.PaginatedRequestParams | None,
    ) -> types.ListPromptsResult:
        return await bridge.list_prompts(params.cursor if params else None)

    async def _get_prompt(
        _context: ServerRequestContext,
        params: types.GetPromptRequestParams,
    ) -> types.GetPromptResult:
        return await bridge.get_prompt(params.name, params.arguments)

    async def _list_resource_templates(
        _context: ServerRequestContext,
        params: types.PaginatedRequestParams | None,
    ) -> types.ListResourceTemplatesResult:
        return await bridge.list_resource_templates(params.cursor if params else None)

    server = Server(
        WOLFRAM_MANAGED_SERVER_KEY,
        version=GPD_VERSION,
        lifespan=lifespan,
        on_list_tools=_list_tools,
        on_call_tool=_call_tool,
        on_list_resources=_list_resources,
        on_read_resource=_read_resource,
        on_list_prompts=_list_prompts,
        on_get_prompt=_get_prompt,
        on_list_resource_templates=_list_resource_templates,
    )

    return server, bridge


async def _run() -> None:
    config = load_settings()
    server, _bridge = build_server(config)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Console entry point for the Wolfram MCP bridge."""
    try:
        asyncio.run(_run())
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc


__all__ = [
    "DEFAULT_WOLFRAM_MCP_ENDPOINT",
    "GPD_WOLFRAM_MCP_API_KEY_ENV",
    "WOLFRAM_BRIDGE_MODULE",
    "WOLFRAM_MANAGED_SERVER_KEY",
    "WolframBridge",
    "WolframBridgeConfig",
    "build_auth_headers",
    "build_server",
    "load_settings",
    "main",
    "resolve_api_key",
    "resolve_endpoint",
]


if __name__ == "__main__":
    main()
