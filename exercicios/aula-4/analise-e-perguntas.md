# AV1.4 — Análise do legado, comandos manuais e perguntas

Rascunho de trabalho (não é a entrega). Linhas citadas referem-se a `caso/legado/` no estado do merge `a03a70a`.
O `README.md` do legado **não foi lido** (o enunciado avisa que pode estar desatualizado).

## 1. Comandos manuais (offline, na cópia, sem tocar no repositório)

PowerShell, na raiz do repositório:

```powershell
$env:CIENTO_OFFLINE="1"; $env:CIENTO_AMBIENTE="dev"; $env:PYTHONUTF8="1"
Remove-Item -Recurse -Force $env:TEMP\legado -ErrorAction SilentlyContinue
Copy-Item -Recurse caso\legado $env:TEMP\legado; cd $env:TEMP\legado

python -B -m cienciometria.jobs ingest                              # 120 trabalhos
python -B -m cienciometria.jobs enriquecer                          # 30 autores
python -B -m cienciometria.jobs sql scripts/corrigir_anos.sql
python -B -m cienciometria.jobs relatorio top_instituicoes
python -B -m cienciometria.jobs relatorio evolucao_anual
python -B -m cienciometria.jobs relatorio areas_autores
python -B -m cienciometria.jobs relatorio conceitos                 # ValueError: desabilitado
python -B -m cienciometria.jobs relatorio exporta_parceiro          # gera o CSV
python -B -m cienciometria.jobs refresh                             # 41 trabalhos
```

Golden master (automatiza a sequência acima e compara com a saída gravada):

```powershell
python -B exercicios/aula-4/golden-master/golden.py check     # esperado: 0 diferença(s)
python -B exercicios/aula-4/golden-master/golden.py record    # só para regravar de propósito
```

Cobertura: 11 passos, stdout/exit code, dump ordenado das 5 tabelas em 4 pontos do pipeline e o CSV do parceiro byte a byte.
Não cobre: rede real, ambiente `prod`, concorrência, `rodar_tudo.sh` em si.

## 2. As cinco perguntas — estado da evidência

| # | Afirmação | Trecho | Contraevidência | Status |
| --- | --- | --- | --- | --- |
| 1 | A ingestão começa em `ingest.run` | `ingest.py:43`; chamado de `jobs.py:23` (`ingest`), `jobs.py:10` (`refresh_diario`) e `scripts/rodar_tudo.sh:6,11` | Buscar `ingest.run` e `-m cienciometria.jobs` em todo o repo | provisória |
| 2 | Escrevem em `trabalhos`: `gravar_trabalho` **e mais três** | `ingest.py:17` (INSERT OR REPLACE); `jobs.py:12` (UPDATE citacoes); `exporta_parceiro.py:11` (UPDATE exportado); `scripts/corrigir_anos.sql:2` (via `jobs sql`, `jobs.py:30-33`) | Refuta "só `gravar_trabalho` escreve" | provisória |
| 3 | Trabalho = `concepts[0]` da API; autor = maior score entre `x_concepts` nível 0; dois critérios diferentes | `ingest.py:14-15`; `instituicoes.py:21-26`; `conceitos.py:16-26` | Conferir se algum outro lugar classifica (grep `level`, `x_concepts`) | provisória |
| 4 | Há 5 relatórios (`rel_*`), 4 habilitados; disparo só por `jobs relatorio` e `rodar_tudo.sh` (2 deles) | `relatorios.py:7-38, 41-45`; `config.ini:21`; `jobs.py:26-27`; `rodar_tudo.sh:9-10` | `rel_conceitos` existe mas falha pelo CLI (golden `07`); resolução por `getattr` (dinâmico) | provisória |
| 5 | Ambiente vem de `CIENTO_AMBIENTE`; o cron define `CIENTO_AMBIENT` (typo), então **o agendamento roda em `dev`** | `config.py:10-17`; `rodar_tudo.sh:3` | `CIENTO_OFFLINE=1` (`rodar_tudo.sh:4`, `cliente.py:26`) vale de fato; `por_pagina` (`config.ini:6`) parece sem uso | provisória |

Observações de comportamento (provadas na golden):

- `INSERT OR REPLACE` (`ingest.py:17`) zera `exportado`: o dump após `ingest` repetido tem 0 trabalhos exportados (antes: 120).
- Reingestão desfaz `corrigir_anos.sql`: `W9000007` vai de `ano=NULL` para `ano=0` após `refresh`.
- `rel_exporta_parceiro` é "relatório" com efeito colateral de escrita (`exporta_parceiro.py:11`).
- Dependência declarada `requests==2.28.1` (`requirements.txt`), mas o código usa `urllib` (`cliente.py:6-7`).

## 3. Eixos que você pediu — onde olhar

