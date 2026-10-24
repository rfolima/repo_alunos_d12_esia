"""Relatórios. Cada relatório é uma função rel_<nome>; executar() descobre pelo nome."""
import sys

from cienciometria import config, conceitos, exporta_parceiro, modelos


def rel_top_instituicoes(n=5):
    conn = modelos.conectar()
    for nome, qtd in conn.execute(
        "SELECT instituicao_nome, COUNT(DISTINCT trabalho_id) FROM autorias "
        "WHERE instituicao_nome IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT ?", (n,)
    ):
        print("%-45s %4d" % (nome, qtd))


def rel_evolucao_anual():
    conn = modelos.conectar()
    for ano, qtd, cit in conn.execute(
        "SELECT ano, COUNT(*), SUM(citacoes) FROM trabalhos WHERE ano IS NOT NULL GROUP BY ano ORDER BY ano"
    ):
        print("%s  trabalhos=%3d  citacoes=%5d" % (ano, qtd, cit))


def rel_areas_autores():
    conn = modelos.conectar()
    for area, qtd in conn.execute(
        "SELECT area_principal, COUNT(*) FROM autores GROUP BY 1 ORDER BY 2 DESC"
    ):
        print("%-30s %3d" % (area, qtd))


def rel_conceitos():
    for nome, qtd in conceitos.trabalhos_por_conceito(modelos.conectar()):
        print("%-30s %3d" % (nome, qtd))


def rel_exporta_parceiro():
    print("gerado:", exporta_parceiro.exportar())


def executar(nome):
    if nome not in config.relatorios_habilitados():
        raise ValueError("relatório desabilitado: " + nome)
    fn = getattr(sys.modules[__name__], "rel_" + nome)
    return fn()
