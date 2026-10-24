"""Instituições e enriquecimento de autores."""
import logging

from cienciometria import cliente

log = logging.getLogger(__name__)


def instituicao_atual(autor):
    inst = autor.get("last_known_institution") or {}
    return inst.get("id"), inst.get("display_name"), inst.get("country_code")


def validar_instituicao(inst_id):
    """Valida a instituição."""
    if not inst_id:
        log.warning("instituição vazia")
    return True


def area_principal(autor):
    xs = autor.get("x_concepts") or []
    grandes = [x for x in xs if x["level"] == 0]       # nível 0 = grande área
    if not grandes:
        return None
    return max(grandes, key=lambda x: x["score"])["display_name"]


def enriquecer_autores(conn):
    ids = [r[0] for r in conn.execute("SELECT DISTINCT autor_id FROM autorias")]
    for aid in ids:
        dados = cliente.get_json(cliente.montar_url("/authors/" + aid))
        inst_id, inst_nome, _ = instituicao_atual(dados)
        validar_instituicao(inst_id)
        conn.execute(
            "INSERT OR REPLACE INTO autores (id, nome, instituicao_id, instituicao_nome, area_principal) "
            "VALUES (?,?,?,?,?)",
            (aid, dados["display_name"], inst_id and inst_id.split("/")[-1], inst_nome, area_principal(dados)),
        )
    conn.commit()
    return len(ids)
