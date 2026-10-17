"""AV1.3 (b): testes que matam mutantes sobreviventes de testes/mutacao_manual.py.

Esperados calculados à mão a partir de caso/regras.md (R1), não do código. Verdes no código atual.
Os dois do registro: frete RJ (calculo.py) e VIP15 (descontos.py). NATAL fica como extra.
Uso, na raiz do pacote: python -B exercicios/aula-3/test_av13_mutantes.py [--codigo DIR]
"""
import os
import sys
import unittest

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CODIGO = sys.argv[sys.argv.index("--codigo") + 1] if "--codigo" in sys.argv else os.path.join(_RAIZ, "caso")
sys.path.insert(0, os.path.abspath(_CODIGO))

from miniloja.calculo import calcular_total  # noqa: E402
from miniloja.descontos import aplicar_desconto  # noqa: E402


class TestMutantes(unittest.TestCase):
    def test_frete_rj_sem_cupom(self):
        # mutante "frete RJ". R1.3/R1.4: 40,00 + 21,50 (RJ) = 61,50; × 1,06 = 65,19
        self.assertEqual(calcular_total([{"preco": 40.0, "qtd": 1}], None, "RJ"), 65.19)

    def test_vip15_simulacao_aplica_quinze_por_cento(self):
        # mutante "percentual do VIP15". R1.2 lido também para a simulação de descontos.py
        # (o módulo é do relatório de marketing; o contrato fala de calcular_total): 200,00 × 0,85 = 170,00
        self.assertEqual(aplicar_desconto(200.0, "VIP15"), 170.0)


class TestMutantesExtras(unittest.TestCase):
    """Fora da seleção do registro; mantido porque mata um sobrevivente real."""

    def test_natal_com_flag_aplica_vinte_por_cento(self):
        # mutante "NATAL: 20% -> 21%". R1.2/R1.3/R1.4: 100,00 × 0,80 = 80,00; + 12,90 = 92,90; × 1,05 = 97,545 → 97,55
        os.environ["MINILOJA_PROMO_NATAL"] = "1"
        try:
            self.assertEqual(calcular_total([{"preco": 100.0, "qtd": 1}], "NATAL", "PE"), 97.55)
        finally:
            os.environ.pop("MINILOJA_PROMO_NATAL", None)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]], verbosity=2)
