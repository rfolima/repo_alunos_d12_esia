# Registro individual — AV1.2

**Limite: uma página, incluindo evidências essenciais.** Estudante: Rafael Lima — Data: 17/10/2026
Origem: `caso/miniloja/calculo.py` fictício; modalidade: **[x] execução própria** / [ ] resposta simulada.

**Golden master:** **325 entradas** = 8 carrinhos (C1–C3, vazio, 200,00, 199,99, 222,23, 235,30) × 8 cupons (nenhum, PROMO10, VIP15, FRETEGRATIS, NATAL off/on, inválido, `promo10`) × 5 UFs (PE, SP, RJ, XX, `pe`) + 5 bordas (15,645, cupom `""`, UF padrão, item sem `qtd`). O limite de 200 após desconto é coberto por C2 + NATAL on (250 × 0,8 = 200,00). Gerado por `exercicios/aula-2/golden_master.py --gerar` no código original (`a6e3195`); comparação exata por `==` sobre o JSON, sem tolerância; exceções gravadas como `{"erro": ...}`. Resultado: 0 divergências nas duas rodadas; validado com mutante `> 200`→`>= 200` em cópia → **25 divergências, saída 1**.

| Medida | Rodada 1 (sem escopo) | Rodada 2 (com escopo) |
| --- | --- | --- |
| Linhas adicionadas/removidas | +23 / −61 | +27 / −7 |
| Arquivos alterados (e quais estavam fora do esperado) | 1 (`calculo.py`); nenhum fora | 1 (`calculo.py`); nenhum fora |
| Mudou comportamento? (golden master) | Não (0/325). Mas **quebrou `mutacao_manual.py`** em `calculo.py` | Não (0/325); mutação 18/15/3 com os **mesmos 3 sobreviventes** do baseline |
| Tempo de ponta a ponta (agente + conferência) | ~2,5 min (agente ~1m40s) | ~3,7 min (plano ~1,5 + revisão do plano + execução ~1,3 + conferência) |
| Idas e vindas | 1 | 2 (plano → execução) |

**Escopo da rodada 2:** objetivo: extrair desconto, frete e taxa em funções privadas sem mudar saída; pode tocar: só `caso/miniloja/calculo.py`; não pode tocar: `regras.md`, `testes/`, `testes_existentes/`, `dados/`, demais módulos, `exercicios/` (golden master), assinatura pública, dependências, commit; invariantes: golden master exato, ordem desconto→frete→taxa, `> 200` e `round(total, 2)` intactos, verificações 11 com 3 falhas (v08–v10), existentes 26 OK; pronto quando: invariantes conferidos por comando e `git diff --name-only` = só `calculo.py`; pare e pergunte se: divergência no golden master, outro arquivo/assinatura, algo parecer bug, precisar de `Decimal`. Os seis campos foram escritos antes da rodada 1; **depois** dela acrescentei o conflito com a ferramenta de mutação ao "pare e pergunte", pedindo que o agente apresentasse opções sem decidir.
**Plano do agente: o que eu cortei ou corrigi antes de executar:** opção A (preservar os trechos literais da mutação); B rejeitada porque exigiria alterar `testes/`; cortei "achatar `if cupom is not None`" (opcional, não pedido); proibi docstrings/comentários novos; exigi a saída literal dos comandos.
**Algo que parecia bug e eu apenas reportei:** R1.3 — `> 200` em vez de `>= 200` (`exato_200|sem_cupom|PE` = 223.55; pelo contrato, 210,00). R1.5 — `round()` de float não arredonda meio para cima (15,645 → 15.64). Ambíguos: cupom/UF em minúsculas ignorados; carrinho vazio cobra frete+taxa (13.54); item sem `qtd` → `KeyError`.
**`AGENTS.md` mínimo:** na raiz do pacote (6 linhas): comandos de verificação e golden master, pastas proibidas, "reporte, não corrija", trechos literais da mutação e `MINILOJA_TEST_CMD` no Windows.

**Trecho essencial de evidência:** `python -B exercicios/aula-2/golden_master.py` → `325 casos gravados, 0 divergências` (exit 0). Rodada 1: `mutacao_manual.py calculo.py` → `AssertionError: trecho não encontrado em calculo.py: 'total = total * 0.9\n'`. Rodada 2: `Mutantes: 18 | mortos: 15 | sobreviventes: 3 | escore: 83%`.
**Limite e condição para rever o escopo:** o golden master preserva o comportamento atual, inclusive os erros (R1.3, R1.5), e cobre só as 325 entradas escolhidas. Ele não detectou a quebra da ferramenta de mutação na rodada 1 (quem apontou foi o relato do agente, confirmado ao rodar a ferramenta); na rodada 2, o invariante do escopo evitou a quebra. Ampliar o escopo (usar `FRETE_POR_UF`/`TAXA_POR_UF`, remover `desconto_aplicado`) só se `mutacao_manual.py` puder ser adaptada, o que hoje não é permitido; reduzir se aparecer qualquer divergência.

**Procedência/IA:** Claude Code (Claude Opus 5.5, `claude-opus-5-5`) e subagentes do mesmo modelo. Tarefa delegada: gerar o golden master, executar as duas rodadas (rodada 1 só com "refatore `calcular_total`"; rodada 2 com os seis campos e plano antes) e medir. Trecho aproveitado: `golden_master.py`, refatoração da rodada 2, `AGENTS.md`. Verificação: 3 saídas conferidas à mão contra R1, comparador validado com mutante, escopo checado por `git diff`/`find` após cada rodada; a conferência foi executada pela IA e os resultados foram revisados por mim. **Erros da IA:** na rodada 1, quebrou a ferramenta de mutação mesmo depois de avisar do risco, e removeu `desconto_aplicado` e o comentário de 2023, além de criar 5 constantes, sem que nada disso tivesse sido pedido; estimou +60/−50 na rodada 2 (real: +27/−7). Decisões minhas: seguir etapa a etapa e deixar o conflito para o agente propor; a opção A e os cortes foram propostos pela IA e aceitos por mim.

**Revisão:** [x] golden master; [x] duas rodadas com números; [x] seis campos; [x] AGENTS.md; [x] até uma página.
