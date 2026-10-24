"""Ingestão de trabalhos do OpenAlex para o SQLite."""
from cienciometria import cliente, config, conceitos, modelos


def params_works(conceito_id, ano_ini, ano_fim):
    return {
        "filter": "concepts.id:%s,publication_year:%s-%s" % (conceito_id, ano_ini, ano_fim),
        "per-page": 200,
    }


def gravar_trabalho(conn, w):
    wid = w["id"].split("/")[-1]
    cs = w.get("concepts") or []
    principal = cs[0]["display_name"] if cs else None
    conn.execute(
        "INSERT OR REPLACE INTO trabalhos (id, titulo, ano, citacoes, conceito_principal) VALUES (?,?,?,?,?)",
        (wid, w.get("title"), w.get("publication_year"), w.get("cited_by_count", 0), principal),
    )
    conn.execute("DELETE FROM autorias WHERE trabalho_id = ?", (wid,))
    for a in w.get("authorships", []):
        insts = a.get("institutions") or [{}]
        for i in insts:
            conn.execute(
                "INSERT INTO autorias VALUES (?,?,?,?,?,?)",
                (
                    wid,
                    a["author"]["id"].split("/")[-1],
                    a["author"]["display_name"],
                    (i.get("id") or "").split("/")[-1] or None,
                    i.get("display_name"),
                    i.get("country_code"),
                ),
            )
    conn.execute("DELETE FROM conceitos_trabalho WHERE trabalho_id = ?", (wid,))
    for c in cs:
        conn.execute(
            "INSERT INTO conceitos_trabalho VALUES (?,?,?,?,?)",
            (wid, c["id"].split("/")[-1], c["display_name"], c["level"], c["score"]),
        )


def run(conceito_id=None, ano_ini=None, ano_fim=None):
    conceito_id = conceito_id or config.get("conceito_padrao")
    ano_ini = ano_ini or int(config.get("ano_inicial"))
    ano_fim = ano_fim or int(config.get("ano_final"))
    conn = modelos.conectar()
    conceito = cliente.get_json(cliente.montar_url("/concepts/" + conceito_id))
    conceitos.salvar(conn, conceito)
    n = 0
    for pagina in cliente.paginar("/works", params_works(conceito_id, ano_ini, ano_fim)):
        for w in pagina["results"]:
            gravar_trabalho(conn, w)
            n += 1
    conn.commit()
    return n
