from __future__ import annotations

import logging
from typing import Any

from mcp.server.mcpserver import MCPServer

from .client import search_components

logger = logging.getLogger(__name__)


async def tool_find_jlc_part(
    keyword: str,
    prefer_basic: bool = True,
    min_stock: int = 1,
    limit: int = 10,
) -> dict[str, Any]:
    """Search JLCPCB & LCSC SMT components by MPN, keyword, or value (e.g. 'AO3400A', 'TPS54302', '10k 0603 1%').

    Args:
        keyword: Search query (MPN, value, or description).
        prefer_basic: If True, prioritizes Basic parts (no feeder setup fee at JLCPCB) at top of list.
        min_stock: Minimum warehouse stock required.
        limit: Max number of components to return.
    """
    data = await search_components(keyword=keyword, page_size=max(limit * 2, 20))
    results = data.get("results", [])

    # Filter min stock
    filtered = [p for p in results if p.get("stock", 0) >= min_stock]

    # Sort Basic first if requested
    if prefer_basic:
        filtered.sort(key=lambda p: (not p.get("is_basic", False), -p.get("stock", 0)))
    else:
        filtered.sort(key=lambda p: -p.get("stock", 0))

    final_list = filtered[:limit]
    return {
        "query": keyword,
        "total_found": len(filtered),
        "prefer_basic": prefer_basic,
        "parts": final_list,
    }


async def tool_get_part_details(
    lcsc_code: str,
) -> dict[str, Any]:
    """Retrieves live stock, package, datasheet, and basic/extended classification for an LCSC part code (e.g. 'C20917').

    Args:
        lcsc_code: LCSC C-number (e.g. 'C20917' or 'C9864').
    """
    code = lcsc_code.strip().upper()
    if not code.startswith("C"):
        code = f"C{code}"

    data = await search_components(keyword=code, page_size=5)
    for p in data.get("results", []):
        if p.get("lcsc", "").upper() == code:
            return {
                "status": "found",
                "part": p,
            }

    if data.get("results"):
        return {
            "status": "partial_match",
            "part": data["results"][0],
        }

    return {
        "status": "not_found",
        "message": f"Part {lcsc_code} not found in JLCPCB database.",
    }


def create_server() -> MCPServer:
    """Creates the JLCPCB / LCSC SMT Lookup MCP server."""
    server = MCPServer(
        name="jlcpcb-lcsc",
        version="0.1.0",
        description="Live parametric search and stock checker for JLCPCB & LCSC SMT components",
    )

    server.tool(
        name="find_jlc_part",
        description="Search JLCPCB SMT component catalog by MPN, keyword, or value with Basic/Extended classification.",
    )(tool_find_jlc_part)

    server.tool(
        name="get_part_details",
        description="Get live stock, pricing tier, package, and datasheet for an LCSC C-part number.",
    )(tool_get_part_details)

    return server