| Eixo | Pontos concretos |
| --- | --- |
| Semântica entre bibliotecas | `urllib` vs `requests` (timeout, redirecionamento, erros HTTP); `INSERT OR REPLACE` vs upsert; `json.load` e encoding; `time.sleep` de retry |
| API pública consumida por terceiros | CSV `trabalhos_por_instituicao.csv`, colunas `COLUNAS` (`exporta_parceiro.py:7`), pasta `/mnt/compartilhado/parceiro` em prod; parâmetros do OpenAlex (`concepts`, `x_concepts`, `cursor`) |
| Migração de dados | reset de `exportado`; `ano=0` vs `NULL`; `ancestrais` em JSON texto; tabelas sem chave em `autorias`/`conceitos_trabalho` |
| Concorrência | SQLite sem timeout/WAL; commit só no fim de `run` (`ingest.py:55`); cron 03:00 e `refresh` encadeados; duas execuções simultâneas |
| Segurança | `jobs sql <arquivo>` executa script arbitrário (`jobs.py:32`); `getattr` por nome (limitado pela lista habilitada); e-mail fixo no User-Agent/`mailto`; cache MD5 sem validação; `except Exception` engole erros (`cliente.py:46`) |

## 4. Perguntas para você responder

Preencha abaixo de cada pergunta.

**Sobre a leitura**

1. Na pergunta 1 você citou `gravar_trabalhos`; no código é `gravar_trabalho` (singular, `ingest.py:12`). Quer manter essa correção no registro como erro de nomenclatura do assistente ou seu?
   R: eu errei, colocar gravar_trabalho
2. Pergunta 2: você aceita que "só `gravar_trabalho` escreve em `trabalhos`" é **refutada** (há 4 escritores)? Esse é um bom candidato à "resposta que parecia certa e estava errada". Qual afirmação do assistente (ou sua) você quer usar?
   R: Poderia afirmar que um ponto que eu sozinho identifiquei apenas 1 e na realidade tinha 4. 
3. Pergunta 5: você não encontrou. Depois de ver `rodar_tudo.sh:3`, você confirma o typo `CIENTO_AMBIENT`? Que busca você faria para derrubar essa afirmação (ex.: outro lugar que defina o ambiente)?
   R: na config.py ele espera por CIENTO_AMBIENTE 
   def ambiente():
    return os.environ.get("CIENTO_AMBIENTE", _cfg["geral"]["ambiente"])
4. Pergunta 3: confirma que você leu `ingest.py:15` (conceito principal do trabalho) e `instituicoes.py:21-26` (área do autor) como critérios diferentes? Há dependência de campos que o OpenAlex atual descontinuou?
   R: Nao entendi.

**Sobre a caracterização**

5. Você prefere gravar como "caracterização mínima" quais dois relatórios? Sugestão: `top_instituicoes` e `exporta_parceiro` (os dois do cron). `evolucao_anual` é alternativa por expor o `ano=0`.
   R: evolucao_anual 
6. Aceita a golden master como está (11 passos, dev, offline) ou quer incluir `rodar_tudo.sh` executado via bash?
   R: Sim aceito e golden master. Mas como oraculo.

**Sobre o plano de migração (3 fatias)**

7. Você consultou a documentação oficial do OpenAlex? Anote URL e data de acesso. Resumo do que mudou (concepts → topics, `x_concepts`, limites, autenticação):
   R: https://help.openalex.org/api/authentication/ 
8. Sugestão de fatias: (1) trocar `urllib` por cliente isolado atrás da mesma interface, só mecânico; (2) trocar `concepts`/`x_concepts` pelos campos atuais, decisão humana (muda a classificação e os números do relatório); (3) trocar `INSERT OR REPLACE` por upsert preservando `exportado`, decisão humana. Concorda com a ordem e o que é mecânico × humano?
   R: 1 - analise qual o impacto dessa troca.
      2 - Seria para aplicar o OpenAlex?
      3 - Isso seria para impedir um sqlinjection?
      Preciso de mais informacoes para analisar essa questao.
9. Quem decide sobre o CSV do parceiro (colunas e caminho)? Que verificação você usaria (byte a byte contra a golden `09`)?
   R: Report da diferente entre relatorios gerados da golden e do refatorado para o tomada de decisao humana sobre a refatoracao realizada pela ai.

**Sobre limites e IA**

10. Qual o limite da leitura que você quer declarar (ex.: prod, `/mnt/compartilhado`, quem lê o CSV, cron real, versão atual da API)? Qual condição reabre cada resposta?
    R: Reports realizados pela AI e analisado pelo humano.
11. Declaração de IA: ferramenta/modelo (Claude Code, Sonnet 5.5), tarefa delegada (leitura, golden master, rascunho da análise) e o que você mesmo verificou.
    R: Sim, analisado e confrontado para gerar mais evidencias.
12. Seu nome e a modalidade a marcar no template ("execução/leitura própria" ou "resposta simulada")?
    R: Rafael Lima Execucao e leitura propria. fiz as leituras dos codigos para responder as 5 perguntas antes de inciar os prompt com ai e aprovei manual a execucao de cada comando.
   