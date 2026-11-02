# Registro individual — AV3

**Limite: três páginas + até duas de evidências.** Estudante: Rafael Lima — Data: 02/11/2026  — Caminho: **B (MiniLoja: B1)**

**Modo de interação usado e por quê (raio de impacto, oráculo, familiaridade):** agente (Claude Code) em branch própria `av3-b1-r4`, com escopo escrito antes e verificação por comando. Raio de impacto baixo (uma condição em `handlers.get_pedido`, pacote fictício em memória); oráculo forte (teste negativo, 26 testes existentes, golden master de 325 entradas); familiaridade alta (R4 e `handlers.py` já revistos na AV1.5). **Alternativa comparada:** escrever à mão. Para uma linha o tempo seria parecido; o custo está em achar o ponto e provar a falha, e o agente acelera a prova. Escolhi o agente também para exercitar o fluxo que a AV1.6 propõe medir. Se o raio de impacto fosse alto ou o oráculo fraco (autorização real, dado de cliente), faria manualmente ou com aprovação passo a passo.

**Escopo declarado antes (seis campos):** `avaliacoes/av3/escopo-av3.md`, escrito antes de tocar no código. Objetivo: `get_pedido` só devolve pedido do próprio usuário (R4.1). Pode tocar: `handlers.py` (só `get_pedido`), novo teste, o escopo. Não pode: `regras.md`, `testes/`, `testes_existentes/`, dados, outros módulos, dependências. Invariantes: 11 verificações com 3 falhas (v08–v10), 26 existentes OK, próprio pedido 200, inexistente 404. Pronto quando: teste falha antes e passa depois, diff só nos arquivos listados. Pare e pergunte se: tocar teste existente ou outro módulo. **Cumprido?** Sim: `git diff --name-only` → só `caso/miniloja/handlers.py`; arquivos novos só em `avaliacoes/av3/`; barreira = esse comando.

**Verificação:** teste que falharia sem a mudança: `avaliacoes/av3/test_av3_r4.py::test_outro_usuario_nao_ve_pedido_alheio` e `test_alheio_e_inexistente_sao_indistinguiveis`. Prova: **antes** (código original) `AssertionError: 200 != 404`, `FAILED (failures=2)`; **depois** `Ran 3 tests ... OK`. **Sabotagem** em cópia (remover `or pedido["usuario_id"] != usuario_id`) → `FAILED (failures=2)`; **mutante** `!=` → `==` → `FAILED (failures=3)` (o teste do dono também morre). Demais: `--codigo caso` → 11 testes, 3 falhas (v08–v10, as de antes); `--existentes` → `Ran 26 tests ... OK`; `golden_master.py` → `325 casos gravados, 0 divergências`.
**Mudança:** `if pedido is None or pedido["usuario_id"] != usuario_id: return 404`. **Decisão de contrato:** R4 não diz o status; usei 404, igual a inexistente, para não revelar que o id existe. Se o contrato preferir 403, é troca de um número e do teste.

| O que a IA errou (o quê, onde) | Como detectei | O que corrigi e por quê (causa e impacto) |
| --- | --- | --- |
| Ao rodar o teste "antes", o `exit=0` impresso era o do `tail`, não do teste (mesmo erro da AV1.3) | Vi a saída `FAILED (failures=2)` com `exit=0` | Não usei o código de saída da cadeia como evidência; a prova é o texto `FAILED`/`OK` do próprio `unittest` |
| Teste novo inicialmente isolaria só `handlers._repo`, mas `_service` guarda a própria referência ao repositório (`pedidos.py:13`) | Li `pedidos.py` antes de rodar; o padrão da AV1.5 (`handlers._repo = ...`) não bastaria aqui | `setUp` também atribui `handlers._service.repo`; sem isso o pedido iria para outro repositório e o teste testaria o vazio |
| Pedi para o claude analisar e informar os erros encontrados. | | |

Nota de honestidade: nesta tarefa pequena o agente não mexeu fora do escopo nem alterou teste existente; não registro erros que não observei.

**Dependências novas (se houver) e checagem:** nenhuma (`requirements.txt` intocado).

| Medição do meu time | Meu desenho |
| --- | --- |
| Pergunta e decisão | O fluxo com escopo, plano revisado e verificação reduz o tempo até "verificado" sem piorar a qualidade? Decide manter, ampliar ou abandonar o fluxo e liberar a automação abaixo. |
| Métrica primária e guardrail | Mediana do tempo até "verificado" por faixa de tamanho. Guardrail: escore de mutação nos arquivos tocados, taxa de revert em 2 semanas, nenhum arquivo fora do escopo. |
| Baseline, período e método | AV1.1–AV1.3 (T2 ~22s; refatoração sem escopo ~2,5 min e quebrou a mutação, com escopo ~3,7 min e nada quebrado; mutação 74%) e, no time, as 8 semanas anteriores; 8 semanas contra 8, por tarefa, n e dispersão. |
| Risco de manipulação e contramedida | Fatiar PR, declarar "verificado" sem rodar, testes tautológicos. Contramedida: comando e saída anexados, mutação em vez de cobertura, amostra revisada por outra pessoa, métrica de time e não individual. |
| Tarefa recorrente a automatizar e verificação exigida | Agente **propõe** atualização de dependência com CVE (PR em rascunho, sem merge). Antes de agir: pacote existe no índice e tem mantenedor (AV1.5), hash fixado, suíte e golden master verdes, diff só em manifesto; sem segredos, nunca em PR de fork, teto de tempo e custo, responsável de plantão. |

**Limites e condição para rever:** uma tarefa pequena, uma pessoa, pacote fictício, tempos sem a minha revisão contada; o teste prova a regra para o par de usuários testado, não autenticação (o `usuario_id` chega como argumento, e quem o garante é outra camada, fora do escopo). Revejo o 404 se o contrato fixar 403. Interrompo o piloto da medição se o guardrail piorar 2 semanas seguidas.

**Procedência/IA:** ferramenta e modelo visíveis: Claude Code, `claude-sonnet-5-5`; tarefa delegada e contexto: ler README/rubrica da AV3, `regras.md` e `handlers.py`, escrever escopo, teste, correção, rodar as verificações e redigir este registro e a descrição do PR; trecho aproveitado: correção, teste, escopo e texto; minha verificação/intervenção: pedi a tarefa e a finalização; conferência do diff e reexecução dos comandos: O raciocínio e a decisão registrados são meus após revisão.

**Revisão:** [x] modo; [x] escopo; [x] verificação; [x] erros da IA; [x] medição e automação; [x] procedência.
