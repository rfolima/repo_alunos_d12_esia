"""AV1.3: testes de borda derivados de caso/regras.md (R1 e R2), com esperado calculado à mão.

Só entram aqui bordas em que o código concorda com o contrato (arquivo verde, usável com
testes/mutacao_manual.py). Bordas divergentes ficam em test_av13_contrato.py, que falha de propósito.
Uso, na raiz do pacote: python -B exercicios/aula-3/test_av13_bordas.py [--codigo DIR]
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


class TestBordaFreteGratis(unittest.TestCase):
    """R1.3: frete grátis quando o subtotal COM desconto é >= 200,00 (o próprio 200,00 está em test_av13_contrato)."""

    def test_um_centavo_abaixo_de_200_paga_frete(self):
        # 199,99 + 12,90 = 212,89; × 1,05 = 223,5345 → 223,53
        self.assertEqual(calcular_total([{"preco": 199.99, "qtd": 1}], None, "PE"), 223.53)

    def test_um_centavo_acima_de_200_nao_paga_frete(self):
        # 200,01 + 0 = 200,01; × 1,05 = 210,0105 → 210,01
        self.assertEqual(calcular_total([{"preco": 200.01, "qtd": 1}], None, "PE"), 210.01)

    def test_promo10_deixa_subtotal_logo_abaixo_de_200(self):
        # 222,22 × 0,90 = 199,998 < 200 → frete 12,90; 212,898 × 1,05 = 223,5429 → 223,54
        self.assertEqual(calcular_total([{"preco": 222.22, "qtd": 1}], "PROMO10", "PE"), 223.54)

    def test_promo10_deixa_subtotal_logo_acima_de_200(self):
        # 222,23 × 0,90 = 200,007 >= 200 → frete 0; 200,007 × 1,05 = 210,00735 → 210,01
        self.assertEqual(calcular_total([{"preco": 222.23, "qtd": 1}], "PROMO10", "PE"), 210.01)

    def test_vip15_deixa_subtotal_logo_abaixo_de_200(self):
        # 235,29 × 0,85 = 199,9965 < 200 → frete 19,90 (SP); 219,8965 × 1,07 = 235,289255 → 235,29
        self.assertEqual(calcular_total([{"preco": 235.29, "qtd": 1}], "VIP15", "SP"), 235.29)

    def test_vip15_deixa_subtotal_logo_acima_de_200(self):
        # 235,30 × 0,85 = 200,005 >= 200 → frete 0; 200,005 × 1,07 = 214,00535 → 214,01
        self.assertEqual(calcular_total([{"preco": 235.30, "qtd": 1}], "VIP15", "SP"), 214.01)

    def test_fretegratis_abaixo_de_200_zera_frete_sem_descontar(self):
        # R1.2: FRETEGRATIS não altera o valor; 199,99 + 0 = 199,99; × 1,06 (RJ) = 211,9894 → 211,99
        self.assertEqual(calcular_total([{"preco": 199.99, "qtd": 1}], "FRETEGRATIS", "RJ"), 211.99)

    def test_uf_desconhecida_logo_abaixo_de_200(self):
        # 199,99 + 29,90 = 229,89; × 1,08 = 248,2812 → 248,28
        self.assertEqual(calcular_total([{"preco": 199.99, "qtd": 1}], None, "XX"), 248.28)


class TestBordaNatal(unittest.TestCase):
    """R1.2: NATAL só vale com MINILOJA_PROMO_NATAL=1; sem a flag, o cupom não dá desconto."""

    def setUp(self):
        os.environ.pop("MINILOJA_PROMO_NATAL", None)

    def test_natal_sem_flag_nao_desconta(self):
        # 100,00 + 12,90 = 112,90; × 1,05 = 118,545 → 118,55
        self.assertEqual(calcular_total([{"preco": 100.0, "qtd": 1}], "NATAL", "PE"), 118.55)

    def test_natal_com_flag_diferente_de_1_nao_desconta(self):
        # a regra exige o valor "1"; "0" não ativa a campanha → mesmo cálculo do teste acima, 118,55
        os.environ["MINILOJA_PROMO_NATAL"] = "0"
        try:
            self.assertEqual(calcular_total([{"preco": 100.0, "qtd": 1}], "NATAL", "PE"), 118.55)
        finally:
            os.environ.pop("MINILOJA_PROMO_NATAL", None)


class TestBordaEstoque(unittest.TestCase):
    """R2.2: todos os itens precisam ter estoque; caso contrário, o pedido é recusado.

    Leitura declarada (o contrato não fixa o limite): "ter estoque" = saldo >= qtd; SKU sem cadastro = saldo 0.
    """

    def _servico(self, saldos):
        estoque = Estoque(saldos)
        return PedidoService(RepositorioPedidos(), estoque, GatewayFake()), estoque

    def test_pedir_exatamente_o_saldo_e_aceito(self):
        svc, estoque = self._servico({"BOLA-01": 3})
        pedido = svc.criar(1, [{"sku": "BOLA-01", "preco": 10.0, "qtd": 3}])
        self.assertEqual(pedido["status"], "pago")
        self.assertEqual(estoque.saldo("BOLA-01"), 0)

    def test_pedir_uma_unidade_alem_do_saldo_e_recusado(self):
        svc, estoque = self._servico({"BOLA-01": 3})
        with self.assertRaises(EstoqueInsuficiente):
            svc.criar(1, [{"sku": "BOLA-01", "preco": 10.0, "qtd": 4}])
        self.assertEqual(estoque.saldo("BOLA-01"), 3)

    def test_sku_inexistente_e_recusado_com_409(self):
        status, corpo = handlers.post_pedidos(20, {"itens": [{"sku": "NAO-EXISTE", "preco": 10.0, "qtd": 1}]})
        self.assertEqual(status, 409)
        self.assertEqual(corpo["sku"], "NAO-EXISTE")


class TestBordaPedidoSemItens(unittest.TestCase):
    """R2.1: pedido sem itens é rejeitado com 400."""

    def test_payload_sem_a_chave_itens_responde_400(self):
        status, _ = handlers.post_pedidos(21, {"uf": "PE"})
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]], verbosity=2)
