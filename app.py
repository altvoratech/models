from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse


DEFAULT_URL = "https://api.kilo.ai/api/gateway/models"
CACHE_TTL_S = 60

APP_DIR = Path(__file__).resolve().parent
INDEX_HTML = (APP_DIR / "web" / "index.html").read_text(encoding="utf-8")

app = FastAPI(title="Kilo Gateway Models Browser")

_cache: dict[str, Any] = {"ts": 0.0, "payload": None}


def _kilo_api_key() -> str | None:
    return os.getenv("KILO_API_KEY") or None


def _fetch_gateway_models(url: str) -> Any:
    headers = {
        "Accept": "application/json",
        "User-Agent": "kilo-models-fastapi/1.0 (+python urllib)",
    }
    api_key = _kilo_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(url=url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
        text = raw.decode(charset, errors="replace")
        return json.loads(text)


def _get_models_payload(url: str) -> Any:
    now = time.time()
    if _cache["payload"] is not None and (now - float(_cache["ts"])) < CACHE_TTL_S:
        return _cache["payload"]

    payload = _fetch_gateway_models(url)
    _cache["ts"] = now
    _cache["payload"] = payload
    return payload


def _items_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        for key in ("data", "models", "items", "result"):
            if isinstance(payload.get(key), list):
                items = payload[key]
                break
        else:
            items = []
    else:
        items = []

    normalized: list[dict[str, Any]] = []
    for i, raw in enumerate(items):
        if isinstance(raw, dict):
            name = raw.get("name") or raw.get("id") or raw.get("model") or f"item-{i}"
            model = raw.get("model") or raw.get("model_name") or raw.get("slug")
            brand = raw.get("brand") or raw.get("provider") or raw.get("vendor") or raw.get("org")
            ident = raw.get("id") or raw.get("key") or raw.get("slug") or name
            normalized.append(
                {
                    "id": str(ident),
                    "name": str(name),
                    "model": str(model) if model is not None else "",
                    "brand": str(brand) if brand is not None else "",
                    "raw": raw,
                }
            )
        else:
            normalized.append(
                {
                    "id": str(i),
                    "name": str(raw),
                    "model": "",
                    "brand": "",
                    "raw": raw,
                }
            )
    return normalized


def _filter_items(
    items: list[dict[str, Any]], q: str | None, model: str | None, brand: str | None
) -> list[dict[str, Any]]:
    qn = (q or "").strip().lower()
    mn = (model or "").strip().lower()
    bn = (brand or "").strip().lower()

    out: list[dict[str, Any]] = []
    for it in items:
        if mn and it.get("model", "").lower() != mn:
            continue
        if bn and it.get("brand", "").lower() != bn:
            continue
        if qn:
            blob = json.dumps(it.get("raw", it), ensure_ascii=False).lower()
            if qn not in blob and qn not in it.get("name", "").lower() and qn not in it.get("id", "").lower():
                continue
        out.append(it)
    return out


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)


@app.get("/api/models")
def api_models(url: str = DEFAULT_URL) -> JSONResponse:
    try:
        payload = _get_models_payload(url)
        items = _items_from_payload(payload)
        models = sorted({it["model"] for it in items if it.get("model")})
        brands = sorted({it["brand"] for it in items if it.get("brand")})
        return JSONResponse({"models": models, "brands": brands, "count": len(items)})
    except urllib.error.HTTPError as e:
        return JSONResponse({"error": f"HTTP {e.code}"}, status_code=502)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=502)


@app.get("/api/search")
def api_search(
    q: str | None = None,
    model: str | None = None,
    brand: str | None = None,
    url: str = DEFAULT_URL,
    limit: int = 200,
) -> JSONResponse:
    try:
        payload = _get_models_payload(url)
        items = _items_from_payload(payload)
        filtered = _filter_items(items, q=q, model=model, brand=brand)[: max(1, min(limit, 2000))]
        return JSONResponse({"count": len(filtered), "items": filtered})
    except urllib.error.HTTPError as e:
        return JSONResponse({"error": f"HTTP {e.code}"}, status_code=502)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=502)

