"""Exportação para o parceiro (planilha dele lê este CSV)."""
import csv
import os

from cienciometria import config, modelos

COLUNAS = ["instituicao", "trabalhos", "citacoes"]   # NÃO MUDAR A ORDEM (a planilha do parceiro depende)


def marcar_exportados(conn):
    conn.execute("UPDATE trabalhos SET exportado = 1 WHERE id IN (SELECT trabalho_id FROM autorias)")
    conn.commit()


def exportar():
    conn = modelos.conectar()
    linhas = conn.execute(
        "SELECT a.instituicao_nome, COUNT(DISTINCT a.trabalho_id), SUM(t.citacoes) "
        "FROM autorias a JOIN trabalhos t ON t.id = a.trabalho_id "
        "WHERE a.instituicao_nome IS NOT NULL GROUP BY a.instituicao_nome ORDER BY 2 DESC"
    ).fetchall()
    pasta = config.get("parceiro_pasta")
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, "trabalhos_por_instituicao.csv")
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLUNAS)
        w.writerows(linhas)
    marcar_exportados(conn)
    return caminho
