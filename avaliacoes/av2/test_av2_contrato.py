"""Suíte AV2 de calcular_total, derivada de caso/regras.md (R1), não do código.

Os valores esperados foram calculados fora do código, com Decimal e arredondamento
meio para cima, e escolhidos sem empate de arredondamento: assim R1.4 (taxa/frete por UF)
não se mistura com o bug R1.5. Os casos que revelam R1.3 e R1.5 ficam em classe à parte.

Uso, na raiz do pacote:
    python -B avaliacoes/av2/test_av2_contrato.py                    # contrato + diferencial
    python -B avaliacoes/av2/test_av2_contrato.py --sem-diferencial  # só o contrato
    python -B avaliacoes/av2/test_av2_contrato.py --bugs             # bugs R1.3 e R1.5 (falham hoje)
Variável MINILOJA_CODIGO aponta para outra pasta com o pacote miniloja (padrão: caso).
"""
import importlib.util
import itertools
import os
import sys
import unittest
from unittest import mock

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
CODIGO = os.path.abspath(os.path.join(RAIZ, os.environ.get("MINILOJA_CODIGO", "caso")))
sys.path.insert(0, CODIGO)

from miniloja.calculo import calcular_total  # noqa: E402

NATAL = "MINILOJA_PROMO_NATAL"


def total(itens, cupom=None, uf="PE", natal=False):
    """Chama calcular_total com a campanha NATAL ligada ou desligada de forma explícita."""
    ambiente = {NATAL: "1"} if natal else {}
    with mock.patch.dict(os.environ, ambiente):
        if not natal:
            os.environ.pop(NATAL, None)
        return calcular_total([{"preco": p, "qtd": q} for p, q in itens], cupom, uf)


class TestContrato(unittest.TestCase):
    """R1.2 a R1.6. Esperado = (subtotal com desconto + frete) x (1 + taxa), já arredondado."""

    def test_frete_e_taxa_de_cada_uf(self):  # R1.3 (tabela de frete) e R1.4 (tabela de taxa)
        # subtotal 40,10: (40,10 + frete) x (1 + taxa)
        casos = {"PE": 55.65, "SP": 64.20, "RJ": 65.30, "XX": 75.60}
        for uf, esperado in casos.items():
            with self.subTest(uf=uf):
                self.assertEqual(total([(40.10, 1)], None, uf), esperado)

    def test_uf_ausente_assume_pe_do_padrao_da_assinatura(self):  # assinatura: uf="PE"
        self.assertEqual(calcular_total([{"preco": 40.10, "qtd": 1}]), 55.65)

    def test_uf_em_minuscula_cai_em_demais_ufs(self):  # R1.3/R1.4 "demais UFs": leitura declarada
        # Leitura minha: o contrato lista siglas em maiúsculas; "pe" não é "PE", logo é "demais".
        self.assertEqual(total([(40.10, 1)], None, "pe"), 75.60)

    def test_taxa_por_uf_com_frete_gratis_por_valor(self):  # R1.4
        # subtotal 250,00, frete 0: só a taxa aparece
        casos = {"PE": 262.50, "SP": 267.50, "RJ": 265.00, "XX": 270.00}
        for uf, esperado in casos.items():
            with self.subTest(uf=uf):
                self.assertEqual(total([(250.00, 1)], None, uf), esperado)

    def test_desconto_promo10_e_vip15(self):  # R1.2
        self.assertEqual(total([(100.00, 1)], "PROMO10", "SP"), 117.59)  # 90 + 19,90 = 109,90 x 1,07
        self.assertEqual(total([(120.00, 1)], "VIP15", "RJ"), 130.91)    # 102 + 21,50 = 123,50 x 1,06

    def test_natal_so_com_campanha_ativa(self):  # R1.2
        self.assertEqual(total([(100.00, 1)], "NATAL", "SP", natal=False), 128.29)  # sem desconto: 119,90 x 1,07
        self.assertEqual(total([(100.00, 1)], "NATAL", "SP", natal=True), 106.89)   # 80 + 19,90 = 99,90 x 1,07
        self.assertEqual(total([(300.00, 1)], "NATAL", "PE", natal=False), 315.00)  # frete grátis, só taxa
        self.assertEqual(total([(300.00, 1)], "NATAL", "PE", natal=True), 252.00)   # 240 >= 200, frete 0, x 1,05

    def test_cupom_desconhecido_e_ignorado(self):  # R1.2
        self.assertEqual(total([(40.10, 1)], "ZZ", "PE"), total([(40.10, 1)], None, "PE"))
        self.assertEqual(total([(40.10, 1)], "ZZ", "PE"), 55.65)

    def test_fretegratis_zera_frete_sem_alterar_valor(self):  # R1.2, R1.3
        self.assertEqual(total([(40.10, 1)], "FRETEGRATIS", "XX"), 43.31)  # 40,10 x 1,08
        self.assertEqual(total([(40.10, 1)], "FRETEGRATIS", "SP"), 42.91)  # 40,10 x 1,07

    def test_frete_gratis_usa_subtotal_com_desconto(self):  # R1.3 (decisivo: "com desconto") e R1.6
        # 300 x 0,85 = 255 >= 200: frete grátis
        self.assertEqual(total([(300.00, 1)], "VIP15", "RJ"), 270.30)
        # 220 x 0,85 = 187 < 200: cobra frete, embora 220 sem desconto não cobrasse
        self.assertEqual(total([(220.00, 1)], "VIP15", "SP"), 221.38)

    def test_frete_cobrado_logo_abaixo_do_limite(self):  # R1.3
        self.assertEqual(total([(199.99, 1)], None, "SP"), 235.28)

    def test_subtotal_soma_preco_vezes_quantidade(self):  # R1.1
        self.assertEqual(total([(19.99, 3), (5.50, 2)], None, "RJ"), 98.02)
        self.assertEqual(total([(10.05, 3)], None, "SP"), 53.55)

    def test_arredondamento_em_duas_casas_sem_empate(self):  # R1.5 (parte sem empate; o empate está em TestBugsReportados)
        # 40,10 em RJ vale 65,296 exato: duas casas dão 65,30; três casas dariam 65,296
        self.assertEqual(total([(40.10, 1)], None, "RJ"), 65.30)


