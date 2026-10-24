"""Cliente HTTP da API do OpenAlex (com cache em disco)."""
import hashlib
import json
import os
import time
import urllib.parse
import urllib.request

from cienciometria import config

BASE = "https://api.openalex.org"


def montar_url(caminho, params=None):
    p = dict(params or {})
    p["mailto"] = config.get("mailto")      # polite pool
    return BASE + caminho + "?" + urllib.parse.urlencode(p, safe=":,|*")


def _arquivo_cache(url):
    return os.path.join(config.get("cache_dir"), hashlib.md5(url.encode()).hexdigest() + ".json")


def get_json(url):
    arq = _arquivo_cache(url)
    offline = os.environ.get("CIENTO_OFFLINE") == "1"
    if os.path.exists(arq):
        idade_h = (time.time() - os.path.getmtime(arq)) / 3600
        if offline or config.get_bool("usar_cache_agressivo") or idade_h < 24:
            with open(arq, encoding="utf-8") as f:
                return json.load(f)
    if offline:
        raise RuntimeError("modo offline e sem cache para: " + url)
    req = urllib.request.Request(
        url, headers={"User-Agent": "cienciometria/0.3 (mailto:%s)" % config.get("mailto")}
    )
    erro = None
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                dados = json.load(r)
            os.makedirs(config.get("cache_dir"), exist_ok=True)
            with open(arq, "w", encoding="utf-8") as f:
                json.dump(dados, f)
            return dados
        except Exception as e:  # noqa: BLE001
            erro = e
            time.sleep(2 * (tentativa + 1))
    raise erro


def paginar(caminho, params, limite=None):
    limite = limite or int(config.get("limite_paginas"))
    cursor = "*"
    for _ in range(limite):
        p = dict(params, cursor=cursor)
        dados = get_json(montar_url(caminho, p))
        yield dados
        cursor = dados["meta"].get("next_cursor")
        if not cursor:
            break
