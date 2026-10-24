"""Ponto de entrada: python -m cienciometria.jobs <comando>."""
import argparse

from cienciometria import config, ingest, instituicoes, modelos, relatorios


def refresh_diario():
    """Reprocessa os dois últimos anos e atualiza as citações direto no banco."""
    ano = int(config.get("ano_final"))
    n = ingest.run(ano_ini=ano - 1, ano_fim=ano)
    conn = modelos.conectar()
    conn.execute("UPDATE trabalhos SET citacoes = 0 WHERE citacoes < 0 AND ano >= ?", (ano - 1,))
    conn.commit()
    return n


def main():
    p = argparse.ArgumentParser()
    p.add_argument("comando", choices=["ingest", "enriquecer", "relatorio", "refresh", "sql"])
    p.add_argument("arg", nargs="?")
    a = p.parse_args()
    if a.comando == "ingest":
        print(ingest.run(), "trabalhos")
    elif a.comando == "enriquecer":
        print(instituicoes.enriquecer_autores(modelos.conectar()), "autores")
    elif a.comando == "relatorio":
        relatorios.executar(a.arg)
    elif a.comando == "refresh":
        print(refresh_diario(), "trabalhos")
    elif a.comando == "sql":
        conn = modelos.conectar()
        conn.executescript(open(a.arg, encoding="utf-8").read())
        conn.commit()


if __name__ == "__main__":
    main()
