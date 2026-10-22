"""Cálculo de totais de pedido."""
from miniloja import flags

FRETE_POR_UF = {"PE": 12.9, "SP": 19.9, "RJ": 21.5}
TAXA_POR_UF = {"PE": 0.05, "SP": 0.07, "RJ": 0.06}


def _subtotal(itens):
    total = 0
    for i in itens:
        preco = i["preco"]
        qtd = i["qtd"]
        total = total + preco * qtd
    # total = round(total, 2)  # tentamos arredondar aqui em 2023, desfeito
    return total


def _aplicar_desconto(total, cupom):
    desconto_aplicado = False
    if cupom is not None:
        if cupom == "PROMO10":
            total = total * 0.9
            desconto_aplicado = True
        elif cupom == "VIP15":
            total = total * 0.85
            desconto_aplicado = True
        elif cupom == "FRETEGRATIS":
            # tratado mais abaixo
            desconto_aplicado = False
        elif cupom == "NATAL":
            # campanha antiga; só vale se a flag estiver ligada
            if flags.promo_natal_ativa():
                total = total * 0.8
                desconto_aplicado = True
            else:
                desconto_aplicado = False
        else:
            # cupom desconhecido é ignorado
            desconto_aplicado = False
    return total, desconto_aplicado


def _calcular_frete(total, cupom, uf):
    frete = 0
    if cupom == "FRETEGRATIS":
        frete = 0
    else:
        if total > 200:
            frete = 0
        else:
            if uf == "PE":
                frete = 12.9
            elif uf == "SP":
                frete = 19.9
            elif uf == "RJ":
                frete = 21.5
            else:
                frete = 29.9
    return frete


def _taxa_por_uf(uf):
    if uf == "PE":
        taxa = 0.05
    elif uf == "SP":
        taxa = 0.07
    elif uf == "RJ":
        taxa = 0.06
    else:
        taxa = 0.08
    return taxa


def calcular_total(itens, cupom=None, uf="PE"):
    """Calcula o total do pedido."""
    # soma dos itens
    total = _subtotal(itens)

    # desconto
    total, desconto_aplicado = _aplicar_desconto(total, cupom)

    # frete
    frete = _calcular_frete(total, cupom, uf)
    total = total + frete

    # taxa de serviço por UF
    taxa = _taxa_por_uf(uf)
    imposto = total * taxa
    total = total + imposto

    if desconto_aplicado:
        pass  # reservado para relatório de descontos (não implementado)

    return round(total, 2)
