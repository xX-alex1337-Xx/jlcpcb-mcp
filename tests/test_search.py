from __future__ import annotations

import pytest
from jlcpcb_mcp.server import tool_find_jlc_part, tool_get_part_details


@pytest.mark.asyncio
async def test_find_jlc_part_basic_ranking():
    res = await tool_find_jlc_part("AO3400A", prefer_basic=True, limit=5)
    assert res["total_found"] > 0
    assert len(res["parts"]) > 0

    first = res["parts"][0]
    assert first["is_basic"] is True
    assert first["lcsc"] == "C20917"
    assert first["stock"] > 1000


@pytest.mark.asyncio
async def test_get_part_details():
    res = await tool_get_part_details("C20917")
    assert res["status"] == "found"
    part = res["part"]
    assert part["lcsc"] == "C20917"
    assert part["library_type"] == "Basic"
    assert "Alpha & Omega" in part["manufacturer"]
