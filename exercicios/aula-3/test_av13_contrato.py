"""AV1.3 (c): casos derivados do contrato (caso/regras.md), com esperado calculado à mão.

TestCasosRegistro: os três casos do registro (R1.3 fronteira, R1.5 arredondamento, R2.3).
TestBugsReportados: outros bugs reais encontrados, reportados e não corrigidos.
Os testes que FALHAM no código atual registram divergências de propósito. Não ajuste o esperado ao código.
Uso, na raiz do pacote: python -B exercicios/aula-3/test_av13_contrato.py [--codigo DIR]
"""
import os
import sys
import unittest

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CODIGO = sys.argv[sys.argv.index("--codigo") + 1] if "--codigo" in sys.argv else os.path.join(_RAIZ, "caso")
sys.path.insert(0, os.path.abspath(_CODIGO))

from miniloja import handlers  # noqa: E402
from miniloja.calculo import calcular_total  # noqa: E402
from miniloja.estoque import Estoque, EstoqueInsuficiente  # noqa: E402
from miniloja.pagamentos import GatewayFake  # noqa: E402
from miniloja.pedidos import PedidoService  # noqa: E402
from miniloja.repositorio import RepositorioPedidos  # noqa: E402


def _total_natal(itens, uf):
    os.environ["MINILOJA_PROMO_NATAL"] = "1"
    try:
        return calcular_total(itens, "NATAL", uf)
    finally:
        os.environ.pop("MINILOJA_PROMO_NATAL", None)


class TestCasosRegistro(unittest.TestCase):
    def test_r13_fronteira_200_apos_desconto_natal(self):
        # R1.2/R1.3: 250,00 × 0,80 = 200,00 ≥ 200,00 → frete 0; R1.4: 200,00 × 1,05 = 210,00
        self.assertEqual(_total_natal([{"preco": 250.0, "qtd": 1}], "PE"), 210.0)

    def test_r15_arredonda_meio_para_cima(self):
        # R1.3/R1.4: 4,00 + 12,90 = 16,90; × 1,05 = 17,745; R1.5 (meio para cima) → 17,75
        self.assertEqual(calcular_total([{"preco": 4.0, "qtd": 1}], None, "PE"), 17.75)

    def test_r23_pagamento_recusado_responde_402_e_nao_salva(self):
        # R2.3: pagamento recusado → 402 e o pedido não é salvo
        antes = len(handlers._repo.todos())
        status, _ = handlers.post_pedidos(30, {"itens": [{"sku": "BOLA-01", "preco": 10.0, "qtd": 2}], "token": "recusado"})
        self.assertEqual(status, 402)
        self.assertEqual(len(handlers._repo.todos()), antes)


class TestBugsReportados(unittest.TestCase):
    def test_r13_subtotal_exatamente_200(self):
        # R1.3: 2 × 100,00 = 200,00 ≥ 200,00 → frete 0; × 1,05 = 210,00
        self.assertEqual(calcular_total([{"preco": 100.0, "qtd": 2}], None, "PE"), 210.0)

    def test_r13_200_por_quantidade(self):
        # R1.1/R1.3: 50,00 × 4 = 200,00 ≥ 200,00 → frete 0; × 1,05 = 210,00
        self.assertEqual(calcular_total([{"preco": 50.0, "qtd": 4}], None, "PE"), 210.0)

    def test_r13_200_por_soma_de_itens(self):
        # R1.1/R1.3: 99,99 + 100,01 = 200,00 ≥ 200,00 → frete 0; × 1,05 = 210,00
        self.assertEqual(calcular_total([{"preco": 99.99, "qtd": 1}, {"preco": 100.01, "qtd": 1}], None, "PE"), 210.0)

    def test_r15_meio_centavo_2_00(self):
        # R1.3/R1.4: 2,00 + 12,90 = 14,90; × 1,05 = 15,645; R1.5 → 15,65
        self.assertEqual(calcular_total([{"preco": 2.0, "qtd": 1}], None, "PE"), 15.65)

    def test_r15_meio_centavo_1_20(self):
        # R1.3/R1.4: 1,20 + 12,90 = 14,10; × 1,05 = 14,805; R1.5 → 14,81
        self.assertEqual(calcular_total([{"preco": 1.2, "qtd": 1}], None, "PE"), 14.81)

    def test_r22_recusa_por_estoque_nao_deixa_reserva(self):
        # R2.2: CHUTEIRA-42 sem saldo suficiente → pedido recusado e nenhuma reserva permanece:
        # BOLA-01 continua com saldo 5
        estoque = Estoque({"BOLA-01": 5, "CHUTEIRA-42": 1})
        svc = PedidoService(RepositorioPedidos(), estoque, GatewayFake())
        itens = [{"sku": "BOLA-01", "preco": 10.0, "qtd": 1}, {"sku": "CHUTEIRA-42", "preco": 300.0, "qtd": 2}]
        with self.assertRaises(EstoqueInsuficiente):
            svc.criar(1, itens)
        self.assertEqual(estoque.saldo("BOLA-01"), 5)

    def test_r22_r23_pagamento_recusado_nao_deixa_reserva(self):
        # Leitura por extensão (declarada no registro): R2.3 só diz "não salva"; tratamos como bug porque um
        # pedido recusado não pode reter estoque (R2.2: "nenhuma reserva pode permanecer"). Saldo deve seguir 5.
        estoque = Estoque({"BOLA-01": 5})
        svc = PedidoService(RepositorioPedidos(), estoque, GatewayFake())
        r = svc.criar(1, [{"sku": "BOLA-01", "preco": 10.0, "qtd": 1}], token="recusado")
        self.assertEqual(r["status"], "pagamento_recusado")
        self.assertEqual(estoque.saldo("BOLA-01"), 5)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]], verbosity=2)
