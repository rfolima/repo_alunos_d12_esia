"""Golden master do legado caso/legado (AV1.4): grava e compara o comportamento ATUAL.

Uso (na raiz do repositório):
    python -B exercicios/aula-4/golden-master/golden.py record   # grava golden/
    python -B exercicios/aula-4/golden-master/golden.py check    # compara com golden/

Roda numa cópia temporária de caso/legado (nunca altera o original), offline,
em ambiente dev, só biblioteca padrão. Não corrige nada: registra o que o código faz hoje,
inclusive o que parece bug.
"""
import difflib
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
LEGADO = os.path.normpath(os.path.join(AQUI, "..", "..", "..", "caso", "legado"))
GOLDEN = os.path.join(AQUI, "golden")

# (nome, argumentos de `python -m cienciometria.jobs` ou ("py", código))
PASSOS = [
    ("01_ingest", ["ingest"]),
    ("02_enriquecer", ["enriquecer"]),
    ("03_sql_corrigir_anos", ["sql", "scripts/corrigir_anos.sql"]),
    ("04_rel_top_instituicoes", ["relatorio", "top_instituicoes"]),
    ("05_rel_evolucao_anual", ["relatorio", "evolucao_anual"]),
    ("06_rel_areas_autores", ["relatorio", "areas_autores"]),
    ("07_rel_conceitos_desabilitado", ["relatorio", "conceitos"]),
    ("08_rel_conceitos_direto", ("py", "from cienciometria import relatorios; relatorios.rel_conceitos()")),
    ("09_rel_exporta_parceiro", ["relatorio", "exporta_parceiro"]),
    ("10_refresh", ["refresh"]),
    ("11_ingest_repetido", ["ingest"]),
]
TABELAS = {
    "trabalhos": "id",
    "autorias": "trabalho_id, autor_id, instituicao_id",
    "conceitos": "id",
    "conceitos_trabalho": "trabalho_id, conceito_id",
    "autores": "id",
}


def ambiente():
    env = dict(os.environ)
    for k in list(env):
        if k.startswith("CIENTO_"):
            del env[k]
    env.update(CIENTO_OFFLINE="1", CIENTO_AMBIENTE="dev", PYTHONUTF8="1",
               PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    return env


def dump_banco(raiz):
    conn = sqlite3.connect(os.path.join(raiz, "data", "cienciometria.sqlite"))
    saida = []
    for tabela, ordem in TABELAS.items():
        saida.append("## " + tabela)
        for linha in conn.execute("SELECT * FROM %s ORDER BY %s" % (tabela, ordem)):
            saida.append(repr(linha))
    conn.close()
    return "\n".join(saida) + "\n"


def executar():
    """Devolve {arquivo: conteúdo} do comportamento observado."""
    obs = {}
    tmp = tempfile.mkdtemp(prefix="golden_legado_")
    try:
        raiz = os.path.join(tmp, "legado")
        shutil.copytree(LEGADO, raiz, ignore=shutil.ignore_patterns("*.sqlite", "*.csv", "__pycache__"))
        for nome, passo in PASSOS:
            cmd = [sys.executable, "-B"]
            cmd += ["-c", passo[1]] if isinstance(passo, tuple) else ["-m", "cienciometria.jobs"] + passo
            r = subprocess.run(cmd, cwd=raiz, env=ambiente(), capture_output=True, text=True, encoding="utf-8")
            erro = r.stderr.strip().splitlines()[-1:] if r.returncode else []
            obs[nome + ".txt"] = "exit=%d\n--stdout--\n%s--stderr(ultima linha)--\n%s\n" % (
                r.returncode, r.stdout, "\n".join(erro))
            if nome == "09_rel_exporta_parceiro":
                with open(os.path.join(raiz, "saida_parceiro", "trabalhos_por_instituicao.csv"), "rb") as f:
                    obs["09_trabalhos_por_instituicao.csv"] = f.read().decode("utf-8")
            if nome in ("03_sql_corrigir_anos", "09_rel_exporta_parceiro", "10_refresh", "11_ingest_repetido"):
                obs[nome + ".db.txt"] = dump_banco(raiz)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return obs


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "check"
    obs = executar()
    if modo == "record":
        shutil.rmtree(GOLDEN, ignore_errors=True)
        os.makedirs(GOLDEN)
        for nome, conteudo in obs.items():
            with open(os.path.join(GOLDEN, nome), "w", encoding="utf-8", newline="\n") as f:
                f.write(conteudo)
        print("golden gravada: %d arquivos em %s" % (len(obs), GOLDEN))
        return 0
    falhas = 0
    for nome, conteudo in sorted(obs.items()):
        caminho = os.path.join(GOLDEN, nome)
        if not os.path.exists(caminho):
            print("FALTA golden:", nome)
            falhas += 1
            continue
        with open(caminho, encoding="utf-8", newline="") as f:
            esperado = f.read()
        if esperado == conteudo:
            print("ok    ", nome)
        else:
            falhas += 1
            print("DIFERE", nome)
            sys.stdout.writelines(difflib.unified_diff(
                esperado.splitlines(True), conteudo.splitlines(True), "golden", "atual", n=1))
    print("%d diferença(s)" % falhas)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
