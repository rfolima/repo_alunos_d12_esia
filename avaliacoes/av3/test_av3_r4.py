"""AV3 (B1): R4.1, um usuário só vê os próprios pedidos.

Uso, na raiz do repositório: python -B avaliacoes/av3/test_av3_r4.py [--codigo DIR]
"""
import os
import sys
import unittest

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CODIGO = sys.argv[sys.argv.index("--codigo") + 1] if "--codigo" in sys.argv else os.path.join(_RAIZ, "caso")
sys.path.insert(0, os.path.abspath(_CODIGO))

from miniloja import handlers  # noqa: E402
from miniloja.repositorio import RepositorioPedidos  # noqa: E402

ITENS = {"itens": [{"sku": "BOLA-01", "preco": 50.0, "qtd": 1}], "uf": "PE"}


class TestAcessoPedidos(unittest.TestCase):
    def setUp(self):
        handlers._repo = RepositorioPedidos()
        handlers._service.repo = handlers._repo
        _, self.pedido = handlers.post_pedidos(1, ITENS)

    def test_dono_ve_o_proprio_pedido(self):
        status, corpo = handlers.get_pedido(1, self.pedido["id"])
        self.assertEqual(status, 200)
        self.assertEqual(corpo["id"], self.pedido["id"])

    def test_outro_usuario_nao_ve_pedido_alheio(self):
        status, corpo = handlers.get_pedido(2, self.pedido["id"])
        self.assertEqual(status, 404)
        self.assertNotIn("total", corpo)

    def test_alheio_e_inexistente_sao_indistinguiveis(self):
        self.assertEqual(handlers.get_pedido(2, self.pedido["id"]), handlers.get_pedido(2, 9999))


if __name__ == "__main__":
    unittest.main(argv=[a for a in sys.argv[:1]])
