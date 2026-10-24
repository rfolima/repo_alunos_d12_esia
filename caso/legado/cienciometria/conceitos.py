"""Conceitos (classificação por áreas)."""
import json

from cienciometria import config


def salvar(conn, c):
    cid = c["id"].split("/")[-1]
    anc = [a["id"].split("/")[-1] for a in c.get("ancestors", [])]
    conn.execute(
        "INSERT OR REPLACE INTO conceitos (id, nome, nivel, ancestrais) VALUES (?,?,?,?)",
        (cid, c["display_name"], c["level"], json.dumps(anc)),
    )


def nivel_minimo():
    return int(config.get("nivel_minimo_conceito"))


def trabalhos_por_conceito(conn):
    """Quantidade de trabalhos por conceito, só de nível >= nivel_minimo (grandes áreas ficam de fora)."""
    return conn.execute(
        "SELECT nome, COUNT(DISTINCT trabalho_id) FROM conceitos_trabalho "
        "WHERE nivel >= ? GROUP BY nome ORDER BY 2 DESC",
        (nivel_minimo(),),
    ).fetchall()
