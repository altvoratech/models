#!/usr/bin/env python3
"""
Baixa a lista de modelos do Kilo Gateway.

Endpoint padrão:
  https://api.kilo.ai/api/gateway/models

Uso:
  python kilo_models.py
  python kilo_models.py --api-key SEU_TOKEN
  setx KILO_API_KEY "SEU_TOKEN"   # Windows (persistente)
  $env:KILO_API_KEY="SEU_TOKEN"   # PowerShell (sessão atual)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


DEFAULT_URL = "https://api.kilo.ai/api/gateway/models"


def _build_request(url: str, api_key: str | None, extra_headers: list[str]) -> urllib.request.Request:
    headers: dict[str, str] = {
        "Accept": "application/json",
        "User-Agent": "kilo-models-script/1.0 (+python urllib)",
    }

    if api_key:
        # Padrão mais comum (Bearer). Caso sua conta use outro esquema,
        # ajuste aqui conforme a documentação do Kilo.
        headers["Authorization"] = f"Bearer {api_key}"

    for item in extra_headers:
        if ":" not in item:
            raise ValueError(f"Header inválido (use 'Chave: Valor'): {item!r}")
        key, value = item.split(":", 1)
        headers[key.strip()] = value.strip()

    return urllib.request.Request(url=url, headers=headers, method="GET")


def fetch_models(
    url: str,
    api_key: str | None,
    timeout_s: float,
    retries: int,
    retry_backoff_s: float,
    extra_headers: list[str],
) -> object:
    last_err: BaseException | None = None

    for attempt in range(retries + 1):
        try:
            req = _build_request(url, api_key, extra_headers)
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                raw = resp.read()
                charset = resp.headers.get_content_charset() or "utf-8"
                text = raw.decode(charset, errors="replace")
                return json.loads(text)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
            if attempt >= retries:
                break
            time.sleep(retry_backoff_s * (2**attempt))

    assert last_err is not None
    raise last_err


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Obtém modelos do Kilo Gateway e imprime em JSON.")
    p.add_argument("--url", default=DEFAULT_URL, help="Endpoint do gateway de modelos.")
    p.add_argument(
        "--api-key",
        default=os.getenv("KILO_API_KEY"),
        help="Token de acesso. Se omitido, usa a variável de ambiente KILO_API_KEY.",
    )
    p.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        help="Header extra (pode repetir). Ex.: -H 'X-Org: minha-org'",
    )
    p.add_argument("--timeout", type=float, default=30.0, help="Timeout (segundos).")
    p.add_argument("--retries", type=int, default=2, help="Número de tentativas extras em caso de falha.")
    p.add_argument(
        "--backoff",
        type=float,
        default=0.8,
        help="Backoff base em segundos (exponencial: base * 2^tentativa).",
    )
    p.add_argument("--compact", action="store_true", help="Imprime JSON em uma linha.")
    p.add_argument("--out", help="Salva o JSON em arquivo em vez de imprimir.")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    try:
        payload = fetch_models(
            url=args.url,
            api_key=args.api_key,
            timeout_s=args.timeout,
            retries=args.retries,
            retry_backoff_s=args.backoff,
            extra_headers=args.header,
        )
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        sys.stderr.write(f"HTTP {e.code} ao chamar {args.url}\n")
        if body.strip():
            sys.stderr.write(body.strip() + "\n")
        return 2
    except urllib.error.URLError as e:
        sys.stderr.write(f"Erro de rede ao chamar {args.url}: {e}\n")
        return 2
    except TimeoutError:
        sys.stderr.write(f"Timeout ao chamar {args.url}\n")
        return 2
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Resposta não é JSON válido: {e}\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"Falha inesperada: {e}\n")
        return 2

    indent = None if args.compact else 2
    text = json.dumps(payload, ensure_ascii=False, indent=indent, sort_keys=False)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
            f.write("\n")
    else:
        sys.stdout.write(text + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
