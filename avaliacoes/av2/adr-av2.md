# ADR — Tabelas por UF em `calculo.py` (AV2)

**Contexto.** `caso/miniloja/calculo.py` declarava `FRETE_POR_UF` e `TAXA_POR_UF` (linhas 4–5) que ninguém usava, enquanto `_calcular_frete` e `_taxa_por_uf` repetiam os mesmos valores em cadeias `if/elif`. Os valores existiam em dois lugares: mudar o frete de uma UF exigia editar dois pontos e nada avisava se divergissem. O contrato (`caso/regras.md`, R1.3 e R1.4) define frete por UF (PE 12,90, SP 19,90, RJ 21,50, demais 29,90) e taxa por UF (5%, 7%, 6%, demais 8%).

**Decisão.** As duas funções passam a consultar as tabelas, com o valor de "demais UFs" como default do `dict.get`: `FRETE_POR_UF.get(uf, 29.9)` e `TAXA_POR_UF.get(uf, 0.08)`. Sem normalização da UF: `"pe"` continua sendo "demais UFs", como antes. Assinatura, ordem desconto → frete → taxa, `if total > 200` e `round(total, 2)` ficam intactos.

**Por que não corrigir os bugs na mesma mudança.** O código diverge do contrato em R1.3 (`> 200` em vez de `>= 200` sobre o subtotal com desconto) e em R1.5 (`round()` de float não arredonda meio para cima: 17,745 vira 17,74). Corrigir junto invalidaria a evidência de comportamento preservado (golden master com igualdade exata, 0/325). Os bugs seguem reportados e executáveis em `TestBugsReportados` (4 falhas hoje). A correção pede tarefa própria, novo golden master e atualização de `test_cenarios_gravados`, que hoje afirma 223,55.

**Consequências.**
- `testes/mutacao_manual.py` deixa de funcionar em `calculo.py`: ele exige trechos literais (`frete = 12.9`, `taxa = 0.05` etc.) que não existem mais e aborta com `AssertionError`. A prova de falha usa `avaliacoes/av2/mutacao_av2.py`, em cópia temporária. Quem puder alterar `testes/` deve atualizar os alvos para `"PE": 12.9`, `.get(uf, 29.9)` e equivalentes.
- Um valor de UF não hashável (lista, dict) agora levanta `TypeError`, onde antes caía em "demais UFs". Nenhum dado do caso faz isso e o golden master não cobre; é um limite conhecido.
- Mudar um valor de frete ou taxa passa a ser edição de uma linha em um só lugar.

**Alternativa descartada.** Manter os `if/elif` e apagar as constantes mortas: preservaria a ferramenta de mutação, mas manteria a duplicação que motivou a mudança.

**Rever se:** o contrato mudar a lista de UFs ou a regra de "demais UFs"; a ferramenta de mutação oficial for adaptada; ou a UF passar a vir de entrada externa (aí normalização e UF inválida precisam de decisão própria).
