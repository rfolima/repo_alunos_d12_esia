# Registro individual — AV1.3

**Limite: uma página, incluindo evidências essenciais.** Estudante: Rafael Lima — Data: 17/10/2026
Origem: `caso/testes_existentes/` e `caso/regras.md` fictícios; modalidade: **[x] execução própria** / [ ] transcrição. Código: `calculo.py` refatorado na AV1.2 (golden master 0/325).

| Teste suspeito | Tipo de tautologia | Sabotagem que apliquei (ou raciocínio) | Continuou verde? |
| --- | --- | --- | --- |
| `test_calculo::test_cenarios_gravados` | snapshot do próprio código (`limite_200: 223.55`) | `if total > 200:` → `>= 200` (a correção pedida por R1.3) | **Não**: foi o **único** a falhar, e protegeu o bug |
| `test_pedidos::test_fluxo_chama_colaboradores` | afirma o mock (só `.called`) | `"total_fmt": moeda(total)` → `moeda(0)`; depois `total = calcular_total(...)` → `total = 0` | **Sim** nas duas |
| `test_descontos::test_aplicar_desconto` | **espelho parcial**: o esperado reescreve a fórmula (`total - total*10/100`) em vez de afirmar 180,00 | S1: `"VIP15": 15` → `5`; S2: `"PROMO10": 10` → `11` | S1 **sim**; S2 **não**. Pega o percentual do PROMO10 e "desconto vira acréscimo"; não pega o VIP15 nem um erro da própria fórmula |

| Mutante sobrevivente | Por que sobreviveu | Teste que o mataria (ou "equivalente", com justificativa) |
| --- | --- | --- |
| `calculo.py`: frete RJ 21,50 → 22,50 | o teste de RJ usa `FRETEGRATIS` e nunca chega ao frete do RJ | 1×40,00, sem cupom, RJ: (40,00 + 21,50) × 1,06 = **65,19** (`test_frete_rj_sem_cupom`) |
| `descontos.py`: VIP15 15% → 5% | o único teste com cupom em `descontos.py` usa PROMO10 (é a sabotagem S1 acima) | `aplicar_desconto(200, "VIP15")`: 200,00 × 0,85 = **170,00**. Leitura declarada: apliquei R1.2 à simulação de marketing |
| *(equivalente)* `desconto_aplicado = True→False` | a variável só é lida em `if desconto_aplicado: pass` (`calculo.py:91-92`) | nenhum teste mata o mutante: a saída é a mesma para qualquer entrada |

| Caso derivado do contrato (entrada) | Esperado (cálculo à mão) | Observado no código | Decisão |
| --- | --- | --- | --- |
| R1.3 fronteira: 1×250,00, NATAL com flag, PE | 250,00 × 0,80 = 200,00 ≥ 200 → frete 0; × 1,05 = **210,00** | 223.55 | **código errado**: "com desconto ≥ 200" no texto; o código usa `>` |
| R1.5 arredondamento: 1×4,00, sem cupom, PE | (4,00 + 12,90) × 1,05 = 17,745 → meio para cima **17,75** | 17.74 | **código errado**: `round()` de float não arredonda meio para cima |
| R2.3: BOLA-01×2, token `recusado` (handler) | **402** e nenhum pedido salvo | 402; pedidos 0 → 0 | código e contrato **concordam** |

**Outros bugs reais reportados (não corrigidos, em `TestBugsReportados`):** R1.3 também com 2×100,00, 4×50,00 e 99,99 + 100,01 (223.55 ≠ 210,00); R1.5 com 2,00 (15.64 ≠ 15,65) e 1,20 (14.8 ≠ 14,81); R2.2: recusa por estoque deixa reserva (saldo 4 ≠ 5); **pagamento recusado deixa reserva** (saldo 4 ≠ 5). Este último é uma leitura minha por extensão: R2.3 só manda não salvar, mas um pedido recusado não pode reter estoque (R2.2).

**ADR curto:** contexto: R1.3 manda frete grátis com subtotal **com desconto** ≥ 200,00; o código usa `> 200`, e `test_cenarios_gravados` e o golden master da AV1.2 gravam 223,55. Decisão: o contrato prevalece e o código está errado. O teste afirma 210,00 e falha hoje; só reporto, e a correção fica para uma tarefa com escopo próprio. Consequências: corrigir exige atualizar `test_cenarios_gravados` (hoje fora do escopo) e aceitar as 25 divergências conhecidas do golden master. Alternativa descartada: trocar o esperado para 223,55, o que tornaria o teste um espelho do bug.

**Trecho essencial de evidência** (raiz do pacote; Python 3.12): sabotagem `cp -r caso trabalho && sed -i 's/"VIP15": 15/"VIP15": 5/' trabalho/miniloja/descontos.py && python -B testes/test_miniloja.py --codigo trabalho --existentes` → `OK` (26). Mutação de base `mutacao_manual.py` → `31 | mortos: 23 | sobreviventes: 8 | 74%`. `MINILOJA_TEST_CMD="python -B exercicios/aula-3/test_av13_mutantes.py" python -B testes/mutacao_manual.py calculo.py descontos.py` → frete RJ e VIP15 fora dos sobreviventes. `test_av13_contrato.py` → `FAILED (failures=9)`, só o R2.3 passa. `git status`: só arquivos novos em `exercicios/aula-3/`.
**Limite e condição para rever:** na suíte existente seguem vivos e-mail obrigatório, `total_fmt` e formatação do relatório. O mutante "estoque no saldo exato" só morre com a minha leitura de R2.2 (saldo ≥ qtd), declarada em `test_av13_bordas.py`. Mutação medida arquivo por arquivo, sem escore combinado. Os casos cobrem pontos, não classes inteiras (o arredondamento falha para muitos valores); R3/R4 não foram tocados. Reviso o ADR se o contrato mudar R1.3 para "maior que" ou se o professor indicar o golden master como referência.

**Procedência/IA:** Claude Code (Claude Opus 5.5, `claude-opus-5-5`). Tarefa delegada: análise e plano, sabotagens, testes, execução da mutação e rascunho do registro. **Decisões minhas**, entre opções apresentadas pela IA: os 3 testes, os 2 mutantes, os 3 casos, o tema e a decisão do ADR, declarar a leitura de R2.2, tratar a reserva após pagamento recusado como bug, reportar todos os bugs reais e manter a evidência só com comandos do repositório. **Minha verificação:** aprovei o plano; refiz à mão 65,19, 170,00 e 17,745 → 17,75; o 210,00 seguiu o exemplo resolvido pela IA; gerei o `git status`. As execuções foram feitas pela IA e as saídas estão transcritas acima. **Erros da IA:** na primeira interação o agente tentou resolver e concluir o problema sozinho; redigiu a procedência declarando como minhas verificações que não fiz; deixou o registro desatualizado (3 → 7 falhas) ao acrescentar bordas; mediu a mutação com um script temporário fora do repositório; afirmou a causa do 15,64 antes de verificá-la; leu o código de saída do `tail` em vez do teste; apresentou como derivadas do contrato leituras de R2.2. O raciocínio e a decisão registrados são meus.

**Revisão:** [x] três testes; [x] dois mutantes; [x] três casos do contrato; [x] ADR; [x] até uma página.