def _carregar_original():
    spec = importlib.util.spec_from_file_location("calculo_original", os.path.join(AQUI, "calculo_original.py"))
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.calcular_total


class TestDiferencial(unittest.TestCase):
    """Compara com o calculo.py do commit af1a38b (antes da AV2): igualdade exata, inclusive os bugs."""

    def test_igual_ao_original_em_grade(self):
        original = _carregar_original()
        carrinhos = [[], [(40.10, 1)], [(100.0, 2)], [(222.23, 1)], [(235.3, 1)], [(19.99, 3), (5.5, 2)], [(2.0, 1)], [(4.0, 1)]]
        cupons = [None, "PROMO10", "VIP15", "FRETEGRATIS", "NATAL", "ZZ", "", "promo10"]
        ufs = ["PE", "SP", "RJ", "XX", "pe", "", None, "sp"]
        for itens, cupom, uf, natal in itertools.product(carrinhos, cupons, ufs, [False, True]):
            lista = [{"preco": p, "qtd": q} for p, q in itens]
            ambiente = {NATAL: "1"} if natal else {}
            with mock.patch.dict(os.environ, ambiente):
                if not natal:
                    os.environ.pop(NATAL, None)
                with self.subTest(itens=itens, cupom=cupom, uf=uf, natal=natal):
                    self.assertEqual(calcular_total(lista, cupom, uf), original(lista, cupom, uf))


class TestBugsReportados(unittest.TestCase):
    """Esperado do contrato; FALHAM hoje (bugs só reportados na AV2, correção em tarefa própria)."""

    def test_r13_frete_gratis_em_exatamente_200_com_desconto(self):
        # 250 x 0,80 = 200,00 >= 200: frete 0; 200,00 x 1,05 = 210,00 (código atual usa > 200: 223,55)
        self.assertEqual(total([(250.00, 1)], "NATAL", "PE", natal=True), 210.00)

    def test_r13_frete_gratis_em_200_sem_cupom(self):
        self.assertEqual(total([(100.00, 2)], None, "PE"), 210.00)

    def test_r15_meio_para_cima(self):
        # (4,00 + 12,90) x 1,05 = 17,745 -> 17,75 (round() de float dá 17,74)
        self.assertEqual(total([(4.00, 1)], None, "PE"), 17.75)

    def test_r15_meio_para_cima_outro_valor(self):
        # (2,00 + 12,90) x 1,05 = 15,645 -> 15,65 (exemplo do próprio contrato)
        self.assertEqual(total([(2.00, 1)], None, "PE"), 15.65)


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    if "--bugs" in argumentos:
        classes = [TestBugsReportados]
    elif "--sem-diferencial" in argumentos:
        classes = [TestContrato]
    else:
        classes = [TestContrato, TestDiferencial]
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in classes)
    resultado = unittest.TextTestRunner(verbosity=1).run(suite)
    sys.exit(0 if resultado.wasSuccessful() else 1)
