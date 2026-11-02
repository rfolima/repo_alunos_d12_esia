# Registro individual — AV1.6

**Limite: uma página, incluindo evidências essenciais.** Estudante: Rafael Lima — Data: 02/11/2026
Origem: meus registros AV1.1 a AV1.3 (baseline em miniatura) e um contexto de time descrito de forma genérica: time pequeno (4–6 pessoas) que mantém um serviço web com testes automatizados e revisão de PR. Nenhum dado do empregador; os números do time são estimativas minhas, a confirmar no levantamento.

| Campo da medição | Meu desenho |
| --- | --- |
| Pergunta (uma frase) | Trabalhar com agente com escopo declarado, plano revisado e verificação antes de aceitar reduz o tempo até "verificado" sem piorar a qualidade do que entra? |
| Decisão que depende da resposta | Manter, ampliar ou abandonar o fluxo com escopo e plano como padrão do time para mudanças com agente, e liberar ou não a tarefa candidata abaixo. |
| Métrica primária | Mediana do tempo até "verificado" (da tarefa aberta até o critério de aceite conferido por comando), por faixa de tamanho de tarefa. Não uso sugestões aceitas nem linhas geradas: medem uso, não valor. |
| Guardrail de qualidade | (a) escore de mutação nos arquivos tocados não cai; (b) taxa de revert/correção em até 2 semanas não sobe; (c) `git diff --name-only` sem arquivo fora do escopo. |
| Baseline (de onde vem, que período) | Meus AV1.1–AV1.3 (16–17/10/2026): T2 com agente verificado em ~22s; refatoração AV1.2 sem escopo ~2,5 min, 1 ida e vinda, +23/−61 e quebrou `mutacao_manual.py`; com escopo ~3,7 min, 2 idas e vindas, +27/−7, nada quebrado; mutação base 23/31 = 74% (AV1.3). No time: as 8 semanas anteriores de PRs, levantadas antes de mudar o fluxo. |
| Período e método de comparação | 8 semanas com o fluxo contra as 8 anteriores, mesma mediana por faixa de tamanho; análise por tarefa, nunca por pessoa; relato de n e dispersão, não só da mediana. |
| Confundidores previstos | Tamanho e tipo da tarefa; feriados e releases; novatos contra experientes; troca de ferramenta no período; aprendizado do próprio time; regressão à média; tarefas escolhidas por serem fáceis para o agente. |
| Como a métrica poderia ser gamificada | Fatiar tarefas em PRs minúsculos; declarar "verificado" sem rodar a verificação; testes tautológicos que passam (na AV1.3, 26 testes verdes com o mutante VIP15 vivo); escolher só tarefas fáceis; esconder retrabalho em PR novo. |

**Contramedida contra a manipulação:** "verificado" só vale com comando e saída anexados; guardrail por mutação, não por cobertura (AV1.3); amostra aleatória de PRs revisada por outra pessoa; métrica de time, nunca avaliação individual; tarefas sorteadas por tipo; rever a métrica se ela virar meta.

| Tarefa recorrente candidata | Frequência e custo atual | Verificação da saída (determinística) | Permissões mínimas e orçamento | Responsável |
| --- | --- | --- | --- | --- |
| Agente **propõe** (PR em rascunho, sem merge) atualização de dependência com CVE | Semanal a quinzenal; estimativa de 1–2 h por atualização; baixa variabilidade; raio de impacto médio | Antes de agir: pacote existe no índice e tem mantenedor (lição do `csv-export-helper`, 404, AV1.5); versão e hash fixados; breaking changes listadas; suíte completa verde; golden master 0 divergências; `git diff` só em manifesto e lockfile | Leitura do repositório e do índice; escrita só em branch própria; sem segredos; nunca sobre PR de fork; teto de ~US$ 1 e 10 min por execução; sem merge | Pessoa de plantão da semana; quem revisa aprova, não o agente |

**Limite da medição e condição para interromper ou rever:** base de n=1 por condição, tarefas fictícias de uma pessoa, tempo de T1 simulado e sem a minha revisão contada: calibra o desenho, não prova ganho. Na AV1.2 a rodada com escopo foi mais lenta, mas não quebrou nada, então só o tempo premiaria a pior rodada, e por isso existe o guardrail. Interrompo o piloto se o guardrail piorar em 2 semanas seguidas ou se uma atualização chegar a merge sem a verificação anexada; reviso a tarefa se o custo de manter as verificações superar o tempo economizado.

**Procedência/IA:** ferramenta e modelo visíveis: Claude Code, `claude-sonnet-5-5`; tarefa delegada e contexto: ler o README da aula-6, a avaliação e meus registros AV1.1–AV1.5 e redigir o rascunho e este registro; trecho aproveitado: desenho da medição, tabela da tarefa candidata e baseline; minha verificação/intervenção: pedi a leitura e o rascunho e pedi a finalização; conferência dos números contra os registros anteriores: O raciocínio e a decisão registrados são meus após revisão.

**Revisão:** [x] medição completa; [x] risco de manipulação; [x] automação com verificação; [x] limite; [x] até uma página.
