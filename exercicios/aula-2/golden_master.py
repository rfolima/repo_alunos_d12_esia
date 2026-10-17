"""Golden master de calcular_total (AV1.2, passo zero).

Grava as saídas atuais de calcular_total para um conjunto fixo de entradas
e compara execuções futuras com igualdade exata (sem tolerância). Preserva o
comportamento atual, inclusive o que diverge do contrato.

Uso, na raiz do pacote:
    python -B exercicios/aula-2/golden_master.py --gerar    # grava o JSON (só no código original)
    python -B exercicios/aula-2/golden_master.py            # compara; sai 1 se houver divergência
    python -B exercicios/aula-2/golden_master.py --codigo DIR
"""
import argparse
import importlib
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
ARQUIVO = os.path.join(AQUI, "golden_master.json")
ENV_NATAL = "MINILOJA_PROMO_NATAL"


def _carrinhos():
    with open(os.path.join(RAIZ, "caso", "dados", "carrinhos.json"), encoding="utf-8") as f:
        dados = json.load(f)["carrinhos"]
    dados.update({
        "vazio": [],
        "exato_200": [{"preco": 100.0, "qtd": 2}],
        "abaixo_200": [{"preco": 199.99, "qtd": 1}],
        "200_apos_promo10": [{"preco": 222.23, "qtd": 1}],
        "200_apos_vip15": [{"preco": 235.3, "qtd": 1}],
    })
    return dados


# (rótulo, cupom, valor de MINILOJA_PROMO_NATAL ou None para ausente)
CUPONS = [
    ("sem_cupom", None, None),
    ("PROMO10", "PROMO10", None),
    ("VIP15", "VIP15", None),
    ("FRETEGRATIS", "FRETEGRATIS", None),
    ("NATAL_off", "NATAL", None),
    ("NATAL_on", "NATAL", "1"),
    ("CUPOMFALSO", "CUPOMFALSO", None),
    ("promo10_minusculo", "promo10", None),
]
UFS = ["PE", "SP", "RJ", "XX", "pe"]

# Casos de borda avulsos: (nome, itens, cupom, uf, natal)
EXTRAS = [
    # 15,645 antes de arredondar (contrato R1.5 manda 15,65)
    ("arred_15645_fretegratis", [{"preco": 14.9, "qtd": 1}], "FRETEGRATIS", "PE", None),
    ("arred_15645_frete_pe", [{"preco": 2.0, "qtd": 1}], None, "PE", None),
    ("cupom_string_vazia", [{"preco": 50.0, "qtd": 2}], "", "PE", None),
    ("uf_padrao", [{"preco": 50.0, "qtd": 2}], None, "<padrao>", None),
    ("item_sem_qtd", [{"preco": 10.0}], None, "PE", None),
]


def casos():
    lista = []
    for nome_c, itens in _carrinhos().items():
        for rotulo, cupom, natal in CUPONS:
            for uf in UFS:
                lista.append((f"{nome_c}|{rotulo}|{uf}", itens, cupom, uf, natal))
    lista.extend(EXTRAS)
    return lista


def executar(calcular_total, itens, cupom, uf, natal):
    anterior = os.environ.pop(ENV_NATAL, None)
    if natal is not None:
        os.environ[ENV_NATAL] = natal
    try:
        if uf == "<padrao>":
            return {"total": calcular_total(itens, cupom)}
        return {"total": calcular_total(itens, cupom, uf)}
    except Exception as e:  # o golden master grava erros também
        return {"erro": type(e).__name__}
    finally:
        os.environ.pop(ENV_NATAL, None)
        if anterior is not None:
            os.environ[ENV_NATAL] = anterior


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--codigo", default="caso", help="pasta com o pacote miniloja (padrão: caso)")
    p.add_argument("--gerar", action="store_true", help="grava o golden master em vez de comparar")
    args = p.parse_args()

    sys.path.insert(0, os.path.abspath(os.path.join(RAIZ, args.codigo)))
    calcular_total = importlib.import_module("miniloja.calculo").calcular_total

    obtido = {nome: executar(calcular_total, itens, cupom, uf, natal)
              for nome, itens, cupom, uf, natal in casos()}

    if args.gerar:
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            linhas = [f"{json.dumps(k, ensure_ascii=False)}: {json.dumps(v)}" for k, v in obtido.items()]
            f.write("{\n" + ",\n".join(linhas) + "\n}\n")
        print(f"golden master gravado: {len(obtido)} casos em {os.path.relpath(ARQUIVO, RAIZ)}")
        return 0

    with open(ARQUIVO, encoding="utf-8") as f:
        esperado = json.load(f)

    divergencias = []
    for nome in sorted(set(esperado) | set(obtido)):
        if esperado.get(nome) != obtido.get(nome):  # igualdade exata, sem tolerância
            divergencias.append((nome, esperado.get(nome), obtido.get(nome)))

    for nome, esp, obt in divergencias:
        print(f"DIVERGE {nome}: esperado={esp} obtido={obt}")
    print(f"{len(esperado)} casos gravados, {len(divergencias)} divergências")
    return 1 if divergencias else 0


if __name__ == "__main__":
    sys.exit(main())
