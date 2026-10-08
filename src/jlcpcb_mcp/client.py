from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

JLCPCB_SMT_API = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"


async def search_components(
    keyword: str,
    page_size: int = 10,
    current_page: int = 1,
    first_sort_name: str | None = None,
    second_sort_name: str | None = None,
    component_attributes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Queries JLCPCB overseas SMT database for matching components."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
    }

    payload: dict[str, Any] = {
        "keyword": keyword,
        "pageSize": page_size,
        "currentPage": current_page,
    }
    if first_sort_name:
        payload["firstSortName"] = first_sort_name
    if second_sort_name:
        payload["seconSortName"] = second_sort_name
    if component_attributes:
        payload["componentAttributes"] = component_attributes

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(JLCPCB_SMT_API, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    if data.get("code") != 200 or "data" not in data:
        raise RuntimeError(f"JLCPCB API returned error: {data.get('message', 'Unknown error')}")

    info = data["data"].get("componentPageInfo", {})
    raw_list = info.get("list", [])

    results = []
    for item in raw_list:
        raw_type = item.get("componentLibraryType", "")
        # Map 'base' -> Basic (free loading fee), 'expand' -> Extended ($3 loading fee)
        is_basic = raw_type == "base"
        classification = "Basic" if is_basic else ("Extended" if raw_type == "expand" else raw_type)

        results.append({
            "lcsc": item.get("componentCode"),
            "mpn": item.get("componentModelEn"),
            "manufacturer": item.get("componentBrandEn"),
            "package": item.get("componentSpecificationEn"),
            "category": item.get("componentTypeEn"),
            "library_type": classification,
            "is_basic": is_basic,
            "stock": item.get("stockCount", 0),
            "description": item.get("describe", ""),
            "datasheet_url": item.get("dataManualUrl"),
        })

    return {
        "total": info.get("total", len(results)),
        "page": current_page,
        "results": results,
    }
