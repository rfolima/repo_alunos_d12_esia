# Rascunho — AV1.6 (medir e escolher o que automatizar)

> Rascunho preparado com assistência de IA. Conferir, ajustar o contexto de time (campos marcados com **[CONFIRMAR]**) e reescrever com suas palavras antes de entregar. O registro final tem até uma página; o apêndice não conta.

# Registro individual — AV1.6

**Limite: uma página, incluindo evidências essenciais.** Estudante: Rafael Lima — Data: 02/11/2026
Origem: meus registros AV1.1 a AV1.3 (baseline em miniatura) e um contexto de time descrito de forma genérica: **time pequeno (4–6 pessoas) que mantém um serviço web com testes automatizados e revisão de PR [CONFIRMAR]**; nenhum dado do empregador.

| Campo da medição | Meu desenho |
| --- | --- |
| Pergunta (uma frase) | Trabalhar com agente **com escopo declarado, plano revisado e verificação antes de aceitar** reduz o tempo até "verificado" sem piorar a qualidade do que entra? |
| Decisão que depende da resposta | Manter, ampliar ou abandonar o fluxo com escopo e plano como padrão do time para mudanças com agente (e liberar a tarefa candidata abaixo). |
| Métrica primária | **Mediana** do tempo até "verificado" (da tarefa aberta até critério de aceite conferido por comando), por tarefa de tamanho comparável. Não mede sugestões aceitas nem linhas geradas. |
| Guardrail de qualidade | (a) escore de mutação nos arquivos tocados não pode cair; (b) taxa de revert/correção em até 2 semanas não pode subir; (c) nenhum arquivo fora do escopo no `git diff --name-only`. |
| Baseline (de onde vem, que período) | Meus AV1.1–AV1.3 (16–17/10/2026): T2 agente sem escopo → verificado em ~22s (tarefa pequena, contrato claro); refatoração AV1.2 **sem escopo ~2,5 min, 1 ida e vinda, quebrou `mutacao_manual.py`** vs **com escopo ~3,7 min, 2 idas e vindas, nada quebrado** (+27/−7 vs +23/−61); mutação base `calculo`/`descontos` 23/31 = 74% (AV1.3). No time real: **8 semanas anteriores** de PRs, a levantar antes de mudar o fluxo **[CONFIRMAR]**. |
| Período e método de comparação | 8 semanas com o fluxo vs as 8 anteriores; mesma mediana por faixa de tamanho de PR (pequeno/médio); análise por tarefa, nunca por pessoa; relatar n e dispersão, não só a mediana. |
| Confundidores previstos | Tamanho e tipo da tarefa; feriados e releases; novatos vs experientes; mudança de ferramenta no meio do período; aprendizado (o time melhora sozinho); regressão à média; tarefas escolhidas por serem fáceis para o agente. |
| Como a métrica poderia ser gamificada | Fatiar tarefas em PRs minúsculos; declarar "verificado" sem rodar a verificação; escrever testes tautológicos que passam (26 testes verdes e o mutante VIP15 vivo, AV1.3); escolher só tarefas fáceis; esconder retrabalho em PR novo. |

**Contramedida contra a manipulação:** "verificado" só vale com o comando e a saída anexados; guardrail por **mutação** (não por cobertura), como na AV1.3; amostra aleatória de PRs revisada por outra pessoa; métricas de time, nunca avaliação individual; tarefas sorteadas por tipo, não escolhidas; revisar a métrica se ela virar meta (lei de Goodhart).

| Tarefa recorrente candidata | Frequência e custo atual | Verificação da saída (determinística) | Permissões mínimas e orçamento | Responsável |
| --- | --- | --- | --- | --- |
| Agente **propõe** atualização de dependência com CVE (PR em rascunho), sem mesclar | Semanal/quinzenal; ~1–2 h por atualização **[CONFIRMAR]**; baixa variabilidade; raio de impacto médio | Antes de qualquer ação: pacote **existe** no índice e mantenedor conhecido (lição do `csv-export-helper`, 404, AV1.5); versão e hash fixados; changelog/breaking changes listados; suíte completa verde; golden master 0 divergências; `git diff` só em manifesto/lockfile | Leitura do repositório e do índice; escrita só em branch própria, **sem segredos** e **nunca sobre PR de fork**; teto de ~US$ 1 e 10 min por execução; sem merge | Pessoa de plantão da semana; aprova quem revisa, não o agente |

**Limite da medição e condição para interromper ou rever:** minha base é n=1 por condição, tarefas fictícias de um autor, tempos de T1 simulados e sem a minha revisão contada: serve para calibrar o desenho, não prova ganho. Interromper o piloto se o guardrail piorar (reverts acima do baseline, escore de mutação em queda ou arquivo fora do escopo) em 2 semanas seguidas, ou se uma atualização proposta chegar a merge sem a verificação anexada; rever a tarefa se o custo de manter as verificações superar o tempo economizado.

**Procedência/IA:** ferramenta e modelo visíveis: Claude Code, `claude-sonnet-5-5`; tarefa delegada e contexto: ler README da aula-6, avaliação e meus registros AV1.1–AV1.5 e redigir este rascunho; trecho aproveitado: **[CONFIRMAR após revisão]**; minha verificação/intervenção: **[CONFIRMAR]** (conferir os números contra os registros e escolher o contexto de time). O raciocínio e a decisão registrados são meus.

**Revisão:** [ ] medição completa; [ ] risco de manipulação; [ ] automação com verificação; [ ] limite; [ ] até uma página.

---

## Apêndice (não conta na página)

**Leitura.** Rubrica AV1: aplicação/decisão 30%, evidência 40%, limites 30%. Dica da aula: sem baseline não há ganho, há impressão; métrica de uso não é métrica de valor. Esta é uma das duas avaliações com devolutiva individual desenvolvida (força, lacuna, ação). O desenho também alimenta a meia página de medição e automação da AV3 (15%).

**Números de origem (para conferir).**
- AV1.1 T2: agente, 22:13:52 → 22:14:14 (~22s), 11/11 verificações, 26/26 existentes.
- AV1.2: rodada 1 ~2,5 min, 1 ida e vinda, +23/−61, quebrou `mutacao_manual.py`; rodada 2 ~3,7 min, 2 idas e vindas, +27/−7, mutação 18/15/3 (83%), mesmos 3 sobreviventes; golden master 325 entradas.
- AV1.3: mutação de base 31 mortos 23 (74%); 3 testes suspeitos e 2 mutantes mortos pelos meus testes.
- Atenção: AV1.2 usa **mesmo tamanho de tarefa** nas duas rodadas, mas a rodada 2 inclui revisão do plano; o ganho do escopo aparece em qualidade (nada quebrado), **não em tempo** — o baseline mostra que a métrica primária de tempo sozinha premiaria a rodada 1. Isso justifica o guardrail e vale citar no registro final.

**Pontos fracos a decidir antes de entregar.**
1. Contexto de time: preencher com algo real mas genérico (tamanho, tipo de serviço, ritmo de PRs). Hoje está suposto.
2. Tarefa candidata alternativa se preferir fugir do exemplo do guia (atualização de dependências é o exemplo "de outro time"): triagem de falha de CI com resumo da causa provável (verificável por reexecução; saída só comentário) ou geração de rascunho de testes de caracterização para módulo sem teste (verificável por mutação). A atual foi escolhida por ligar ao achado da AV1.5.
3. Cabe em uma página? Provavelmente passa um pouco: cortar confundidores e o detalhe do baseline do corpo.
4. Declarar com honestidade o que a IA fez; a AV1.3 tinha erro de procedência por atribuir a mim verificações que não fiz.
