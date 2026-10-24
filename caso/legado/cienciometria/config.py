"""Leitura de config.ini com override por ambiente."""
import configparser
import os

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(_RAIZ, "config.ini"), encoding="utf-8")


def ambiente():
    return os.environ.get("CIENTO_AMBIENTE", _cfg["geral"]["ambiente"])


def get(chave):
    if ambiente() == "prod" and chave in _cfg["producao"]:
        return _cfg["producao"][chave]
    return _cfg["geral"][chave]


def get_bool(chave):
    return get(chave).strip().lower() in ("1", "true", "sim")


def relatorios_habilitados():
    return [r.strip() for r in _cfg["relatorios"]["habilitados"].split(",")]
