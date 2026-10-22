#!/usr/bin/env python3
"""Mutação da AV2 sobre o calculo.py refatorado, só biblioteca padrão.

Diferença para testes/mutacao_manual.py: trabalha em CÓPIA temporária de caso/ (o repositório não é
alterado em nenhum momento) e os mutantes visam o código depois da refatoração (tabelas por UF).
Cada mutante é rodado duas vezes: só com o contrato (--sem-diferencial) e com o contrato + diferencial.

Uso, na raiz do pacote:  python -B avaliacoes/av2/mutacao_av2.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
TESTE = os.path.join(AQUI, "test_av2_contrato.py")

MUTANTES = [
    # (trecho original, trecho mutado, descrição)
    ('"PE": 12.9', '"PE": 13.9', "frete PE"),
    ('"SP": 19.9', '"SP": 20.9', "frete SP"),
    ('"RJ": 21.5', '"RJ": 22.5', "frete RJ"),
    ("FRETE_POR_UF.get(uf, 29.9)", "FRETE_POR_UF.get(uf, 30.9)", "frete de UF desconhecida"),
    ('"PE": 0.05', '"PE": 0.06', "taxa PE"),
    ('"SP": 0.07', '"SP": 0.08', "taxa SP"),
    ('"RJ": 0.06', '"RJ": 0.07', "taxa RJ"),
    ("TAXA_POR_UF.get(uf, 0.08)", "TAXA_POR_UF.get(uf, 0.09)", "taxa de UF desconhecida"),
    ("FRETE_POR_UF.get(uf, 29.9)", "FRETE_POR_UF.get(str(uf).upper(), 29.9)", "frete normaliza UF para maiúscula"),
    ("TAXA_POR_UF.get(uf, 0.08)", "TAXA_POR_UF.get(str(uf).upper(), 0.08)", "taxa normaliza UF para maiúscula"),
    ("if total > 200:", "if total > 300:", "limite do frete grátis: 200 vira 300"),
    ("if total > 200:", "if total > 100:", "limite do frete grátis: 200 vira 100"),
    ("if total > 200:", "if total >= 200:", "limite do frete grátis: > vira >= (corrige R1.3)"),
    ("frete = _calcular_frete(total, cupom, uf)", "frete = _calcular_frete(_subtotal(itens), cupom, uf)",
     "frete decidido pelo subtotal sem desconto (ordem R1.6)"),
    ('if cupom == "FRETEGRATIS":\n        frete = 0', 'if cupom == "XFRETEGRATIS":\n        frete = 0', "FRETEGRATIS deixa de zerar o frete"),
    ("total = total * 0.9\n", "total = total * 0.91\n", "PROMO10 10% vira 9%"),
    ("total = total * 0.85", "total = total * 0.86", "VIP15 15% vira 14%"),
    ("total = total * 0.8\n", "total = total * 0.79\n", "NATAL 20% vira 21%"),
    ("if flags.promo_natal_ativa():", "if True:", "NATAL ignora a campanha"),
    ("total = total + frete\n", "total = total\n", "frete não é somado"),
    ("total = total + imposto\n", "total = total\n", "taxa não é somada"),
    ("total = total + preco * qtd", "total = total + preco + qtd", "subtotal: * vira +"),
    ("return round(total, 2)", "return round(total, 3)", "arredondamento em 3 casas"),
    ("desconto_aplicado = True", "desconto_aplicado = False", "variável sem efeito (equivalente)"),
]


def rodar(pasta, extra):
    env = dict(os.environ, MINILOJA_CODIGO=pasta, PYTHONDONTWRITEBYTECODE="1")
    env.pop("MINILOJA_PROMO_NATAL", None)
    return subprocess.run([sys.executable, "-B", TESTE] + extra, cwd=RAIZ, env=env,
                          capture_output=True, text=True, timeout=120).returncode == 0


def main():
    tmp = tempfile.mkdtemp(prefix="miniloja_mut_")
    try:
        copia = os.path.join(tmp, "caso")
        shutil.copytree(os.path.join(RAIZ, "caso"), copia, ignore=shutil.ignore_patterns("__pycache__"))
        alvo = os.path.join(copia, "miniloja", "calculo.py")
        with open(alvo, encoding="utf-8") as f:
            original = f.read()
        if not (rodar(copia, ["--sem-diferencial"]) and rodar(copia, [])):
            sys.exit("A suíte já falha sem mutação; corrija antes de rodar.")
        linhas, so_contrato, com_dif = [], 0, 0
        for velho, novo, desc in MUTANTES:
            assert original.count(velho) >= 1, f"trecho não encontrado: {velho!r}"
            with open(alvo, "w", encoding="utf-8") as f:
                f.write(original.replace(velho, novo, 1))
            mata_contrato = not rodar(copia, ["--sem-diferencial"])
            mata_dif = not rodar(copia, [])
            so_contrato += mata_contrato
            com_dif += mata_dif
            linhas.append((desc, mata_contrato, mata_dif))
        with open(alvo, "w", encoding="utf-8") as f:
            f.write(original)
        for desc, c, d in linhas:
            marca = "MORTO" if d else "SOBREVIVEU"
            print(f"{marca:10} contrato={'mata' if c else 'não'} | +diferencial={'mata' if d else 'não'} | {desc}")
        n = len(MUTANTES)
        print(f"Mutantes: {n} | mortos só com contrato: {so_contrato} | mortos com contrato+diferencial: {com_dif} "
              f"| sobreviventes: {n - com_dif}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
